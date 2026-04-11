package com.luganda.offlinereview;

import android.content.Context;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public final class DicExporter {
    private DicExporter() {}

    public static void exportWorkingDic(Context context, OutputStream out, JSONObject decisionsPayload) throws Exception {
        Map<String, Set<String>> approvals = buildApprovalsMap(decisionsPayload);

        try (InputStream is = context.getAssets().open("Luganda.dic");
             BufferedReader r = new BufferedReader(new InputStreamReader(is, StandardCharsets.UTF_8));
             BufferedWriter w = new BufferedWriter(new OutputStreamWriter(out, StandardCharsets.UTF_8))) {

            String line;
            int idx = 0;
            while ((line = r.readLine()) != null) {
                idx++;
                if (idx == 1) {
                    // Count line unchanged.
                    w.write(line);
                    w.write("\n");
                    continue;
                }

                String updated = applyApprovalsToDicLine(line, approvals);
                w.write(updated);
                w.write("\n");
            }
            w.flush();
        }
    }

    private static Map<String, Set<String>> buildApprovalsMap(JSONObject decisionsPayload) {
        Map<String, Set<String>> out = new HashMap<>();
        JSONArray arr = decisionsPayload.optJSONArray("decisions");
        if (arr == null) return out;

        for (int i = 0; i < arr.length(); i++) {
            JSONObject row = arr.optJSONObject(i);
            if (row == null) continue;
            String decision = row.optString("decision", "").trim().toLowerCase();
            if (!(decision.equals("approved") || decision.equals("approve"))) {
                continue;
            }
            String stem = row.optString("stem", "").trim();
            String flag = row.optString("flag", "").trim();
            if (stem.isEmpty() || flag.isEmpty()) continue;
            Set<String> flags = out.get(stem);
            if (flags == null) {
                flags = new HashSet<>();
                out.put(stem, flags);
            }
            flags.add(flag);
        }
        return out;
    }

    private static int indexOfWhitespace(String s) {
        for (int i = 0; i < s.length(); i++) {
            if (Character.isWhitespace(s.charAt(i))) return i;
        }
        return -1;
    }

    private static String applyApprovalsToDicLine(String line, Map<String, Set<String>> approvals) {
        if (line == null) return "";
        if (line.trim().isEmpty()) return line;
        String ltrim = line.trim();
        if (ltrim.startsWith("#")) return line;

        int firstWs = indexOfWhitespace(line);
        String token = firstWs >= 0 ? line.substring(0, firstWs) : line;
        String trailing = firstWs >= 0 ? line.substring(firstWs) : "";

        int slash = token.indexOf('/');
        String stem = slash >= 0 ? token.substring(0, slash) : token;
        String flagsRaw = slash >= 0 ? token.substring(slash + 1) : "";

        stem = stem.trim();
        if (stem.isEmpty()) return line;

        Set<String> toAdd = approvals.get(stem);
        if (toAdd == null || toAdd.isEmpty()) return line;

        String merged = mergeLongFlags(flagsRaw, toAdd);
        String newToken = merged.isEmpty() ? stem : (stem + "/" + merged);
        return newToken + trailing;
    }

    // FLAG long: flags are concatenated 2-char tokens.
    private static String mergeLongFlags(String existingFlagsRaw, Set<String> flagsToAdd) {
        String existing = existingFlagsRaw == null ? "" : existingFlagsRaw;
        Map<String, Boolean> seen = new HashMap<>();
        StringBuilder out = new StringBuilder();

        // Existing tokens preserve order.
        for (String tok : splitLongFlags(existing)) {
            if (tok.isEmpty()) continue;
            if (seen.containsKey(tok)) continue;
            seen.put(tok, true);
            out.append(tok);
        }

        // Add new tokens in stable (sorted) order.
        String[] add = flagsToAdd.toArray(new String[0]);
        java.util.Arrays.sort(add);
        for (String f : add) {
            if (f == null) continue;
            String[] parts = f.split("\\+");
            for (String p : parts) {
                String t = p == null ? "" : p.trim();
                if (t.isEmpty()) continue;
                if (seen.containsKey(t)) continue;
                seen.put(t, true);
                out.append(t);
            }
        }

        return out.toString();
    }

    private static String[] splitLongFlags(String flagsRaw) {
        if (flagsRaw == null) return new String[0];
        String s = flagsRaw.trim().replace("+", "");
        if (s.isEmpty()) return new String[0];
        int n = (s.length() + 1) / 2;
        String[] out = new String[n];
        int idx = 0;
        for (int i = 0; i < s.length(); i += 2) {
            int end = Math.min(i + 2, s.length());
            out[idx++] = s.substring(i, end);
        }
        return out;
    }
}
