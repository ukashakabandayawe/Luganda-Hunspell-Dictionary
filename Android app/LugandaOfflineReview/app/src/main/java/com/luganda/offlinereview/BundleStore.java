package com.luganda.offlinereview;

import android.content.Context;
import android.net.Uri;

import androidx.annotation.Nullable;

import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import java.util.zip.GZIPOutputStream;
import java.util.zip.GZIPInputStream;

public final class BundleStore {
    private static final String BUNDLE_FILE_NAME = "review_bundle.json.gz";
    private static final String BASE_DIC_FILE_NAME = "Luganda.dic";

    private BundleStore() {}

    public static File getBundleFile(Context context) {
        return new File(context.getFilesDir(), BUNDLE_FILE_NAME);
    }

    public static File getBaseDicFile(Context context) {
        return new File(context.getFilesDir(), BASE_DIC_FILE_NAME);
    }

    public static boolean hasBundle(Context context) {
        return getBundleFile(context).exists();
    }

    public static void importBundle(Context context, Uri uri) throws Exception {
        if (uri == null) {
            throw new IllegalArgumentException("uri is required");
        }

        // Capture previous bundle user so we can preserve decisions when re-importing
        // an updated bundle for the same reviewer.
        BundleHeader prevHeader = null;
        try {
            if (getBundleFile(context).exists()) {
                prevHeader = readBundleHeader(context);
            }
        } catch (Throwable ignored) {
            prevHeader = null;
        }

        byte[] data;
        try (InputStream is = context.getContentResolver().openInputStream(uri)) {
            if (is == null) {
                throw new IllegalStateException("Could not open selected file");
            }
            data = readAllBytes(is);
        }

        if (data.length == 0) {
            throw new IllegalStateException("Selected file is empty");
        }

        // ZIP? (magic 'PK')
        boolean isZip = data.length >= 2 && (data[0] == (byte) 'P') && (data[1] == (byte) 'K');
        if (isZip) {
            importZipBundle(context, data);

            // Validate without materializing the full JSON into memory.
            BundleHeader header = readBundleHeader(context);
            if (header.schema != 1) {
                throw new IllegalStateException("Unsupported bundle schema: " + header.schema);
            }
            if (!header.hasStems) {
                throw new IllegalStateException("Invalid bundle: missing 'stems'");
            }

            handleDecisionsOnImport(context, prevHeader, header);
            return;
        }

        // If file is already gzip (magic 1F 8B), store as-is.
        boolean isGz = data.length >= 2 && (data[0] == (byte) 0x1f) && (data[1] == (byte) 0x8b);
        File outFile = getBundleFile(context);

        if (isGz) {
            try (FileOutputStream fos = new FileOutputStream(outFile, false)) {
                fos.write(data);
            }
        } else {
            // Assume JSON, gzip it to keep storage small.
            try (FileOutputStream fos = new FileOutputStream(outFile, false);
                 GZIPOutputStream gz = new GZIPOutputStream(fos)) {
                gz.write(data);
            }
        }

        // Validate without materializing the full JSON into memory.
        BundleHeader header = readBundleHeader(context);
        if (header.schema != 1) {
            throw new IllegalStateException("Unsupported bundle schema: " + header.schema);
        }
        if (!header.hasStems) {
            throw new IllegalStateException("Invalid bundle: missing 'stems'");
        }

        handleDecisionsOnImport(context, prevHeader, header);
    }

    private static void handleDecisionsOnImport(Context context, BundleHeader prevHeader, BundleHeader newHeader) {
        boolean keep = false;
        if (prevHeader != null && newHeader != null) {
            if (prevHeader.userId > 0 && newHeader.userId > 0 && prevHeader.userId == newHeader.userId) {
                keep = true;
            } else {
                String pu = prevHeader.username == null ? "" : prevHeader.username.trim();
                String nu = newHeader.username == null ? "" : newHeader.username.trim();
                if (!pu.isEmpty() && pu.equalsIgnoreCase(nu)) {
                    keep = true;
                }
            }
        }

        if (keep) {
            return;
        }

        // New assignment or unknown -> clear previous decisions.
        File decisions = DecisionsStore.getDecisionsFile(context);
        if (decisions.exists()) {
            // Best-effort backup.
            try {
                File bak = new File(context.getFilesDir(), "decisions.backup.json");
                try (FileInputStream in = new FileInputStream(decisions);
                     FileOutputStream out = new FileOutputStream(bak, false)) {
                    byte[] buf = new byte[8192];
                    int n;
                    while ((n = in.read(buf)) >= 0) {
                        if (n == 0) continue;
                        out.write(buf, 0, n);
                    }
                }
            } catch (Throwable ignored) {}

            // noinspection ResultOfMethodCallIgnored
            decisions.delete();
        }
    }

