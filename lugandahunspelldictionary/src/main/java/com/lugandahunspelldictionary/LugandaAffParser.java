package com.lugandahunspelldictionary;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class LugandaAffParser {

    public static class AffixEntry {
        public final char type; // 'P' for prefix, 'S' for suffix
        public final String strip;
        public final String affix;
        public final String condition;
        public final String flag; // flag identifier (needed for combos)
        public final boolean combinable; // copied from header Y/N

        public AffixEntry(char type, String strip, String affix, String condition, String flag, boolean combinable) {
            this.type = type;
            this.strip = strip == null ? "" : strip;
            this.affix = affix == null ? "" : affix;
            this.condition = condition == null ? "." : condition;
            this.flag = flag == null ? "" : flag;
            this.combinable = combinable;
        }
    }

    public static class AffixGroup {
        public final char type; // 'P' or 'S'
        public final boolean combinable; // header Y/N
        public final List<AffixEntry> entries = new ArrayList<>();

        public AffixGroup(char type, boolean combinable) {
            this.type = type;
            this.combinable = combinable;
        }
    }

    /**
     * Parse a Hunspell .aff file and return a map from flag -> list of affix entries.
     * This parser supports the simple PFX style used in the provided `Luganda.aff`.
     */
    public static Map<String, List<AffixEntry>> parseAff(Path affPath) throws IOException {
        Map<String, AffixGroup> meta = parseAffWithMeta(affPath);
        Map<String, List<AffixEntry>> legacy = new LinkedHashMap<>();
        for (Map.Entry<String, AffixGroup> e : meta.entrySet()) {
            legacy.put(e.getKey(), e.getValue().entries);
        }
        return legacy;
    }

    /**
     * Parse a Hunspell .aff file and return a map from flag -> AffixGroup (with combinable metadata).
     */
    public static Map<String, AffixGroup> parseAffWithMeta(Path affPath) throws IOException {
        List<String> lines = Files.readAllLines(affPath);
        Map<String, AffixGroup> map = new LinkedHashMap<>();

        for (String raw : lines) {
            if (raw == null) continue;
            String line = raw.trim();
            if (line.isEmpty()) continue;
            if (line.startsWith("#")) continue;

            String[] toks = line.split("\\s+");
            if (toks.length < 1) continue;
            if (!toks[0].equalsIgnoreCase("PFX") && !toks[0].equalsIgnoreCase("SFX")) continue;

            boolean isHeader = toks.length >= 4 && (toks[2].equalsIgnoreCase("Y") || toks[2].equalsIgnoreCase("N"));
            if (isHeader) {
                String flag = toks[1];
                char type = toks[0].equalsIgnoreCase("PFX") ? 'P' : 'S';
                boolean combinable = toks[2].equalsIgnoreCase("Y");
                map.put(flag, new AffixGroup(type, combinable));
                continue;
            }

            // Affix line example: PFX VB 0 tu .
            if (toks.length >= 4) {
                char type = toks[0].equalsIgnoreCase("PFX") ? 'P' : 'S';
                String flag = toks[1];
                String strip = toks[2];
                String aff = toks[3];
                String condition = toks.length >= 5 ? toks[4] : ".";
                if ("0".equals(strip)) strip = "";
                if ("0".equals(aff)) aff = "";

                // If header was missing, assume non-combinable by default for safety.
                AffixGroup group = map.get(flag);
                if (group == null) {
                    group = new AffixGroup(type, false);
                    map.put(flag, group);
                }
                group.entries.add(new AffixEntry(type, strip, aff, condition, flag, group.combinable));
            }
        }

        return map;
    }

    /**
     * Generate words for a single root using the parsed affix map.
     */
    public static List<String> generateFromRoot(String root, Map<String, List<AffixEntry>> affMap) {
        // Legacy helper retained for compatibility: assumes all affixes are non-combinable and flat.
        Map<String, AffixGroup> meta = new LinkedHashMap<>();
        for (Map.Entry<String, List<AffixEntry>> e : affMap.entrySet()) {
            AffixGroup g = new AffixGroup(e.getValue().isEmpty() ? 'P' : e.getValue().get(0).type, false);
            g.entries.addAll(e.getValue());
            meta.put(e.getKey(), g);
        }
        return generateFromRootWithMeta(root, meta);
    }

    /**
     * Generate words for a single root using combinable metadata. Allows prefix+suffix chaining only when both
     * headers specify Y and the types differ.
     */
    public static List<String> generateFromRootWithMeta(String root, Map<String, AffixGroup> affMap) {
        if (root == null || root.isEmpty()) {
            return new ArrayList<>();
        }
        if (affMap == null || affMap.isEmpty()) {
            List<String> out = new ArrayList<>();
            out.add(root);
            return out;
        }

        // Preserve encounter order but avoid duplicates.
        Set<String> out = new LinkedHashSet<>();
        out.add(root); // include bare root

        List<AffixEntry> combinablePrefixes = new ArrayList<>();
        List<AffixEntry> combinableSuffixes = new ArrayList<>();

        for (AffixGroup group : affMap.values()) {
            if (group == null || group.entries == null) continue;
            for (AffixEntry ae : group.entries) {
                String generated = apply(ae, root);
                if (generated != null && !generated.isEmpty()) {
                    out.add(generated);
                }

                if (group.combinable && group.type == 'P') {
                    combinablePrefixes.add(ae);
                } else if (group.combinable && group.type == 'S') {
                    combinableSuffixes.add(ae);
                }
            }
        }

        // Combine prefix then suffix when both headers allow it (Y) and types differ.
        for (AffixEntry p : combinablePrefixes) {
            String prefixed = apply(p, root);
            if (prefixed == null || prefixed.isEmpty()) continue;
            for (AffixEntry s : combinableSuffixes) {
                String combined = apply(s, prefixed);
                if (combined != null && !combined.isEmpty()) {
                    out.add(combined);
                }
            }
        }

        return new ArrayList<>(out);
    }

    public static String apply(AffixEntry entry, String root) {
        if (entry == null || root == null || root.isEmpty()) {
            return null;
        }

        // Check if the condition is met
        if (entry.condition != null && !entry.condition.isEmpty() && !entry.condition.equals(".")) {
            if (entry.type == 'S') {
                // For suffix, check if root ends with condition pattern
                if (!root.matches(".*" + entry.condition + "$")) {
                    return null;
                }
            } else {
                // For prefix, check if root starts with condition pattern
                if (!root.matches("^" + entry.condition + ".*")) {
                    return null;
                }
            }
        }

        String result = root;

        // Remove characters if strip is specified
        if (entry.strip != null && !entry.strip.equals("0") && !entry.strip.isEmpty()) {
            if (entry.type == 'S') {
                // Suffix: strip from end
                if (result.endsWith(entry.strip)) {
                    result = result.substring(0, result.length() - entry.strip.length());
                } else {
                    return null; // Can't apply this affix
                }
            } else {
                // Prefix: strip from beginning
                if (result.startsWith(entry.strip)) {
                    result = result.substring(entry.strip.length());
                } else {
                    return null; // Can't apply this affix
                }
            }
        }

        // Add the affix
        if (entry.affix != null && !entry.affix.equals("0") && !entry.affix.isEmpty()) {
            if (entry.type == 'S') {
                result = result + entry.affix; // Suffix
            } else if (entry.type == 'P') {
                result = entry.affix + result; // Prefix
            }
        }

        return result;
    }
}
