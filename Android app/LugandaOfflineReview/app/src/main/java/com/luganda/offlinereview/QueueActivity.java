package com.luganda.offlinereview;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.text.InputType;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import com.google.android.material.progressindicator.LinearProgressIndicator;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.DiffUtil;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.card.MaterialCardView;
import com.google.android.material.shape.ShapeAppearanceModel;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.LinkedHashSet;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class QueueActivity extends AppCompatActivity {

    private static final String TAG = "QueueActivity";

    public static final String EXTRA_STEM_INDEX = "stem_index";
    public static final String EXTRA_RESULT_PENDING = "result_pending";
    public static final String EXTRA_RESULT_DONE = "result_done";
    public static final String EXTRA_CROSSCHECK_MODE = "crosscheck_mode";
    public static final String EXTRA_CROSSCHECK_FLAGS = "crosscheck_flags";
    public static final String EXTRA_CROSSCHECK_SUMMARY = "crosscheck_summary";

    private static final int REQ_REVIEW_STEM = 1001;
    private static final String PREFS_CROSSCHECK = "crosscheck_mode";
    private static final String KEY_CROSSCHECK_ACTIVE = "active";
    private static final String KEY_CROSSCHECK_FLAGS = "flags";
    private static final String KEY_CROSSCHECK_SUMMARY = "summary";
    private static final Pattern CROSSCHECK_FLAG_PATTERN = Pattern.compile("[A-Za-z0-9]+(?:[+-][A-Za-z0-9]+)*");

    private static CachedQueue sCache;

    private Map<String, Map<String, String>> decisionMap;

    private TextView title;
    private RecyclerView rv;
    private QueueAdapter adapter;
    private LinearProgressIndicator progress;
    private TextView crossCheckStatus;
    private Button crossCheckButton;
    private Button clearCrossCheckButton;

    private final Map<String, Boolean> expandedByGroupKey = new HashMap<>();
    private List<GroupBucket> lastBuckets = new ArrayList<>();
    private boolean skipNextResumeReload = false;
    private long lastLoadedBundleMtime = -1L;
    private long lastLoadedDecisionsMtime = -1L;
    private boolean crossCheckActive = false;
    private LinkedHashSet<String> crossCheckFlags = new LinkedHashSet<>();
    private String crossCheckSummary = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_queue);
        Watchdog.start(this);

        MaterialToolbar toolbar = findViewById(R.id.queueToolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }

        title = findViewById(R.id.queueTitle);
        crossCheckStatus = findViewById(R.id.queueCrossCheckStatus);
        crossCheckButton = findViewById(R.id.btnCrossCheckMode);
        clearCrossCheckButton = findViewById(R.id.btnClearCrossCheckMode);
        progress = findViewById(R.id.queueProgress);
        rv = findViewById(R.id.queueRecycler);
        rv.setLayoutManager(new LinearLayoutManager(this));
        rv.setVerticalScrollBarEnabled(true);

        restoreCrossCheckState();
        refreshCrossCheckUi();

        adapter = new QueueAdapter(new ArrayList<>(),
                stemItem -> {
                    Intent intent = new Intent(this, ReviewActivity.class);
                    intent.putExtra(EXTRA_STEM_INDEX, stemItem.stemIndex);
                    if (crossCheckActive && !crossCheckFlags.isEmpty()) {
                        intent.putExtra(ReviewActivity.EXTRA_CROSSCHECK_MODE, true);
                        intent.putStringArrayListExtra(ReviewActivity.EXTRA_CROSSCHECK_FLAGS, new ArrayList<>(crossCheckFlags));
                        intent.putExtra(ReviewActivity.EXTRA_CROSSCHECK_SUMMARY, crossCheckSummary);
                    }
                    skipNextResumeReload = true;
                    startActivityForResult(intent, REQ_REVIEW_STEM);
                },
                header -> {
                    boolean expanded = expandedByGroupKey.get(header.groupKey) != null && expandedByGroupKey.get(header.groupKey);
                    expandedByGroupKey.put(header.groupKey, !expanded);
                    adapter.setItems(buildQueueItems(lastBuckets));
                    saveCacheIfPossible();
                }
        );
        rv.setAdapter(adapter);

        if (crossCheckButton != null) {
            crossCheckButton.setOnClickListener(v -> showCrossCheckDialog());
        }
        if (clearCrossCheckButton != null) {
            clearCrossCheckButton.setOnClickListener(v -> clearCrossCheckMode());
        }

        // Always show skeleton quickly; restore/parse cache off the UI thread.
        setLoading(true);
        restoreFromPersistentCacheIfFreshAsync();
    }

    private void restoreFromPersistentCacheIfFreshAsync() {
        // Fast path: in-memory cache.
        if (sCache != null && sCache.isFreshFor(this) && sCache.buckets != null) {
            renderFromCacheAsync(sCache);
            return;
        }

        new Thread(() -> {
            QueueSnapshotStore.Snapshot snapshot = QueueSnapshotStore.load(QueueActivity.this);
            if (snapshot == null || !snapshot.isFreshFor(QueueActivity.this) || snapshot.buckets == null) {
                runOnUiThread(() -> loadAndRenderAsync());
                return;
            }

            CachedQueue cache = new CachedQueue();
            cache.bundleMtime = snapshot.bundleMtime;
            cache.decisionsMtime = snapshot.decisionsMtime;
            cache.titleText = snapshot.titleText;
            cache.username = snapshot.username;
            cache.stems = snapshot.stems;
            cache.tasks = snapshot.tasks;
            cache.pending = snapshot.pending;
            cache.decided = snapshot.decided;
            cache.approved = snapshot.approved;
            cache.rejected = snapshot.rejected;
            cache.buckets = snapshot.buckets;
            cache.expandedByGroupKey = snapshot.expandedByGroupKey;

            sCache = cache;
            renderFromCacheAsync(cache);
        }, "queue-cache-restore").start();
    }

    private void renderFromCacheAsync(CachedQueue cache) {
        if (cache == null || cache.buckets == null) {
            runOnUiThread(() -> loadAndRenderAsync());
            return;
        }

        new Thread(() -> {
            // Restore expansion state before building items.
            expandedByGroupKey.clear();
            if (cache.expandedByGroupKey != null) {
                expandedByGroupKey.putAll(cache.expandedByGroupKey);
            }

            List<GroupBucket> buckets = cache.buckets;
            List<QueueItem> items = buildQueueItems(buckets);

            runOnUiThread(() -> {
                lastBuckets = buckets;
                lastLoadedBundleMtime = cache.bundleMtime;
                lastLoadedDecisionsMtime = cache.decisionsMtime;
                setLoading(false);
                if (title != null) title.setText(cache.titleText == null ? "My Queue" : cache.titleText);
                if (adapter != null) adapter.setItems(items);
            });
        }, "queue-cache-render").start();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (skipNextResumeReload) {
            skipNextResumeReload = false;
            return;
        }
        // Avoid re-parsing the full gzip bundle on every resume; it can be expensive.
        // If the underlying files changed (bundle imported, decisions imported), reload.
        if (!isCurrentDataFresh()) {
            setLoading(true);
            loadAndRenderAsync();
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != REQ_REVIEW_STEM) return;
        if (resultCode != RESULT_OK || data == null) return;

        int stemIndex = data.getIntExtra(EXTRA_STEM_INDEX, -1);
        int pending = data.getIntExtra(EXTRA_RESULT_PENDING, -1);
        int done = data.getIntExtra(EXTRA_RESULT_DONE, -1);
        if (stemIndex < 0 || pending < 0 || done < 0) return;

        applyStemCountsUpdate(stemIndex, pending, done);
    }

    // restoreFromPersistentCacheIfFresh removed; cache restore is now async to avoid ANRs.

    private boolean isCurrentDataFresh() {
        long bm = getBundleMtime();
        long dm = getDecisionsMtime();
        if (bm <= 0) return false;
        if (lastLoadedBundleMtime <= 0) return false;

        // decisions file may not exist; treat missing as 0.
        return bm == lastLoadedBundleMtime && dm == lastLoadedDecisionsMtime;
    }

    long getBundleMtime() {
        try {
            java.io.File f = BundleStore.getBundleFile(this);
            return (f != null && f.exists()) ? f.lastModified() : 0L;
        } catch (Throwable ignored) {
            return 0L;
        }
    }

    long getDecisionsMtime() {
        try {
            java.io.File f = DecisionsStore.getDecisionsFile(this);
            return (f != null && f.exists()) ? f.lastModified() : 0L;
        } catch (Throwable ignored) {
            return 0L;
        }
    }

    private void applyStemCountsUpdate(int stemIndex, int pending, int done) {
        if (lastBuckets == null) return;
        boolean changed = false;

        for (GroupBucket b : lastBuckets) {
            if (b == null) continue;
            for (int i = 0; i < b.stems.size(); i++) {
                StemItem s = b.stems.get(i);
                if (s == null) continue;
                if (s.stemIndex != stemIndex) continue;

                int oldPending = s.pending;
                int oldDone = s.done;
                if (oldPending == pending && oldDone == done) {
                    // Still update mtimes so we don't trigger a reload.
                    lastLoadedDecisionsMtime = getDecisionsMtime();
                    saveCacheIfPossible();
                    return;
                }

                b.pendingTotal += (pending - oldPending);
                b.doneTotal += (done - oldDone);
                b.stems.set(i, new StemItem(s.stemIndex, s.stem, pending, done, s.sourceLineNo, s.groupKey));
                changed = true;
                break;
            }
            if (changed) break;
        }

        if (changed && adapter != null) {
            adapter.setItems(buildQueueItems(lastBuckets));
        }

        lastLoadedDecisionsMtime = getDecisionsMtime();
        saveCacheIfPossible();
    }

    private void saveCacheIfPossible() {
        if (lastBuckets == null || lastBuckets.isEmpty()) return;
        if (title == null) return;

        long bm = getBundleMtime();
        long dm = getDecisionsMtime();
        if (bm <= 0) return;

        if (sCache == null) sCache = new CachedQueue();
        sCache.bundleMtime = bm;
        sCache.decisionsMtime = dm;
        sCache.titleText = title.getText() == null ? "My Queue" : title.getText().toString();
        sCache.username = extractUsernameFromTitle(sCache.titleText);
        sCache.stems = countStems(lastBuckets);
        sCache.tasks = countTasks(lastBuckets);
        sCache.pending = countPending(lastBuckets);
        sCache.decided = sCache.tasks - sCache.pending;
        sCache.approved = 0;
        sCache.rejected = 0;
        sCache.buckets = lastBuckets;
        sCache.expandedByGroupKey = new HashMap<>(expandedByGroupKey);

        QueueSnapshotStore.Snapshot snapshot = new QueueSnapshotStore.Snapshot();
        snapshot.bundleMtime = sCache.bundleMtime;
        snapshot.decisionsMtime = sCache.decisionsMtime;
        snapshot.titleText = sCache.titleText;
        snapshot.username = sCache.username;
        snapshot.stems = sCache.stems;
        snapshot.tasks = sCache.tasks;
        snapshot.pending = sCache.pending;
        snapshot.decided = sCache.decided;
        snapshot.approved = sCache.approved;
        snapshot.rejected = sCache.rejected;
        snapshot.buckets = new ArrayList<>(lastBuckets);
        snapshot.expandedByGroupKey = new HashMap<>(expandedByGroupKey);
        new Thread(() -> QueueSnapshotStore.save(QueueActivity.this, snapshot)).start();
    }

    private void restoreCrossCheckState() {
        SharedPreferences prefs = getSharedPreferences(PREFS_CROSSCHECK, MODE_PRIVATE);
        crossCheckActive = prefs.getBoolean(KEY_CROSSCHECK_ACTIVE, false);
        crossCheckSummary = prefs.getString(KEY_CROSSCHECK_SUMMARY, "");
        crossCheckFlags = parseFlagSet(prefs.getString(KEY_CROSSCHECK_FLAGS, ""));
        if (crossCheckFlags.isEmpty()) {
            crossCheckActive = false;
            crossCheckSummary = "";
        }
    }

    private void persistCrossCheckState() {
        SharedPreferences prefs = getSharedPreferences(PREFS_CROSSCHECK, MODE_PRIVATE);
        prefs.edit()
                .putBoolean(KEY_CROSSCHECK_ACTIVE, crossCheckActive && !crossCheckFlags.isEmpty())
                .putString(KEY_CROSSCHECK_FLAGS, String.join(" ", crossCheckFlags))
                .putString(KEY_CROSSCHECK_SUMMARY, crossCheckSummary == null ? "" : crossCheckSummary)
                .apply();
    }

    private void showCrossCheckDialog() {
        EditText input = new EditText(this);
        input.setMinLines(4);
        input.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_MULTI_LINE | InputType.TYPE_TEXT_FLAG_CAP_CHARACTERS);
        input.setHint("Paste unique flags here");
        if (!crossCheckFlags.isEmpty()) {
            input.setText(String.join(" ", crossCheckFlags));
            input.setSelection(input.getText() == null ? 0 : input.getText().length());
        }

        new AlertDialog.Builder(this)
                .setTitle("Decision cross-check mode")
                .setMessage("Paste the unique flags for this stem group. The app will deduplicate the pasted text and reuse the set while you review multiple stems.")
                .setView(input)
                .setPositiveButton("Use set", (dialog, which) -> {
                    LinkedHashSet<String> parsed = parseFlagSet(input.getText() == null ? "" : input.getText().toString());
                    if (parsed.isEmpty()) {
                        clearCrossCheckMode();
                        Toast.makeText(this, "No flags found", Toast.LENGTH_SHORT).show();
                        return;
                    }
                    crossCheckActive = true;
                    crossCheckFlags = parsed;
                    crossCheckSummary = "Cross-check: " + crossCheckFlags.size() + " unique flags";
                    persistCrossCheckState();
                    refreshCrossCheckUi();
                    Toast.makeText(this, "Cross-check mode enabled", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void clearCrossCheckMode() {
        crossCheckActive = false;
        crossCheckFlags.clear();
        crossCheckSummary = "";
        persistCrossCheckState();
        refreshCrossCheckUi();
    }

    private void refreshCrossCheckUi() {
        if (crossCheckStatus != null) {
            if (!crossCheckActive || crossCheckFlags.isEmpty()) {
                crossCheckStatus.setText("Cross-check: off");
            } else {
                crossCheckStatus.setText("Cross-check: " + crossCheckFlags.size() + " unique flags active");
            }
        }
        if (clearCrossCheckButton != null) {
            clearCrossCheckButton.setEnabled(crossCheckActive && !crossCheckFlags.isEmpty());
        }
    }

    private static LinkedHashSet<String> parseFlagSet(String text) {
        LinkedHashSet<String> out = new LinkedHashSet<>();
        if (text == null) {
            return out;
        }

        Matcher matcher = CROSSCHECK_FLAG_PATTERN.matcher(text);
        while (matcher.find()) {
            String token = matcher.group();
            if (token != null) {
                String normalized = token.trim();
                if (!normalized.isEmpty()) {
                    out.add(normalized);
                }
            }
        }
        return out;
    }

    private void loadAndRenderAsync() {
        new Thread(() -> {
            try {
                BundleStore.BundleHeader loadedHeader = BundleStore.readBundleHeader(QueueActivity.this);
                Map<String, Map<String, String>> loadedDecisionMap = DecisionsStore.loadDecisionStatusMap(QueueActivity.this);
                List<BundleStore.QueueStemLite> stems = BundleStore.loadQueueStems(QueueActivity.this, loadedDecisionMap);

                List<GroupBucket> buckets = buildBucketsFromLite(stems);
                List<QueueItem> items = buildQueueItems(buckets);

                String username = loadedHeader == null ? "" : loadedHeader.username;
                if (username == null) username = "";
                username = username.trim();
                String header = username.isEmpty() ? "My Queue" : ("My Queue (" + username + ")");

                final long bm = getBundleMtime();
                final long dm = getDecisionsMtime();

                runOnUiThread(() -> {
                    setLoading(false);
                    decisionMap = loadedDecisionMap;
                    lastBuckets = buckets;
                    lastLoadedBundleMtime = bm;
                    lastLoadedDecisionsMtime = dm;
                    title.setText(header);
                    if (adapter != null) adapter.setItems(items);
                    refreshCrossCheckUi();
                    saveCacheIfPossible();
                    // Build a stem cache in background for faster stem opens later.
                    BundleStore.buildStemCacheIfNeededAsync(QueueActivity.this);
                });
            } catch (Throwable t) {
                String bundleSize = "(unknown)";
                try {
                    java.io.File f = BundleStore.getBundleFile(QueueActivity.this);
                    if (f != null && f.exists()) {
                        bundleSize = String.valueOf(f.length());
                    }
                } catch (Throwable ignored) {}

                Log.e(TAG, "Failed to load/render queue. bundle_bytes=" + bundleSize, t);

                final String msg =
                        "Failed to open queue.\n" +
                        "Bundle bytes: " + bundleSize + "\n\n" +
                        t.getClass().getSimpleName() + ": " + (t.getMessage() == null ? "" : t.getMessage()) + "\n\n" +
                        "Tip: Re-export the bundle with Limit examples = 0.";

                runOnUiThread(() -> {
                    setLoading(false);
                    title.setText(msg);
                    if (adapter != null) adapter.setItems(new ArrayList<>());
                });
            }
        }).start();
    }

    private void setLoading(boolean isLoading) {
        if (progress != null) {
            progress.setVisibility(isLoading ? View.VISIBLE : View.GONE);
        }
        if (rv != null) {
            // Keep visible so we can show a skeleton list.
            rv.setVisibility(View.VISIBLE);
        }
        if (title != null && isLoading) {
            title.setText(" ");
        }
        if (adapter != null && isLoading) {
            adapter.setItems(buildSkeletonItems());
        }
    }

    private List<QueueItem> buildSkeletonItems() {
        List<QueueItem> out = new ArrayList<>();
        // Two sections, similar to the eventual accordion.
        for (int section = 0; section < 2; section++) {
            out.add(new SkeletonHeaderItem("sk-h-" + section));
            for (int i = 0; i < 4; i++) {
                boolean isLast = (i == 3);
                out.add(new SkeletonStemItem("sk-s-" + section + "-" + i, isLast));
            }
        }
        return out;
    }

    private List<GroupBucket> buildBucketsFromLite(List<BundleStore.QueueStemLite> stems) {
        if (stems == null) return new ArrayList<>();

        Map<String, GroupBucket> bucketsByKey = new LinkedHashMap<>();
        for (BundleStore.QueueStemLite s : stems) {
            if (s == null) continue;

            String groupKey = (s.groupKey == null || s.groupKey.trim().isEmpty()) ? "ungrouped" : s.groupKey;
            String groupTitle = (s.groupTitle == null || s.groupTitle.trim().isEmpty()) ? "Ungrouped" : s.groupTitle;
            int groupLine = s.groupLine;

            GroupBucket bucket = bucketsByKey.get(groupKey);
            if (bucket == null) {
                bucket = new GroupBucket(groupKey, groupTitle, groupLine);
                bucketsByKey.put(groupKey, bucket);
            }

            StemItem item = new StemItem(s.index, s.stem, s.pending, s.done, s.sourceLineNo, groupKey);
            bucket.stems.add(item);
            bucket.pendingTotal += s.pending;
            bucket.doneTotal += s.done;
        }

        // Preserve the bundle's file order (stems are already streamed in order).
        // Sorting can be very expensive for huge reviewer assignments.
        return new ArrayList<>(bucketsByKey.values());
    }

    @Override
    public boolean onSupportNavigateUp() {
        finish();
        return true;
    }

    // buildBuckets(JSONArray) removed; we now stream from bundle.

    private List<QueueItem> buildQueueItems(List<GroupBucket> buckets) {
        if (buckets == null) return new ArrayList<>();
        List<QueueItem> out = new ArrayList<>();

        for (GroupBucket b : buckets) {
            boolean expanded = expandedByGroupKey.get(b.key) != null && expandedByGroupKey.get(b.key);
            out.add(new GroupHeaderItem(b.key, b.title, b.stems.size(), b.pendingTotal, b.doneTotal, expanded));
            if (expanded) {
                for (int i = 0; i < b.stems.size(); i++) {
                    StemItem s = b.stems.get(i);
                    boolean isLast = (i == b.stems.size() - 1);
                    out.add(new StemItem(
                            s.stemIndex,
                            s.stem,
                            s.pending,
                            s.done,
                            s.sourceLineNo,
                            s.groupKey,
                            isLast
                    ));
                }
            }
        }

        return out;
    }

    private static int countStems(List<GroupBucket> buckets) {
        int total = 0;
        if (buckets == null) return 0;
        for (GroupBucket bucket : buckets) {
            if (bucket == null || bucket.stems == null) continue;
            total += bucket.stems.size();
        }
        return total;
    }

    private static int countTasks(List<GroupBucket> buckets) {
        int total = 0;
        if (buckets == null) return 0;
        for (GroupBucket bucket : buckets) {
            if (bucket == null) continue;
            if (bucket.stems == null) continue;
            for (StemItem stem : bucket.stems) {
                if (stem == null) continue;
                total += stem.pending + stem.done;
            }
        }
        return total;
    }

    private static int countPending(List<GroupBucket> buckets) {
        int total = 0;
        if (buckets == null) return 0;
        for (GroupBucket bucket : buckets) {
            if (bucket == null) continue;
            total += bucket.pendingTotal;
        }
        return total;
    }

    private static int countDone(List<GroupBucket> buckets) {
        int total = 0;
        if (buckets == null) return 0;
        for (GroupBucket bucket : buckets) {
            if (bucket == null) continue;
            total += bucket.doneTotal;
        }
        return total;
    }

    private static String extractUsernameFromTitle(String titleText) {
        if (titleText == null) return "";
        int open = titleText.indexOf('(');
        int close = titleText.lastIndexOf(')');
        if (open >= 0 && close > open) {
            return titleText.substring(open + 1, close).trim();
        }
        return "";
    }

    static final class GroupBucket {
        final String key;
        final String title;
        final int orderLine;
        final List<StemItem> stems = new ArrayList<>();
        int pendingTotal = 0;
        int doneTotal = 0;

        GroupBucket(String key, String title, int orderLine) {
            this.key = key;
            this.title = title == null ? "" : title;
            this.orderLine = orderLine;
        }
    }

    static abstract class QueueItem {
        abstract int viewType();
    }

    static final class SkeletonHeaderItem extends QueueItem {
        static final int TYPE = 2;
        final String id;

        SkeletonHeaderItem(String id) {
            this.id = id;
        }

        @Override
        int viewType() {
            return TYPE;
        }
    }

    static final class SkeletonStemItem extends QueueItem {
        static final int TYPE = 3;
        final String id;
        final boolean isLastInSection;

        SkeletonStemItem(String id, boolean isLastInSection) {
            this.id = id;
            this.isLastInSection = isLastInSection;
        }

        @Override
        int viewType() {
            return TYPE;
        }
    }

    static final class GroupHeaderItem extends QueueItem {
        static final int TYPE = 0;
        final String groupKey;
        final String title;
        final int stemsCount;
        final int pending;
        final int done;
        final boolean expanded;

        GroupHeaderItem(String groupKey, String title, int stemsCount, int pending, int done, boolean expanded) {
            this.groupKey = groupKey;
            this.title = title == null ? "" : title;
            this.stemsCount = stemsCount;
            this.pending = pending;
            this.done = done;
            this.expanded = expanded;
        }

        @Override
        int viewType() {
            return TYPE;
        }
    }

    static final class StemItem extends QueueItem {
        static final int TYPE = 1;
        final int stemIndex;
        final String stem;
        final int pending;
        final int done;
        final int sourceLineNo;
        final String groupKey;
        final boolean isLastInGroup;

        StemItem(int stemIndex, String stem, int pending, int done, int sourceLineNo, String groupKey) {
            this(stemIndex, stem, pending, done, sourceLineNo, groupKey, false);
        }

        StemItem(int stemIndex, String stem, int pending, int done, int sourceLineNo, String groupKey, boolean isLastInGroup) {
            this.stemIndex = stemIndex;
            this.stem = stem == null ? "" : stem;
            this.pending = pending;
            this.done = done;
            this.sourceLineNo = sourceLineNo;
            this.groupKey = groupKey;
            this.isLastInGroup = isLastInGroup;
        }

        @Override
        int viewType() {
            return TYPE;
        }
    }

    interface OnStemClick {
        void onClick(StemItem item);
    }

    interface OnGroupHeaderClick {
        void onClick(GroupHeaderItem header);
    }

    static final class QueueAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {
        private final List<QueueItem> items;
        private final OnStemClick onStemClick;
        private final OnGroupHeaderClick onHeaderClick;

        QueueAdapter(List<QueueItem> items, OnStemClick onStemClick, OnGroupHeaderClick onHeaderClick) {
            this.items = items;
            this.onStemClick = onStemClick;
            this.onHeaderClick = onHeaderClick;
        }

        void setItems(List<QueueItem> newItems) {
            final List<QueueItem> next = (newItems == null) ? new ArrayList<>() : new ArrayList<>(newItems);
            final List<QueueItem> prev = new ArrayList<>(items);

            DiffUtil.DiffResult diff = DiffUtil.calculateDiff(new DiffUtil.Callback() {
                @Override
                public int getOldListSize() {
                    return prev.size();
                }

                @Override
                public int getNewListSize() {
                    return next.size();
                }

                @Override
                public boolean areItemsTheSame(int oldItemPosition, int newItemPosition) {
                    QueueItem o = prev.get(oldItemPosition);
                    QueueItem n = next.get(newItemPosition);
                    if (o.viewType() != n.viewType()) return false;
                    if (o instanceof GroupHeaderItem && n instanceof GroupHeaderItem) {
                        return ((GroupHeaderItem) o).groupKey.equals(((GroupHeaderItem) n).groupKey);
                    }
                    if (o instanceof StemItem && n instanceof StemItem) {
                        StemItem so = (StemItem) o;
                        StemItem sn = (StemItem) n;
                        return so.stemIndex == sn.stemIndex && so.groupKey.equals(sn.groupKey);
                    }
                    if (o instanceof SkeletonHeaderItem && n instanceof SkeletonHeaderItem) {
                        return ((SkeletonHeaderItem) o).id.equals(((SkeletonHeaderItem) n).id);
                    }
                    if (o instanceof SkeletonStemItem && n instanceof SkeletonStemItem) {
                        return ((SkeletonStemItem) o).id.equals(((SkeletonStemItem) n).id);
                    }
                    return false;
                }

                @Override
                public boolean areContentsTheSame(int oldItemPosition, int newItemPosition) {
                    QueueItem o = prev.get(oldItemPosition);
                    QueueItem n = next.get(newItemPosition);
                    if (o.viewType() != n.viewType()) return false;

                    if (o instanceof GroupHeaderItem && n instanceof GroupHeaderItem) {
                        GroupHeaderItem go = (GroupHeaderItem) o;
                        GroupHeaderItem gn = (GroupHeaderItem) n;
                        return go.title.equals(gn.title)
                                && go.stemsCount == gn.stemsCount
                                && go.pending == gn.pending
                                && go.done == gn.done
                                && go.expanded == gn.expanded;
                    }
                    if (o instanceof StemItem && n instanceof StemItem) {
                        StemItem so = (StemItem) o;
                        StemItem sn = (StemItem) n;
                        return so.stem.equals(sn.stem)
                                && so.pending == sn.pending
                                && so.done == sn.done
                                && so.isLastInGroup == sn.isLastInGroup;
                    }
                    if (o instanceof SkeletonStemItem && n instanceof SkeletonStemItem) {
                        return ((SkeletonStemItem) o).isLastInSection == ((SkeletonStemItem) n).isLastInSection;
                    }
                    return false;
                }
            }, true);

            items.clear();
            items.addAll(next);
            diff.dispatchUpdatesTo(this);
        }

        @Override
        public int getItemViewType(int position) {
            return items.get(position).viewType();
        }

        @Override
        public RecyclerView.ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
            LayoutInflater inflater = LayoutInflater.from(parent.getContext());
            if (viewType == GroupHeaderItem.TYPE) {
                View v = inflater.inflate(R.layout.row_group_header, parent, false);
                return new GroupHeaderViewHolder(v);
            }
            if (viewType == SkeletonHeaderItem.TYPE) {
                View v = inflater.inflate(R.layout.row_skeleton_group_header, parent, false);
                return new SkeletonHeaderViewHolder(v);
            }
            if (viewType == SkeletonStemItem.TYPE) {
                View v = inflater.inflate(R.layout.row_skeleton_stem, parent, false);
                return new SkeletonStemViewHolder(v);
            }
            View v = inflater.inflate(R.layout.row_stem, parent, false);
            return new StemViewHolder(v);
        }

        @Override
        public void onBindViewHolder(RecyclerView.ViewHolder holder, int position) {
            QueueItem qi = items.get(position);
            if (qi instanceof GroupHeaderItem) {
                ((GroupHeaderViewHolder) holder).bind((GroupHeaderItem) qi, onHeaderClick);
            } else if (qi instanceof StemItem) {
                ((StemViewHolder) holder).bind((StemItem) qi, onStemClick);
            } else if (qi instanceof SkeletonHeaderItem) {
                ((SkeletonHeaderViewHolder) holder).bind((SkeletonHeaderItem) qi);
            } else if (qi instanceof SkeletonStemItem) {
                ((SkeletonStemViewHolder) holder).bind((SkeletonStemItem) qi);
            }
        }

        @Override
        public int getItemCount() {
            return items.size();
        }
    }

    static final class GroupHeaderViewHolder extends RecyclerView.ViewHolder {
        private final TextView title;
        private final TextView counts;
        private final ImageView chevron;
        private final MaterialCardView card;

        GroupHeaderViewHolder(View itemView) {
            super(itemView);
            card = (itemView instanceof MaterialCardView) ? (MaterialCardView) itemView : null;
            title = itemView.findViewById(R.id.groupRowTitle);
            counts = itemView.findViewById(R.id.groupRowCounts);
            chevron = itemView.findViewById(R.id.groupRowChevron);
        }

        void bind(GroupHeaderItem header, OnGroupHeaderClick onHeaderClick) {
            title.setText(header.title);
            counts.setText("Stems: " + header.stemsCount + "   Pending: " + header.pending + "   Done: " + header.done);
            if (chevron != null) {
                float target = header.expanded ? 90f : 0f;
                chevron.animate().rotation(target).setDuration(160).start();
            }

            // Make header look like the top of a connected accordion panel.
            if (card != null) {
                float r = dp(itemView, 16);
                ShapeAppearanceModel.Builder b = card.getShapeAppearanceModel().toBuilder();
                b.setTopLeftCornerSize(r);
                b.setTopRightCornerSize(r);
                b.setBottomLeftCornerSize(header.expanded ? 0f : r);
                b.setBottomRightCornerSize(header.expanded ? 0f : r);
                card.setShapeAppearanceModel(b.build());
            }

            itemView.setOnClickListener(v -> onHeaderClick.onClick(header));
        }
    }

    static final class StemViewHolder extends RecyclerView.ViewHolder {
        private final TextView stemText;
        private final TextView countsText;
        private final View divider;
        private final MaterialCardView card;
        private final ImageView doneIcon;

        StemViewHolder(View itemView) {
            super(itemView);
            card = (itemView instanceof MaterialCardView) ? (MaterialCardView) itemView : null;
            stemText = itemView.findViewById(R.id.rowStemText);
            countsText = itemView.findViewById(R.id.rowCountsText);
            divider = itemView.findViewById(R.id.rowDivider);
            doneIcon = itemView.findViewById(R.id.rowDoneIcon);
        }

        void bind(StemItem item, OnStemClick onClick) {
            stemText.setText(item.stem);
            countsText.setText("Pending: " + item.pending + "   Done: " + item.done);

            if (doneIcon != null) {
                boolean completed = item.pending == 0 && item.done > 0;
                doneIcon.setVisibility(completed ? View.VISIBLE : View.GONE);
            }

            // Connected panel: only the last stem gets rounded bottom corners.
            if (card != null) {
                float r = dp(itemView, 16);
                ShapeAppearanceModel.Builder b = card.getShapeAppearanceModel().toBuilder();
                b.setTopLeftCornerSize(0f);
                b.setTopRightCornerSize(0f);
                b.setBottomLeftCornerSize(item.isLastInGroup ? r : 0f);
                b.setBottomRightCornerSize(item.isLastInGroup ? r : 0f);
                card.setShapeAppearanceModel(b.build());
            }

            if (divider != null) {
                divider.setVisibility(item.isLastInGroup ? View.GONE : View.VISIBLE);
            }

            // Add a small gap after the last item so sections separate.
            ViewGroup.LayoutParams lp = itemView.getLayoutParams();
            if (lp instanceof ViewGroup.MarginLayoutParams) {
                ViewGroup.MarginLayoutParams mlp = (ViewGroup.MarginLayoutParams) lp;
                mlp.bottomMargin = item.isLastInGroup ? (int) dp(itemView, 10) : 0;
                itemView.setLayoutParams(mlp);
            }

            itemView.setOnClickListener(v -> onClick.onClick(item));
        }
    }

    static final class SkeletonHeaderViewHolder extends RecyclerView.ViewHolder {
        SkeletonHeaderViewHolder(View itemView) {
            super(itemView);
        }

        void bind(SkeletonHeaderItem item) {
            // Shimmer auto-starts via XML.
        }
    }

    static final class SkeletonStemViewHolder extends RecyclerView.ViewHolder {
        private final View divider;

        SkeletonStemViewHolder(View itemView) {
            super(itemView);
            divider = itemView.findViewById(R.id.skStemDivider);
        }

        void bind(SkeletonStemItem item) {
            if (divider != null) {
                divider.setVisibility(item.isLastInSection ? View.GONE : View.VISIBLE);
            }

            ViewGroup.LayoutParams lp = itemView.getLayoutParams();
            if (lp instanceof ViewGroup.MarginLayoutParams) {
                ViewGroup.MarginLayoutParams mlp = (ViewGroup.MarginLayoutParams) lp;
                mlp.bottomMargin = item.isLastInSection ? (int) dp(itemView, 10) : 0;
                itemView.setLayoutParams(mlp);
            }
        }
    }

    private static float dp(View v, float dp) {
        return dp * v.getResources().getDisplayMetrics().density;
    }

    private static final class CachedQueue {
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
        List<GroupBucket> buckets;
        Map<String, Boolean> expandedByGroupKey;

        boolean isFreshFor(QueueActivity a) {
            if (a == null) return false;
            long bm = a.getBundleMtime();
            long dm = a.getDecisionsMtime();
            return bm > 0 && bm == bundleMtime && dm == decisionsMtime;
        }
    }
}
