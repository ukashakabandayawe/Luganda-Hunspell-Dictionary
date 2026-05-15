package com.luganda.offlinereview;

import android.content.Context;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TimeZone;

public final class DecisionsStore {
    private static final String DECISIONS_FILE_NAME = "decisions.json";

    private DecisionsStore() {}

    public static File getDecisionsFile(Context context) {
        return new File(context.getFilesDir(), DECISIONS_FILE_NAME);
    }

    public static JSONObject loadDecisionsPayload(Context context) throws Exception {
        File f = getDecisionsFile(context);
        if (!f.exists()) {
            JSONObject payload = new JSONObject();
            payload.put("schema", 1);
            payload.put("generated_at", nowIsoUtc());
            payload.put("decisions", new JSONArray());
            return payload;
        }
        byte[] bytes;
        try (FileInputStream fis = new FileInputStream(f)) {
            bytes = readAllBytes(fis);
        }
        String json = new String(bytes, StandardCharsets.UTF_8);
        return new JSONObject(json);
    }

    public static void saveDecisionsPayload(Context context, JSONObject payload) throws Exception {
        File f = getDecisionsFile(context);
        File tmp = new File(context.getFilesDir(), DECISIONS_FILE_NAME + ".tmp");
        payload.put("schema", 1);
        payload.put("generated_at", nowIsoUtc());
        byte[] bytes = payload.toString().getBytes(StandardCharsets.UTF_8);
        try (FileOutputStream fos = new FileOutputStream(tmp, false)) {
            fos.write(bytes);
        }
        if (!tmp.renameTo(f)) {
            // Best-effort fallback.
            try (FileOutputStream fos = new FileOutputStream(f, false)) {
                fos.write(bytes);
            }
            // noinspection ResultOfMethodCallIgnored
            tmp.delete();
        }
    }

    public static void upsertDecision(Context context, String stem, String flag, String decision, String note) throws Exception {
        JSONObject payload = loadDecisionsPayload(context);
        JSONArray arr = payload.optJSONArray("decisions");
        if (arr == null) arr = new JSONArray();

        // Replace if existing.
        int replaceAt = -1;
        for (int i = 0; i < arr.length(); i++) {
            JSONObject row = arr.optJSONObject(i);
            if (row == null) continue;
            String s = row.optString("stem", "");
            String f = row.optString("flag", "");
            if (stem.equals(s) && flag.equals(f)) {
                replaceAt = i;
                break;
            }
        }

        JSONObject row = new JSONObject();
        row.put("stem", stem);
        row.put("flag", flag);
        row.put("decision", decision);
        row.put("note", note == null ? "" : note);
        row.put("decided_at", nowIsoUtc());

        if (replaceAt >= 0) {
            arr.put(replaceAt, row);
        } else {
            arr.put(row);
        }

        payload.put("decisions", arr);
        saveDecisionsPayload(context, payload);
    }

    public static JSONObject findDecisionRow(Context context, String stem, String flag) throws Exception {
        if (stem == null || flag == null) return null;
        JSONObject payload = loadDecisionsPayload(context);
        JSONArray arr = payload.optJSONArray("decisions");
        if (arr == null) return null;

        for (int i = 0; i < arr.length(); i++) {
            JSONObject row = arr.optJSONObject(i);
            if (row == null) continue;
            String s = row.optString("stem", "");
            String f = row.optString("flag", "");
            if (stem.equals(s) && flag.equals(f)) {
                return row;
            }
        }
        return null;
    }

    public static Map<String, Map<String, String>> loadDecisionStatusMap(Context context) throws Exception {
        JSONObject payload = loadDecisionsPayload(context);
        JSONArray arr = payload.optJSONArray("decisions");
        Map<String, Map<String, String>> out = new HashMap<>();
        if (arr == null) return out;

        for (int i = 0; i < arr.length(); i++) {
            JSONObject row = arr.optJSONObject(i);
            if (row == null) continue;
            String stem = row.optString("stem", "").trim();
            String flag = row.optString("flag", "").trim();
            String decision = row.optString("decision", "").trim();
            if (stem.isEmpty() || flag.isEmpty() || decision.isEmpty()) continue;
            Map<String, String> byFlag = out.get(stem);
            if (byFlag == null) {
                byFlag = new HashMap<>();
                out.put(stem, byFlag);
            }
            byFlag.put(flag, decision);
        }
        return out;
    }

    public static Map<String, Map<String, String>> loadDecisionNoteMap(Context context) throws Exception {
        JSONObject payload = loadDecisionsPayload(context);
        JSONArray arr = payload.optJSONArray("decisions");
        Map<String, Map<String, String>> out = new HashMap<>();
        if (arr == null) return out;

        for (int i = 0; i < arr.length(); i++) {
            JSONObject row = arr.optJSONObject(i);
            if (row == null) continue;
            String stem = row.optString("stem", "").trim();
            String flag = row.optString("flag", "").trim();
            if (stem.isEmpty() || flag.isEmpty()) continue;

            String note = row.optString("note", "");
            Map<String, String> byFlag = out.get(stem);
            if (byFlag == null) {
                byFlag = new HashMap<>();
                out.put(stem, byFlag);
            }
            byFlag.put(flag, note == null ? "" : note);
        }
        return out;
    }

    public static JSONObject buildExportPayload(Context context, JSONObject userJson) throws Exception {
        JSONObject payload = loadDecisionsPayload(context);
        payload.put("schema", 1);
        payload.put("generated_at", nowIsoUtc());

        if (userJson != null) {
            payload.put("user", userJson);
        }
        return payload;
    }

    private static String nowIsoUtc() {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.US);
        sdf.setTimeZone(TimeZone.getTimeZone("UTC"));
        return sdf.format(new Date());
    }

    private static byte[] readAllBytes(FileInputStream is) throws Exception {
        byte[] buf = new byte[8192];
        int n;
        List<byte[]> chunks = new ArrayList<>();
        int total = 0;
        while ((n = is.read(buf)) >= 0) {
            if (n == 0) continue;
            byte[] chunk = new byte[n];
            System.arraycopy(buf, 0, chunk, 0, n);
            chunks.add(chunk);
            total += n;
        }
        byte[] out = new byte[total];
        int pos = 0;
        for (byte[] c : chunks) {
            System.arraycopy(c, 0, out, pos, c.length);
            pos += c.length;
        }
        return out;
    }
}
