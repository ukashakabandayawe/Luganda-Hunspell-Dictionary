package com.lugandahunspelldictionary;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public final class DicParser {
    private static final Pattern GROUP_RE = Pattern.compile("^#\\s*-+\\s*(.*?)\\s*-+\\s*#\\s*$");

    private DicParser() {
    }

    public static CommonFlagAnalyzer.DicFileData load(Path dicPath) throws IOException {
        List<String> lines = Files.readAllLines(dicPath, StandardCharsets.UTF_8);
        List<DicEntry> entries = new ArrayList<>();
        String currentCategory = "";

        for (int i = 0; i < lines.size(); i++) {
            String raw = lines.get(i);
            if (raw == null) {
                continue;
            }
            String line = raw.trim();
            if (line.isEmpty()) {
                continue;
            }
            if (line.startsWith("#")) {
                String marker = parseGroupMarker(line);
                if (marker == null) {
                    continue;
                }
                if ("__END__".equals(marker)) {
                    currentCategory = "";
                } else {
                    currentCategory = marker;
                }
                continue;
            }
            if (i == 0 && line.matches("^\\d+$")) {
                continue;
            }
            DicEntry entry = parseEntryLine(raw);
            if (entry != null) {
                entries.add(new DicEntry(entry.getStem(), entry.getFlagsRaw(), entry.getTrailing(), currentCategory));
            }
        }

        CommonFlagAnalyzer.FlagMode detectedMode = CommonFlagAnalyzer.detectMode(entries);
        return new CommonFlagAnalyzer.DicFileData(dicPath, detectedMode, entries);
    }

    private static String parseGroupMarker(String line) {
        String trimmed = line == null ? "" : line.trim();
        if (trimmed.isEmpty() || !trimmed.startsWith("#")) {
            return null;
        }

        String content = trimmed.substring(1).trim();
        if (content.endsWith("#")) {
            content = content.substring(0, content.length() - 1).trim();
        }
        if (content.isEmpty()) {
            return null;
        }

        boolean onlyDashAndSpace = true;
        for (int i = 0; i < content.length(); i++) {
            char ch = content.charAt(i);
            if (ch != '-' && ch != ' ') {
                onlyDashAndSpace = false;
                break;
            }
        }
        if (onlyDashAndSpace) {
            return "__END__";
        }

        Matcher matcher = GROUP_RE.matcher(trimmed);
        if (!matcher.matches()) {
            return null;
        }

        String title = matcher.group(1) == null ? "" : matcher.group(1).trim();
        if (title.isEmpty()) {
            return null;
        }
        return title;
    }

    public static DicEntry parseEntryLine(String line) {
        if (line == null) {
            return null;
        }
        String trimmed = line.trim();
        if (trimmed.isEmpty() || trimmed.startsWith("#")) {
            return null;
        }

        int firstWhitespace = -1;
        for (int i = 0; i < line.length(); i++) {
            if (Character.isWhitespace(line.charAt(i))) {
                firstWhitespace = i;
                break;
            }
        }

        String token = firstWhitespace >= 0 ? line.substring(0, firstWhitespace) : line;
        String trailing = firstWhitespace >= 0 ? line.substring(firstWhitespace) : "";
        int slash = token.indexOf('/');

        String stem = slash >= 0 ? token.substring(0, slash) : token;
        String flagsRaw = slash >= 0 ? token.substring(slash + 1) : "";
        stem = stem.trim();

        if (stem.isEmpty()) {
            return null;
        }

        return new DicEntry(stem, flagsRaw, trailing);
    }
}