package com.luganda.offlinereview;

import android.content.Intent;
import android.os.Bundle;
import android.os.Process;
import android.content.SharedPreferences;
import android.text.SpannableString;
import android.text.Spanned;
import android.text.style.ForegroundColorSpan;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewConfiguration;
import android.widget.ScrollView;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;

import com.google.android.material.appbar.MaterialToolbar;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class ReviewActivity extends AppCompatActivity {

    // Auto-backup policy: run a backup after completing N stems.
    private static final int AUTO_BACKUP_EVERY_N_STEMS = 3;
    private static final String PREFS_AUTO_BACKUP = "review_auto_backup";
    private static final String KEY_STEMS_SINCE_BACKUP_PREFIX = "stemsSinceBackup_";

    private static final Pattern[] HIGHLIGHT_PATTERNS = new Pattern[] {
            Pattern.compile("\\breflexive\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bimmediate[\\s-]+past\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bpresent[\\s-]+simple\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bpresent[\\s-]+progressive\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bpast\\b", Pattern.CASE_INSENSITIVE),
            Pattern.compile("\\bfuture\\b", Pattern.CASE_INSENSITIVE)
    };

    private CharSequence highlightKeywordsGreen(String text) {
        if (text == null || text.isEmpty()) return "";
        int color = ContextCompat.getColor(this, R.color.success_green);
        SpannableString s = new SpannableString(text);
        for (Pattern p : HIGHLIGHT_PATTERNS) {
            Matcher m = p.matcher(text);
            while (m.find()) {
                int start = m.start();
                int end = m.end();
                if (start >= 0 && end > start) {
                    s.setSpan(new ForegroundColorSpan(color), start, end, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
                }
            }
        }
        return s;
    }

    private BundleStore.BundleHeader bundleHeader;
    private Map<String, Map<String, String>> decisionMap;
    private Map<String, Map<String, String>> noteMap;

    private int stemIndex;
    private String stemText;
    private JSONArray tasks;

    private TextView stemTitle;
    private TextView flagTitle;
    private TextView descText;
    private TextView examplesText;
    private TextView progressText;
    private EditText noteEdit;
    private View loadingOverlay;
    private ScrollView reviewScroll;

    private Button approveBtn;
    private Button rejectBtn;
    private Button prevBtn;
    private Button nextBtn;

    private int currentTaskIndex = -1;
    private volatile boolean decisionSaveInFlight = false;
    private final Object backupLock = new Object();
    private boolean backupRunning = false;
    private boolean backupQueued = false;

    // When the reviewer navigates using Prev/Next, we keep them in sequential mode
    // so approving/rejecting doesn't jump to the next pending task elsewhere.
    private boolean manualNavigationMode = false;

    private float swipeDownX;
    private float swipeDownY;
    private int swipeMinDistancePx;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_review);
        Watchdog.start(this);

        swipeMinDistancePx = Math.max(90, ViewConfiguration.get(this).getScaledTouchSlop() * 3);

        MaterialToolbar toolbar = findViewById(R.id.reviewToolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }

        stemTitle = findViewById(R.id.reviewStem);
        flagTitle = findViewById(R.id.reviewFlag);
        descText = findViewById(R.id.reviewDescription);
        examplesText = findViewById(R.id.reviewExamples);
        progressText = findViewById(R.id.reviewProgress);
        noteEdit = findViewById(R.id.reviewNote);
        loadingOverlay = findViewById(R.id.reviewLoadingOverlay);

        approveBtn = findViewById(R.id.btnApprove);
        rejectBtn = findViewById(R.id.btnReject);
        prevBtn = findViewById(R.id.btnPrevTask);
        nextBtn = findViewById(R.id.btnNextTask);

        // Replace prev/next buttons with swipe.
        if (prevBtn != null) prevBtn.setVisibility(View.GONE);
        if (nextBtn != null) nextBtn.setVisibility(View.GONE);

        reviewScroll = findViewById(R.id.reviewScroll);
        if (reviewScroll != null) {
            reviewScroll.setOnTouchListener((v, event) -> handleSwipeTouch(event));
        }

        setLoadingState(true);

        stemIndex = getIntent().getIntExtra(QueueActivity.EXTRA_STEM_INDEX, -1);
        if (stemIndex < 0) {
            Toast.makeText(this, "Missing stem index", Toast.LENGTH_LONG).show();
            finish();
            return;
        }

        // Load bundle header, decisions and stem off the UI thread to avoid ANR on large bundles.
        new Thread(() -> {
            try {
                BundleStore.BundleHeader hdr = BundleStore.readBundleHeader(ReviewActivity.this);
                java.util.Map<String, java.util.Map<String, String>> dmap = DecisionsStore.loadDecisionStatusMap(ReviewActivity.this);
                java.util.Map<String, java.util.Map<String, String>> nmap = DecisionsStore.loadDecisionNoteMap(ReviewActivity.this);
                org.json.JSONObject stemObj = BundleStore.loadStemAtIndex(ReviewActivity.this, stemIndex);

                if (stemObj == null) {
                    runOnUiThread(() -> {
                        setLoadingState(false);
                        Toast.makeText(ReviewActivity.this, "Stem not found in bundle", Toast.LENGTH_LONG).show();
                        finish();
                    });
                    return;
                }

                // assign to fields then finish UI setup on main thread
                bundleHeader = hdr;
                decisionMap = dmap;
                noteMap = nmap;

                final org.json.JSONObject finalStem = stemObj;
                runOnUiThread(() -> {
                    stemText = finalStem.optString("stem", "");
                    tasks = finalStem.optJSONArray("tasks");
                    if (tasks == null) tasks = new org.json.JSONArray();

                    stemTitle.setText(stemText);
                    if (getSupportActionBar() != null) {
                        getSupportActionBar().setTitle(stemText);
                    }

                    approveBtn.setOnClickListener(v -> onDecide("approved"));
                    rejectBtn.setOnClickListener(v -> onDecide("rejected"));
                    // Buttons are hidden; keep behavior reachable by swipe.
                    prevBtn.setOnClickListener(v -> goPrevTask());
                    nextBtn.setOnClickListener(v -> goNextTask());

                    setLoadingState(false);
                    showNextPendingOrFirst();
                });
            } catch (Exception ex) {
                runOnUiThread(() -> {
                    setLoadingState(false);
                    Toast.makeText(ReviewActivity.this, "Failed to load bundle/decisions: " + ex, Toast.LENGTH_LONG).show();
                    finish();
                });
            }
        }, "review-load").start();
    }

    private boolean handleSwipeTouch(MotionEvent event) {
        if (event == null) return false;

        switch (event.getActionMasked()) {
            case MotionEvent.ACTION_DOWN:
                swipeDownX = event.getX();
                swipeDownY = event.getY();
                return false;
            case MotionEvent.ACTION_UP:
                float dx = event.getX() - swipeDownX;
                float dy = event.getY() - swipeDownY;

                if (Math.abs(dx) > swipeMinDistancePx && Math.abs(dx) > Math.abs(dy)) {
                    if (dx > 0) {
                        goPrevTask();
                    } else {
                        goNextTask();
                    }
                    return true;
                }
                return false;
            default:
                return false;
        }
    }

    @Override
    public boolean onSupportNavigateUp() {
        finishAndReturnQueueUpdate(computeStemCounts());
        return true;
    }

    @Override
    public void onBackPressed() {
        finishAndReturnQueueUpdate(computeStemCounts());
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        Watchdog.stop();
    }

    private void onDecide(String decision) {
        if (decisionSaveInFlight) {
            return;
        }
        if (currentTaskIndex < 0 || currentTaskIndex >= tasks.length()) {
            Toast.makeText(this, "No task selected", Toast.LENGTH_SHORT).show();
            return;
        }
        JSONObject t = tasks.optJSONObject(currentTaskIndex);
        if (t == null) return;
        String flag = t.optString("flag", "");
        if (flag.isEmpty()) return;

        String baseStatusBefore = t.optString("status", "pending");
        boolean wasPendingBefore = "pending".equals(effectiveStatus(stemText, flag, baseStatusBefore));

        String note = noteEdit.getText() == null ? "" : noteEdit.getText().toString();

        decisionSaveInFlight = true;
        setDecisionButtonsEnabled(false);

        new Thread(() -> {
            Exception saveError = null;
            int[] counts = null;
            boolean stemComplete = false;

            try {
                DecisionsStore.upsertDecision(ReviewActivity.this, stemText, flag, decision, note);
                applyDecisionToMemory(stemText, flag, decision, note);
                counts = computeStemCounts();
                stemComplete = wasPendingBefore && counts[0] == 0;
            } catch (Exception ex) {
                saveError = ex;
            }

            final Exception finalSaveError = saveError;
            final int[] finalCounts = counts;
            final boolean finalStemComplete = stemComplete;

            runOnUiThread(() -> {
                decisionSaveInFlight = false;
                setDecisionButtonsEnabled(true);

                if (finalSaveError != null) {
                    Toast.makeText(this, "Failed saving decision: " + finalSaveError, Toast.LENGTH_LONG).show();
                    return;
                }

                noteEdit.setText("");
                Toast.makeText(this, decision.toUpperCase() + " saved", Toast.LENGTH_SHORT).show();

                // If this was the last pending flag for the stem, return to the queue.
                // (Avoid looping back to the first flag.)
                if (finalStemComplete) {
                    if (BackupFolderStore.isConfigured(this)) {
                        String who = getUsernameFromBundle();
                        int completed = incrementCompletedStemsSinceBackup(who);
                        if (completed >= AUTO_BACKUP_EVERY_N_STEMS) {
                            resetCompletedStemsSinceBackup(who);
                            requestDriveBackupCoalesced(who);
                        }
                    }
                    Toast.makeText(this, "Stem complete", Toast.LENGTH_SHORT).show();
                    finishAndReturnQueueUpdate(finalCounts);
                    return;
                }

                if (manualNavigationMode) {
                    int before = currentTaskIndex;
                    goNextTask();
                    if (currentTaskIndex == before) {
                        // We stayed on the same task (likely end of list); refresh header/buttons.
                        bindTask(tasks.optJSONObject(currentTaskIndex));
                    }
                } else {
                    showNextPendingOrFirst();
                }
            });
        }).start();
    }

    private void setDecisionButtonsEnabled(boolean enabled) {
        if (approveBtn != null) approveBtn.setEnabled(enabled);
        if (rejectBtn != null) rejectBtn.setEnabled(enabled);
    }

    private void applyDecisionToMemory(String stem, String flag, String decision, String note) {
        if (stem == null || flag == null || decision == null) return;
        if (decisionMap == null) {
            decisionMap = new java.util.HashMap<>();
        }
        Map<String, String> byFlag = decisionMap.get(stem);
        if (byFlag == null) {
            byFlag = new java.util.HashMap<>();
            decisionMap.put(stem, byFlag);
        }
        byFlag.put(flag, decision);

        if (noteMap == null) {
            noteMap = new java.util.HashMap<>();
        }
        Map<String, String> noteByFlag = noteMap.get(stem);
        if (noteByFlag == null) {
            noteByFlag = new java.util.HashMap<>();
            noteMap.put(stem, noteByFlag);
        }
        noteByFlag.put(flag, note == null ? "" : note);
    }

    private String getUsernameFromBundle() {
        if (bundleHeader == null) return "reviewer";
        String u = bundleHeader.username;
        if (u == null || u.trim().isEmpty()) return "reviewer";
        return u.trim();
    }

    private int incrementCompletedStemsSinceBackup(String username) {
        String who = (username == null || username.trim().isEmpty()) ? "reviewer" : username.trim();
        SharedPreferences prefs = getSharedPreferences(PREFS_AUTO_BACKUP, MODE_PRIVATE);
        String key = KEY_STEMS_SINCE_BACKUP_PREFIX + who;
        int cur = prefs.getInt(key, 0);
        int next = cur + 1;
        prefs.edit().putInt(key, next).apply();
        return next;
    }

    private void resetCompletedStemsSinceBackup(String username) {
        String who = (username == null || username.trim().isEmpty()) ? "reviewer" : username.trim();
        SharedPreferences prefs = getSharedPreferences(PREFS_AUTO_BACKUP, MODE_PRIVATE);
        prefs.edit().putInt(KEY_STEMS_SINCE_BACKUP_PREFIX + who, 0).apply();
    }

    private void requestDriveBackupCoalesced(String username) {
        final String who = (username == null || username.trim().isEmpty()) ? "reviewer" : username.trim();

        boolean startWorker = false;
        synchronized (backupLock) {
            if (backupRunning) {
                backupQueued = true;
            } else {
                backupRunning = true;
                startWorker = true;
            }
        }
        if (!startWorker) return;

        new Thread(() -> {
            try {
                Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND);
            } catch (Throwable ignored) {}

            boolean rerun;
            do {
                try {
                    JSONObject payload = DecisionsStore.buildExportPayload(
                            ReviewActivity.this,
                            bundleHeader == null ? null : bundleHeader.toUserJson()
                    );
                    DriveBackupWriter.writeAllBackups(ReviewActivity.this, who, payload);
                } catch (Exception ex) {
                    runOnUiThread(() -> Toast.makeText(
                            ReviewActivity.this,
                            "Backup failed: " + ex.getMessage(),
                            Toast.LENGTH_LONG
                    ).show());
                }

                synchronized (backupLock) {
                    if (backupQueued) {
                        backupQueued = false;
                        rerun = true;
                    } else {
                        backupRunning = false;
                        rerun = false;
                    }
                }
            } while (rerun);
        }, "review-backup").start();
    }

    private void showNextPendingOrFirst() {
        manualNavigationMode = false;
        int pendingIdx = findNextPendingTaskIndexFrom(currentTaskIndex + 1);
        if (pendingIdx >= 0) {
            currentTaskIndex = pendingIdx;
            bindTask(tasks.optJSONObject(currentTaskIndex));
            return;
        }

        // No pending tasks left; show first task (read-only) if available.
        if (tasks.length() > 0) {
            currentTaskIndex = 0;
            bindTask(tasks.optJSONObject(currentTaskIndex));
            Toast.makeText(this, "No pending tasks for this stem", Toast.LENGTH_SHORT).show();
        } else {
            currentTaskIndex = -1;
            flagTitle.setText("No tasks");
            descText.setText("");
            examplesText.setText("");
        }
    }

    private void finishAndReturnQueueUpdate(int[] counts) {
        try {
            Intent data = new Intent();
            data.putExtra(QueueActivity.EXTRA_STEM_INDEX, stemIndex);
            data.putExtra(QueueActivity.EXTRA_RESULT_PENDING, counts[0]);
            data.putExtra(QueueActivity.EXTRA_RESULT_DONE, counts[1]);
            setResult(RESULT_OK, data);
        } catch (Throwable ignored) {
            // Best-effort; still allow navigation away.
        }
        finish();
    }

    private int[] computeStemCounts() {
        int pending = 0;
        int done = 0;
        if (tasks == null) return new int[]{0, 0};

        for (int i = 0; i < tasks.length(); i++) {
            JSONObject tt = tasks.optJSONObject(i);
            if (tt == null) continue;
            String ff = tt.optString("flag", "");
            String bs = tt.optString("status", "pending");
            String eff = effectiveStatus(stemText, ff, bs);
            if ("pending".equals(eff)) pending++;
            else done++;
        }
        return new int[]{pending, done};
    }

    private int findNextPendingTaskIndex() {
        return findNextPendingTaskIndexFrom(0);
    }

    private int findNextPendingTaskIndexFrom(int startIndex) {
        if (tasks == null) return -1;
        int n = tasks.length();
        if (n == 0) return -1;
        if (startIndex < 0) startIndex = 0;
        if (startIndex >= n) startIndex = 0;

        for (int i = startIndex; i < n; i++) {
            JSONObject t = tasks.optJSONObject(i);
            if (t == null) continue;
            String flag = t.optString("flag", "");
            String baseStatus = t.optString("status", "pending");
            String effective = effectiveStatus(stemText, flag, baseStatus);
            if ("pending".equals(effective)) return i;
        }
        for (int i = 0; i < startIndex; i++) {
            JSONObject t = tasks.optJSONObject(i);
            if (t == null) continue;
            String flag = t.optString("flag", "");
            String baseStatus = t.optString("status", "pending");
            String effective = effectiveStatus(stemText, flag, baseStatus);
            if ("pending".equals(effective)) return i;
        }
        return -1;
    }

    private void bindTask(JSONObject t) {
        if (t == null) return;
        String flag = t.optString("flag", "");
        String desc = t.optString("description", "");
        JSONArray examples = t.optJSONArray("examples");

        String baseStatus = t.optString("status", "pending");
        String effective = effectiveStatus(stemText, flag, baseStatus);

        flagTitle.setText(flag + "  (" + effective + ")");
        descText.setText(highlightKeywordsGreen(desc));

        StringBuilder sb = new StringBuilder();
        if (examples != null) {
            for (int i = 0; i < examples.length(); i++) {
                String w = examples.optString(i, "");
                if (w == null || w.isEmpty()) continue;
                sb.append(w).append("\n");
            }
        }
        examplesText.setText(sb.toString().trim());

        // Preload note from in-memory map to avoid disk I/O on the UI thread.
        noteEdit.setText(getDecisionNote(stemText, flag));

        // Progress line
        int pending = 0;
        int done = 0;
        for (int i = 0; i < tasks.length(); i++) {
            JSONObject tt = tasks.optJSONObject(i);
            if (tt == null) continue;
            String ff = tt.optString("flag", "");
            String bs = tt.optString("status", "pending");
            String eff = effectiveStatus(stemText, ff, bs);
            if ("pending".equals(eff)) pending++;
            else done++;
        }
        progressText.setText("Pending: " + pending + "   Done: " + done);

        refreshNavButtons(effective);
    }

    private void refreshNavButtons(String effectiveStatus) {
        if (prevBtn != null) {
            prevBtn.setEnabled(currentTaskIndex > 0);
        }
        if (nextBtn != null) {
            boolean hasNext = tasks != null && currentTaskIndex >= 0 && currentTaskIndex < (tasks.length() - 1);
            boolean mustDecide = "pending".equals(effectiveStatus);
            nextBtn.setEnabled(hasNext && !mustDecide);
        }
    }

    private void goPrevTask() {
        if (tasks == null || tasks.length() == 0) return;

        manualNavigationMode = true;

        int idx = currentTaskIndex;
        if (idx < 0) idx = 0;
        idx = idx - 1;
        while (idx >= 0) {
            JSONObject t = tasks.optJSONObject(idx);
            if (t != null) {
                currentTaskIndex = idx;
                bindTask(t);
                return;
            }
            idx--;
        }

        Toast.makeText(this, "Already at first group", Toast.LENGTH_SHORT).show();
    }

    private void goNextTask() {
        if (tasks == null || tasks.length() == 0) return;

        manualNavigationMode = true;

        if (currentTaskIndex >= 0 && currentTaskIndex < tasks.length()) {
            JSONObject cur = tasks.optJSONObject(currentTaskIndex);
            if (cur != null) {
                String flag = cur.optString("flag", "");
                String baseStatus = cur.optString("status", "pending");
                String effective = effectiveStatus(stemText, flag, baseStatus);
                if ("pending".equals(effective)) {
                    Toast.makeText(this, "Please approve/reject before going next", Toast.LENGTH_SHORT).show();
                    refreshNavButtons(effective);
                    return;
                }
            }
        }

        int idx = currentTaskIndex;
        if (idx < 0) idx = -1;
        idx = idx + 1;
        while (idx < tasks.length()) {
            JSONObject t = tasks.optJSONObject(idx);
            if (t != null) {
                currentTaskIndex = idx;
                bindTask(t);
                return;
            }
            idx++;
        }

        Toast.makeText(this, "Already at last group", Toast.LENGTH_SHORT).show();
    }

    private String effectiveStatus(String stem, String flag, String baseStatus) {
        if (decisionMap != null) {
            Map<String, String> byFlag = decisionMap.get(stem);
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

    private String getDecisionNote(String stem, String flag) {
        if (noteMap == null) return "";
        Map<String, String> byFlag = noteMap.get(stem);
        if (byFlag == null) return "";
        String n = byFlag.get(flag);
        return n == null ? "" : n;
    }

    private void setLoadingState(boolean loading) {
        if (loadingOverlay != null) {
            loadingOverlay.setVisibility(loading ? View.VISIBLE : View.GONE);
        }
        if (reviewScroll != null) {
            reviewScroll.setVisibility(loading ? View.INVISIBLE : View.VISIBLE);
        }
        if (progressText != null && loading) {
            progressText.setText("Loading stem...");
        }
    }

}
