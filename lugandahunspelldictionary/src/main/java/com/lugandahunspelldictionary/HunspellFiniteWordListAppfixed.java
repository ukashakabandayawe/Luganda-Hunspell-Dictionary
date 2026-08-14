package com.lugandahunspelldictionary;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.concurrent.Task;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.ButtonType;
import javafx.scene.control.Label;
import javafx.scene.control.ProgressBar;
import javafx.scene.control.Spinner;
import javafx.scene.control.SpinnerValueFactory;
import javafx.scene.control.TextArea;
import javafx.scene.control.TextField;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Priority;
import javafx.scene.layout.VBox;
import javafx.stage.FileChooser;
import javafx.stage.Stage;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeSet;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class HunspellFiniteWordListAppfixed extends Application {

    private final TextField affField = new TextField();
    private final TextField dicField = new TextField();
    private final TextField outField = new TextField();
    private final TextField stemField = new TextField();

    private final Spinner<Integer> maxCompoundPartsSpinner =
        new Spinner<>(new SpinnerValueFactory.IntegerSpinnerValueFactory(2, 3, 2));
    private final Spinner<Integer> maxWordsSpinner =
        new Spinner<>(new SpinnerValueFactory.IntegerSpinnerValueFactory(1000, 2147483647, 500000));

    private final ProgressBar progressBar = new ProgressBar(0);
    private final Label progressLabel = new Label("Idle");
    private final TextArea logArea = new TextArea();
    private final TextArea inspectArea = new TextArea();

    private final AtomicBoolean busy = new AtomicBoolean(false);

    private final ModelCache cache = new ModelCache();

    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage stage) {
        stage.setTitle("Hunspell Finite Word List Expander");

        affField.setPromptText("Path to .aff");
        dicField.setPromptText("Path to .dic");
        outField.setPromptText("Path to output .txt");
        stemField.setPromptText("Type root/stem from dictionary");

        maxCompoundPartsSpinner.setEditable(true);
        maxWordsSpinner.setEditable(true);

        Button pickAffBtn = new Button("Browse .aff");
        Button pickDicBtn = new Button("Browse .dic");
        Button pickOutBtn = new Button("Browse output");
        Button runBtn = new Button("Expand to TXT");
        Button inspectBtn = new Button("Inspect Stem");

        pickAffBtn.setOnAction(e -> chooseFile(stage, affField, "AFF Files", "*.aff"));
        pickDicBtn.setOnAction(e -> chooseFile(stage, dicField, "DIC Files", "*.dic"));
        pickOutBtn.setOnAction(e -> chooseSave(stage));

        runBtn.setOnAction(e -> runExpansion());
        inspectBtn.setOnAction(e -> inspectStem());

        GridPane fileGrid = new GridPane();
        fileGrid.setHgap(8);
        fileGrid.setVgap(8);
        fileGrid.add(new Label("AFF"), 0, 0);
        fileGrid.add(affField, 1, 0);
        fileGrid.add(pickAffBtn, 2, 0);
        fileGrid.add(new Label("DIC"), 0, 1);
        fileGrid.add(dicField, 1, 1);
        fileGrid.add(pickDicBtn, 2, 1);
        fileGrid.add(new Label("Output TXT"), 0, 2);
        fileGrid.add(outField, 1, 2);
        fileGrid.add(pickOutBtn, 2, 2);

        GridPane.setHgrow(affField, Priority.ALWAYS);
        GridPane.setHgrow(dicField, Priority.ALWAYS);
        GridPane.setHgrow(outField, Priority.ALWAYS);

        HBox options = new HBox(10,
            new Label("Max compound parts:"), maxCompoundPartsSpinner,
            new Label("Max output words:"), maxWordsSpinner,
            runBtn
        );

        HBox stemBox = new HBox(8, new Label("Stem:"), stemField, inspectBtn);
        HBox.setHgrow(stemField, Priority.ALWAYS);

        progressBar.setPrefWidth(500);

        logArea.setEditable(false);
        logArea.setWrapText(true);
        logArea.setPromptText("Progress log...");
        inspectArea.setEditable(false);
        inspectArea.setWrapText(true);
        inspectArea.setPromptText("Stem forms and compounds...");

        VBox root = new VBox(10,
            fileGrid,
            options,
            new HBox(10, progressBar, progressLabel),
            new Label("Run Log"),
            logArea,
            stemBox,
            new Label("Stem Inspector"),
            inspectArea
        );
        root.setPadding(new Insets(12));
        VBox.setVgrow(logArea, Priority.ALWAYS);
        VBox.setVgrow(inspectArea, Priority.ALWAYS);

        stage.setScene(new Scene(root, 1100, 760));
        stage.show();

        // Convenient default paths if user opens from this repo root.
        Path cwd = Paths.get(System.getProperty("user.dir"));
        Path defaultAff = cwd.resolve("Luganda.aff");
        Path defaultDic = cwd.resolve("Luganda.dic");
        if (Files.exists(defaultAff) && affField.getText().isBlank()) {
            affField.setText(defaultAff.toString());
        }
        if (Files.exists(defaultDic) && dicField.getText().isBlank()) {
            dicField.setText(defaultDic.toString());
        }
        if (outField.getText().isBlank()) {
            outField.setText(cwd.resolve("expanded_words.txt").toString());
        }
    }

    private void inspectStem() {
        if (!busy.compareAndSet(false, true)) {
            showWarn("A task is already running.");
            return;
        }

        String stem = stemField.getText() == null ? "" : stemField.getText().trim();
        if (stem.isEmpty()) {
            busy.set(false);
            showWarn("Please type a stem/root word.");
            return;
        }

        Path affPath = safePath(affField.getText());
        Path dicPath = safePath(dicField.getText());
        if (affPath == null || dicPath == null) {
            busy.set(false);
            showWarn("Please provide valid AFF and DIC paths.");
            return;
        }

        int maxParts = maxCompoundPartsSpinner.getValue();
        final int inspectorMax = 200_000;

        Task<String> task = new Task<>() {
            @Override
            protected String call() throws Exception {
                updateMessage("Loading model...");
                HunspellModel model = cache.getOrLoad(affPath, dicPath);

                List<DicEntry> matching = new ArrayList<>();
                for (DicEntry e : model.entries) {
                    if (e.stem.equals(stem)) {
                        matching.add(e);
                    }
                }

                if (matching.isEmpty()) {
                    return "Stem not found in dictionary: " + stem;
                }

                StringBuilder sb = new StringBuilder();
                sb.append("Stem: ").append(stem).append('\n');
                sb.append("Matching DIC entries: ").append(matching.size()).append("\n\n");

                LinkedHashSet<String> affixed = new LinkedHashSet<>();
                for (DicEntry entry : matching) {
                    Set<String> forms = generateAffixedForms(entry, model);
                    affixed.addAll(forms);

                    sb.append("Entry flags: ").append(flagsToString(entry.flags)).append('\n');
                    sb.append("Affixed forms for this entry: ").append(forms.size()).append('\n');
                }

                List<String> affixedSorted = new ArrayList<>(affixed);
                Collections.sort(affixedSorted);

                sb.append("\nAll affixed forms (unique): ").append(affixedSorted.size()).append("\n");
                appendLimited(sb, affixedSorted, 400);

                /*
                 * Build the candidate index once, but do not create the huge
                 * allCandidates list that the original inspector used.
                 */
                CompoundCandidates candidates = new CompoundCandidates();
                int processed = 0;
                for (DicEntry entry : model.entries) {
                    if (isCancelled()) {
                        return "Cancelled.";
                    }

                    Set<String> forms = generateAffixedForms(entry, model);
                    for (String form : forms) {
                        addCompoundCandidate(
                            candidates,
                            new WordRecord(form, entry.flags),
                            model
                        );
                    }

                    processed++;
                    if (processed % 200 == 0 || processed == model.entries.size()) {
                        updateProgress(processed,
                            Math.max(model.entries.size(), 1));
                        updateMessage("Indexing compound candidates: "
                            + processed + "/" + model.entries.size());
                    }
                }

                Set<String> targetForms = new HashSet<>(affixed);

                LinkedHashSet<String> involvingStem = new LinkedHashSet<>();

                updateMessage("Finding compounds involving the selected stem...");
                generateCompoundsInvolvingTarget(
                    model,
                    candidates,
                    targetForms,
                    maxParts,
                    inspectorMax,
                    involvingStem,
                    (done, total, message) -> updateMessage(message),
                    this::isCancelled
                );

                List<String> involvingStemSorted = new ArrayList<>(involvingStem);
                Collections.sort(involvingStemSorted);

                sb.append("\nCompounded forms involving this stem/forms: ")
                  .append(involvingStemSorted.size()).append("\n");
                appendLimited(sb, involvingStemSorted, 400);

                return sb.toString();
            }
        };

        task.setOnRunning(e -> progressLabel.textProperty().bind(task.messageProperty()));
        task.setOnSucceeded(e -> {
            progressLabel.textProperty().unbind();
            progressLabel.setText("Done");
            inspectArea.setText(task.getValue());
            busy.set(false);
        });
        task.setOnFailed(e -> {
            progressLabel.textProperty().unbind();
            progressLabel.setText("Failed");
            Throwable ex = task.getException();
            inspectArea.setText("Error: " + (ex == null ? "Unknown" : ex.toString()));
            busy.set(false);
        });
        task.setOnCancelled(e -> {
            progressLabel.textProperty().unbind();
            progressLabel.setText("Cancelled");
            busy.set(false);
        });

        Thread t = new Thread(task, "hunspell-inspect-task");
        t.setDaemon(true);
        t.start();
    }

    private void chooseSave(Stage stage) {
        FileChooser chooser = new FileChooser();
        chooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("Text Files", "*.txt"));
        chooser.setInitialFileName("expanded_words.txt");
        if (!outField.getText().isBlank()) {
            Path p = safePath(outField.getText());
            if (p != null && p.getParent() != null && Files.exists(p.getParent())) {
                chooser.setInitialDirectory(p.getParent().toFile());
            }
        }
        java.io.File f = chooser.showSaveDialog(stage);
        if (f != null) {
            outField.setText(f.toPath().toAbsolutePath().toString());
        }
    }

    private void runExpansion() {
        if (!busy.compareAndSet(false, true)) {
            showWarn("A task is already running.");
            return;
        }

        Path affPath = safePath(affField.getText());
        Path dicPath = safePath(dicField.getText());
        Path outPath = safePath(outField.getText());

        if (affPath == null || dicPath == null || outPath == null) {
            busy.set(false);
            showWarn("Please provide valid AFF, DIC and output paths.");
            return;
        }

        int maxParts = maxCompoundPartsSpinner.getValue();
        int maxWords = maxWordsSpinner.getValue();

        Task<Void> task = new Task<>() {
            @Override
            protected Void call() throws Exception {
                long t0 = System.currentTimeMillis();
                updateMessage("Parsing AFF and DIC...");
                updateProgress(0, 1);

                HunspellModel model = cache.getOrLoad(affPath, dicPath);
                log("Loaded AFF rules: " + model.affixRulesByFlag.size() + " flags");
                log("Loaded DIC entries: " + model.entries.size());

                LinkedHashSet<String> words = new LinkedHashSet<>();
                List<WordRecord> candidatesForCompounds = new ArrayList<>();

                int total = model.entries.size();
                int idx = 0;
                for (DicEntry entry : model.entries) {
                    if (isCancelled()) {
                        break;
                    }
                    idx++;

                    Set<String> forms = generateAffixedForms(entry, model);
                    if (!entry.hasFlag(model.onlyInCompoundFlag)) {
                        words.addAll(forms);
                    }

                    for (String form : forms) {
                        candidatesForCompounds.add(new WordRecord(form, entry.flags));
                    }

                    if (idx % 200 == 0 || idx == total) {
                        updateProgress(idx, Math.max(total, 1));
                        updateMessage("Expanding affixes: " + idx + "/" + total);
                    }

                    if (words.size() >= maxWords) {
                        log("Max output words reached while building affixed forms. Stopping early.");
                        break;
                    }
                }

                updateMessage("Building compounds...");
                Set<String> compounds = generateCompounds(
                    model,
                    candidatesForCompounds,
                    maxParts,
                    maxWords - words.size(),
                    (done, ttl, message) -> {
                        updateProgress(done, total);
                        updateMessage(message);
                    }
                );
                words.addAll(compounds);

                updateMessage("Sorting and writing output...");
                List<String> sorted = new ArrayList<>(words);
                sorted.sort(Comparator.naturalOrder());

                writeWordList(outPath, sorted);

                long dt = System.currentTimeMillis() - t0;
                updateProgress(1, 1);
                updateMessage("Done");

                log("Final words: " + sorted.size());
                log("Output: " + outPath.toAbsolutePath());
                log("Elapsed: " + dt + " ms");
                return null;
            }
        };

        bindTask(task);
        task.setOnSucceeded(e -> busy.set(false));
        task.setOnFailed(e -> {
            busy.set(false);
            Throwable ex = task.getException();
            log("ERROR: " + (ex == null ? "Unknown" : ex.getMessage()));
            showError(ex == null ? "Unknown error" : ex.toString());
        });
        task.setOnCancelled(e -> busy.set(false));

        Thread thread = new Thread(task, "hunspell-expand-task");
        thread.setDaemon(true);
        thread.start();
    }

    private static void writeWordList(Path outPath, List<String> words) throws IOException {
        if (outPath.getParent() != null) {
            Files.createDirectories(outPath.getParent());
        }

        try (BufferedWriter bw = Files.newBufferedWriter(
                outPath, StandardCharsets.UTF_8)) {
            bw.write(Integer.toString(words.size()));
            bw.newLine();

            for (String w : words) {
                bw.write(w);
                bw.newLine();
            }
        }
    }

    private static List<String> sortedWords(Set<String> words) {
        List<String> sorted = new ArrayList<>(words);
        sorted.sort(Comparator.naturalOrder());
        return sorted;
    }

    private static void appendLimited(StringBuilder sb, List<String> items, int limit) {
        int n = Math.min(items.size(), limit);
        for (int i = 0; i < n; i++) {
            sb.append(items.get(i)).append('\n');
        }
        if (items.size() > limit) {
            sb.append("... truncated, showing ").append(limit).append(" of ").append(items.size()).append("\n");
        }
    }

    private void bindTask(Task<?> task) {
        progressBar.progressProperty().unbind();
        progressLabel.textProperty().unbind();

        progressBar.progressProperty().bind(task.progressProperty());
        progressLabel.textProperty().bind(task.messageProperty());

        task.setOnSucceeded(e -> {
            progressBar.progressProperty().unbind();
            progressLabel.textProperty().unbind();
            progressBar.setProgress(1.0);
            progressLabel.setText("Done");
        });
        task.setOnCancelled(e -> {
            progressBar.progressProperty().unbind();
            progressLabel.textProperty().unbind();
            progressLabel.setText("Cancelled");
        });
    }

    private void log(String s) {
        Platform.runLater(() -> {
            logArea.appendText(s + "\n");
            logArea.setScrollTop(Double.MAX_VALUE);
        });
    }

    private void showWarn(String msg) {
        Alert alert = new Alert(Alert.AlertType.WARNING, msg, ButtonType.OK);
        alert.setHeaderText(null);
        alert.showAndWait();
    }

    private void showError(String msg) {
        Alert alert = new Alert(Alert.AlertType.ERROR, msg, ButtonType.OK);
        alert.setHeaderText(null);
        alert.showAndWait();
    }

    private static Path safePath(String raw) {
        if (raw == null || raw.isBlank()) {
            return null;
        }
        try {
            return Paths.get(raw.trim());
        } catch (Exception e) {
            return null;
        }
    }

    private static Set<String> generateAffixedForms(DicEntry entry, HunspellModel model) {
        LinkedHashSet<String> out = new LinkedHashSet<>();
        out.add(entry.stem);

        List<AffixRule> pfxRules = new ArrayList<>();
        List<AffixRule> sfxRules = new ArrayList<>();

        for (String flag : entry.flags) {
            List<AffixRule> rules = model.affixRulesByFlag.get(flag);
            if (rules == null || rules.isEmpty()) {
                continue;
            }
            for (AffixRule r : rules) {
                String w = r.apply(entry.stem);
                if (w != null) {
                    out.add(w);
                }
                if (r.type == AffixType.PREFIX) {
                    pfxRules.add(r);
                } else {
                    sfxRules.add(r);
                }
            }
        }

        // Prefix+suffix only when both rules explicitly allow cross product (Y).
        for (AffixRule p : pfxRules) {
            if (!p.crossProduct) {
                continue;
            }
            String pw = p.apply(entry.stem);
            if (pw == null) {
                continue;
            }
            for (AffixRule s : sfxRules) {
                if (!s.crossProduct) {
                    continue;
                }
                String sw = s.apply(pw);
                if (sw != null) {
                    out.add(sw);
                }
            }
        }

        if (entry.hasFlag(model.forbiddenWordFlag)) {
            out.clear();
        }
        return out;
    }

    private static void addCompoundCandidate(
            CompoundCandidates candidates,
            WordRecord wr,
            HunspellModel model) {

        if (wr == null || wr.word == null || wr.word.isEmpty()) {
            return;
        }

        if (countWordChars(wr.word, model.wordChars) < model.compoundMin) {
            return;
        }

        boolean onlyInCompound = wr.hasFlag(model.onlyInCompoundFlag);

        boolean isBegin =
            wr.hasFlag(model.compoundBeginFlag) ||
            wr.hasFlag(model.compoundFlag);

        boolean isEnd =
            wr.hasFlag(model.compoundEndFlag) ||
            wr.hasFlag(model.compoundFlag);

        boolean isMid =
            wr.hasFlag(model.compoundFlag) ||
            wr.hasFlag(model.compoundPermitFlag);

        if (isBegin) {
            candidates.begin.add(wr);
        }

        if (isMid) {
            candidates.mid.add(wr);
        }

        if (isEnd || onlyInCompound) {
            candidates.end.add(wr);
        }
    }

    private static final class CompoundCandidates {
        final List<WordRecord> begin = new ArrayList<>();
        final List<WordRecord> mid = new ArrayList<>();
        final List<WordRecord> end = new ArrayList<>();

        boolean isEmpty() {
            return begin.isEmpty() && mid.isEmpty() && end.isEmpty();
        }
    }

    private static void generateCompoundsInto(
            HunspellModel model,
            CompoundCandidates candidates,
            int maxParts,
            int maxWords,
            Set<String> output,
            ProgressReporter progressOrNull,
            BooleanSupplier cancelled) {

        if (maxWords <= 0 || candidates.isEmpty()) {
            return;
        }

        boolean hasCompoundDirectives =
            model.compoundFlag != null ||
            model.compoundBeginFlag != null ||
            model.compoundEndFlag != null;

        if (!hasCompoundDirectives) {
            return;
        }

        long totalPairs =
            (long) candidates.begin.size() *
            Math.max(1, candidates.end.size());

        long done = 0;
        int added = 0;

        for (WordRecord b : candidates.begin) {
            for (WordRecord e : candidates.end) {
                if (cancelled != null && cancelled.getAsBoolean()) {
                    return;
                }

                done++;

                if (progressOrNull != null &&
                    (done % 20_000 == 0 || done == totalPairs)) {

                    progressOrNull.report(
                        done,
                        Math.max(totalPairs, 1),
                        "Compounding (2-part): "
                            + done + "/" + totalPairs
                    );
                }

                if (!matchesCompoundRule(model, List.of(b, e))) {
                    continue;
                }

                String c2 = b.word + e.word;

                if (!isLegalCompound(
                        model,
                        List.of(b.word, e.word),
                        c2)) {
                    continue;
                }

                if (output.add(c2)) {
                    added++;
                    if (added >= maxWords) {
                        return;
                    }
                }
            }
        }

        if (maxParts >= 3 && !candidates.mid.isEmpty()) {
            long totalTriples =
                (long) candidates.begin.size() *
                candidates.mid.size() *
                Math.max(1, candidates.end.size());

            long done3 = 0;

            for (WordRecord b : candidates.begin) {
                for (WordRecord m : candidates.mid) {
                    for (WordRecord e : candidates.end) {
                        if (cancelled != null && cancelled.getAsBoolean()) {
                            return;
                        }

                        done3++;

                        if (progressOrNull != null &&
                            (done3 % 50_000 == 0 || done3 == totalTriples)) {

                            progressOrNull.report(
                                done3,
                                Math.max(totalTriples, 1),
                                "Compounding (3-part): "
                                    + done3 + "/" + totalTriples
                            );
                        }

                        if (!matchesCompoundRule(
                                model,
                                List.of(b, m, e))) {
                            continue;
                        }

                        String c3 = b.word + m.word + e.word;

                        if (!isLegalCompound(
                                model,
                                List.of(b.word, m.word, e.word),
                                c3)) {
                            continue;
                        }

                        if (output.add(c3)) {
                            added++;
                            if (added >= maxWords) {
                                return;
                            }
                        }
                    }
                }
            }
        }
    }

    /*
     * Inspector-specific generator.
     *
     * Instead of generating every possible compound and subsequently checking
     * whether the finished string contains one of the stem forms, this method
     * only considers combinations in which a component is one of targetWords.
     */
    private static void generateCompoundsInvolvingTarget(
            HunspellModel model,
            CompoundCandidates candidates,
            Set<String> targetWords,
            int maxParts,
            int maxWords,
            Set<String> output,
            ProgressReporter progressOrNull,
            BooleanSupplier cancelled) {

        if (maxWords <= 0 || targetWords.isEmpty()) {
            return;
        }

        int added = 0;

        // Two-part: target as beginning.
        for (WordRecord b : candidates.begin) {
            if (!targetWords.contains(b.word)) {
                continue;
            }

            for (WordRecord e : candidates.end) {
                if (cancelled != null && cancelled.getAsBoolean()) {
                    return;
                }

                if (!matchesCompoundRule(model, List.of(b, e))) {
                    continue;
                }

                String c = b.word + e.word;

                if (isLegalCompound(model, List.of(b.word, e.word), c)
                        && output.add(c)) {

                    added++;
                    if (progressOrNull != null && added % 1000 == 0) {
                        progressOrNull.report(
                            added, maxWords,
                            "Inspecting compounds: " + added + "/" + maxWords
                        );
                    }

                    if (added >= maxWords) {
                        return;
                    }
                }
            }
        }

        // Two-part: target as ending.
        for (WordRecord b : candidates.begin) {
            for (WordRecord e : candidates.end) {
                if (cancelled != null && cancelled.getAsBoolean()) {
                    return;
                }

                if (!targetWords.contains(e.word)) {
                    continue;
                }

                if (!matchesCompoundRule(model, List.of(b, e))) {
                    continue;
                }

                String c = b.word + e.word;

                if (isLegalCompound(model, List.of(b.word, e.word), c)
                        && output.add(c)) {

                    added++;
                    if (added >= maxWords) {
                        return;
                    }
                }
            }
        }

        if (maxParts < 3 || candidates.mid.isEmpty()) {
            return;
        }

        // Three-part: target as beginning.
        for (WordRecord b : candidates.begin) {
            if (!targetWords.contains(b.word)) {
                continue;
            }

            for (WordRecord m : candidates.mid) {
                for (WordRecord e : candidates.end) {
                    if (cancelled != null && cancelled.getAsBoolean()) {
                        return;
                    }

                    if (!matchesCompoundRule(model, List.of(b, m, e))) {
                        continue;
                    }

                    String c = b.word + m.word + e.word;

                    if (isLegalCompound(
                            model,
                            List.of(b.word, m.word, e.word),
                            c)
                            && output.add(c)) {

                        added++;
                        if (added >= maxWords) {
                            return;
                        }
                    }
                }
            }
        }

        // Three-part: target as middle.
        for (WordRecord b : candidates.begin) {
            for (WordRecord m : candidates.mid) {
                if (!targetWords.contains(m.word)) {
                    continue;
                }

                for (WordRecord e : candidates.end) {
                    if (cancelled != null && cancelled.getAsBoolean()) {
                        return;
                    }

                    if (!matchesCompoundRule(model, List.of(b, m, e))) {
                        continue;
                    }

                    String c = b.word + m.word + e.word;

                    if (isLegalCompound(
                            model,
                            List.of(b.word, m.word, e.word),
                            c)
                            && output.add(c)) {

                        added++;
                        if (added >= maxWords) {
                            return;
                        }
                    }
                }
            }
        }

        // Three-part: target as ending.
        for (WordRecord b : candidates.begin) {
            for (WordRecord m : candidates.mid) {
                for (WordRecord e : candidates.end) {
                    if (cancelled != null && cancelled.getAsBoolean()) {
                        return;
                    }

                    if (!targetWords.contains(e.word)) {
                        continue;
                    }

                    if (!matchesCompoundRule(model, List.of(b, m, e))) {
                        continue;
                    }

                    String c = b.word + m.word + e.word;

                    if (isLegalCompound(
                            model,
                            List.of(b.word, m.word, e.word),
                            c)
                            && output.add(c)) {

                        added++;
                        if (added >= maxWords) {
                            return;
                        }
                    }
                }
            }
        }
    }

    private static boolean isLegalCompound(HunspellModel model, List<String> parts, String fullWord) {
        if (parts.size() < 2) {
            return false;
        }
        if (fullWord == null || fullWord.isEmpty()) {
            return false;
        }
        if (model.forbiddenWords.contains(fullWord)) {
            return false;
        }

        for (int i = 0; i < parts.size(); i++) {
            if (countWordChars(parts.get(i), model.wordChars) < model.compoundMin) {
                return false;
            }
        }

        for (int i = 0; i < parts.size() - 1; i++) {
            String left = parts.get(i);
            String right = parts.get(i + 1);
            for (CheckCompoundPattern p : model.checkCompoundPatterns) {
                if (p.blocks(left, right)) {
                    return false;
                }
            }
        }
        return true;
    }

    private static boolean matchesCompoundRule(HunspellModel model, List<WordRecord> parts) {
        if (model.compoundRules.isEmpty()) {
            return true;
        }
        for (List<String> rule : model.compoundRules) {
            if (rule.size() != parts.size()) {
                continue;
            }
            boolean ok = true;
            for (int i = 0; i < rule.size(); i++) {
                String needed = rule.get(i);
                if (!parts.get(i).hasFlag(needed)) {
                    ok = false;
                    break;
                }
            }
            if (ok) {
                return true;
            }
        }
        return false;
    }

    private static int countWordChars(String s, Set<Character> extraWordChars) {
        if (s == null || s.isEmpty()) {
            return 0;
        }
        int n = 0;
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (Character.isLetterOrDigit(ch) || extraWordChars.contains(ch)) {
                n++;
            }
        }
        return n;
    }

    private static String flagsToString(Set<String> flags) {
        if (flags == null || flags.isEmpty()) {
            return "(none)";
        }
        List<String> list = new ArrayList<>(flags);
        Collections.sort(list);
        return String.join(",", list);
    }

    @FunctionalInterface
    private interface ProgressReporter {
        void report(long done, long total, String message);
    }

    // ------------------------------------------------------------
    // Parsing and model classes
    // ------------------------------------------------------------

    private static final class ModelCache {
        private Path lastAff;
        private Path lastDic;
        private long lastAffMtime;
        private long lastDicMtime;
        private HunspellModel lastModel;

        synchronized HunspellModel getOrLoad(Path affPath, Path dicPath) throws IOException {
            Path na = affPath.toAbsolutePath().normalize();
            Path nd = dicPath.toAbsolutePath().normalize();
            long am = Files.getLastModifiedTime(na).toMillis();
            long dm = Files.getLastModifiedTime(nd).toMillis();
            if (lastModel != null && na.equals(lastAff) && nd.equals(lastDic) && am == lastAffMtime && dm == lastDicMtime) {
                return lastModel;
            }
            HunspellModel m = HunspellParser.parse(na, nd);
            lastAff = na;
            lastDic = nd;
            lastAffMtime = am;
            lastDicMtime = dm;
            lastModel = m;
            return m;
        }
    }

    private enum FlagMode {
        SHORT,
        LONG,
        NUM,
        UTF8
    }

    private enum AffixType {
        PREFIX,
        SUFFIX
    }

    private static final class AffixRule {
        final String flag;
        final AffixType type;
        final String strip;
        final String add;
        final String condition;
        final boolean crossProduct;
        final Pattern conditionPattern;

        AffixRule(String flag, AffixType type, String strip, String add, String condition, boolean crossProduct) {
            this.flag = flag;
            this.type = type;
            this.strip = normalizeZero(strip);
            this.add = normalizeZero(add);
            this.condition = (condition == null || condition.isBlank()) ? "." : condition.trim();
            this.crossProduct = crossProduct;
            this.conditionPattern = compileCondition(this.condition, type);
        }

        String apply(String stem) {
            if (stem == null || stem.isEmpty()) {
                return null;
            }
            if (!conditionPattern.matcher(stem).matches()) {
                return null;
            }

            String base = stem;
            if (!strip.isEmpty()) {
                if (type == AffixType.PREFIX) {
                    if (!base.startsWith(strip)) {
                        return null;
                    }
                    base = base.substring(strip.length());
                } else {
                    if (!base.endsWith(strip)) {
                        return null;
                    }
                    base = base.substring(0, base.length() - strip.length());
                }
            }

            if (type == AffixType.PREFIX) {
                return add + base;
            }
            return base + add;
        }

        private static Pattern compileCondition(String cond, AffixType type) {
            String c = cond == null ? "." : cond.trim();
            if (c.isEmpty() || c.equals(".")) {
                return Pattern.compile(".*", Pattern.UNICODE_CASE);
            }
            String regex;
            if (type == AffixType.PREFIX) {
                regex = "^(?:" + c + ").*";
            } else {
                regex = ".*(?:" + c + ")$";
            }
            try {
                return Pattern.compile(regex, Pattern.UNICODE_CASE);
            } catch (Exception ex) {
                // Fail-safe: if malformed regex in affix file, make it not apply.
                return Pattern.compile("a^", Pattern.UNICODE_CASE);
            }
        }
    }

    private static final class DicEntry {
        final String stem;
        final Set<String> flags;

        DicEntry(String stem, Set<String> flags) {
            this.stem = stem;
            this.flags = flags == null ? Collections.emptySet() : flags;
        }

        boolean hasFlag(String f) {
            return f != null && !f.isBlank() && flags.contains(f);
        }
    }

    private static final class WordRecord {
        final String word;
        final Set<String> sourceFlags;

        WordRecord(String word, Set<String> sourceFlags) {
            this.word = word;
            this.sourceFlags = sourceFlags == null ? Collections.emptySet() : sourceFlags;
        }

        boolean hasFlag(String f) {
            return f != null && !f.isBlank() && sourceFlags.contains(f);
        }
    }

    private static final class CheckCompoundPattern {
        final String leftEnd;
        final String rightStart;

        CheckCompoundPattern(String leftEnd, String rightStart) {
            this.leftEnd = leftEnd == null ? "" : leftEnd;
            this.rightStart = rightStart == null ? "" : rightStart;
        }

        boolean blocks(String left, String right) {
            if (left == null || right == null) {
                return false;
            }
            boolean leftOk = leftEnd.isEmpty() || left.endsWith(leftEnd);
            boolean rightOk = rightStart.isEmpty() || right.startsWith(rightStart);
            return leftOk && rightOk;
        }
    }

    private static final class HunspellModel {
        final FlagMode flagMode;
        final Set<Character> wordChars;

        final Map<String, List<AffixRule>> affixRulesByFlag;
        final List<DicEntry> entries;

        final String onlyInCompoundFlag;
        final String compoundFlag;
        final String compoundPermitFlag;
        final String compoundBeginFlag;
        final String compoundEndFlag;
        final String forbiddenWordFlag;
        final int compoundMin;

        final List<CheckCompoundPattern> checkCompoundPatterns;
        final List<List<String>> compoundRules;
        final Set<String> forbiddenWords;

        HunspellModel(
            FlagMode flagMode,
            Set<Character> wordChars,
            Map<String, List<AffixRule>> affixRulesByFlag,
            List<DicEntry> entries,
            String onlyInCompoundFlag,
            String compoundFlag,
            String compoundPermitFlag,
            String compoundBeginFlag,
            String compoundEndFlag,
            String forbiddenWordFlag,
            int compoundMin,
            List<CheckCompoundPattern> checkCompoundPatterns,
            List<List<String>> compoundRules,
            Set<String> forbiddenWords
        ) {
            this.flagMode = flagMode;
            this.wordChars = wordChars;
            this.affixRulesByFlag = affixRulesByFlag;
            this.entries = entries;
            this.onlyInCompoundFlag = onlyInCompoundFlag;
            this.compoundFlag = compoundFlag;
            this.compoundPermitFlag = compoundPermitFlag;
            this.compoundBeginFlag = compoundBeginFlag;
            this.compoundEndFlag = compoundEndFlag;
            this.forbiddenWordFlag = forbiddenWordFlag;
            this.compoundMin = compoundMin;
            this.checkCompoundPatterns = checkCompoundPatterns;
            this.compoundRules = compoundRules;
            this.forbiddenWords = forbiddenWords;
        }
    }

    private static final class HunspellParser {

        private static HunspellModel parse(Path affPath, Path dicPath) throws IOException {
            AffData aff = parseAff(affPath);
            List<DicEntry> entries = parseDic(dicPath, aff);

            Set<String> forbiddenWords = new HashSet<>();
            if (aff.forbiddenWordFlag != null && !aff.forbiddenWordFlag.isBlank()) {
                for (DicEntry e : entries) {
                    if (e.hasFlag(aff.forbiddenWordFlag)) {
                        forbiddenWords.add(e.stem);
                    }
                }
            }

            return new HunspellModel(
                aff.flagMode,
                aff.wordChars,
                aff.affixRulesByFlag,
                entries,
                aff.onlyInCompoundFlag,
                aff.compoundFlag,
                aff.compoundPermitFlag,
                aff.compoundBeginFlag,
                aff.compoundEndFlag,
                aff.forbiddenWordFlag,
                aff.compoundMin,
                aff.checkCompoundPatterns,
                aff.compoundRules,
                forbiddenWords
            );
        }

        private static AffData parseAff(Path affPath) throws IOException {
            FlagMode mode = FlagMode.SHORT;
            Set<Character> wordChars = new HashSet<>();
            Map<String, List<AffixRule>> rulesByFlag = new LinkedHashMap<>();

            Map<String, Boolean> crossByFlag = new HashMap<>();
            Map<String, AffixType> typeByFlag = new HashMap<>();

            String onlyInCompoundFlag = null;
            String compoundFlag = null;
            String compoundPermitFlag = null;
            String compoundBeginFlag = null;
            String compoundEndFlag = null;
            String forbiddenWordFlag = null;
            int compoundMin = 3;
            List<CheckCompoundPattern> checkPatterns = new ArrayList<>();
            List<List<String>> compoundRules = new ArrayList<>();

            Map<Integer, String> afAlias = new HashMap<>();

            try (BufferedReader br = Files.newBufferedReader(affPath, StandardCharsets.UTF_8)) {
                String raw;
                while ((raw = br.readLine()) != null) {
                    String line = stripInlineComment(raw).trim();
                    if (line.isEmpty()) {
                        continue;
                    }
                    String[] toks = line.split("\\s+");
                    if (toks.length == 0) {
                        continue;
                    }

                    String key = toks[0].toUpperCase(Locale.ROOT);

                    switch (key) {
                        case "FLAG":
                            if (toks.length >= 2) {
                                String f = toks[1].toLowerCase(Locale.ROOT);
                                if ("long".equals(f)) {
                                    mode = FlagMode.LONG;
                                } else if ("num".equals(f)) {
                                    mode = FlagMode.NUM;
                                } else if ("utf-8".equals(f) || "utf8".equals(f)) {
                                    mode = FlagMode.UTF8;
                                } else {
                                    mode = FlagMode.SHORT;
                                }
                            }
                            break;
                        case "WORDCHARS":
                            if (toks.length >= 2) {
                                String chars = line.substring(line.indexOf(toks[1]));
                                for (int i = 0; i < chars.length(); i++) {
                                    wordChars.add(chars.charAt(i));
                                }
                            }
                            break;
                        case "AF":
                            // AF header: AF 168
                            // AF value line: AF CENAAd
                            if (toks.length >= 2 && toks[1].matches("\\d+")) {
                                // Header line, nothing to store.
                            } else if (toks.length >= 2) {
                                int idx = afAlias.size() + 1;
                                afAlias.put(idx, toks[1]);
                            }
                            break;
                        case "ONLYINCOMPOUND":
                            if (toks.length >= 2) {
                                onlyInCompoundFlag = toks[1];
                            }
                            break;
                        case "COMPOUNDFLAG":
                            if (toks.length >= 2) {
                                compoundFlag = toks[1];
                            }
                            break;
                        case "COMPOUNDPERMITFLAG":
                            if (toks.length >= 2) {
                                compoundPermitFlag = toks[1];
                            }
                            break;
                        case "COMPOUNDBEGIN":
                            if (toks.length >= 2) {
                                compoundBeginFlag = toks[1];
                            }
                            break;
                        case "COMPOUNDEND":
                            if (toks.length >= 2) {
                                compoundEndFlag = toks[1];
                            }
                            break;
                        case "COMPOUNDMIN":
                            if (toks.length >= 2 && toks[1].matches("\\d+")) {
                                compoundMin = Integer.parseInt(toks[1]);
                            }
                            break;
                        case "FORBIDDENWORD":
                            if (toks.length >= 2) {
                                forbiddenWordFlag = toks[1];
                            }
                            break;
                        case "CHECKCOMPOUNDPATTERN":
                            // Simple interpretation of common usage: leftEnd rightStart.
                            if (toks.length >= 2) {
                                String leftEnd = toks[1];
                                String rightStart = toks.length >= 3 ? toks[2] : "";
                                if (!leftEnd.matches("\\d+")) {
                                    checkPatterns.add(new CheckCompoundPattern(normalizeZero(leftEnd), normalizeZero(rightStart)));
                                }
                            }
                            break;
                        case "COMPOUNDRULE":
                            // Header: COMPOUNDRULE N
                            // Rule:   COMPOUNDRULE (AA)(BB)
                            if (toks.length >= 2 && !toks[1].matches("\\d+")) {
                                String expr = line.substring("COMPOUNDRULE".length()).trim();
                                List<String> parsed = parseCompoundRuleExpression(expr);
                                if (!parsed.isEmpty()) {
                                    compoundRules.add(parsed);
                                }
                            }
                            break;
                        case "PFX":
                        case "SFX":
                            parseAffixLine(toks, key, rulesByFlag, crossByFlag, typeByFlag);
                            break;
                        default:
                            break;
                    }
                }
            }

            // Fill crossProduct by header if a rule landed before header.
            for (List<AffixRule> list : rulesByFlag.values()) {
                for (int i = 0; i < list.size(); i++) {
                    AffixRule r = list.get(i);
                    boolean c = crossByFlag.getOrDefault(r.flag, false);
                    if (r.crossProduct != c) {
                        list.set(i, new AffixRule(r.flag, r.type, r.strip, r.add, r.condition, c));
                    }
                }
            }

            AffData out = new AffData();
            out.flagMode = mode;
            out.wordChars = wordChars;
            out.affixRulesByFlag = rulesByFlag;
            out.afAliasByIndex = afAlias;
            out.onlyInCompoundFlag = onlyInCompoundFlag;
            out.compoundFlag = compoundFlag;
            out.compoundPermitFlag = compoundPermitFlag;
            out.compoundBeginFlag = compoundBeginFlag;
            out.compoundEndFlag = compoundEndFlag;
            out.forbiddenWordFlag = forbiddenWordFlag;
            out.compoundMin = compoundMin;
            out.checkCompoundPatterns = checkPatterns;
            out.compoundRules = compoundRules;
            return out;
        }

        private static List<String> parseCompoundRuleExpression(String expr) {
            if (expr == null || expr.isBlank()) {
                return Collections.emptyList();
            }
            List<String> out = new ArrayList<>();
            Matcher m = Pattern.compile("\\(([^)]+)\\)").matcher(expr);
            while (m.find()) {
                String flag = m.group(1) == null ? "" : m.group(1).trim();
                if (!flag.isEmpty()) {
                    out.add(flag);
                }
            }
            return out;
        }

        private static void parseAffixLine(
            String[] toks,
            String key,
            Map<String, List<AffixRule>> rulesByFlag,
            Map<String, Boolean> crossByFlag,
            Map<String, AffixType> typeByFlag
        ) {
            if (toks.length < 4) {
                return;
            }
            AffixType type = "PFX".equals(key) ? AffixType.PREFIX : AffixType.SUFFIX;
            String flag = toks[1];

            // Header: PFX AA Y 123
            if (toks.length >= 4 && ("Y".equalsIgnoreCase(toks[2]) || "N".equalsIgnoreCase(toks[2])) && toks[3].matches("\\d+")) {
                boolean cross = "Y".equalsIgnoreCase(toks[2]);
                crossByFlag.put(flag, cross);
                typeByFlag.put(flag, type);
                rulesByFlag.computeIfAbsent(flag, k -> new ArrayList<>());
                return;
            }

            // Rule line: PFX AA strip add condition
            if (toks.length >= 5) {
                String strip = toks[2];
                String addRaw = toks[3];
                String add = addRaw;
                int slash = addRaw.indexOf('/');
                if (slash >= 0) {
                    add = addRaw.substring(0, slash);
                }
                String cond = toks[4];
                boolean cross = crossByFlag.getOrDefault(flag, false);
                AffixRule rule = new AffixRule(flag, type, strip, add, cond, cross);
                rulesByFlag.computeIfAbsent(flag, k -> new ArrayList<>()).add(rule);
            }
        }

        private static List<DicEntry> parseDic(Path dicPath, AffData aff) throws IOException {
            List<DicEntry> out = new ArrayList<>();
            try (BufferedReader br = Files.newBufferedReader(dicPath, StandardCharsets.UTF_8)) {
                String raw;
                boolean firstNonEmptySeen = false;
                while ((raw = br.readLine()) != null) {
                    String line = stripInlineComment(raw).trim();
                    if (line.isEmpty()) {
                        continue;
                    }
                    if (!firstNonEmptySeen) {
                        firstNonEmptySeen = true;
                        if (line.matches("\\d+")) {
                            continue;
                        }
                    }
                    if (line.startsWith("#")) {
                        continue;
                    }

                    String token = firstToken(line);
                    if (token.isEmpty()) {
                        continue;
                    }

                    String stem;
                    String flagsRaw = null;
                    int slash = token.indexOf('/');
                    if (slash >= 0) {
                        stem = token.substring(0, slash);
                        flagsRaw = token.substring(slash + 1);
                    } else {
                        stem = token;
                    }

                    stem = stem.trim();
                    if (stem.isEmpty()) {
                        continue;
                    }

                    Set<String> flags = parseFlags(flagsRaw, aff.flagMode, aff.afAliasByIndex);
                    out.add(new DicEntry(stem, flags));
                }
            }
            return out;
        }

        private static Set<String> parseFlags(String raw, FlagMode mode, Map<Integer, String> afAliasByIndex) {
            if (raw == null || raw.isBlank()) {
                return Collections.emptySet();
            }
            String src = raw.trim();

            // AF alias can appear as a numeric reference.
            if (src.matches("\\d+")) {
                String alias = afAliasByIndex.get(Integer.parseInt(src));
                if (alias != null) {
                    return parseAliasFlags(alias, mode);
                }
            }

            LinkedHashSet<String> flags = new LinkedHashSet<>();

            if (mode == FlagMode.NUM) {
                String[] parts = src.split(",");
                for (String p : parts) {
                    String q = p.trim();
                    if (!q.isEmpty()) {
                        flags.add(q);
                    }
                }
            } else if (mode == FlagMode.LONG) {
                for (int i = 0; i + 1 < src.length(); i += 2) {
                    flags.add(src.substring(i, i + 2));
                }
            } else {
                // SHORT and UTF8 fallback per character unit.
                for (int i = 0; i < src.length(); i++) {
                    flags.add(String.valueOf(src.charAt(i)));
                }
            }

            // Expand AF aliases when dic flag list contains numeric alias references.
            LinkedHashSet<String> expanded = new LinkedHashSet<>();
            for (String f : flags) {
                if (f.matches("\\d+")) {
                    String alias = afAliasByIndex.get(Integer.parseInt(f));
                    if (alias != null) {
                        expanded.addAll(parseAliasFlags(alias, mode));
                    }
                } else {
                    expanded.add(f);
                }
            }
            return expanded;
        }

        private static Set<String> parseAliasFlags(String alias, FlagMode mode) {
            if (alias == null || alias.isBlank()) {
                return Collections.emptySet();
            }
            LinkedHashSet<String> out = new LinkedHashSet<>();
            String src = alias.trim();
            if (mode == FlagMode.NUM) {
                for (String p : src.split(",")) {
                    String q = p.trim();
                    if (!q.isEmpty()) {
                        out.add(q);
                    }
                }
            } else if (mode == FlagMode.LONG) {
                for (int i = 0; i + 1 < src.length(); i += 2) {
                    out.add(src.substring(i, i + 2));
                }
            } else {
                for (int i = 0; i < src.length(); i++) {
                    out.add(String.valueOf(src.charAt(i)));
                }
            }
            return out;
        }

        private static String firstToken(String line) {
            int ws = -1;
            for (int i = 0; i < line.length(); i++) {
                if (Character.isWhitespace(line.charAt(i))) {
                    ws = i;
                    break;
                }
            }
            return ws < 0 ? line : line.substring(0, ws);
        }

        private static String stripInlineComment(String raw) {
            if (raw == null) {
                return "";
            }
            int idx = raw.indexOf('#');
            if (idx < 0) {
                return raw;
            }
            return raw.substring(0, idx);
        }

        private static final class AffData {
            FlagMode flagMode = FlagMode.SHORT;
            Set<Character> wordChars = new HashSet<>();
            Map<String, List<AffixRule>> affixRulesByFlag = new LinkedHashMap<>();
            Map<Integer, String> afAliasByIndex = new HashMap<>();

            String onlyInCompoundFlag;
            String compoundFlag;
            String compoundPermitFlag;
            String compoundBeginFlag;
            String compoundEndFlag;
            String forbiddenWordFlag;
            int compoundMin = 3;
            List<CheckCompoundPattern> checkCompoundPatterns = new ArrayList<>();
            List<List<String>> compoundRules = new ArrayList<>();
        }
    }

    private void chooseFile(Stage stage, TextField target, String description, String glob) {
        FileChooser chooser = new FileChooser();
        chooser.getExtensionFilters().add(new FileChooser.ExtensionFilter(description, glob));
        if (!target.getText().isBlank()) {
            Path p = safePath(target.getText());
            if (p != null && Files.exists(p.getParent())) {
                chooser.setInitialDirectory(p.getParent().toFile());
            }
        }
        java.io.File f = chooser.showOpenDialog(stage);
        if (f != null) {
            target.setText(f.toPath().toAbsolutePath().toString());
        }
    }

    private static String normalizeZero(String s) {
        if (s == null) {
            return "";
        }
        String t = s.trim();
        return "0".equals(t) ? "" : t;
    }
    private static Set<String> generateCompounds(
        HunspellModel model,
        List<WordRecord> forms,
        int maxParts,
        int maxWords,
        ProgressReporter progressOrNull
    ) {
        if (maxWords <= 0) {
            return Collections.emptySet();
        }

        boolean hasCompoundDirectives =
            model.compoundFlag != null || model.compoundBeginFlag != null || model.compoundEndFlag != null;
        if (!hasCompoundDirectives) {
            return Collections.emptySet();
        }

        List<WordRecord> begin = new ArrayList<>();
        List<WordRecord> mid = new ArrayList<>();
        List<WordRecord> end = new ArrayList<>();

        for (WordRecord wr : forms) {
            if (wr.word == null || wr.word.isEmpty()) {
                continue;
            }
            if (countWordChars(wr.word, model.wordChars) < model.compoundMin) {
                continue;
            }
            boolean onlyInCompound = wr.hasFlag(model.onlyInCompoundFlag);

            boolean isBegin = wr.hasFlag(model.compoundBeginFlag) || wr.hasFlag(model.compoundFlag);
            boolean isEnd = wr.hasFlag(model.compoundEndFlag) || wr.hasFlag(model.compoundFlag);
            boolean isMid = wr.hasFlag(model.compoundFlag) || wr.hasFlag(model.compoundPermitFlag);

            if (isBegin) {
                begin.add(wr);
            }
            if (isMid) {
                mid.add(wr);
            }
            if (isEnd || onlyInCompound) {
                end.add(wr);
            }
        }

        LinkedHashSet<String> compounds = new LinkedHashSet<>();
        long totalPairs = (long) begin.size() * Math.max(1, end.size());
        long done = 0;

        for (WordRecord b : begin) {
            for (WordRecord e : end) {
                done++;
                if (progressOrNull != null && (done % 20000 == 0 || done == totalPairs)) {
                    progressOrNull.report(done, Math.max(totalPairs, 1), "Compounding (2-part): " + done + "/" + totalPairs);
                }

                String c2 = b.word + e.word;
                if (matchesCompoundRule(model, List.of(b, e)) && isLegalCompound(model, List.of(b.word, e.word), c2)) {
                    compounds.add(c2);
                    if (compounds.size() >= maxWords) {
                        return compounds;
                    }
                }
            }
        }

        if (maxParts >= 3 && !mid.isEmpty()) {
            long totalTriples = (long) begin.size() * mid.size() * Math.max(1, end.size());
            long d3 = 0;
            for (WordRecord b : begin) {
                for (WordRecord m : mid) {
                    for (WordRecord e : end) {
                        d3++;
                        if (progressOrNull != null && (d3 % 50000 == 0 || d3 == totalTriples)) {
                            progressOrNull.report(d3, Math.max(totalTriples, 1), "Compounding (3-part): " + d3 + "/" + totalTriples);
                        }

                        String c3 = b.word + m.word + e.word;
                        if (matchesCompoundRule(model, List.of(b, m, e)) && isLegalCompound(model, List.of(b.word, m.word, e.word), c3)) {
                            compounds.add(c3);
                            if (compounds.size() >= maxWords) {
                                return compounds;
                            }
                        }
                    }
                }
            }
        }

        return compounds;
    }

}
