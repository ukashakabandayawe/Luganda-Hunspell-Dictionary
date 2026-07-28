package com.lugandahunspelldictionary;

import javafx.application.Application;
import javafx.application.Platform;
import javafx.beans.property.SimpleStringProperty;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.collections.transformation.FilteredList;
import javafx.concurrent.Task;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.ButtonType;
import javafx.scene.control.ChoiceBox;
import javafx.scene.control.Label;
import javafx.scene.control.ProgressIndicator;
import javafx.scene.control.SelectionMode;
import javafx.scene.control.SplitPane;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.TextArea;
import javafx.scene.control.TextField;
import javafx.scene.control.Tooltip;
import javafx.scene.control.cell.CheckBoxTableCell;
import javafx.scene.input.Clipboard;
import javafx.scene.input.ClipboardContent;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Priority;
import javafx.scene.layout.VBox;
import javafx.stage.FileChooser;
import javafx.stage.Stage;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.StringJoiner;
import java.util.prefs.Preferences;

public class CommonFlagAnalyzerApp extends Application {
    private final ObservableList<DicEntry> allEntries = FXCollections.observableArrayList();
    private FilteredList<DicEntry> filteredEntries = new FilteredList<>(allEntries, entry -> true);
    private final Label sourceLabel = new Label("No dictionary loaded.");
    private final Label modeLabel = new Label("Detected mode: -");
    private final Label statusLabel = new Label("Load a .dic file to begin.");
    private final TextField searchField = new TextField();
    private final ChoiceBox<CommonFlagAnalyzer.FlagMode> modeChoice = new ChoiceBox<>(FXCollections.observableArrayList(CommonFlagAnalyzer.FlagMode.values()));
    private final TableView<DicEntry> tableView = new TableView<>();
    private final TextArea selectionArea = new TextArea();
    private final TextArea resultArea = new TextArea();
    private final Button selectAllButton = new Button("Select all");
    private final Button clearAllButton = new Button("Clear all");
    private final Button analyzeButton = new Button("Analyze selection");
    private final Button copyButton = new Button("Copy result");
    private final Button exportButton = new Button("Export report");
    private Path currentDicPath;
    private CommonFlagAnalyzer.DicFileData currentData;
    private final Preferences prefs = Preferences.userNodeForPackage(CommonFlagAnalyzerApp.class);

    @Override
    public void start(Stage stage) {
        stage.setTitle("Luganda Common Flag Analyzer");

        BorderPane root = new BorderPane();
        root.setPadding(new Insets(12));
        root.setTop(buildTopBar(stage));
        root.setCenter(buildCenter());
        root.setBottom(buildBottomBar());

        configureTable();
        configureSearch();
        configureActions(stage);

        Scene scene = new Scene(root, 1000, 600);
        stage.setScene(scene);
        stage.show();
    }

    private HBox buildTopBar(Stage stage) {
        Button openButton = new Button("Open dictionary");
        openButton.setOnAction(e -> chooseDic(stage));

        searchField.setPromptText("Search stems...");
        searchField.setPrefColumnCount(24);

        modeChoice.getSelectionModel().select(CommonFlagAnalyzer.FlagMode.AUTO);
        modeChoice.setTooltip(new Tooltip("AUTO uses the loaded dictionary to guess the flag format."));

        HBox top = new HBox(10,
                openButton,
                new Label("Mode:"),
                modeChoice,
                new Label("Search:"),
                searchField,
                new VBox(2, sourceLabel, modeLabel)
        );
        top.setAlignment(Pos.CENTER_LEFT);
        HBox.setHgrow(searchField, Priority.ALWAYS);
        return top;
    }

    private SplitPane buildCenter() {
        VBox left = new VBox(8, tableView, statusLabel);
        VBox.setVgrow(tableView, Priority.ALWAYS);

        selectionArea.setEditable(false);
        selectionArea.setWrapText(false);
        selectionArea.setPromptText("Selected stems and their flags will appear here.");

        resultArea.setEditable(false);
        resultArea.setWrapText(false);
        resultArea.setPromptText("Common flag analysis results.");

        VBox right = new VBox(8,
                new Label("Selection Preview"),
                selectionArea,
                new Label("Common Flags"),
                resultArea
        );
        VBox.setVgrow(selectionArea, Priority.ALWAYS);
        VBox.setVgrow(resultArea, Priority.ALWAYS);

        SplitPane split = new SplitPane(left, right);
        split.setDividerPositions(0.58);
        return split;
    }