    private static void importZipBundle(Context context, byte[] zipBytes) throws Exception {
        File outBundle = getBundleFile(context);
        File outDic = getBaseDicFile(context);

        boolean wroteBundle = false;
        boolean wroteDic = false;

        try (java.io.ByteArrayInputStream bais = new java.io.ByteArrayInputStream(zipBytes);
             ZipInputStream zis = new ZipInputStream(bais)) {
            ZipEntry e;
            while ((e = zis.getNextEntry()) != null) {
                String name = e.getName() == null ? "" : e.getName();
                String lname = name.toLowerCase();
                if (e.isDirectory()) {
                    zis.closeEntry();
                    continue;
                }

                if (lname.endsWith("review_bundle.json.gz") || lname.endsWith("bundle.json.gz") || lname.endsWith(".json.gz")) {
                    try (FileOutputStream fos = new FileOutputStream(outBundle, false)) {
                        copyAll(zis, fos);
                    }
                    wroteBundle = true;
                } else if (lname.endsWith("luganda.dic") || lname.endsWith("luganda_dic.txt")) {
                    try (FileOutputStream fos = new FileOutputStream(outDic, false)) {
                        copyAll(zis, fos);
                    }
                    wroteDic = true;
                }

                zis.closeEntry();
            }
        }

        if (!wroteBundle) {
            throw new IllegalStateException("Zip bundle missing review_bundle.json.gz");
        }
        // dic is optional for backwards compatibility; if missing, we keep any previously stored base dic.
        if (!wroteDic) {
            // no-op
        }
    }

    private static void copyAll(InputStream in, FileOutputStream out) throws Exception {
        byte[] buf = new byte[8192];
        int n;
        while ((n = in.read(buf)) >= 0) {
            if (n == 0) continue;
            out.write(buf, 0, n);
        }
        out.flush();
    }

    /**
     * Legacy method: loads full bundle into memory. Avoid for large bundles.
     */
    @Deprecated
    public static JSONObject loadBundleJson(Context context) throws Exception {
        File f = getBundleFile(context);
        if (!f.exists()) throw new IllegalStateException("Bundle not found");
        try (FileInputStream fis = new FileInputStream(f);
             GZIPInputStream gis = new GZIPInputStream(fis)) {
            byte[] bytes = readAllBytes(gis);
            String json = new String(bytes, StandardCharsets.UTF_8);
            return new JSONObject(json);
        }
    }

    public static final class BundleHeader {
        public final int schema;
        public final boolean hasStems;
        public final int userId;
        public final String username;

        BundleHeader(int schema, boolean hasStems, int userId, String username) {
            this.schema = schema;
            this.hasStems = hasStems;
            this.userId = userId;
            this.username = username == null ? "" : username;
        }

        public JSONObject toUserJson() {
            JSONObject u = new JSONObject();
            try {
                if (userId > 0) u.put("id", userId);
                if (!username.isEmpty()) u.put("username", username);
            } catch (Exception ignored) {}
            return u;
        }
    }

    public static BundleHeader readBundleHeader(Context context) throws Exception {
        File f = getBundleFile(context);
        if (!f.exists()) throw new IllegalStateException("Bundle not found");

        int schema = 0;
        boolean hasStems = false;
        int userId = 0;
        String username = "";

        try (FileInputStream fis = new FileInputStream(f);
             GZIPInputStream gis = new GZIPInputStream(fis);
             InputStreamReader isr = new InputStreamReader(gis, StandardCharsets.UTF_8);
             JsonReader r = new JsonReader(isr)) {

            r.setLenient(true);
            r.beginObject();
            while (r.hasNext()) {
                String name = r.nextName();
                if ("schema".equals(name)) {
                    schema = safeNextInt(r);
                } else if ("user".equals(name)) {
                    if (r.peek() == JsonToken.NULL) {
                        r.nextNull();
                    } else {
                        r.beginObject();
                        while (r.hasNext()) {
                            String un = r.nextName();
                            if ("id".equals(un)) userId = safeNextInt(r);
                            else if ("username".equals(un)) username = safeNextString(r);
                            else r.skipValue();
                        }
                        r.endObject();
                    }
                } else if ("stems".equals(name)) {
                    hasStems = true;
                    // We don't need to read them now.
                    r.skipValue();
                } else {
                    r.skipValue();
                }

                if (schema != 0 && hasStems) {
                    // Good enough for validation.
                    break;
                }
            }
        }

        return new BundleHeader(schema, hasStems, userId, username);
    }

