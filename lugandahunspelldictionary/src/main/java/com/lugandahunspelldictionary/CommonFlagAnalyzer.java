package com.lugandahunspelldictionary;

import java.nio.file.Path;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

public final class CommonFlagAnalyzer {
    public enum FlagMode {
        AUTO,
        DEFAULT,
        LONG,
        NUM
    }

    public static final class DicFileData {
        private final Path path;
        private final FlagMode detectedMode;
        private final List<DicEntry> entries;

        public DicFileData(Path path, FlagMode detectedMode, List<DicEntry> entries) {
            this.path = path;
            this.detectedMode = detectedMode == null ? FlagMode.DEFAULT : detectedMode;
            this.entries = entries == null ? List.of() : List.copyOf(entries);
        }

        public Path getPath() {
            return path;
        }

        public FlagMode getDetectedMode() {
            return detectedMode;
        }

        public List<DicEntry> getEntries() {
            return entries;
        }
    }

    public static final class AnalysisResult {
        private final FlagMode mode;
        private final List<DicEntry> selectedEntries;
        private final List<StemAnalysis> stemAnalyses;
        private final LinkedHashSet<String> commonFlags;
        private final LinkedHashSet<String> uniqueFlags;
        private final String category;

        public AnalysisResult(FlagMode mode, List<DicEntry> selectedEntries, List<StemAnalysis> stemAnalyses, LinkedHashSet<String> commonFlags, LinkedHashSet<String> uniqueFlags, String category) {
            this.mode = mode == null ? FlagMode.DEFAULT : mode;
            this.selectedEntries = selectedEntries == null ? List.of() : List.copyOf(selectedEntries);
            this.stemAnalyses = stemAnalyses == null ? List.of() : List.copyOf(stemAnalyses);
            this.commonFlags = commonFlags == null ? new LinkedHashSet<>() : new LinkedHashSet<>(commonFlags);
            this.uniqueFlags = uniqueFlags == null ? new LinkedHashSet<>() : new LinkedHashSet<>(uniqueFlags);
            this.category = category == null ? "" : category.trim();
        }

        public FlagMode getMode() {
            return mode;
        }

        public List<DicEntry> getSelectedEntries() {
            return selectedEntries;
        }

        public List<StemAnalysis> getStemAnalyses() {
            return stemAnalyses;
        }

        public LinkedHashSet<String> getCommonFlags() {
            return new LinkedHashSet<>(commonFlags);
        }

        public LinkedHashSet<String> getUniqueFlags() {
            return new LinkedHashSet<>(uniqueFlags);
        }

        public boolean isEmpty() {
            return commonFlags.isEmpty();
        }

        public String getCommonFlagsText() {
            return formatFlags(commonFlags, mode);
        }

        public String getUniqueFlagsText() {
            return formatFlags(uniqueFlags, mode);
        }

        public String getCategory() {
            return category;
        }
    }

    public static final class StemAnalysis {
        private final DicEntry entry;
        private final LinkedHashSet<String> normalizedFlags;
        private final LinkedHashSet<String> uniqueFlags;

        public StemAnalysis(DicEntry entry, LinkedHashSet<String> normalizedFlags, LinkedHashSet<String> uniqueFlags) {
            this.entry = entry;
            this.normalizedFlags = normalizedFlags == null ? new LinkedHashSet<>() : new LinkedHashSet<>(normalizedFlags);
            this.uniqueFlags = uniqueFlags == null ? new LinkedHashSet<>() : new LinkedHashSet<>(uniqueFlags);
        }

        public DicEntry getEntry() {
            return entry;
        }

        public LinkedHashSet<String> getNormalizedFlags() {
            return new LinkedHashSet<>(normalizedFlags);
        }

        public String getNormalizedFlagsText() {
            return formatFlags(normalizedFlags, FlagMode.DEFAULT);
        }

        public LinkedHashSet<String> getUniqueFlags() {
            return new LinkedHashSet<>(uniqueFlags);
        }

        public String getUniqueFlagsText() {
            return formatFlags(uniqueFlags, FlagMode.DEFAULT);
        }
    }

    private CommonFlagAnalyzer() {
    }