    private HBox buildBottomBar() {
        selectAllButton.setDisable(true);
        clearAllButton.setDisable(true);
        analyzeButton.setDisable(true);
        copyButton.setDisable(true);
        exportButton.setDisable(true);

        ProgressIndicator busy = new ProgressIndicator();
        busy.setPrefSize(18, 18);
        busy.setVisible(false);
        busy.setManaged(false);

        HBox bottom = new HBox(10, selectAllButton, clearAllButton, analyzeButton, copyButton, exportButton, busy);
        bottom.setAlignment(Pos.CENTER_LEFT);
        bottom.setPadding(new Insets(8, 0, 0, 0));
        return bottom;
    }

    private void configureTable() {
        tableView.setEditable(true);
        tableView.setColumnResizePolicy(TableView.CONSTRAINED_RESIZE_POLICY);

        TableColumn<DicEntry, Boolean> checkCol = new TableColumn<>("");
        checkCol.setPrefWidth(42);
        checkCol.setEditable(true);
        checkCol.setCellValueFactory(cell -> cell.getValue().checkedProperty());
        checkCol.setCellFactory(CheckBoxTableCell.forTableColumn(checkCol));

        TableColumn<DicEntry, String> stemCol = new TableColumn<>("Stem");
        stemCol.setCellValueFactory(cell -> new SimpleStringProperty(cell.getValue().getStem()));

        TableColumn<DicEntry, String> flagsCol = new TableColumn<>("Flags raw");
        flagsCol.setCellValueFactory(cell -> new SimpleStringProperty(cell.getValue().getFlagsRaw()));

        TableColumn<DicEntry, String> countCol = new TableColumn<>("Tokens");
        countCol.setCellValueFactory(cell -> new SimpleStringProperty(String.valueOf(cell.getValue().getFlagTokenCount(getEffectiveMode()))));

        tableView.getColumns().addAll(checkCol, stemCol, flagsCol, countCol);
    }

    private void configureSearch() {
        searchField.textProperty().addListener((obs, oldValue, newValue) -> {
            String needle = newValue == null ? "" : newValue.trim().toLowerCase(Locale.ROOT);
            filteredEntries.setPredicate(entry -> {
                if (needle.isEmpty()) {
                    return true;
                }
                return entry.getStem().toLowerCase(Locale.ROOT).contains(needle)
                        || entry.getFlagsRaw().toLowerCase(Locale.ROOT).contains(needle);
            });
        });
    }

    private void configureActions(Stage stage) {
        selectAllButton.setOnAction(e -> setAllChecked(true));
        clearAllButton.setOnAction(e -> setAllChecked(false));
        analyzeButton.setOnAction(e -> runAnalysis());
        copyButton.setOnAction(e -> copyResultToClipboard());
        exportButton.setOnAction(e -> exportReport(stage));

        modeChoice.getSelectionModel().selectedItemProperty().addListener((obs, oldValue, newValue) -> {
            if (currentData != null) {
                modeLabel.setText("Detected mode: " + currentData.getDetectedMode() + " | Active: " + getEffectiveMode());
            }
            tableView.refresh();
            refreshSelectionPreview();
        });
    }

    private void chooseDic(Stage stage) {

    FileChooser chooser = new FileChooser();
    chooser.setTitle("Select reviewer dictionary");

    chooser.getExtensionFilters().addAll(
            new FileChooser.ExtensionFilter("Hunspell dictionaries", "*.dic", "*.txt"),
            new FileChooser.ExtensionFilter("Dictionary text files", "*.dic.txt", "*.txt"),
            new FileChooser.ExtensionFilter("All files", "*.*")
    );

    // Restore last directory
    String lastDir = prefs.get("lastDictionaryDir", null);
    if (lastDir != null) {
        File dir = new File(lastDir);
        if (dir.exists() && dir.isDirectory()) {
            chooser.setInitialDirectory(dir);
        }
    }

    File chosen = chooser.showOpenDialog(stage);

    if (chosen == null) {
        return;
    }

    // Save directory for next time
    prefs.put(
            "lastDictionaryDir",
            chosen.getParentFile().getAbsolutePath()
    );

    Path path = chosen.toPath();
    loadDictionary(path);
}

