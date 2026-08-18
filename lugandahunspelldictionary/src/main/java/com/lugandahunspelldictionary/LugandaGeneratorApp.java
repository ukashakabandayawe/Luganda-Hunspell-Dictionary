package com.lugandahunspelldictionary;

import javafx.application.Application;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.control.cell.TextFieldTableCell;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import javafx.application.Platform;
import javafx.collections.ObservableListBase;
import javafx.concurrent.Task;

import java.io.BufferedWriter;
import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collections;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicLong;

public class LugandaGeneratorApp extends Application {

    private Path defaultAffPath = Paths.get("Luganda.aff");
    private Path defaultDicPath = Paths.get("Luganda.dic");

    private enum HunspellFlagMode {
        DEFAULT,
        LONG,
        NUM
    }

    private static final int MAX_FILTER_MATCHES = 50_000;
    private static final int MAX_STATS_ROWS = 200_000;
    private static final int MAX_WORDS_BY_FLAG_COLUMNS = 300;
    private static final int MAX_WORDS_PER_FLAG_BUCKET = 5000;
    private static final int MAX_COMBO_FLAGS = 500;
    private static final long MAX_COMBO_OPS = 25_000_000L;

    private static final class ErrorStore {
        private final Map<Long, Set<String>> errorsByRowKey = new LinkedHashMap<>();

        public boolean isError(long rowKey, String root) {
            Set<String> set = errorsByRowKey.get(rowKey);
            return set != null && set.contains(root);
        }

        public void toggle(long rowKey, String root) {
            Set<String> set = errorsByRowKey.get(rowKey);
            if (set == null) {
                set = new LinkedHashSet<>();
                errorsByRowKey.put(rowKey, set);
            }
            if (!set.add(root)) {
                set.remove(root);
                if (set.isEmpty()) {
                    errorsByRowKey.remove(rowKey);
                }
            }
        }
    }

    private static final class LazyResultsList extends ObservableListBase<Result> {
        private final List<LugandaAffParser.AffixEntry> simpleEntries;
        private final List<LugandaAffParser.AffixEntry> prefixEntries;
        private final List<LugandaAffParser.AffixEntry> suffixEntries;
        private final long comboCount;
        private final ErrorStore errorStore;

        LazyResultsList(
                List<LugandaAffParser.AffixEntry> simpleEntries,
                List<LugandaAffParser.AffixEntry> prefixEntries,
                List<LugandaAffParser.AffixEntry> suffixEntries,
                ErrorStore errorStore
        ) {
            this.simpleEntries = simpleEntries == null ? Collections.emptyList() : simpleEntries;
            this.prefixEntries = prefixEntries == null ? Collections.emptyList() : prefixEntries;
            this.suffixEntries = suffixEntries == null ? Collections.emptyList() : suffixEntries;
            this.errorStore = errorStore;
            this.comboCount = (long) this.prefixEntries.size() * (long) this.suffixEntries.size();
        }

        @Override
        public Result get(int index) {
            long rowKey = index;
            int simpleCount = simpleEntries.size();

            if (index < simpleCount) {
                LugandaAffParser.AffixEntry ae = simpleEntries.get(index);
                return Result.single(rowKey, ae, errorStore);
            }

            long comboStart = simpleCount;
            long comboEndExclusive = comboStart + comboCount;
            if (rowKey >= comboStart && rowKey < comboEndExclusive) {
                long comboIndex = rowKey - comboStart;
                int suffixCount = suffixEntries.size();
                int pIndex = (int) (comboIndex / suffixCount);
                int sIndex = (int) (comboIndex % suffixCount);
                LugandaAffParser.AffixEntry p = prefixEntries.get(pIndex);
                LugandaAffParser.AffixEntry s = suffixEntries.get(sIndex);
                return Result.combo(rowKey, p, s, errorStore);
            }

            return Result.bareRoot(rowKey, errorStore);
        }

        @Override
        public int size() {
            long total = (long) simpleEntries.size() + comboCount + 1L;
            return total > Integer.MAX_VALUE ? Integer.MAX_VALUE : (int) total;
        }

        // public boolean isTruncatedByIntMax() {
        //     long total = (long) simpleEntries.size() + comboCount + 1L;
        //     return total > Integer.MAX_VALUE;
        // }
    }

    public static class Result {
        private enum Kind { SINGLE, COMBO, ROOT }

        private final Kind kind;
        private final long rowKey;
        private final String flag;
        private final String affix;
        private final LugandaAffParser.AffixEntry single;
        private final LugandaAffParser.AffixEntry prefix;
        private final LugandaAffParser.AffixEntry suffix;
        private final ErrorStore errorStore;

        private Result(Kind kind,
                       long rowKey,
                       String flag,
                       String affix,
                       LugandaAffParser.AffixEntry single,
                       LugandaAffParser.AffixEntry prefix,
                       LugandaAffParser.AffixEntry suffix,
                       ErrorStore errorStore) {
            this.kind = kind;
            this.rowKey = rowKey;
            this.flag = flag;
            this.affix = affix;
            this.single = single;
            this.prefix = prefix;
            this.suffix = suffix;
            this.errorStore = errorStore;
        }

        @SuppressWarnings("exports")
        public static Result single(long rowKey, LugandaAffParser.AffixEntry ae, ErrorStore errorStore) {
            String affixDisplay = (ae == null || ae.affix == null || ae.affix.isEmpty()) ? "0" : ae.affix;
            String flag = ae == null ? "" : ae.flag;
            return new Result(Kind.SINGLE, rowKey, flag, affixDisplay, ae, null, null, errorStore);
        }

        @SuppressWarnings("exports")
        public static Result combo(long rowKey, LugandaAffParser.AffixEntry prefix, LugandaAffParser.AffixEntry suffix, ErrorStore errorStore) {
            String pAff = (prefix == null || prefix.affix == null || prefix.affix.isEmpty()) ? "0" : prefix.affix;
            String sAff = (suffix == null || suffix.affix == null || suffix.affix.isEmpty()) ? "0" : suffix.affix;
            String affixDisplay = pAff + " + " + sAff;
            String flag = (prefix == null ? "" : prefix.flag) + "+" + (suffix == null ? "" : suffix.flag);
            return new Result(Kind.COMBO, rowKey, flag, affixDisplay, null, prefix, suffix, errorStore);
        }

        public static Result bareRoot(long rowKey, ErrorStore errorStore) {
            return new Result(Kind.ROOT, rowKey, "ROOT", "", null, null, null, errorStore);
        }

        public String getFlag() { return flag; }
        public String getAffix() { return affix; }
        public LugandaAffParser.AffixEntry getAffixEntry() { return single; }

        public String getWordForRoot(String root) {
            if (root == null || root.isEmpty()) return "";
            if (kind == Kind.ROOT) {
                return root;
            }
            if (kind == Kind.SINGLE) {
                String word = LugandaAffParser.apply(single, root);
                return word == null ? "" : word;
            }
            // COMBO
            String mid = LugandaAffParser.apply(prefix, root);
            if (mid == null) return "";
            String word = LugandaAffParser.apply(suffix, mid);
            return word == null ? "" : word;
        }

        public boolean isError(String root) {
            return errorStore != null && errorStore.isError(rowKey, root);
        }

        public void toggleError(String root) {
            if (errorStore == null) return;
            errorStore.toggle(rowKey, root);
        }
    }

    @Override
    public void start(Stage stage) {
        stage.setTitle("Luganda Affix Generator");

        // Scene 1: ask number of roots
        Spinner<Integer> countSpinner = new Spinner<>(1, 200, 1);
        Button nextBtn = new Button("Next");
        Label affLabel = new Label("Aff file: " + defaultAffPath.toAbsolutePath());
        Button chooseAff = new Button("Choose .aff");

        chooseAff.setOnAction(ev -> {
            FileChooser fc = new FileChooser();
            fc.setTitle("Select .aff file");
            fc.getExtensionFilters().add(new FileChooser.ExtensionFilter("AFF files", "*.aff"));
            File f = fc.showOpenDialog(stage);
            if (f != null) {
                defaultAffPath = f.toPath();
                affLabel.setText("Aff file: " + defaultAffPath.toAbsolutePath());
            }
        });

        HBox topHBox = new HBox(8, new Label("Number of root words:"), countSpinner, nextBtn);
        topHBox.setPadding(new Insets(12));
        VBox scene1 = new VBox(8, affLabel, chooseAff, topHBox);
        scene1.setPadding(new Insets(12));

        Scene sceneOne = new Scene(scene1, 600, 150);

        // Scene 2 will be built dynamically
        nextBtn.setOnAction(e -> buildRootInputScene(stage, countSpinner.getValue(), sceneOne));

        stage.setScene(sceneOne);
        stage.show();
    }

