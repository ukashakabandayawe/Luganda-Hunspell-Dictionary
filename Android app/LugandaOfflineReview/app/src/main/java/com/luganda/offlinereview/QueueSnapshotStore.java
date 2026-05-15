package com.luganda.offlinereview;

import android.content.Context;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

final class QueueSnapshotStore {
    private static final String FILE_NAME = "queue_snapshot.json";
    private static final Object REFRESH_LOCK = new Object();
    private static boolean refreshRunning = false;
    private static boolean refreshQueued = false;

    private QueueSnapshotStore() {}

    static final class Snapshot {
        long bundleMtime;
        long decisionsMtime;
        String titleText;
        String username;
        int stems;
        int tasks;
        int pending;
        int decided;
        int approved;
        int rejected;
        List<QueueActivity.GroupBucket> buckets;
        Map<String, Boolean> expandedByGroupKey;

        boolean isFreshFor(QueueActivity a) {
            if (a == null) return false;
            long bm = a.getBundleMtime();
            long dm = a.getDecisionsMtime();
            return bm > 0 && bm == bundleMtime && dm == decisionsMtime;
        }
    }

    static File getFile(Context context) {
        return new File(context.getFilesDir(), FILE_NAME);
    }

    static Snapshot load(Context context) {
        File f = getFile(context);
        if (!f.exists()) return null;

        try (FileInputStream fis = new FileInputStream(f)) {
            byte[] bytes = readAllBytes(fis);
            String json = new String(bytes, StandardCharsets.UTF_8);
            JSONObject root = new JSONObject(json);

            Snapshot s = new Snapshot();
            s.bundleMtime = root.optLong("bundle_mtime", -1L);
            s.decisionsMtime = root.optLong("decisions_mtime", -1L);
            s.titleText = root.optString("title_text", "My Queue");
            s.username = root.optString("username", "");
            s.stems = root.optInt("stems", 0);
            s.tasks = root.optInt("tasks", 0);
            s.pending = root.optInt("pending", 0);
            s.decided = root.optInt("decided", 0);
            s.approved = root.optInt("approved", 0);
            s.rejected = root.optInt("rejected", 0);
            s.expandedByGroupKey = new HashMap<>();
            JSONObject expanded = root.optJSONObject("expanded");
            if (expanded != null) {
                java.util.Iterator<String> keys = expanded.keys();
                while (keys.hasNext()) {
                    String key = keys.next();
                    s.expandedByGroupKey.put(key, expanded.optBoolean(key, false));
                }
            }
            s.buckets = readBuckets(root.optJSONArray("buckets"));
            return s;
        } catch (Throwable ignored) {
            return null;
        }
    }

    static void save(Context context, Snapshot snapshot) {
        if (context == null || snapshot == null) return;
        File f = getFile(context);
        File tmp = new File(context.getFilesDir(), FILE_NAME + ".tmp");

        try {
            JSONObject root = new JSONObject();
            root.put("bundle_mtime", snapshot.bundleMtime);
            root.put("decisions_mtime", snapshot.decisionsMtime);
            root.put("title_text", snapshot.titleText == null ? "My Queue" : snapshot.titleText);
            root.put("username", snapshot.username == null ? "" : snapshot.username);
            root.put("stems", snapshot.stems);
            root.put("tasks", snapshot.tasks);
            root.put("pending", snapshot.pending);
            root.put("decided", snapshot.decided);
            root.put("approved", snapshot.approved);
            root.put("rejected", snapshot.rejected);

            JSONObject expanded = new JSONObject();
            if (snapshot.expandedByGroupKey != null) {
                for (Map.Entry<String, Boolean> entry : snapshot.expandedByGroupKey.entrySet()) {
                    expanded.put(entry.getKey(), entry.getValue() != null && entry.getValue());
                }
            }
            root.put("expanded", expanded);
            root.put("buckets", writeBuckets(snapshot.buckets));

            byte[] bytes = root.toString().getBytes(StandardCharsets.UTF_8);
            try (FileOutputStream fos = new FileOutputStream(tmp, false)) {
                fos.write(bytes);
            }
            if (!tmp.renameTo(f)) {
                try (FileOutputStream fos = new FileOutputStream(f, false)) {
                    fos.write(bytes);
                }
                // noinspection ResultOfMethodCallIgnored
                tmp.delete();
            }
        } catch (Throwable ignored) {
            // best-effort only
        }
    }

    static void refreshAsync(Context context) {
        if (context == null) return;
        final Context appContext = context.getApplicationContext();

        boolean startWorker = false;
        synchronized (REFRESH_LOCK) {
            if (refreshRunning) {
                refreshQueued = true;
            } else {
                refreshRunning = true;
                startWorker = true;
            }
        }
        if (!startWorker) return;

        new Thread(() -> {
            boolean rerun;
            do {
                try {
                    refreshOnce(appContext);
                } catch (Throwable ignored) {
                }

                synchronized (REFRESH_LOCK) {
                    if (refreshQueued) {
                        refreshQueued = false;
                        rerun = true;
                    } else {
                        refreshRunning = false;
                        rerun = false;
                    }
                }
            } while (rerun);
        }, "queue-snapshot-refresh").start();
    }