    private void loadDictionary(Path path) {
        currentDicPath = path;
        statusLabel.setText("Loading " + path.getFileName() + "...");
        analyzeButton.setDisable(true);
        copyButton.setDisable(true);
        exportButton.setDisable(true);

        Task<CommonFlagAnalyzer.DicFileData> task = new Task<>() {
            @Override
            protected CommonFlagAnalyzer.DicFileData call() throws Exception {
                return DicParser.load(path);
            }
        };

        task.setOnSucceeded(event -> {
            currentData = task.getValue();
            allEntries.setAll(currentData.getEntries());
            attachCheckedListeners(currentData.getEntries());
            filteredEntries = new FilteredList<>(allEntries, entry -> true);
            tableView.setItems(filteredEntries);
            sourceLabel.setText("Loaded: " + path.toAbsolutePath());
            modeLabel.setText("Detected mode: " + currentData.getDetectedMode() + " | Active: " + getEffectiveMode());
            statusLabel.setText("Loaded " + allEntries.size() + " stems. Tick one or more boxes, then analyze.");
            selectAllButton.setDisable(false);
            clearAllButton.setDisable(false);
            analyzeButton.setDisable(false);
            updateButtons();
            refreshSelectionPreview();
        });

        task.setOnFailed(event -> {
            Throwable ex = task.getException();
            showError("Failed to load dictionary", ex == null ? "Unknown error" : ex.getMessage());
            statusLabel.setText("Failed to load dictionary.");
        });

        Thread thread = new Thread(task, "dic-loader");
        thread.setDaemon(true);
        thread.start();
    }

    private CommonFlagAnalyzer.FlagMode getEffectiveMode() {
        CommonFlagAnalyzer.FlagMode selected = modeChoice.getValue();
        if (selected == null) {
            selected = CommonFlagAnalyzer.FlagMode.AUTO;
        }
        if (selected == CommonFlagAnalyzer.FlagMode.AUTO && currentData != null) {
            return currentData.getDetectedMode();
        }
        return selected;
    }

    private void refreshSelectionPreview() {
        List<DicEntry> selected = getCheckedEntries();
        if (selected.isEmpty()) {
            selectionArea.setText("");
            resultArea.setText("");
            statusLabel.setText(currentData == null ? "Load a .dic file to begin." : "Tick one or more stems to analyze.");
            return;
        }

        CommonFlagAnalyzer.FlagMode effectiveMode = getEffectiveMode();
        String selectedCategory = CommonFlagAnalyzer.commonCategory(selected);
        StringJoiner preview = new StringJoiner(System.lineSeparator());
        for (DicEntry entry : selected) {
            preview.add((entry.getCategory().isBlank() ? "(ungrouped)" : entry.getCategory()) + " :: " + entry.getStem() + " -> " + entry.getNormalizedFlagsText(effectiveMode));
        }
        selectionArea.setText(preview.toString());
        statusLabel.setText(selected.size() + " stems checked" + (selectedCategory.isBlank() ? "." : " from category: " + selectedCategory + "."));
    }

    private void runAnalysis() {
        List<DicEntry> selected = getCheckedEntries();
        if (selected.isEmpty()) {
            showInfo("No stems selected", "Tick at least one stem before analyzing common flags.");
            return;
        }

        CommonFlagAnalyzer.AnalysisResult result = CommonFlagAnalyzer.analyze(selected, getEffectiveMode());
        renderResult(result);
        copyButton.setDisable(false);
        exportButton.setDisable(false);
    }

    private void renderResult(CommonFlagAnalyzer.AnalysisResult result) {
        String categoryLabel = result.getCategory().isBlank()
            ? (result.getSelectedEntries().isEmpty() ? "(unknown)" : "mixed")
            : result.getCategory();

        StringBuilder text = new StringBuilder();
        //text.append("Source: ").append(currentDicPath == null ? "(none)" : currentDicPath.toAbsolutePath()).append(System.lineSeparator());
        //text.append("Mode: ").append(result.getMode()).append(System.lineSeparator());
        //text.append("Category: ").append(categoryLabel).append(System.lineSeparator());
        text.append("Selected stems: ").append(result.getSelectedEntries().size()).append(System.lineSeparator());
        text.append("Common flag count: ").append(result.getCommonFlagCount()).append(System.lineSeparator());
        text.append("Common flags (raw): ").append(result.getCommonFlagsText().isEmpty() ? "(none)" : result.getCommonFlagsText()).append(System.lineSeparator());
        //text.append("Common flags (tokens): ").append(result.getCommonFlags().isEmpty() ? "(none)" : String.join(", ", result.getCommonFlags())).append(System.lineSeparator());
        text.append("Unique flag count: ").append(result.getUniqueFlagCount()).append(System.lineSeparator());
        text.append("Unique flags across selected stems: ").append(result.getUniqueFlags().isEmpty() ? "(none)" : String.join(", ", result.getUniqueFlags())).append(System.lineSeparator());
        text.append(System.lineSeparator());
        text.append("Selected stem details:").append(System.lineSeparator());
        for (CommonFlagAnalyzer.StemAnalysis stemAnalysis : result.getStemAnalyses()) {
            DicEntry entry = stemAnalysis.getEntry();
            text.append("- ")
                    .append(entry.getStem())
                .append(" -> unique flag count: ")
                .append(stemAnalysis.getUniqueFlagCount())
                .append("; unique flags: ")
                    .append(stemAnalysis.getUniqueFlags().isEmpty() ? "(none)" : String.join(", ", stemAnalysis.getUniqueFlags()))
                    .append(System.lineSeparator());
        }

        // if (result.isEmpty()) {
        //     text.append(System.lineSeparator())
        //             .append("No common flag group was found for the selected stems.")
        //             .append(System.lineSeparator());
        // } else {
        //     text.append(System.lineSeparator())
        //             .append("Suggested common group flags: ")
        //             .append(result.getCommonFlagsText())
        //             .append(System.lineSeparator());
        // }

        resultArea.setText(text.toString());
        statusLabel.setText(result.isEmpty()
                ? "No common flags found for the selected stems."
                : "Common group candidate found: " + result.getCommonFlagsText());
    }