    public static final class ProgressSummary {
        public final int stems;
        public final int tasks;
        public final int pending;
        public final int decided;
        public final int approved;
        public final int rejected;

        ProgressSummary(int stems, int tasks, int pending, int decided, int approved, int rejected) {
            this.stems = stems;
            this.tasks = tasks;
            this.pending = pending;
            this.decided = decided;
            this.approved = approved;
            this.rejected = rejected;
        }
    }

    public static final class QueueStemLite {
        public final int index;
        public final String stem;
        public final int sourceLineNo;

        public final String groupKey;
        public final String groupTitle;
        public final int groupLine;

        public final int pending;
        public final int done;

        QueueStemLite(
                int index,
                String stem,
                int sourceLineNo,
                String groupKey,
                String groupTitle,
                int groupLine,
                int pending,
                int done
        ) {
            this.index = index;
            this.stem = stem == null ? "" : stem;
            this.sourceLineNo = sourceLineNo;
            this.groupKey = groupKey == null ? "" : groupKey;
            this.groupTitle = groupTitle == null ? "" : groupTitle;
            this.groupLine = groupLine;
            this.pending = pending;
            this.done = done;
        }
    }

    public static ProgressSummary computeProgress(
            Context context,
            java.util.Map<String, java.util.Map<String, String>> decisionMap
    ) throws Exception {
        File f = getBundleFile(context);
        if (!f.exists()) throw new IllegalStateException("Bundle not found");

        int stemsCount = 0;
        int tasksTotal = 0;
        int pending = 0;
        int decided = 0;
        int approved = 0;
        int rejected = 0;

        try (FileInputStream fis = new FileInputStream(f);
             GZIPInputStream gis = new GZIPInputStream(fis);
             InputStreamReader isr = new InputStreamReader(gis, StandardCharsets.UTF_8);
             JsonReader r = new JsonReader(isr)) {

            r.setLenient(true);
            r.beginObject();
            while (r.hasNext()) {
                String name = r.nextName();
                if (!"stems".equals(name)) {
                    r.skipValue();
                    continue;
                }
                r.beginArray();
                while (r.hasNext()) {
                    stemsCount++;
                    ProgressCounts counts = readStemCounts(r, decisionMap);
                    tasksTotal += counts.tasks;
                    pending += counts.pending;
                    decided += counts.decided;
                    approved += counts.approved;
                    rejected += counts.rejected;
                }
                r.endArray();
                break;
            }
        }

        return new ProgressSummary(stemsCount, tasksTotal, pending, decided, approved, rejected);
    }

    public static java.util.List<QueueStemLite> loadQueueStems(
            Context context,
            java.util.Map<String, java.util.Map<String, String>> decisionMap
    ) throws Exception {
        File f = getBundleFile(context);
        if (!f.exists()) throw new IllegalStateException("Bundle not found");

        java.util.ArrayList<QueueStemLite> out = new java.util.ArrayList<>();

        try (FileInputStream fis = new FileInputStream(f);
             GZIPInputStream gis = new GZIPInputStream(fis);
             InputStreamReader isr = new InputStreamReader(gis, StandardCharsets.UTF_8);
             JsonReader r = new JsonReader(isr)) {

            r.setLenient(true);
            r.beginObject();
            while (r.hasNext()) {
                String name = r.nextName();
                if (!"stems".equals(name)) {
                    r.skipValue();
                    continue;
                }
                r.beginArray();
                int idx = 0;
                while (r.hasNext()) {
                    out.add(readStemLite(r, idx, decisionMap));
                    idx++;
                }
                r.endArray();
                break;
            }
        }

        return out;
    }

    private static final class ProgressCounts {
        final int tasks;
        final int pending;
        final int decided;
        final int approved;
        final int rejected;

        ProgressCounts(int tasks, int pending, int decided, int approved, int rejected) {
            this.tasks = tasks;
            this.pending = pending;
            this.decided = decided;
            this.approved = approved;
            this.rejected = rejected;
        }
    }

