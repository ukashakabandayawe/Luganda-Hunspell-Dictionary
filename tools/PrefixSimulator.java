import java.io.*;
import java.nio.file.*;
import java.util.*;

public class PrefixSimulator {
    // Simple parser for PFX lines in a Hunspell .aff (handles the style in your Luganda.aff)
    public static Map<String, List<AffixEntry>> parseAffFile(Path affPath) throws IOException {
        Map<String, List<AffixEntry>> map = new LinkedHashMap<>();
        List<String> lines = Files.readAllLines(affPath);
        for (String raw : lines) {
            String line = raw.trim();
            if (line.isEmpty() || line.startsWith("#")) continue;
            String[] toks = line.split("\\s+");
            if (toks.length < 4) continue;
            if (!toks[0].equalsIgnoreCase("PFX")) continue;
            // header like: PFX VB Y 151  -> toks[2] == Y (crossable) and toks[3] is number
            if (toks[2].equalsIgnoreCase("Y") || toks[2].equalsIgnoreCase("N")) {
                map.putIfAbsent(toks[1], new ArrayList<>());
                continue;
            }
            // affix line: PFX <flag> <strip> <affix> [condition]
            String flag = toks[1];
            String strip = toks[2];
            String affix = toks[3];
            if ("0".equals(affix)) affix = ""; // Hunspell uses '0' to mean empty affix
            map.putIfAbsent(flag, new ArrayList<>());
            String condition = (toks.length >= 5) ? toks[4] : ".";
            map.get(flag).add(new AffixEntry(strip, affix, condition));
        }
        return map;
    }

    static class AffixEntry {
        final String strip; // '0' means no strip in file; we store actual '0' as string here
        final String affix;
        final String condition;
        AffixEntry(String strip, String affix, String condition){
            this.strip = strip;
            this.affix = affix;
            this.condition = condition;
        }
    }

    // Apply a single affix entry to a root. If strip != "0", only apply when root startsWith(strip).
    public static Optional<String> apply(AffixEntry e, String root) {
        String s = e.strip;
        String a = e.affix;
        if ("0".equals(s) || s.isEmpty()) {
            return Optional.of(a + root);
        } else {
            if (root.startsWith(s)) {
                return Optional.of(a + root.substring(s.length()));
            } else {
                return Optional.empty();
            }
        }
    }

    public static void main(String[] args) throws Exception {
        Path aff = Paths.get("e:\\Luganda Hunspell Dictionary\\Luganda.aff");
        String root = null;
        String flagFilter = null; // null => all flags
        if (args.length >= 1) root = args[0];
        if (args.length >= 2) flagFilter = args[1];
        if (root == null) {
            System.out.print("Root word: ");
            BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
            root = br.readLine().trim();
        }
        Map<String, List<AffixEntry>> map = parseAffFile(aff);
        Set<String> results = new TreeSet<>();
        for (Map.Entry<String, List<AffixEntry>> ent : map.entrySet()) {
            String flag = ent.getKey();
            if (flagFilter != null && !flag.equalsIgnoreCase(flagFilter)) continue;
            for (AffixEntry e : ent.getValue()) {
                Optional<String> out = apply(e, root);
                out.ifPresent(w -> results.add(flag + ":" + w));
            }
        }
        // Also include the bare root as-is
        results.add("ROOT:" + root);
        // print
        results.forEach(System.out::println);
        // summary
        System.out.println("\nTotal: " + results.size());
    }
}