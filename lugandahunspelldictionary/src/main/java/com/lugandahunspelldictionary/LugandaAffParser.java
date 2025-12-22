package com.lugandahunspelldictionary;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class LugandaAffParser {

    public static class AffixEntry {
        public final char type; // 'P' for prefix, 'S' for suffix
        public final String strip;
        public final String affix;
        public final String condition;

        public AffixEntry(char type, String strip, String affix, String condition) {
            this.type = type;
            this.strip = strip == null ? "" : strip;
            this.affix = affix == null ? "" : affix;
            this.condition = condition == null ? "." : condition;
        }
    }

    /**
     * Parse a Hunspell .aff file and return a map from flag -> list of affix entries.
     * This parser supports the simple PFX style used in the provided `Luganda.aff`.
     */
    public static Map<String, List<AffixEntry>> parseAff(Path affPath) throws IOException {
        List<String> lines = Files.readAllLines(affPath);
        Map<String, List<AffixEntry>> map = new LinkedHashMap<>();

        for (String raw : lines) {
            if (raw == null) continue;
            String line = raw.trim();
            if (line.isEmpty()) continue;
            if (line.startsWith("#")) continue;

            String[] toks = line.split("\\s+");
            if (toks.length < 1) continue;
            if (!toks[0].equalsIgnoreCase("PFX") && !toks[0].equalsIgnoreCase("SFX")) continue;

            // Header example: PFX VB Y 151
            if (toks.length >= 4 && (toks[2].equalsIgnoreCase("Y") || toks[2].equalsIgnoreCase("N"))) {
                String flag = toks[1];
                map.putIfAbsent(flag, new ArrayList<>());
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
                map.putIfAbsent(flag, new ArrayList<>());
                map.get(flag).add(new AffixEntry(type, strip, aff, condition));
            }
        }

        return map;
    }

    /**
     * Generate words for a single root using the parsed affix map.
     */
    public static List<String> generateFromRoot(String root, Map<String, List<AffixEntry>> affMap) {
        List<String> out = new ArrayList<>();
        if (root == null) return out;
        out.add(root); // include bare root

        for (Map.Entry<String, List<AffixEntry>> e : affMap.entrySet()) {
            for (AffixEntry ae : e.getValue()) {
                if (ae.strip.isEmpty()) {
                    out.add(ae.affix + root);
                } else {
                    if (root.startsWith(ae.strip)) {
                        String remainder = root.substring(ae.strip.length());
                        out.add(ae.affix + remainder);
                    }
                }
            }
        }

        return out;
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