    private static ProgressCounts readStemCounts(
            JsonReader r,
            java.util.Map<String, java.util.Map<String, String>> decisionMap
    ) throws Exception {
        String stemText = "";
        int tasksTotal = 0;
        int pending = 0;
        int decided = 0;
        int approved = 0;
        int rejected = 0;

        r.beginObject();
        while (r.hasNext()) {
            String n = r.nextName();
            if ("stem".equals(n)) {
                stemText = safeNextString(r);
            } else if ("tasks".equals(n)) {
                if (r.peek() == JsonToken.NULL) {
                    r.nextNull();
                } else {
                    r.beginArray();
                    while (r.hasNext()) {
                        tasksTotal++;
                        TaskStatusRow row = readTaskStatusRow(r);
                        String eff = effectiveStatusFromMap(decisionMap, stemText, row.flag, row.baseStatus);
                        if ("pending".equals(eff)) {
                            pending++;
                        } else {
                            decided++;
                            if ("approved".equals(eff)) approved++;
                            else if ("rejected".equals(eff)) rejected++;
                        }
                    }
                    r.endArray();
                }
            } else {
                r.skipValue();
            }
        }
        r.endObject();

        return new ProgressCounts(tasksTotal, pending, decided, approved, rejected);
    }

    private static QueueStemLite readStemLite(
            JsonReader r,
            int index,
            java.util.Map<String, java.util.Map<String, String>> decisionMap
    ) throws Exception {
        String stemText = "";
        int stemLine = 1_000_000_000;

        String groupKey = "ungrouped";
        String groupTitle = "Ungrouped";
        int groupLine = 1_000_000_000;

        int pending = 0;
        int done = 0;

        r.beginObject();
        while (r.hasNext()) {
            String n = r.nextName();
            if ("stem".equals(n)) {
                stemText = safeNextString(r);
            } else if ("source_line_no".equals(n)) {
                stemLine = safeNextInt(r);
            } else if ("group".equals(n)) {
                if (r.peek() == JsonToken.NULL) {
                    r.nextNull();
                } else {
                    int gid = 0;
                    String gt = "";
                    int gl = 1_000_000_000;
                    r.beginObject();
                    while (r.hasNext()) {
                        String gn = r.nextName();
                        if ("id".equals(gn)) gid = safeNextInt(r);
                        else if ("title".equals(gn)) gt = safeNextString(r);
                        else if ("source_line_no".equals(gn)) gl = safeNextInt(r);
                        else r.skipValue();
                    }
                    r.endObject();

                    if (gt == null || gt.trim().isEmpty()) gt = stemText;
                    groupTitle = gt;
                    groupLine = gl;
                    if (gid > 0) groupKey = "g:" + gid;
                    else groupKey = "gl:" + gl + ":" + groupTitle;
                }
            } else if ("tasks".equals(n)) {
                if (r.peek() == JsonToken.NULL) {
                    r.nextNull();
                } else {
                    r.beginArray();
                    while (r.hasNext()) {
                        TaskStatusRow row = readTaskStatusRow(r);
                        String eff = effectiveStatusFromMap(decisionMap, stemText, row.flag, row.baseStatus);
                        if ("pending".equals(eff)) pending++;
                        else done++;
                    }
                    r.endArray();
                }
            } else {
                r.skipValue();
            }
        }
        r.endObject();

        return new QueueStemLite(index, stemText, stemLine, groupKey, groupTitle, groupLine, pending, done);
    }

    private static final class TaskStatusRow {
        final String flag;
        final String baseStatus;

        TaskStatusRow(String flag, String baseStatus) {
            this.flag = flag == null ? "" : flag;
            this.baseStatus = baseStatus == null ? "pending" : baseStatus;
        }
    }

    private static TaskStatusRow readTaskStatusRow(JsonReader r) throws Exception {
        String flag = "";
        String status = "pending";

        r.beginObject();
        while (r.hasNext()) {
            String n = r.nextName();
            if ("flag".equals(n)) {
                flag = safeNextString(r);
            } else if ("status".equals(n)) {
                status = safeNextString(r);
            } else {
                r.skipValue();
            }
        }
        r.endObject();

        return new TaskStatusRow(flag, status);
    }

    private static String effectiveStatusFromMap(
            java.util.Map<String, java.util.Map<String, String>> decisionMap,
            String stem,
            String flag,
            String baseStatus
    ) {
        if (decisionMap != null) {
            java.util.Map<String, String> byFlag = decisionMap.get(stem);
            if (byFlag != null) {
                String d = byFlag.get(flag);
                if (d != null) {
                    String dl = d.trim().toLowerCase();
                    if (dl.equals("approved") || dl.equals("approve")) return "approved";
                    if (dl.equals("rejected") || dl.equals("reject")) return "rejected";
                }
            }
        }
        return baseStatus == null ? "pending" : baseStatus;
    }

