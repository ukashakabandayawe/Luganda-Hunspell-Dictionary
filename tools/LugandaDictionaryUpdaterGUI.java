import javax.swing.*;
import javax.swing.filechooser.FileNameExtensionFilter;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashSet;
import java.util.Set;

public class LugandaDictionaryUpdaterGUI {

    public static void main(String[] args) {

        Set<String> words = new LinkedHashSet<>();

        // 1️⃣ Choose existing clean .txt (optional)
        File existingTxt = chooseFile(
            "Select existing clean .txt dictionary (Cancel if none)",
            JFileChooser.OPEN_DIALOG,
            "Text files",
            "txt"
        );
        if (existingTxt != null) {
            loadSimpleWordList(existingTxt, words);
        }

        // 2️⃣ Choose existing .dic (optional)
        File existingDic = chooseFile(
            "Select existing .dic dictionary (Cancel if none)",
            JFileChooser.OPEN_DIALOG,
            "Dic files",
            "dic"
        );
        if (existingDic != null) {
            loadHunspellDic(existingDic, words);
        }

        // 3️⃣ Choose new raw dictionary (required) i.e a disorganized dictionary
        File rawFile = chooseFile(
            "Select NEW raw Luganda dictionary (required)",
            JFileChooser.OPEN_DIALOG,
            "Supported",
            "txt",
            "dic"
        );
        if (rawFile == null) {
            JOptionPane.showMessageDialog(null, "No raw dictionary selected. Exiting.");
            return;
        }
        loadRawDictionary(rawFile, words);

        // 4️⃣ Choose where to save updated .txt
        File saveTxt = chooseFile(
            "Save updated .txt dictionary",
            JFileChooser.SAVE_DIALOG,
            "Text files",
            "txt"
        );
        if (saveTxt != null) {
            if (!saveTxt.getName().toLowerCase().endsWith(".txt")) {
                saveTxt = new File(saveTxt.getAbsolutePath() + ".txt");
            }
            writeTxt(saveTxt, words);
            JOptionPane.showMessageDialog(null, "Saved .txt to:\n" + saveTxt.getAbsolutePath());
        }

        // 5️⃣ Choose where to save updated .dic
        File saveDic = chooseFile(
            "Save updated .dic dictionary",
            JFileChooser.SAVE_DIALOG,
            "Dic files",
            "dic"
        );
        if (saveDic != null) {
            if (!saveDic.getName().toLowerCase().endsWith(".dic")) {
                saveDic = new File(saveDic.getAbsolutePath() + ".dic");
            }
            writeDic(saveDic, words);
            JOptionPane.showMessageDialog(null, "Saved .dic to:\n" + saveDic.getAbsolutePath());
        }

        JOptionPane.showMessageDialog(null, "✔ Dictionary update completed successfully");
    }

    // ---------------- File chooser ----------------

    private static File chooseFile(String title, int mode, String filterDesc, String... extensions) {
        JFileChooser chooser = new JFileChooser();
        chooser.setDialogTitle(title);
        chooser.setFileSelectionMode(JFileChooser.FILES_ONLY);

        if (extensions != null && extensions.length > 0) {
            FileNameExtensionFilter filter = new FileNameExtensionFilter(filterDesc, extensions);
            chooser.addChoosableFileFilter(filter);
            chooser.setAcceptAllFileFilterUsed(false);
        }

        int result = (mode == JFileChooser.SAVE_DIALOG)
                ? chooser.showSaveDialog(null)
                : chooser.showOpenDialog(null);

        if (result == JFileChooser.APPROVE_OPTION) {
            return chooser.getSelectedFile();
        }
        return null;
    }

    // ---------------- Loaders ----------------

    private static void loadSimpleWordList(File file, Set<String> words) {
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(new FileInputStream(file), StandardCharsets.UTF_8))) {

            String line;
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                if (!line.isEmpty()) {
                    words.add(line);
                }
            }
        } catch (IOException e) {
            showError(e);
        }
    }

    private static void loadHunspellDic(File file, Set<String> words) {
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(new FileInputStream(file), StandardCharsets.UTF_8))) {

            String line;
            boolean firstLine = true;
            while ((line = reader.readLine()) != null) {
                if (firstLine) {
                    firstLine = false; // skip count
                    continue;
                }
                line = line.trim();
                if (!line.isEmpty()) {
                    words.add(line);
                }
            }
        } catch (IOException e) {
            showError(e);
        }
    }

    private static void loadRawDictionary(File file, Set<String> words) {
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(new FileInputStream(file), StandardCharsets.UTF_8))) {

            String line;
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty()) continue;

                String[] tokens = line.split("[\\s|,;]+");
                words.add(tokens[0]); // left-most Luganda word
            }
        } catch (IOException e) {
            showError(e);
        }
    }

    // ---------------- Writers ----------------

    private static void writeTxt(File file, Set<String> words) {
        try (BufferedWriter writer = new BufferedWriter(
                new OutputStreamWriter(new FileOutputStream(file), StandardCharsets.UTF_8))) {

            for (String word : words) {
                writer.write(word);
                writer.newLine();
            }
        } catch (IOException e) {
            showError(e);
        }
    }

    private static void writeDic(File file, Set<String> words) {
        try (BufferedWriter writer = new BufferedWriter(
                new OutputStreamWriter(new FileOutputStream(file), StandardCharsets.UTF_8))) {

            writer.write(String.valueOf(words.size()));
            writer.newLine();

            for (String word : words) {
                writer.write(word);
                writer.newLine();
            }
        } catch (IOException e) {
            showError(e);
        }
    }

    private static void showError(Exception e) {
        JOptionPane.showMessageDialog(null, e.getMessage(), "Error", JOptionPane.ERROR_MESSAGE);
    }
}