    private void copyResultToClipboard() {
        String text = resultArea.getText();
        if (text == null || text.trim().isEmpty()) {
            showInfo("Nothing to copy", "Run an analysis first.");
            return;
        }
        ClipboardContent content = new ClipboardContent();
        content.putString(text);
        Clipboard.getSystemClipboard().setContent(content);
        statusLabel.setText("Result copied to clipboard.");
    }

    private void exportReport(Stage stage) {
        String text = resultArea.getText();
        if (text == null || text.trim().isEmpty()) {
            showInfo("Nothing to export", "Run an analysis first.");
            return;
        }

        FileChooser chooser = new FileChooser();
        chooser.setTitle("Export common flag analysis");
        chooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("Text report", "*.txt"));
        String baseName = currentDicPath == null ? "common-flags" : stripDictionaryExtension(currentDicPath.getFileName().toString());
        chooser.setInitialFileName(baseName + ".common-flags.txt");
        java.io.File target = chooser.showSaveDialog(stage);
        if (target == null) {
            return;
        }
        try {
            java.nio.file.Files.writeString(target.toPath(), text, java.nio.charset.StandardCharsets.UTF_8);
            statusLabel.setText("Exported report to " + target.getAbsolutePath());
        } catch (IOException ex) {
            showError("Failed to export report", ex.getMessage());
        }
    }

    private void updateButtons() {
        boolean hasSelection = !getCheckedEntries().isEmpty();
        analyzeButton.setDisable(!hasSelection || currentData == null);
        copyButton.setDisable(resultArea.getText() == null || resultArea.getText().trim().isEmpty());
        exportButton.setDisable(resultArea.getText() == null || resultArea.getText().trim().isEmpty());
    }

    private List<DicEntry> getCheckedEntries() {
        List<DicEntry> checked = new ArrayList<>();
        for (DicEntry entry : allEntries) {
            if (entry != null && entry.isChecked()) {
                checked.add(entry);
            }
        }
        return checked;
    }

    private void setAllChecked(boolean checked) {
        for (DicEntry entry : allEntries) {
            if (entry != null) {
                entry.setChecked(checked);
            }
        }
        tableView.refresh();
        refreshSelectionPreview();
        updateButtons();
    }

    private void attachCheckedListeners(List<DicEntry> entries) {
        if (entries == null) {
            return;
        }
        for (DicEntry entry : entries) {
            if (entry == null) {
                continue;
            }
            entry.checkedProperty().addListener((obs, oldValue, newValue) -> {
                refreshSelectionPreview();
                updateButtons();
            });
        }
    }

    private void showInfo(String title, String message) {
        Alert alert = new Alert(Alert.AlertType.INFORMATION, message, ButtonType.OK);
        alert.setHeaderText(title);
        alert.showAndWait();
    }

    private void showError(String title, String message) {
        Alert alert = new Alert(Alert.AlertType.ERROR, message, ButtonType.OK);
        alert.setHeaderText(title);
        alert.showAndWait();
    }

    private static String stripDictionaryExtension(String fileName) {
        if (fileName == null || fileName.isBlank()) {
            return "common-flags";
        }
        String out = fileName.trim();
        if (out.toLowerCase(Locale.ROOT).endsWith(".dic.txt")) {
            return out.substring(0, out.length() - ".dic.txt".length());
        }
        if (out.toLowerCase(Locale.ROOT).endsWith(".dic")) {
            return out.substring(0, out.length() - ".dic".length());
        }
        if (out.toLowerCase(Locale.ROOT).endsWith(".txt")) {
            return out.substring(0, out.length() - ".txt".length());
        }
        return out;
    }

    public static void main(String[] args) {
        launch(args);
    }
}