    /**
     * Load a single stem object (and its tasks) by index from the stems array.
     * This streams through the gzip without loading the entire bundle.
     */
    public static JSONObject loadStemAtIndex(Context context, int stemIndex) throws Exception {
        if (stemIndex < 0) throw new IllegalArgumentException("stemIndex must be >= 0");

        File f = getBundleFile(context);
        if (!f.exists()) throw new IllegalStateException("Bundle not found");

        try (FileInputStream fis = new FileInputStream(f);
             GZIPInputStream gis = new GZIPInputStream(fis);
             InputStreamReader isr = new InputStreamReader(gis, StandardCharsets.UTF_8);
             JsonReader r = new JsonReader(isr)) {

            r.setLenient(true);
            r.beginObject();
            while (r.hasNext()) {
                String name = r.nextName();
                if (!"stems".equals(name)) {
                    r.skipValue();
                    continue;
                }

                // stems
                r.beginArray();
                int idx = 0;
                while (r.hasNext()) {
                    if (idx == stemIndex) {
                        return readStemObject(r);
                    }
                    r.skipValue();
                    idx++;
                }
                r.endArray();
                break;
            }
        }

        return null;
    }

    private static JSONObject readStemObject(JsonReader r) throws Exception {
        JSONObject stem = new JSONObject();
        r.beginObject();
        while (r.hasNext()) {
            String n = r.nextName();
            if ("stem".equals(n)) {
                stem.put("stem", safeNextString(r));
            } else if ("source_line_no".equals(n)) {
                stem.put("source_line_no", safeNextInt(r));
            } else if ("group".equals(n)) {
                if (r.peek() == JsonToken.NULL) {
                    r.nextNull();
                    stem.put("group", JSONObject.NULL);
                } else {
                    JSONObject g = new JSONObject();
                    r.beginObject();
                    while (r.hasNext()) {
                        String gn = r.nextName();
                        if ("id".equals(gn)) g.put("id", safeNextInt(r));
                        else if ("title".equals(gn)) g.put("title", safeNextString(r));
                        else if ("source_line_no".equals(gn)) g.put("source_line_no", safeNextInt(r));
                        else r.skipValue();
                    }
                    r.endObject();
                    stem.put("group", g);
                }
            } else if ("tasks".equals(n)) {
                org.json.JSONArray tasks = new org.json.JSONArray();
                if (r.peek() == JsonToken.NULL) {
                    r.nextNull();
                } else {
                    r.beginArray();
                    while (r.hasNext()) {
                        tasks.put(readTaskObject(r));
                    }
                    r.endArray();
                }
                stem.put("tasks", tasks);
            } else {
                r.skipValue();
            }
        }
        r.endObject();
        return stem;
    }

    private static JSONObject readTaskObject(JsonReader r) throws Exception {
        JSONObject task = new JSONObject();
        r.beginObject();
        while (r.hasNext()) {
            String n = r.nextName();
            if ("task_id".equals(n)) {
                task.put("task_id", safeNextInt(r));
            } else if ("flag".equals(n)) {
                task.put("flag", safeNextString(r));
            } else if ("status".equals(n)) {
                task.put("status", safeNextString(r));
            } else if ("description".equals(n)) {
                task.put("description", safeNextString(r));
            } else if ("examples".equals(n)) {
                org.json.JSONArray ex = new org.json.JSONArray();
                if (r.peek() == JsonToken.NULL) {
                    r.nextNull();
                } else {
                    r.beginArray();
                    while (r.hasNext()) {
                        ex.put(safeNextString(r));
                    }
                    r.endArray();
                }
                task.put("examples", ex);
            } else {
                r.skipValue();
            }
        }
        r.endObject();
        return task;
    }

    private static int safeNextInt(JsonReader r) throws Exception {
        JsonToken t = r.peek();
        if (t == JsonToken.NULL) {
            r.nextNull();
            return 0;
        }
        if (t == JsonToken.STRING) {
            String s = r.nextString();
            try {
                return Integer.parseInt(s);
            } catch (Exception ex) {
                return 0;
            }
        }
        if (t == JsonToken.NUMBER) {
            return r.nextInt();
        }
        r.skipValue();
        return 0;
    }

    @Nullable
    private static String safeNextString(JsonReader r) throws Exception {
        JsonToken t = r.peek();
        if (t == JsonToken.NULL) {
            r.nextNull();
            return "";
        }
        if (t == JsonToken.STRING) {
            return r.nextString();
        }
        if (t == JsonToken.NUMBER) {
            // Best-effort.
            return String.valueOf(r.nextLong());
        }
        if (t == JsonToken.BOOLEAN) {
            return String.valueOf(r.nextBoolean());
        }
        r.skipValue();
        return "";
    }

    private static byte[] readAllBytes(InputStream is) throws Exception {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buf = new byte[8192];
        while (true) {
            int n = is.read(buf);
            if (n < 0) break;
            if (n > 0) out.write(buf, 0, n);
        }
        return out.toByteArray();
    }
}