    private static void refreshOnce(Context context) throws Exception {
        BundleStore.BundleHeader header = BundleStore.readBundleHeader(context);
        java.util.Map<String, java.util.Map<String, String>> decisionMap = DecisionsStore.loadDecisionStatusMap(context);
        java.util.List<BundleStore.QueueStemLite> stems = BundleStore.loadQueueStems(context, decisionMap);

        Snapshot snapshot = new Snapshot();
        snapshot.bundleMtime = safeMtime(BundleStore.getBundleFile(context));
        snapshot.decisionsMtime = safeMtime(DecisionsStore.getDecisionsFile(context));
        snapshot.username = header == null ? "" : header.username;
        snapshot.titleText = snapshot.username == null || snapshot.username.trim().isEmpty()
                ? "My Queue"
                : ("My Queue (" + snapshot.username.trim() + ")");
        snapshot.buckets = buildBuckets(stems);
        snapshot.expandedByGroupKey = new HashMap<>();
        snapshot.stems = 0;
        snapshot.tasks = 0;
        snapshot.pending = 0;
        snapshot.decided = 0;
        for (QueueActivity.GroupBucket bucket : snapshot.buckets) {
            if (bucket == null) continue;
            snapshot.stems += bucket.stems == null ? 0 : bucket.stems.size();
            snapshot.pending += bucket.pendingTotal;
            snapshot.decided += bucket.doneTotal;
            if (bucket.stems != null) {
                for (QueueActivity.StemItem stem : bucket.stems) {
                    if (stem == null) continue;
                    snapshot.tasks += stem.pending + stem.done;
                }
            }
        }
        snapshot.approved = 0;
        snapshot.rejected = 0;
        save(context, snapshot);
    }

    private static JSONArray writeBuckets(List<QueueActivity.GroupBucket> buckets) throws Exception {
        JSONArray out = new JSONArray();
        if (buckets == null) return out;
        for (QueueActivity.GroupBucket bucket : buckets) {
            if (bucket == null) continue;
            JSONObject b = new JSONObject();
            b.put("key", bucket.key);
            b.put("title", bucket.title);
            b.put("orderLine", bucket.orderLine);
            b.put("pendingTotal", bucket.pendingTotal);
            b.put("doneTotal", bucket.doneTotal);

            JSONArray stems = new JSONArray();
            for (QueueActivity.StemItem s : bucket.stems) {
                if (s == null) continue;
                JSONObject item = new JSONObject();
                item.put("stemIndex", s.stemIndex);
                item.put("stem", s.stem);
                item.put("pending", s.pending);
                item.put("done", s.done);
                item.put("sourceLineNo", s.sourceLineNo);
                item.put("groupKey", s.groupKey);
                item.put("isLastInGroup", s.isLastInGroup);
                stems.put(item);
            }
            b.put("stems", stems);
            out.put(b);
        }
        return out;
    }

    private static List<QueueActivity.GroupBucket> readBuckets(JSONArray arr) {
        List<QueueActivity.GroupBucket> out = new java.util.ArrayList<>();
        if (arr == null) return out;

        for (int i = 0; i < arr.length(); i++) {
            JSONObject b = arr.optJSONObject(i);
            if (b == null) continue;
            QueueActivity.GroupBucket bucket = new QueueActivity.GroupBucket(
                    b.optString("key", "ungrouped"),
                    b.optString("title", "Ungrouped"),
                    b.optInt("orderLine", 1_000_000_000)
            );
            bucket.pendingTotal = b.optInt("pendingTotal", 0);
            bucket.doneTotal = b.optInt("doneTotal", 0);

            JSONArray stems = b.optJSONArray("stems");
            if (stems != null) {
                for (int j = 0; j < stems.length(); j++) {
                    JSONObject s = stems.optJSONObject(j);
                    if (s == null) continue;
                    bucket.stems.add(new QueueActivity.StemItem(
                            s.optInt("stemIndex", -1),
                            s.optString("stem", ""),
                            s.optInt("pending", 0),
                            s.optInt("done", 0),
                            s.optInt("sourceLineNo", 1_000_000_000),
                            s.optString("groupKey", bucket.key),
                            s.optBoolean("isLastInGroup", false)
                    ));
                }
            }

            out.add(bucket);
        }

        return out;
    }

    private static List<QueueActivity.GroupBucket> buildBuckets(List<BundleStore.QueueStemLite> stems) {
        List<QueueActivity.GroupBucket> out = new java.util.ArrayList<>();
        if (stems == null) return out;

        java.util.LinkedHashMap<String, QueueActivity.GroupBucket> bucketsByKey = new java.util.LinkedHashMap<>();
        for (BundleStore.QueueStemLite s : stems) {
            if (s == null) continue;

            String groupKey = (s.groupKey == null || s.groupKey.trim().isEmpty()) ? "ungrouped" : s.groupKey;
            String groupTitle = (s.groupTitle == null || s.groupTitle.trim().isEmpty()) ? "Ungrouped" : s.groupTitle;
            int groupLine = s.groupLine;

            QueueActivity.GroupBucket bucket = bucketsByKey.get(groupKey);
            if (bucket == null) {
                bucket = new QueueActivity.GroupBucket(groupKey, groupTitle, groupLine);
                bucketsByKey.put(groupKey, bucket);
            }

            bucket.stems.add(new QueueActivity.StemItem(s.index, s.stem, s.pending, s.done, s.sourceLineNo, groupKey));
            bucket.pendingTotal += s.pending;
            bucket.doneTotal += s.done;
        }

        out.addAll(bucketsByKey.values());
        return out;
    }

    private static long safeMtime(File file) {
        return (file != null && file.exists()) ? file.lastModified() : 0L;
    }

    private static byte[] readAllBytes(FileInputStream is) throws Exception {
        byte[] buf = new byte[8192];
        int n;
        java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream();
        while ((n = is.read(buf)) >= 0) {
            if (n == 0) continue;
            out.write(buf, 0, n);
        }
        return out.toByteArray();
    }
}