    public static AnalysisResult analyze(List<DicEntry> selectedEntries, FlagMode mode) {
        List<DicEntry> safeEntries = selectedEntries == null ? List.of() : selectedEntries;
        FlagMode effectiveMode = mode == null ? FlagMode.DEFAULT : mode;

        if (effectiveMode == FlagMode.AUTO) {
            effectiveMode = detectMode(safeEntries);
        }

        LinkedHashSet<String> intersection = new LinkedHashSet<>();
        String category = commonCategory(safeEntries);
        boolean first = true;
        for (DicEntry entry : safeEntries) {
            if (entry == null) {
                continue;
            }
            Set<String> flags = normalizeFlags(entry.getFlagsRaw(), effectiveMode);
            if (first) {
                intersection.addAll(flags);
                first = false;
            } else {
                intersection.retainAll(flags);
            }
        }

        if (safeEntries.isEmpty()) {
            intersection.clear();
        }

        List<StemAnalysis> stemAnalyses = new java.util.ArrayList<>();
        for (DicEntry entry : safeEntries) {
            if (entry == null) {
                continue;
            }
            LinkedHashSet<String> normalizedFlags = normalizeFlags(entry.getFlagsRaw(), effectiveMode);
            LinkedHashSet<String> uniqueFlags = new LinkedHashSet<>(normalizedFlags);
            uniqueFlags.removeAll(intersection);
            stemAnalyses.add(new StemAnalysis(entry, normalizedFlags, uniqueFlags));
        }

        LinkedHashSet<String> aggregateUniqueFlags = new LinkedHashSet<>();
        for (StemAnalysis stemAnalysis : stemAnalyses) {
            aggregateUniqueFlags.addAll(stemAnalysis.getUniqueFlags());
        }

        return new AnalysisResult(effectiveMode, safeEntries, stemAnalyses, intersection, aggregateUniqueFlags, category);
    }

    public static String commonCategory(List<DicEntry> entries) {
        String category = "";
        if (entries == null || entries.isEmpty()) {
            return category;
        }
        for (DicEntry entry : entries) {
            if (entry == null) {
                continue;
            }
            String current = entry.getCategory() == null ? "" : entry.getCategory().trim();
            if (current.isEmpty()) {
                return "";
            }
            if (category.isEmpty()) {
                category = current;
            } else if (!category.equals(current)) {
                return "";
            }
        }
        return category;
    }

    public static FlagMode detectMode(List<DicEntry> entries) {
        boolean hasComma = false;
        boolean hasPlus = false;
        boolean hasLongCandidate = false;

        if (entries != null) {
            for (DicEntry entry : entries) {
                if (entry == null) {
                    continue;
                }
                String raw = entry.getFlagsRaw();
                if (raw == null || raw.isEmpty()) {
                    continue;
                }
                if (raw.contains(",")) {
                    hasComma = true;
                }
                if (raw.contains("+")) {
                    hasPlus = true;
                }
                String compact = raw.replace("+", "").trim();
                if (compact.length() > 1 && compact.length() % 2 == 0) {
                    hasLongCandidate = true;
                }
            }
        }

        if (hasComma) {
            return FlagMode.NUM;
        }
        if (hasLongCandidate && (hasPlus || !allSingleCharFlags(entries))) {
            return FlagMode.LONG;
        }
        return FlagMode.DEFAULT;
    }

    private static boolean allSingleCharFlags(List<DicEntry> entries) {
        if (entries == null || entries.isEmpty()) {
            return true;
        }
        for (DicEntry entry : entries) {
            if (entry == null) {
                continue;
            }
            String raw = entry.getFlagsRaw();
            if (raw == null || raw.isEmpty()) {
                continue;
            }
            String compact = raw.replace("+", "").replace(",", "").trim();
            if (compact.length() > 1) {
                return false;
            }
        }
        return true;
    }

    public static LinkedHashSet<String> normalizeFlags(String flagsRaw, FlagMode mode) {
        FlagMode effectiveMode = mode == null ? FlagMode.DEFAULT : mode;
        String raw = flagsRaw == null ? "" : flagsRaw.trim();
        LinkedHashSet<String> out = new LinkedHashSet<>();
        if (raw.isEmpty()) {
            return out;
        }

        switch (effectiveMode) {
            case NUM:
                for (String part : raw.replace("+", "").split(",")) {
                    String token = part.trim();
                    if (!token.isEmpty()) {
                        out.add(token);
                    }
                }
                break;
            case LONG:
                String compact = raw.replace("+", "").trim();
                for (int i = 0; i < compact.length(); i += 2) {
                    int end = Math.min(i + 2, compact.length());
                    String token = compact.substring(i, end).trim();
                    if (!token.isEmpty()) {
                        out.add(token);
                    }
                }
                break;
            case AUTO:
            case DEFAULT:
            default:
                for (int i = 0; i < raw.length(); i++) {
                    char ch = raw.charAt(i);
                    if (ch == '+' || Character.isWhitespace(ch)) {
                        continue;
                    }
                    out.add(String.valueOf(ch));
                }
                break;
        }

        return out;
    }

    public static String formatFlags(Set<String> flags, FlagMode mode) {
        if (flags == null || flags.isEmpty()) {
            return "";
        }
        return String.join(", ", flags);
    }
}