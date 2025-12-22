package com.lugandahunspelldictionary;

import javafx.application.Application;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.stage.FileChooser;
import javafx.stage.Stage;

import java.io.BufferedWriter;
import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class LugandaGeneratorApp extends Application {

    private Path defaultAffPath = Paths.get("Luganda.aff");

    public static class Result {
        private final Map<String, String> wordsByRoot; // root -> generated word
        private final String flag;
        private final Map<String, Boolean> errorsByRoot; // root -> is error

        public Result(Map<String, String> wordsByRoot, String flag) {
            this.wordsByRoot = wordsByRoot;
            this.flag = flag;
            this.errorsByRoot = new LinkedHashMap<>();
            // Initialize all as non-errors
            for (String root : wordsByRoot.keySet()) {
                errorsByRoot.put(root, false);
            }
        }

        public String getFlag() { return flag; }
        public Map<String, String> getWordsByRoot() { return wordsByRoot; }
        public boolean isError(String root) { return errorsByRoot.getOrDefault(root, false); }
        public void toggleError(String root) { 
            errorsByRoot.put(root, !errorsByRoot.getOrDefault(root, false)); 
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
        Map<String, List<LugandaAffParser.AffixEntry>> affMap = LugandaAffParser.parseAff(defaultAffPath);
        
        // Count total rules
        int totalRules = 0;
        for (List<LugandaAffParser.AffixEntry> entries : affMap.values()) {
            totalRules += entries.size();
        }

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

        // Add columns for each root
        for (String root : roots) {
            final String r = root;
            TableColumn<Result, String> col = new TableColumn<>(r);
            col.setPrefWidth(150);
            col.setCellValueFactory(cellData -> {
                Map<String, String> words = cellData.getValue().getWordsByRoot();
                return new javafx.beans.property.SimpleStringProperty(words.getOrDefault(r, ""));
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
                            updateStatistics(roots, table.getItems(), statsLabels);
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

        ObservableList<Result> rows = FXCollections.observableArrayList();

        // For each flag and each affix, create one row with all roots applied
        for (Map.Entry<String, List<LugandaAffParser.AffixEntry>> flagEntry : affMap.entrySet()) {
            String flag = flagEntry.getKey();
            for (LugandaAffParser.AffixEntry ae : flagEntry.getValue()) {
                Map<String, String> wordsByRoot = new LinkedHashMap<>();
                for (String root : roots) {
                    String word = LugandaAffParser.apply(ae, root);
                    if (word != null) {
                        wordsByRoot.put(root, word);
                    } else {
                        wordsByRoot.put(root, "");
                    }
                }
                rows.add(new Result(wordsByRoot, flag));
            }
        }

        // Add a row for bare roots
        Map<String, String> bareRoots = new LinkedHashMap<>();
        for (String root : roots) {
            bareRoots.put(root, root);
        }
        rows.add(new Result(bareRoots, "ROOT"));

        // Create filtered list for search
        ObservableList<Result> allRows = FXCollections.observableArrayList(rows);
        ObservableList<Result> filteredRows = FXCollections.observableArrayList(rows);
        table.setItems(filteredRows);
        
        // Search bar
        TextField searchField = new TextField();
        searchField.setPromptText("Search for a word...");
        searchField.setPrefWidth(300);
        
        ToggleButton exactMatchBtn = new ToggleButton("Exact Match");
        exactMatchBtn.setStyle("-fx-font-size: 11px; -fx-padding: 5px 10px;");
        
        searchField.textProperty().addListener((obs, oldVal, newVal) -> {
            filteredRows.clear();
            if (newVal == null || newVal.trim().isEmpty()) {
                filteredRows.addAll(allRows);
            } else {
                String searchText = newVal.toLowerCase().trim();
                boolean exactMatch = exactMatchBtn.isSelected();
                
                for (Result r : allRows) {
                    boolean matches = false;
                    for (String word : r.getWordsByRoot().values()) {
                        if (word != null) {
                            if (exactMatch) {
                                if (word.toLowerCase().equals(searchText)) {
                                    matches = true;
                                    break;
                                }
                            } else {
                                if (word.toLowerCase().contains(searchText)) {
                                    matches = true;
                                    break;
                                }
                            }
                        }
                    }
                    if (!matches && exactMatch) {
                        if (r.getFlag().toLowerCase().equals(searchText)) {
                            matches = true;
                        }
                    } else if (!matches && r.getFlag().toLowerCase().contains(searchText)) {
                        matches = true;
                    }
                    
                    if (matches) {
                        filteredRows.add(r);
                    }
                }
            }
            updateStatistics(roots, filteredRows, statsLabels);
        });
        
        exactMatchBtn.selectedProperty().addListener((obs, oldVal, newVal) -> {
            // Trigger search update
            searchField.setText(searchField.getText());
        });
        
        Button clearSearch = new Button("Clear");
        clearSearch.setOnAction(e -> searchField.clear());
        
        HBox searchBox = new HBox(8, new Label("Search:"), searchField, exactMatchBtn, clearSearch);
        searchBox.setPadding(new Insets(8));
        
        // Initialize statistics with correct totals
        updateStatistics(roots, filteredRows, statsLabels);

        Button save = new Button("Save CSV");
        Button back = new Button("Back");
        Button clearErrors = new Button("Clear All Errors");
        Button refresh = new Button("Refresh from .aff");
        
        clearErrors.setOnMouseClicked(e -> {
            for (Result r : filteredRows) {
                for (String root : roots) {
                    if (r.isError(root)) {
                        r.toggleError(root);
                    }
                }
            }
            table.refresh();
            updateStatistics(roots, filteredRows, statsLabels);
        });
        
        refresh.setOnAction(e -> {
            try {
                showResultsScene(stage, roots);
            } catch (IOException ex) {
                showError("Error reloading .aff file: " + ex.getMessage());
            }
        });
        
        HBox h = new HBox(8, back, save, clearErrors, refresh);
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
                    
                    // Write rows
                    for (Result r : filteredRows) {
                        for (String root : roots) {
                            bw.write(escapeCsv(r.getWordsByRoot().getOrDefault(root, "")));
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

    private void updateStatistics(List<String> roots, ObservableList<Result> rows, Map<String, Label> statsLabels) {
        for (String root : roots) {
            int totalWords = 0;
            int errorWords = 0;
            
            for (Result r : rows) {
                String word = r.getWordsByRoot().get(root);
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