    private void buildRootInputScene(Stage stage, int count, Scene prevScene) {
        GridPane grid = new GridPane();
        grid.setVgap(6);
        grid.setHgap(6);
        grid.setPadding(new Insets(12));

        List<TextField> fields = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            TextField tf = new TextField();
            tf.setPromptText("root " + (i+1));
            fields.add(tf);
            grid.add(new Label("Root " + (i+1) + ":"), 0, i);
            grid.add(tf, 1, i);
        }

        Button gen = new Button("Generate");
        Button back = new Button("Back");
        HBox buttons = new HBox(8, back, gen);

        VBox v = new VBox(8, grid, buttons);
        v.setPadding(new Insets(12));
        Scene scene2 = new Scene(v, 800, Math.min(600, 120 + count * 30));

        back.setOnAction(ev -> stage.setScene(prevScene));

        gen.setOnAction(ev -> {
            List<String> roots = new ArrayList<>();
            for (TextField tf : fields) {
                String t = tf.getText();
                if (t != null && !t.trim().isEmpty()) roots.add(t.trim());
            }
            try {
                showResultsScene(stage, roots);
            } catch (Exception ex) {
                showError("Error generating words: " + ex.getMessage());
            }
        });

        stage.setScene(scene2);
    }

    private void showResultsScene(Stage stage, List<String> roots) throws IOException {
        Map<String, LugandaAffParser.AffixGroup> affMap = LugandaAffParser.parseAffWithMeta(defaultAffPath);
        
        // Count total rules (including combinable prefix+suffix cross-application)
        int totalRules = 0;
        List<LugandaAffParser.AffixGroup> combinablePrefixes = new ArrayList<>();
        List<LugandaAffParser.AffixGroup> combinableSuffixes = new ArrayList<>();

        for (LugandaAffParser.AffixGroup grp : affMap.values()) {
            if (grp == null) continue;
            totalRules += grp.entries.size();
            if (grp.combinable && grp.type == 'P') {
                combinablePrefixes.add(grp);
            } else if (grp.combinable && grp.type == 'S') {
                combinableSuffixes.add(grp);
            }
        }

        // Estimated number of combo rules (prefix then suffix) for stats display
        int comboRules = 0;
        for (LugandaAffParser.AffixGroup p : combinablePrefixes) {
            for (LugandaAffParser.AffixGroup s : combinableSuffixes) {
                comboRules += p.entries.size() * s.entries.size();
            }
        }
        totalRules += comboRules;

        TableView<Result> table = new TableView<>();

        // Statistics panel
        VBox statsPanel = new VBox(8);
        statsPanel.setPadding(new Insets(12));
        Label statsTitle = new Label("Error Statistics");
        statsTitle.setStyle("-fx-font-weight: bold; -fx-font-size: 14px;");
        statsPanel.getChildren().add(statsTitle);
        
        Label rulesInfo = new Label("Total Rules: " + totalRules);
        rulesInfo.setStyle("-fx-font-size: 11px; -fx-text-fill: #666;");
        statsPanel.getChildren().add(rulesInfo);
        statsPanel.getChildren().add(new Separator());

        Map<String, Label> statsLabels = new LinkedHashMap<>();
        for (String root : roots) {
            Label label = new Label(root + ": 0.0% (0/0)");
            statsLabels.put(root, label);
            statsPanel.getChildren().add(label);
        }

        // Add row number column (avoid indexOf() for huge/lazy lists)
        TableColumn<Result, Void> noCol = new TableColumn<>("No.");
        noCol.setPrefWidth(50);
        noCol.setSortable(false);
        noCol.setCellValueFactory(cd -> new javafx.beans.property.SimpleObjectProperty<>(null));
        noCol.setCellFactory(col -> new TableCell<Result, Void>() {
            @Override
            protected void updateItem(Void item, boolean empty) {
                super.updateItem(item, empty);
                setText(empty ? null : String.valueOf(getIndex() + 1));
                setStyle("-fx-alignment: CENTER;");
            }
        });
        table.getColumns().add(noCol);
        
        // Add affix column
        TableColumn<Result, String> affixCol = new TableColumn<>("AFX");
        affixCol.setPrefWidth(80);
        affixCol.setCellValueFactory(cellData -> {
            String affix = cellData.getValue().getAffix();
            return new javafx.beans.property.SimpleStringProperty(affix);
        });
        affixCol.setStyle("-fx-alignment: CENTER;");
        table.getColumns().add(affixCol);

        // Add columns for each root
        for (String root : roots) {
            final String r = root;
            TableColumn<Result, String> col = new TableColumn<>(r);
            col.setPrefWidth(150);
            col.setCellValueFactory(cellData -> {
                return new javafx.beans.property.SimpleStringProperty(cellData.getValue().getWordForRoot(r));
            });
            
            // Custom cell factory to make cells clickable and show error state
            col.setCellFactory(column -> new TableCell<Result, String>() {
                @Override
                protected void updateItem(String item, boolean empty) {
                    super.updateItem(item, empty);
                    if (empty || item == null || item.isEmpty()) {
                        setText(null);
                        setStyle("");
                        setOnMouseClicked(null);
                    } else {
                        setText(item);
                        Result result = getTableView().getItems().get(getIndex());
                        
                        // Update style based on error state
                        if (result.isError(r)) {
                            setStyle("-fx-background-color: #ffcccc; -fx-cursor: hand;");
                        } else {
                            setStyle("-fx-cursor: hand;");
                        }
                        
                        // Make clickable to toggle error
                        setOnMouseClicked(event -> {
                            result.toggleError(r);
                            updateItem(item, false); // Refresh cell
                            maybeUpdateStatistics(roots, table.getItems(), statsLabels);
                        });
                    }
                }
            });
            
            table.getColumns().add(col);
        }

        // Add flag column
        TableColumn<Result, String> flagCol = new TableColumn<>("Flag");
        flagCol.setCellValueFactory(new PropertyValueFactory<>("flag"));
        flagCol.setPrefWidth(120);
        table.getColumns().add(flagCol);

        ErrorStore errorStore = new ErrorStore();

        // Flatten simple rules (flag-specific entries)
        List<LugandaAffParser.AffixEntry> simpleEntries = new ArrayList<>();
        for (Map.Entry<String, LugandaAffParser.AffixGroup> flagEntry : affMap.entrySet()) {
            LugandaAffParser.AffixGroup group = flagEntry.getValue();
            if (group == null || group.entries == null) continue;
            simpleEntries.addAll(group.entries);
        }

        // Flatten combinable prefix/suffix entries for cross-product view
        List<LugandaAffParser.AffixEntry> comboPrefixes = new ArrayList<>();
        for (LugandaAffParser.AffixGroup g : combinablePrefixes) {
            if (g == null || g.entries == null) continue;
            comboPrefixes.addAll(g.entries);
        }
        List<LugandaAffParser.AffixEntry> comboSuffixes = new ArrayList<>();
        for (LugandaAffParser.AffixGroup g : combinableSuffixes) {
            if (g == null || g.entries == null) continue;
            comboSuffixes.addAll(g.entries);
        }

        LazyResultsList baseRows = new LazyResultsList(simpleEntries, comboPrefixes, comboSuffixes, errorStore);
        ObservableList<Result> filteredRows = FXCollections.observableArrayList();
        table.setItems(baseRows);
        
        // Search bar
        TextField searchField = new TextField();
        searchField.setPromptText("Search for a word...");
        searchField.setPrefWidth(300);
        
        ToggleButton exactMatchBtn = new ToggleButton("Exact Match");
        exactMatchBtn.setStyle("-fx-font-size: 11px; -fx-padding: 5px 10px;");
        
        searchField.textProperty().addListener((obs, oldVal, newVal) -> {
            scheduleSearch(roots, table, baseRows, filteredRows, statsLabels, rulesInfo, searchField, exactMatchBtn);
        });
        
        exactMatchBtn.selectedProperty().addListener((obs, oldVal, newVal) -> {
            scheduleSearch(roots, table, baseRows, filteredRows, statsLabels, rulesInfo, searchField, exactMatchBtn);
        });
        
        Button clearSearch = new Button("Clear");
        clearSearch.setOnAction(e -> searchField.clear());
        
        HBox searchBox = new HBox(8, new Label("Search:"), searchField, exactMatchBtn, clearSearch);
        searchBox.setPadding(new Insets(8));
        
        // Initialize statistics: only compute when list is reasonably sized
        maybeUpdateStatistics(roots, table.getItems(), statsLabels);

        Button save = new Button("Save CSV");
        Button back = new Button("Back");
        Button clearErrors = new Button("Clear All Errors");
        Button refresh = new Button("Refresh from .aff");
        Button errorTable = new Button("Error Table");
        Button flagTable = new Button("Words by Flag");
        Button generateRules = new Button("Generate Rules");
        errorTable.setDisable(true);//No longer useful
        generateRules.setDisable(true);//No longer useful
        clearErrors.setDisable(true);//No longer useful
        
        clearErrors.setOnMouseClicked(e -> {
            for (Result r : filteredRows) {
                for (String root : roots) {
                    if (r.isError(root)) {
                        r.toggleError(root);
                    }
                }
            }
            table.refresh();
            maybeUpdateStatistics(roots, filteredRows, statsLabels);
        });
        
        refresh.setOnAction(e -> {
            try {
                showResultsScene(stage, roots);
            } catch (IOException ex) {
                showError("Error reloading .aff file: " + ex.getMessage());
            }
        });
        
        errorTable.setOnAction(e -> showErrorTable(filteredRows.isEmpty() ? FXCollections.observableArrayList(table.getItems()) : filteredRows, roots));
        flagTable.setOnAction(e -> {
            showWordsByFlagTableFromAff(affMap, roots);
        });
        generateRules.setOnAction(e -> showRuleGenerator(filteredRows.isEmpty() ? FXCollections.observableArrayList(table.getItems()) : filteredRows, roots));
        
        HBox h = new HBox(8, back, save, clearErrors, refresh, errorTable, flagTable, generateRules);
        h.setPadding(new Insets(8));

        VBox topBox = new VBox(searchBox, h);

        BorderPane bp = new BorderPane();
        bp.setCenter(table);
        bp.setRight(statsPanel);
        bp.setBottom(topBox);

        Scene scene = new Scene(bp, 1000, 520);

        back.setOnAction(ev -> start(stage));

        save.setOnAction(ev -> {
            FileChooser fc = new FileChooser();
            fc.setTitle("Save results as CSV");
            fc.getExtensionFilters().add(new FileChooser.ExtensionFilter("CSV files", "*.csv"));
            File f = fc.showSaveDialog(stage);
            if (f != null) {
                try (BufferedWriter bw = java.nio.file.Files.newBufferedWriter(f.toPath(), StandardCharsets.UTF_8)) {
                    // Write header
                    for (String root : roots) {
                        bw.write(escapeCsv(root));
                        bw.write(',');
                    }
                    bw.write("flag\n");
                    
                    // Write rows (current table view)
                    for (Result r : table.getItems()) {
                        for (String root : roots) {
                            bw.write(escapeCsv(r.getWordForRoot(root)));
                            bw.write(',');
                        }
                        bw.write(escapeCsv(r.getFlag()));
                        bw.write('\n');
                    }
                } catch (IOException ex) {
                    showError("Failed to save CSV: " + ex.getMessage());
                }
            }
        });

        stage.setScene(scene);
    }

    private void showErrorTable(ObservableList<Result> allRows, List<String> roots) {
        Stage errorStage = new Stage();
        errorStage.setTitle("Error Words Table");
        
        // Collect error words per root
        Map<String, List<String>> errorsByRoot = new LinkedHashMap<>();
        for (String root : roots) {
            errorsByRoot.put(root, new ArrayList<>());
        }
        
        // Gather all error words for each root
        for (Result r : allRows) {
            for (String root : roots) {
                if (r.isError(root)) {
                    String word = r.getWordForRoot(root);
                    if (!word.isEmpty()) {
                        errorsByRoot.get(root).add(word);
                    }
                }
            }
        }
        
        // Find max number of errors across all roots
        int maxErrors = 0;
        for (List<String> errors : errorsByRoot.values()) {
            maxErrors = Math.max(maxErrors, errors.size());
        }
        
        // Create rows with error words aligned by index
        ObservableList<Map<String, String>> errorRows = FXCollections.observableArrayList();
        for (int i = 0; i < maxErrors; i++) {
            Map<String, String> row = new LinkedHashMap<>();
            for (String root : roots) {
                List<String> errors = errorsByRoot.get(root);
                if (i < errors.size()) {
                    row.put(root, errors.get(i));
                } else {
                    row.put(root, "");
                }
            }
            errorRows.add(row);
        }
        
        TableView<Map<String, String>> errorTable = new TableView<>();
        
        // Add row number column
        TableColumn<Map<String, String>, String> noCol = new TableColumn<>("No.");
        noCol.setPrefWidth(50);
        noCol.setCellValueFactory(cd -> new javafx.beans.property.SimpleStringProperty(""));
        noCol.setCellFactory(col -> new TableCell<Map<String, String>, String>() {
            @Override
            protected void updateItem(String item, boolean empty) {
                super.updateItem(item, empty);
                setText(empty ? null : String.valueOf(getIndex() + 1));
                setStyle("-fx-alignment: CENTER;");
            }
        });
        noCol.setStyle("-fx-alignment: CENTER;");
        errorTable.getColumns().add(noCol);
        
        // Add columns for each root
        for (String root : roots) {
            final String r = root;
            TableColumn<Map<String, String>, String> col = new TableColumn<>(r);
            col.setPrefWidth(150);
            col.setCellValueFactory(cellData -> {
                String word = cellData.getValue().getOrDefault(r, "");
                return new javafx.beans.property.SimpleStringProperty(word);
            });
            
            // Style error cells
            col.setCellFactory(column -> new TableCell<Map<String, String>, String>() {
                @Override
                protected void updateItem(String item, boolean empty) {
                    super.updateItem(item, empty);
                    if (empty || item == null || item.isEmpty()) {
                        setText(null);
                        setStyle("");
                    } else {
                        setText(item);
                        setStyle("-fx-background-color: #ffcccc;");
                    }
                }
            });
            
            errorTable.getColumns().add(col);
        }
        
        errorTable.setItems(errorRows);
        
        // Statistics panel
        VBox statsPanel = new VBox(8);
        statsPanel.setPadding(new Insets(12));
        Label statsTitle = new Label("Error Summary");
        statsTitle.setStyle("-fx-font-weight: bold; -fx-font-size: 14px;");
        statsPanel.getChildren().add(statsTitle);
        statsPanel.getChildren().add(new Separator());
        
        for (String root : roots) {
            int errorCount = errorsByRoot.get(root).size();
            Label label = new Label(root + ": " + errorCount + " errors");
            statsPanel.getChildren().add(label);
        }
        
        Label totalLabel = new Label("Total Rows: " + maxErrors);
        totalLabel.setStyle("-fx-font-weight: bold; -fx-padding: 10 0 0 0;");
        statsPanel.getChildren().add(new Separator());
        statsPanel.getChildren().add(totalLabel);
        
        Button exportErrors = new Button("Export Errors CSV");
        exportErrors.setOnAction(e -> {
            FileChooser fc = new FileChooser();
            fc.setTitle("Save errors as CSV");
            fc.getExtensionFilters().add(new FileChooser.ExtensionFilter("CSV files", "*.csv"));
            File f = fc.showSaveDialog(errorStage);
            if (f != null) {
                try (BufferedWriter bw = java.nio.file.Files.newBufferedWriter(f.toPath(), StandardCharsets.UTF_8)) {
                    // Write header
                    for (String root : roots) {
                        bw.write(escapeCsv(root));
                        if (roots.indexOf(root) < roots.size() - 1) {
                            bw.write(',');
                        }
                    }
                    bw.write('\n');
                    
                    // Write error rows
                    for (Map<String, String> row : errorRows) {
                        for (String root : roots) {
                            bw.write(escapeCsv(row.getOrDefault(root, "")));
                            if (roots.indexOf(root) < roots.size() - 1) {
                                bw.write(',');
                            }
                        }
                        bw.write('\n');
                    }
                } catch (IOException ex) {
                    showError("Failed to save errors CSV: " + ex.getMessage());
                }
            }
        });
        
        Button closeBtn = new Button("Close");
        closeBtn.setOnAction(e -> errorStage.close());
        
        HBox buttonBox = new HBox(8, closeBtn, exportErrors);
        buttonBox.setPadding(new Insets(8));
        
        BorderPane bp = new BorderPane();
        bp.setCenter(errorTable);
        bp.setRight(statsPanel);
        bp.setBottom(buttonBox);
        
        Scene scene = new Scene(bp, 1000, 520);
        errorStage.setScene(scene);
        errorStage.show();
    }

    @SuppressWarnings("unused")
    private void showWordsByFlagTable(ObservableList<Result> allRows, List<String> roots) {
        Stage flagStage = new Stage();
        flagStage.setTitle("Words by Flag");

        // Determine flags (in encounter order), excluding ROOT
        List<String> flags = new ArrayList<>();
        for (Result r : allRows) {
            String flag = r.getFlag();
            if (flag == null) continue;
            if ("ROOT".equalsIgnoreCase(flag)) continue;
            if (!flags.contains(flag)) {
                flags.add(flag);
            }
        }

        // root -> flag -> unique words (preserve encounter order)
        Map<String, Map<String, Set<String>>> wordsByRootFlag = new LinkedHashMap<>();
        for (String root : roots) {
            Map<String, Set<String>> byFlag = new LinkedHashMap<>();
            for (String flag : flags) {
                byFlag.put(flag, new LinkedHashSet<>());
            }
            wordsByRootFlag.put(root, byFlag);
        }

        for (Result r : allRows) {
            String flag = r.getFlag();
            if (flag == null) continue;
            if ("ROOT".equalsIgnoreCase(flag)) continue;
            for (String root : roots) {
                String word = r.getWordForRoot(root);
                if (word != null && !word.isEmpty()) {
                    Map<String, Set<String>> byFlag = wordsByRootFlag.get(root);
                    if (byFlag != null) {
                        byFlag.computeIfAbsent(flag, k -> new LinkedHashSet<>()).add(word);
                    }
                }
            }
        }

        // Compute maximum number of words across all (root, flag) buckets
        int maxRows = 0;
        for (String root : roots) {
            Map<String, Set<String>> byFlag = wordsByRootFlag.get(root);
            if (byFlag == null) continue;
            for (Set<String> set : byFlag.values()) {
                maxRows = Math.max(maxRows, set.size());
            }
        }

        // Build aligned rows
        ObservableList<Map<String, String>> tableRows = FXCollections.observableArrayList();
        for (int i = 0; i < maxRows; i++) {
            Map<String, String> row = new LinkedHashMap<>();
            for (String root : roots) {
                Map<String, Set<String>> byFlag = wordsByRootFlag.get(root);
                if (byFlag == null) continue;
                for (String flag : flags) {
                    Set<String> set = byFlag.get(flag);
                    String key = root + "|" + flag;
                    if (set == null || set.isEmpty()) {
                        row.put(key, "");
                    } else {
                        List<String> list = new ArrayList<>(set);
                        row.put(key, i < list.size() ? list.get(i) : "");
                    }
                }
            }
            tableRows.add(row);
        }

        TableView<Map<String, String>> tv = new TableView<>(tableRows);

        TableColumn<Map<String, String>, String> noCol = new TableColumn<>("No.");
        noCol.setPrefWidth(50);
        noCol.setCellValueFactory(cd -> new javafx.beans.property.SimpleStringProperty(""));
        noCol.setCellFactory(col -> new TableCell<Map<String, String>, String>() {
            @Override
            protected void updateItem(String item, boolean empty) {
                super.updateItem(item, empty);
                setText(empty ? null : String.valueOf(getIndex() + 1));
                setStyle("-fx-alignment: CENTER;");
            }
        });
        noCol.setStyle("-fx-alignment: CENTER;");
        tv.getColumns().add(noCol);

        // Flag selection controls: root -> selected flags
        Map<String, Set<String>> selectedFlagsByRoot = new LinkedHashMap<>();
        for (String root : roots) {
            selectedFlagsByRoot.put(root, new LinkedHashSet<>());
        }

        // Nested columns: root -> flags
        for (String root : roots) {
            TableColumn<Map<String, String>, String> rootCol = new TableColumn<>(root);
            for (String flag : flags) {
                final String key = root + "|" + flag;
                // Header checkbox lets user select this flag for this root
                CheckBox headerCheck = new CheckBox(flag);
                headerCheck.setOnAction(e -> {
                    Set<String> set = selectedFlagsByRoot.getOrDefault(root, new LinkedHashSet<>());
                    if (headerCheck.isSelected()) {
                        set.add(flag);
                    } else {
                        set.remove(flag);
                    }
                    selectedFlagsByRoot.put(root, set);
                });

                TableColumn<Map<String, String>, String> flagCol = new TableColumn<>();
                flagCol.setGraphic(headerCheck);
                flagCol.setPrefWidth(140);
                flagCol.setStyle("-fx-alignment: CENTER;");
                flagCol.setCellValueFactory(cd -> new javafx.beans.property.SimpleStringProperty(cd.getValue().getOrDefault(key, "")));
                rootCol.getColumns().add(flagCol);
            }
            tv.getColumns().add(rootCol);
        }

        Label info = new Label("Grouped by root and flag (duplicates removed). Select flags in headers, then Apply to update Luganda.dic.");
        info.setStyle("-fx-font-size: 11px; -fx-text-fill: #666;");

        Button applyBtn = new Button("Apply to Luganda.dic");
        applyBtn.setStyle("-fx-font-weight: bold;");
        applyBtn.setOnAction(e -> {
            Map<String, Set<String>> toApply = new LinkedHashMap<>();
            for (Map.Entry<String, Set<String>> entry : selectedFlagsByRoot.entrySet()) {
                Set<String> sel = entry.getValue();
                if (sel == null || sel.isEmpty()) continue;
                LinkedHashSet<String> flat = new LinkedHashSet<>();
                for (String f : sel) {
                    if (f == null) continue;
                    String[] parts = f.split("\\+");
                    for (String p : parts) {
                        String t = p == null ? "" : p.trim();
                        if (!t.isEmpty()) flat.add(t);
                    }
                }
                if (!flat.isEmpty()) {
                    toApply.put(entry.getKey(), flat);
                }
            }

            if (toApply.isEmpty()) {
                Alert a = new Alert(Alert.AlertType.INFORMATION, "No flags selected.", ButtonType.OK);
                a.setHeaderText(null);
                a.showAndWait();
                return;
            }

            StringBuilder summary = new StringBuilder();
            for (Map.Entry<String, Set<String>> entry : toApply.entrySet()) {
                summary.append(entry.getKey()).append(": ");
                summary.append(String.join(", ", entry.getValue()));
                summary.append("\n");
            }

            Alert confirm = new Alert(
                    Alert.AlertType.CONFIRMATION,
                    "Apply these flags to stems in " + defaultDicPath.toAbsolutePath() + "?\n\n" + summary,
                    ButtonType.OK,
                    ButtonType.CANCEL
            );
            confirm.setHeaderText("Confirm updating Luganda.dic");
            confirm.showAndWait();
            if (confirm.getResult() != ButtonType.OK) {
                return;
            }

            try {
                HunspellFlagMode mode = detectFlagMode(defaultAffPath);
                ApplyResult result = applyFlagsToDic(defaultDicPath, toApply, mode);
                Alert ok = new Alert(Alert.AlertType.INFORMATION, result.toUserMessage(), ButtonType.OK);
                ok.setHeaderText("Luganda.dic updated");
                ok.showAndWait();
                // Clear UI selections after success
                for (TableColumn<Map<String, String>, ?> top : tv.getColumns()) {
                    if (top == noCol) continue;
                    for (TableColumn<Map<String, String>, ?> sub : top.getColumns()) {
                        javafx.scene.Node graphic = sub.getGraphic();
                        if (graphic instanceof CheckBox) {
                            ((CheckBox) graphic).setSelected(false);
                        }
                    }
                }
                for (String root : roots) {
                    selectedFlagsByRoot.put(root, new LinkedHashSet<>());
                }
            } catch (Exception ex) {
                showError("Failed to update Luganda.dic: " + ex.getMessage());
            }
        });

        Button closeBtn = new Button("Close");
        closeBtn.setOnAction(e -> flagStage.close());
        HBox bottom = new HBox(8, closeBtn, applyBtn);
        bottom.setPadding(new Insets(8));

        BorderPane bp = new BorderPane();
        bp.setTop(new VBox(6, info, new Separator()));
        bp.setCenter(tv);
        bp.setBottom(bottom);

        Scene scene = new Scene(bp, 1200, 600);
        flagStage.setScene(scene);
        flagStage.show();
    }

    private static final class WordsByFlagModel {
        private final List<String> flags;
        // root -> flag -> ordered words
        private final Map<String, Map<String, List<String>>> words;
        private final boolean comboIncluded;
        private final boolean truncated;

        private WordsByFlagModel(List<String> flags,
                                 Map<String, Map<String, List<String>>> words,
                                 boolean comboIncluded,
                                 boolean truncated) {
            this.flags = flags;
            this.words = words;
            this.comboIncluded = comboIncluded;
            this.truncated = truncated;
        }
    }

    private void showWordsByFlagTableFromAff(Map<String, LugandaAffParser.AffixGroup> affMap, List<String> roots) {
        Stage flagStage = new Stage();
        flagStage.setTitle("Words by Flag");

        Label status = new Label("Building words-by-flag view…");
        status.setStyle("-fx-font-size: 11px; -fx-text-fill: #666;");
        ProgressIndicator pi = new ProgressIndicator();
        pi.setPrefSize(40, 40);
        Button cancelBtn = new Button("Cancel");

        VBox loading = new VBox(10, status, pi, cancelBtn);
        loading.setPadding(new Insets(12));
        Scene loadingScene = new Scene(loading, 520, 160);
        flagStage.setScene(loadingScene);
        flagStage.show();

        Task<WordsByFlagModel> task = new Task<WordsByFlagModel>() {
            @Override
            protected WordsByFlagModel call() {
                if (roots == null || roots.isEmpty()) {
                    return new WordsByFlagModel(Collections.emptyList(), Collections.emptyMap(), false, false);
                }
                if (affMap == null || affMap.isEmpty()) {
                    return new WordsByFlagModel(Collections.emptyList(), Collections.emptyMap(), false, false);
                }

                Map<String, Map<String, LinkedHashSet<String>>> tmp = new LinkedHashMap<>();
                for (String root : roots) {
                    tmp.put(root, new LinkedHashMap<>());
                }
                LinkedHashSet<String> flagsEncountered = new LinkedHashSet<>();
                boolean truncated = false;

                // Simple (non-combo) flags: only include flags that actually generate at least one word.
                int rootIndex = 0;
                for (String root : roots) {
                    if (isCancelled()) break;
                    rootIndex++;
                    updateMessage("Processing roots " + rootIndex + "/" + roots.size() + "…");

                    for (Map.Entry<String, LugandaAffParser.AffixGroup> entry : affMap.entrySet()) {
                        if (isCancelled()) break;
                        String flag = entry.getKey();
                        if (flag == null) continue;
                        if ("ROOT".equalsIgnoreCase(flag)) continue;
                        LugandaAffParser.AffixGroup group = entry.getValue();
                        if (group == null || group.entries == null) continue;
                        if (group.entries.isEmpty()) continue;

                        for (LugandaAffParser.AffixEntry ae : group.entries) {
                            if (isCancelled()) break;
                            String word = LugandaAffParser.apply(ae, root);
                            if (word == null || word.isEmpty()) continue;

                            flagsEncountered.add(flag);
                            Map<String, LinkedHashSet<String>> byFlag = tmp.get(root);
                            LinkedHashSet<String> set = byFlag.computeIfAbsent(flag, k -> new LinkedHashSet<>());
                            if (set.size() >= MAX_WORDS_PER_FLAG_BUCKET) {
                                truncated = true;
                                continue;
                            }
                            set.add(word);
                        }
                    }
                }

                // Optionally include combinable prefix+suffix (combo) flags, but only when the projected work is safe.
                List<LugandaAffParser.AffixEntry> prefixEntries = new ArrayList<>();
                List<LugandaAffParser.AffixEntry> suffixEntries = new ArrayList<>();
                List<String> prefixFlags = new ArrayList<>();
                List<String> suffixFlags = new ArrayList<>();

                for (Map.Entry<String, LugandaAffParser.AffixGroup> entry : affMap.entrySet()) {
                    LugandaAffParser.AffixGroup group = entry.getValue();
                    if (group == null || group.entries == null) continue;
                    String flag = entry.getKey();
                    if (flag == null) continue;
                    if (group.combinable && group.type == 'P') {
                        prefixEntries.addAll(group.entries);
                        if (!prefixFlags.contains(flag)) prefixFlags.add(flag);
                    } else if (group.combinable && group.type == 'S') {
                        suffixEntries.addAll(group.entries);
                        if (!suffixFlags.contains(flag)) suffixFlags.add(flag);
                    }
                }

                long projectedOps = (long) roots.size() * (long) prefixEntries.size() * (long) suffixEntries.size();
                long projectedComboFlags = (long) prefixFlags.size() * (long) suffixFlags.size();
                boolean includeCombos = projectedComboFlags > 0
                        && projectedComboFlags <= MAX_COMBO_FLAGS
                        && projectedOps <= MAX_COMBO_OPS;

                if (includeCombos) {
                    int idx = 0;
                    for (String root : roots) {
                        if (isCancelled()) break;
                        idx++;
                        updateMessage("Processing combo flags " + idx + "/" + roots.size() + "…");

                        for (LugandaAffParser.AffixEntry p : prefixEntries) {
                            if (isCancelled()) break;
                            String mid = LugandaAffParser.apply(p, root);
                            if (mid == null || mid.isEmpty()) continue;
                            for (LugandaAffParser.AffixEntry s : suffixEntries) {
                                if (isCancelled()) break;
                                String word = LugandaAffParser.apply(s, mid);
                                if (word == null || word.isEmpty()) continue;
                                String comboFlag = (p.flag == null ? "" : p.flag) + "+" + (s.flag == null ? "" : s.flag);
                                if (comboFlag.equals("+")) continue;

                                flagsEncountered.add(comboFlag);
                                Map<String, LinkedHashSet<String>> byFlag = tmp.get(root);
                                LinkedHashSet<String> set = byFlag.computeIfAbsent(comboFlag, k -> new LinkedHashSet<>());
                                if (set.size() >= MAX_WORDS_PER_FLAG_BUCKET) {
                                    truncated = true;
                                    continue;
                                }
                                set.add(word);
                            }
                        }
                    }
                }

                // Convert to lists for stable index access in the table.
                List<String> flags = new ArrayList<>(flagsEncountered);
                if (flags.size() > MAX_WORDS_BY_FLAG_COLUMNS) {
                    flags = flags.subList(0, MAX_WORDS_BY_FLAG_COLUMNS);
                    truncated = true;
                }

                Map<String, Map<String, List<String>>> out = new LinkedHashMap<>();
                for (String root : roots) {
                    Map<String, LinkedHashSet<String>> byFlag = tmp.getOrDefault(root, new LinkedHashMap<>());
                    Map<String, List<String>> lists = new LinkedHashMap<>();
                    for (String flag : flags) {
                        LinkedHashSet<String> set = byFlag.get(flag);
                        if (set == null || set.isEmpty()) {
                            lists.put(flag, Collections.emptyList());
                        } else {
                            lists.put(flag, new ArrayList<>(set));
                        }
                    }
                    out.put(root, lists);
                }

                return new WordsByFlagModel(flags, out, includeCombos, truncated);
            }
        };

        status.textProperty().bind(task.messageProperty());
        cancelBtn.setOnAction(e -> task.cancel(true));
        flagStage.setOnCloseRequest(e -> task.cancel(true));

        task.setOnSucceeded(e -> {
            WordsByFlagModel model = task.getValue();
            buildWordsByFlagStage(flagStage, model, roots);
        });
        task.setOnFailed(e -> {
            Throwable ex = task.getException();
            flagStage.close();
            showError("Failed to build Words by Flag: " + (ex == null ? "unknown error" : ex.getMessage()));
        });

        Thread t = new Thread(task, "lg-words-by-flag");
        t.setDaemon(true);
        t.start();
    }

    private void buildWordsByFlagStage(Stage flagStage, WordsByFlagModel model, List<String> roots) {
        List<String> flags = model == null ? Collections.emptyList() : model.flags;
        Map<String, Map<String, List<String>>> words = model == null ? Collections.emptyMap() : model.words;

        int maxRows = 0;
        for (String root : roots) {
            Map<String, List<String>> byFlag = words.get(root);
            if (byFlag == null) continue;
            for (String flag : flags) {
                List<String> list = byFlag.get(flag);
                if (list != null) maxRows = Math.max(maxRows, list.size());
            }
        }
        maxRows = Math.min(maxRows, MAX_WORDS_PER_FLAG_BUCKET);

        Label info = new Label(
                "Grouped by root and flag (duplicates removed). Select flags in headers, then Apply to update Luganda.dic."
                        + (model != null && !model.comboIncluded ? " Combo flags omitted (too many combinations)." : "")
                        + (model != null && model.truncated ? " Output truncated to keep UI responsive." : "")
        );
        info.setStyle("-fx-font-size: 11px; -fx-text-fill: #666;");

        // Table rows are just indices; cell factories read words from the model.
        ObservableList<Integer> indexRows = FXCollections.observableArrayList();
        for (int i = 0; i < maxRows; i++) {
            indexRows.add(i);
        }
        TableView<Integer> tv = new TableView<>(indexRows);

        TableColumn<Integer, String> noCol = new TableColumn<>("No.");
        noCol.setPrefWidth(50);
        noCol.setSortable(false);
        noCol.setCellValueFactory(cd -> new javafx.beans.property.SimpleStringProperty(String.valueOf(cd.getValue() + 1)));
        noCol.setStyle("-fx-alignment: CENTER;");
        tv.getColumns().add(noCol);

        // Flag selection controls: root -> selected flags
        Map<String, Set<String>> selectedFlagsByRoot = new LinkedHashMap<>();
        for (String root : roots) {
            selectedFlagsByRoot.put(root, new LinkedHashSet<>());
        }

        // Nested columns: root -> flags
        for (String root : roots) {
            TableColumn<Integer, String> rootCol = new TableColumn<>(root);
            for (String flag : flags) {
                final String flagFinal = flag;
                CheckBox headerCheck = new CheckBox(flagFinal);
                headerCheck.setOnAction(e -> {
                    Set<String> set = selectedFlagsByRoot.getOrDefault(root, new LinkedHashSet<>());
                    if (headerCheck.isSelected()) {
                        set.add(flagFinal);
                    } else {
                        set.remove(flagFinal);
                    }
                    selectedFlagsByRoot.put(root, set);
                });

                TableColumn<Integer, String> flagCol = new TableColumn<>();
                flagCol.setGraphic(headerCheck);
                flagCol.setPrefWidth(140);
                flagCol.setStyle("-fx-alignment: CENTER;");
                flagCol.setCellValueFactory(cd -> {
                    int idx = cd.getValue();
                    Map<String, List<String>> byFlag = words.get(root);
                    if (byFlag == null) return new javafx.beans.property.SimpleStringProperty("");
                    List<String> list = byFlag.get(flagFinal);
                    if (list == null || idx < 0 || idx >= list.size()) {
                        return new javafx.beans.property.SimpleStringProperty("");
                    }
                    return new javafx.beans.property.SimpleStringProperty(list.get(idx));
                });
                rootCol.getColumns().add(flagCol);
            }
            tv.getColumns().add(rootCol);
        }

        Button applyBtn = new Button("Apply to Luganda.dic");
        applyBtn.setStyle("-fx-font-weight: bold;");
        applyBtn.setOnAction(e -> {
            Map<String, Set<String>> toApply = new LinkedHashMap<>();
            for (Map.Entry<String, Set<String>> entry : selectedFlagsByRoot.entrySet()) {
                Set<String> sel = entry.getValue();
                if (sel == null || sel.isEmpty()) continue;
                LinkedHashSet<String> flat = new LinkedHashSet<>();
                for (String f : sel) {
                    if (f == null) continue;
                    String[] parts = f.split("\\+");
                    for (String p : parts) {
                        String t = p == null ? "" : p.trim();
                        if (!t.isEmpty()) flat.add(t);
                    }
                }
                if (!flat.isEmpty()) {
                    toApply.put(entry.getKey(), flat);
                }
            }

            if (toApply.isEmpty()) {
                Alert a = new Alert(Alert.AlertType.INFORMATION, "No flags selected.", ButtonType.OK);
                a.setHeaderText(null);
                a.showAndWait();
                return;
            }

            HunspellFlagMode mode = detectFlagMode(defaultAffPath);
            try {
                ApplyResult res = applyFlagsToDic(defaultDicPath, toApply, mode);
                Alert ok = new Alert(Alert.AlertType.INFORMATION, res.toUserMessage(), ButtonType.OK);
                ok.setHeaderText("Updated " + defaultDicPath.toAbsolutePath());
                ok.showAndWait();
            } catch (IOException ex) {
                showError("Failed to update .dic: " + ex.getMessage());
            }
        });

        Button closeBtn = new Button("Close");
        closeBtn.setOnAction(e -> flagStage.close());
        HBox bottom = new HBox(8, closeBtn, applyBtn);
        bottom.setPadding(new Insets(8));

        BorderPane bp = new BorderPane();
        bp.setTop(new VBox(6, info, new Separator()));
        bp.setCenter(tv);
        bp.setBottom(bottom);

        Scene scene = new Scene(bp, 1200, 600);
        flagStage.setScene(scene);
        flagStage.show();
    }

    private static class ApplyResult {
        private final int totalMatchedLines;
        private final int totalChangedLines;
        private final Map<String, Integer> matchedByRoot;
        private final Map<String, Integer> changedByRoot;

        private ApplyResult(int totalMatchedLines, int totalChangedLines, Map<String, Integer> matchedByRoot, Map<String, Integer> changedByRoot) {
            this.totalMatchedLines = totalMatchedLines;
            this.totalChangedLines = totalChangedLines;
            this.matchedByRoot = matchedByRoot;
            this.changedByRoot = changedByRoot;
        }

        private String toUserMessage() {
            StringBuilder sb = new StringBuilder();
            sb.append("Matched lines: ").append(totalMatchedLines).append("\n");
            sb.append("Updated lines: ").append(totalChangedLines).append("\n\n");
            for (String root : matchedByRoot.keySet()) {
                int m = matchedByRoot.getOrDefault(root, 0);
                int c = changedByRoot.getOrDefault(root, 0);
                sb.append(root).append(": ").append(c).append("/").append(m).append(" updated\n");
            }
            return sb.toString().trim();
        }
    }

    private static HunspellFlagMode detectFlagMode(Path affPath) {
        if (affPath == null) return HunspellFlagMode.DEFAULT;
        try {
            for (String raw : Files.readAllLines(affPath)) {
                if (raw == null) continue;
                String line = raw.trim();
                if (line.isEmpty()) continue;
                if (line.startsWith("#")) continue;
                if (!line.toUpperCase().startsWith("FLAG")) continue;
                String[] toks = line.split("\\s+");
                if (toks.length < 2) return HunspellFlagMode.DEFAULT;
                String mode = toks[1].trim().toLowerCase();
                if ("long".equals(mode)) return HunspellFlagMode.LONG;
                if ("num".equals(mode)) return HunspellFlagMode.NUM;
                return HunspellFlagMode.DEFAULT;
            }
        } catch (IOException ignored) {
            // fall back
        }
        return HunspellFlagMode.DEFAULT;
    }

    private static ApplyResult applyFlagsToDic(Path dicPath, Map<String, Set<String>> flagsToAddByRoot, HunspellFlagMode mode) throws IOException {
        if (dicPath == null) throw new IllegalArgumentException("dicPath is null");
        if (flagsToAddByRoot == null || flagsToAddByRoot.isEmpty()) {
            return new ApplyResult(0, 0, Collections.emptyMap(), Collections.emptyMap());
        }

        List<String> lines = Files.readAllLines(dicPath, StandardCharsets.UTF_8);
        Map<String, Integer> matchedByRoot = new LinkedHashMap<>();
        Map<String, Integer> changedByRoot = new LinkedHashMap<>();
        for (String root : flagsToAddByRoot.keySet()) {
            matchedByRoot.put(root, 0);
            changedByRoot.put(root, 0);
        }

        int totalMatched = 0;
        int totalChanged = 0;

        for (int i = 0; i < lines.size(); i++) {
            String line = lines.get(i);
            if (line == null) continue;
            if (i == 0) continue; // count line

            String trimmed = line.trim();
            if (trimmed.isEmpty()) continue;
            if (trimmed.startsWith("#")) continue;

            int firstWs = indexOfWhitespace(line);
            String wordFlagsToken = firstWs >= 0 ? line.substring(0, firstWs) : line;
            String rest = firstWs >= 0 ? line.substring(firstWs) : "";

            int slashIdx = wordFlagsToken.indexOf('/');
            String stem = slashIdx >= 0 ? wordFlagsToken.substring(0, slashIdx) : wordFlagsToken;
            String existingFlagsRaw = slashIdx >= 0 ? wordFlagsToken.substring(slashIdx + 1) : "";

            Set<String> toAdd = flagsToAddByRoot.get(stem);
            if (toAdd == null || toAdd.isEmpty()) continue;

            matchedByRoot.put(stem, matchedByRoot.getOrDefault(stem, 0) + 1);
            totalMatched++;

            String merged = mergeFlags(existingFlagsRaw, toAdd, mode);
            boolean changed = !merged.equals(existingFlagsRaw);
            String newToken = stem + (merged.isEmpty() ? "" : "/" + merged);
            String newLine = newToken + rest;
            if (changed) {
                lines.set(i, newLine);
                changedByRoot.put(stem, changedByRoot.getOrDefault(stem, 0) + 1);
                totalChanged++;
            }
        }

        Files.write(dicPath, lines, StandardCharsets.UTF_8);
        return new ApplyResult(totalMatched, totalChanged, matchedByRoot, changedByRoot);
    }

    private static int indexOfWhitespace(String s) {
        if (s == null) return -1;
        for (int i = 0; i < s.length(); i++) {
            if (Character.isWhitespace(s.charAt(i))) return i;
        }
        return -1;
    }

    private static String mergeFlags(String existingFlagsRaw, Set<String> flagsToAdd, HunspellFlagMode mode) {
        if (existingFlagsRaw == null) existingFlagsRaw = "";
        if (flagsToAdd == null || flagsToAdd.isEmpty()) return existingFlagsRaw;

        if (mode == HunspellFlagMode.LONG) return mergeLongFlags(existingFlagsRaw, flagsToAdd);
        if (mode == HunspellFlagMode.NUM) return mergeNumFlags(existingFlagsRaw, flagsToAdd);
        return mergeDefaultFlags(existingFlagsRaw, flagsToAdd);
    }

    private static String mergeLongFlags(String existingFlagsRaw, Set<String> flagsToAdd) {
        LinkedHashSet<String> tokens = new LinkedHashSet<>();
        tokens.addAll(splitLongFlags(existingFlagsRaw));
        for (String f : flagsToAdd) {
            if (f == null) continue;
            String[] parts = f.split("\\+");
            for (String part : parts) {
                String t = part == null ? "" : part.trim();
                if (t.isEmpty()) continue;
                // For FLAG long, each token should be exactly 2 chars.
                // If user-selected flag isn't 2 chars, keep as-is (best effort).
                tokens.add(t);
            }
        }
        return String.join("", tokens);
    }

    private static List<String> splitLongFlags(String flagsRaw) {
        if (flagsRaw == null) return Collections.emptyList();
        String s = flagsRaw.trim().replace("+", "");
        if (s.isEmpty()) return Collections.emptyList();
        List<String> out = new ArrayList<>();
        for (int i = 0; i < s.length(); i += 2) {
            int end = Math.min(i + 2, s.length());
            out.add(s.substring(i, end));
        }
        return out;
    }

    private static String mergeNumFlags(String existingFlagsRaw, Set<String> flagsToAdd) {
        // Hunspell numeric flags are comma-separated numbers.
        LinkedHashSet<String> tokens = new LinkedHashSet<>();
        String s = existingFlagsRaw == null ? "" : existingFlagsRaw.trim().replace("+", "");
        if (!s.isEmpty()) {
            for (String part : s.split(",")) {
                String t = part.trim();
                if (!t.isEmpty()) tokens.add(t);
            }
        }
        for (String f : flagsToAdd) {
            if (f == null) continue;
            String[] parts = f.split("\\+");
            for (String part : parts) {
                String t = part == null ? "" : part.trim();
                if (!t.isEmpty()) tokens.add(t);
            }
        }
        return String.join(",", tokens);
    }

    private static String mergeDefaultFlags(String existingFlagsRaw, Set<String> flagsToAdd) {
        // Default hunspell flags are single characters concatenated.
        LinkedHashSet<String> tokens = new LinkedHashSet<>();
        String s = existingFlagsRaw == null ? "" : existingFlagsRaw;
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (ch == '+') continue; // strip buggy delimiter
            tokens.add(String.valueOf(ch));
        }
        for (String f : flagsToAdd) {
            if (f == null) continue;
            String[] parts = f.split("\\+");
            for (String part : parts) {
                String t = part == null ? "" : part.trim();
                if (t.isEmpty()) continue;
                // Best-effort: if longer than 1 char, add each char.
                if (t.length() == 1) {
                    tokens.add(t);
                } else {
                    for (int i = 0; i < t.length(); i++) {
                        tokens.add(String.valueOf(t.charAt(i)));
                    }
                }
            }
        }
        StringBuilder out = new StringBuilder();
        for (String tok : tokens) out.append(tok);
        return out.toString();
    }

    public static class ProposedRule {
        private final String root;
        private final char type; // 'P' or 'S'
        private String flag; // editable
        private final String strip;
        private final String affix;
        private final String condition;

        public ProposedRule(String root, char type, String flag, String strip, String affix, String condition) {
            this.root = root;
            this.type = type;
            this.flag = flag == null ? "" : flag;
            this.strip = strip == null ? "" : strip;
            this.affix = affix == null ? "" : affix;
            this.condition = condition == null ? "." : condition;
        }

        public String getRoot() { return root; }
        public String getTypeStr() { return type == 'S' ? "SFX" : "PFX"; }
        public char getType() { return type; }
        public String getFlag() { return flag; }
        public void setFlag(String flag) { this.flag = flag == null ? "" : flag.trim(); }
        public String getStrip() { return strip; }
        public String getAffix() { return affix; }
        public String getCondition() { return condition; }
    }

    @SuppressWarnings("unchecked")
    private void showRuleGenerator(ObservableList<Result> allRows, List<String> roots) {
        Stage rulesStage = new Stage();
        rulesStage.setTitle("Generate Rules from Non-Errors");

        // Build proposed rules grouped by root
        Map<String, List<ProposedRule>> rulesByRoot = new LinkedHashMap<>();
        for (String root : roots) {
            rulesByRoot.put(root, new ArrayList<>());
        }
        for (Result r : allRows) {
            LugandaAffParser.AffixEntry ae = r.getAffixEntry();
            if (ae == null) continue; // skip ROOT row
            for (String root : roots) {
                String word = r.getWordForRoot(root);
                if (word != null && !word.isEmpty() && !r.isError(root)) {
                    rulesByRoot.get(root).add(new ProposedRule(root, ae.type, r.getFlag(), ae.strip, ae.affix, ae.condition));
                }
            }
        }

        // Align into rows by index across roots
        int maxRows = 0;
        for (List<ProposedRule> list : rulesByRoot.values()) {
            maxRows = Math.max(maxRows, list.size());
        }
        ObservableList<Map<String, String>> alignedRows = FXCollections.observableArrayList();
        for (int i = 0; i < maxRows; i++) {
            Map<String, String> row = new LinkedHashMap<>();
            for (String root : roots) {
                List<ProposedRule> list = rulesByRoot.get(root);
                if (i < list.size()) {
                    ProposedRule pr = list.get(i);
                    row.put("type." + root, pr.getTypeStr());
                    row.put("flag." + root, pr.getFlag());
                    row.put("root." + root, pr.getAffix()); // show affix under the root-named column
                    row.put("cond." + root, pr.getCondition());
                } else {
                    row.put("type." + root, "");
                    row.put("flag." + root, "");
                    row.put("root." + root, "");
                    row.put("cond." + root, "");
                }
            }
            alignedRows.add(row);
        }

        TableView<Map<String, String>> tv = new TableView<>(alignedRows);
        tv.setEditable(true);

        TableColumn<Map<String, String>, String> noCol = new TableColumn<>("No.");
        noCol.setPrefWidth(50);
        noCol.setCellValueFactory(cd -> new javafx.beans.property.SimpleStringProperty(String.valueOf(tv.getItems().indexOf(cd.getValue()) + 1)));
        noCol.setStyle("-fx-alignment: CENTER;");
        tv.getColumns().add(noCol);

        // Add 4 columns per root: Type | Flag | <root> | Condition
        for (String root : roots) {
            TableColumn<Map<String, String>, String> typeCol = new TableColumn<>("Type");
            typeCol.setPrefWidth(70);
            typeCol.setCellValueFactory(cd -> new javafx.beans.property.SimpleStringProperty(cd.getValue().getOrDefault("type." + root, "")));
            typeCol.setStyle("-fx-alignment: CENTER;");

            TableColumn<Map<String, String>, String> flagCol = new TableColumn<>("Flag");
            flagCol.setPrefWidth(70);
            flagCol.setCellValueFactory(cd -> new javafx.beans.property.SimpleStringProperty(cd.getValue().getOrDefault("flag." + root, "")));
            flagCol.setCellFactory(TextFieldTableCell.forTableColumn());
            flagCol.setOnEditCommit(ev -> {
                int rowIndex = ev.getTablePosition().getRow();
                String newVal = ev.getNewValue() == null ? "" : ev.getNewValue();
                ev.getRowValue().put("flag." + root, newVal);
                List<ProposedRule> list = rulesByRoot.get(root);
                if (list != null && rowIndex >= 0 && rowIndex < list.size()) {
                    list.get(rowIndex).setFlag(newVal);
                }
            });

            TableColumn<Map<String, String>, String> rootCol = new TableColumn<>(root);
            rootCol.setPrefWidth(120);
            rootCol.setCellValueFactory(cd -> new javafx.beans.property.SimpleStringProperty(cd.getValue().getOrDefault("root." + root, "")));

            TableColumn<Map<String, String>, String> condCol = new TableColumn<>("Condition");
            condCol.setPrefWidth(100);
            condCol.setCellValueFactory(cd -> new javafx.beans.property.SimpleStringProperty(cd.getValue().getOrDefault("cond." + root, "")));

            tv.getColumns().addAll(typeCol, flagCol, rootCol, condCol);
        }

        // Controls: per-root flag entry
        VBox flagControls = new VBox(8);
        flagControls.setPadding(new Insets(8));
        Label flagLabel = new Label("Set Flags:");
        flagLabel.setStyle("-fx-font-weight: bold;");
        flagControls.getChildren().add(flagLabel);
        
        // Create a text field and apply button for each root
        Map<String, TextField> flagFields = new LinkedHashMap<>();
        for (String root : roots) {
            HBox rootFlagBox = new HBox(8);
            Label rootLabel = new Label(root + ":");
            rootLabel.setPrefWidth(80);
            TextField flagField = new TextField();
            flagField.setPromptText("flag");
            flagField.setPrefWidth(80);
            flagFields.put(root, flagField);
            
            Button applyRoot = new Button("Apply");
            applyRoot.setOnAction(e -> {
                String flag = flagField.getText();
                if (flag == null) flag = "";
                List<ProposedRule> list = rulesByRoot.get(root);
                if (list != null) {
                    for (ProposedRule pr : list) {
                        pr.setFlag(flag);
                    }
                    // reflect in table
                    for (int i = 0; i < list.size() && i < alignedRows.size(); i++) {
                        alignedRows.get(i).put("flag." + root, flag);
                    }
                    tv.refresh();
                }
            });
            
            rootFlagBox.getChildren().addAll(rootLabel, flagField, applyRoot);
            flagControls.getChildren().add(rootFlagBox);
        }
        
        // Global apply to all roots
        HBox globalBox = new HBox(8);
        Label globalLabel = new Label("All roots:");
        globalLabel.setPrefWidth(80);
        TextField defaultFlag = new TextField();
        defaultFlag.setPromptText("flag for all");
        defaultFlag.setPrefWidth(80);
        Button applyAll = new Button("Apply to All");
        applyAll.setOnAction(e -> {
            String df = defaultFlag.getText();
            if (df == null) df = "";
            // Update all root flag fields
            for (TextField field : flagFields.values()) {
                field.setText(df);
            }
            // Apply to all rules
            for (Map.Entry<String, List<ProposedRule>> entry : rulesByRoot.entrySet()) {
                List<ProposedRule> list = entry.getValue();
                for (ProposedRule pr : list) {
                    pr.setFlag(df);
                }
            }
            // reflect in table
            for (int i = 0; i < alignedRows.size(); i++) {
                Map<String, String> row = alignedRows.get(i);
                for (String root : roots) {
                    List<ProposedRule> list = rulesByRoot.get(root);
                    if (list != null && i < list.size()) {
                        row.put("flag." + root, df);
                    }
                }
            }
            tv.refresh();
        });
        globalBox.getChildren().addAll(globalLabel, defaultFlag, applyAll);
        flagControls.getChildren().add(new Separator());
        flagControls.getChildren().add(globalBox);

        Button confirm = new Button("Confirm Append to .aff");
        confirm.setStyle("-fx-font-weight: bold;");
        confirm.setOnAction(e -> {
            // Flatten and validate flags
            List<ProposedRule> allRules = new ArrayList<>();
            for (List<ProposedRule> list : rulesByRoot.values()) allRules.addAll(list);
            if (allRules.isEmpty()) {
                Alert info = new Alert(Alert.AlertType.INFORMATION, "No rules to append.", ButtonType.OK);
                info.showAndWait();
                return;
            }
            for (ProposedRule pr : allRules) {
                if (pr.getFlag() == null || pr.getFlag().trim().isEmpty()) {
                    showError("Every rule must have a flag before append.");
                    return;
                }
            }

            Alert a = new Alert(Alert.AlertType.CONFIRMATION, "Append " + allRules.size() + " rules to " + defaultAffPath.toAbsolutePath() + "?", ButtonType.OK, ButtonType.CANCEL);
            a.setHeaderText("Confirm updating Luganda.aff");
            a.showAndWait();
            if (a.getResult() != ButtonType.OK) return;

            try (java.io.BufferedWriter bw = java.nio.file.Files.newBufferedWriter(defaultAffPath, StandardCharsets.UTF_8, java.nio.file.StandardOpenOption.APPEND)) {
                // Group by root, then by (type, flag) within each root
                Map<String, Map<String, List<ProposedRule>>> groupsByRootAndKey = new LinkedHashMap<>();
                for (ProposedRule pr : allRules) {
                    String root = pr.getRoot();
                    String key = pr.getTypeStr() + " " + pr.getFlag();
                    groupsByRootAndKey.computeIfAbsent(root, k -> new LinkedHashMap<>())
                            .computeIfAbsent(key, k2 -> new ArrayList<>()).add(pr);
                }

                bw.write("\n\n# Generated rules on " + java.time.LocalDate.now() + "\n");
                for (Map.Entry<String, Map<String, List<ProposedRule>>> rootEntry : groupsByRootAndKey.entrySet()) {
                    String root = rootEntry.getKey();
                    for (Map.Entry<String, List<ProposedRule>> typeEntry : rootEntry.getValue().entrySet()) {
                        String[] parts = typeEntry.getKey().split(" ", 2);
                        String typeStr = parts[0];
                        String flag = parts.length > 1 ? parts[1] : "";
                        List<ProposedRule> list = typeEntry.getValue();
                        bw.write("# Rules for root '" + root + "'\n");
                        bw.write(typeStr + " " + flag + " Y " + list.size() + "\n");
                        for (ProposedRule pr : list) {
                            String strip = pr.getStrip().isEmpty() ? "0" : pr.getStrip();
                            String aff = pr.getAffix().isEmpty() ? "0" : pr.getAffix();
                            String cond = (pr.getCondition() == null || pr.getCondition().isEmpty()) ? "." : pr.getCondition();
                            bw.write(typeStr + " " + flag + " " + strip + " " + aff + " " + cond + "\n");
                        }
                        bw.write("\n");
                    }
                }
            } catch (IOException ex) {
                showError("Failed to append rules: " + ex.getMessage());
                return;
            }

            Alert ok = new Alert(Alert.AlertType.INFORMATION, "Rules appended successfully.", ButtonType.OK);
            ok.setHeaderText(null);
            ok.showAndWait();
            rulesStage.close();
        });

        Button cancel = new Button("Close");
        cancel.setOnAction(e -> rulesStage.close());

        HBox bottom = new HBox(8, cancel, confirm);
        bottom.setPadding(new Insets(8));

        BorderPane bp = new BorderPane();
        bp.setLeft(flagControls);
        bp.setCenter(tv);
        bp.setBottom(bottom);

        Scene scene = new Scene(bp, 1200, 600);
        rulesStage.setScene(scene);
        rulesStage.show();
    }

    private void maybeUpdateStatistics(List<String> roots, ObservableList<Result> rows, Map<String, Label> statsLabels) {
        if (rows == null) return;
        if (rows.size() > MAX_STATS_ROWS) {
            for (String root : roots) {
                Label label = statsLabels.get(root);
                if (label != null) label.setText(root + ": N/A (too many rows)");
            }
            return;
        }

        for (String root : roots) {
            int totalWords = 0;
            int errorWords = 0;
            
            for (Result r : rows) {
                String word = r.getWordForRoot(root);
                if (word != null && !word.isEmpty()) {
                    totalWords++;
                    if (r.isError(root)) {
                        errorWords++;
                    }
                }
            }
            
            double errorRate = totalWords > 0 ? (errorWords * 100.0 / totalWords) : 0.0;
            String statText = String.format("%s: %.1f%% (%d/%d)", root, errorRate, errorWords, totalWords);
            statsLabels.get(root).setText(statText);
        }
    }

    private static final AtomicLong SEARCH_SEQ = new AtomicLong(0);

    private void scheduleSearch(
            List<String> roots,
            TableView<Result> table,
            LazyResultsList baseRows,
            ObservableList<Result> filteredRows,
            Map<String, Label> statsLabels,
            Label rulesInfo,
            TextField searchField,
            ToggleButton exactMatchBtn
    ) {
        final long seq = SEARCH_SEQ.incrementAndGet();
        String newVal = searchField.getText();
        if (newVal == null || newVal.trim().isEmpty()) {
            filteredRows.clear();
            table.setItems(baseRows);
            rulesInfo.setText("Total Rules: " + table.getItems().size());
            maybeUpdateStatistics(roots, table.getItems(), statsLabels);
            searchField.setDisable(false);
            return;
        }
        final String searchText = newVal.toLowerCase().trim();
        final boolean exactMatch = exactMatchBtn.isSelected();

        searchField.setDisable(true);
        rulesInfo.setText("Searching…");

        Task<List<Result>> task = new Task<List<Result>>() {
            @Override
            protected List<Result> call() {
                List<Result> matches = new ArrayList<>();
                int n = baseRows.size();
                for (int i = 0; i < n; i++) {
                    if (isCancelled()) break;
                    Result r = baseRows.get(i);
                    boolean m = false;

                    // Match by words
                    for (String root : roots) {
                        String word = r.getWordForRoot(root);
                        if (word == null) continue;
                        String w = word.toLowerCase();
                        if (exactMatch ? w.equals(searchText) : w.contains(searchText)) {
                            m = true;
                            break;
                        }
                    }

                    // Match by flag
                    if (!m) {
                        String f = r.getFlag() == null ? "" : r.getFlag().toLowerCase();
                        if (exactMatch ? f.equals(searchText) : f.contains(searchText)) {
                            m = true;
                        }
                    }

                    if (m) {
                        matches.add(r);
                        if (matches.size() >= MAX_FILTER_MATCHES) {
                            break;
                        }
                    }
                }
                return matches;
            }
        };

        task.setOnSucceeded(e -> {
            if (seq != SEARCH_SEQ.get()) return; // superseded
            List<Result> matches = task.getValue();
            filteredRows.setAll(matches);
            table.setItems(filteredRows);
            rulesInfo.setText("Matches: " + filteredRows.size() + (filteredRows.size() >= MAX_FILTER_MATCHES ? " (showing first " + MAX_FILTER_MATCHES + ")" : ""));
            maybeUpdateStatistics(roots, filteredRows, statsLabels);
            searchField.setDisable(false);
        });

        task.setOnFailed(e -> {
            if (seq != SEARCH_SEQ.get()) return;
            Throwable ex = task.getException();
            rulesInfo.setText("Search failed");
            searchField.setDisable(false);
            Platform.runLater(() -> {
                if (ex != null) {
                    showError("Search failed: " + ex.getMessage());
                } else {
                    showError("Search failed.");
                }
            });
        });

        Thread t = new Thread(task, "lg-search");
        t.setDaemon(true);
        t.start();
    }

    private static String escapeCsv(String s) {
        if (s == null) return "";
        if (s.contains(",") || s.contains("\"") || s.contains("\n")) {
            return '"' + s.replace("\"", "\"\"") + '"';
        }
        return s;
    }

    private void showError(String msg) {
        Alert a = new Alert(Alert.AlertType.ERROR, msg, ButtonType.OK);
        a.showAndWait();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
