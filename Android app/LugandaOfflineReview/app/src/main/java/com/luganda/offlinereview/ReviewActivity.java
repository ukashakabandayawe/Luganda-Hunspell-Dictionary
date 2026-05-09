package com.luganda.offlinereview;

import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.google.android.material.appbar.MaterialToolbar;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.Map;

public class ReviewActivity extends AppCompatActivity {

    private BundleStore.BundleHeader bundleHeader;
    private Map<String, Map<String, String>> decisionMap;

    private int stemIndex;
    private String stemText;
    private JSONArray tasks;

    private TextView stemTitle;
    private TextView flagTitle;
    private TextView descText;
    private TextView examplesText;
    private TextView progressText;
    private EditText noteEdit;

    private Button prevBtn;
    private Button nextBtn;

    private int currentTaskIndex = -1;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_review);

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

        Button approveBtn = findViewById(R.id.btnApprove);
        Button rejectBtn = findViewById(R.id.btnReject);
        prevBtn = findViewById(R.id.btnPrevTask);
        nextBtn = findViewById(R.id.btnNextTask);

        stemIndex = getIntent().getIntExtra(QueueActivity.EXTRA_STEM_INDEX, -1);
        if (stemIndex < 0) {
            Toast.makeText(this, "Missing stem index", Toast.LENGTH_LONG).show();
            finish();
            return;
        }

        try {
            bundleHeader = BundleStore.readBundleHeader(this);
            decisionMap = DecisionsStore.loadDecisionStatusMap(this);
        } catch (Exception ex) {
            Toast.makeText(this, "Failed to load bundle/decisions: " + ex, Toast.LENGTH_LONG).show();
            finish();
            return;
        }

        JSONObject stemObj;
        try {
            stemObj = BundleStore.loadStemAtIndex(this, stemIndex);
        } catch (Exception ex) {
            Toast.makeText(this, "Failed to load stem from bundle: " + ex, Toast.LENGTH_LONG).show();
            finish();
            return;
        }
        if (stemObj == null) {
            Toast.makeText(this, "Stem not found in bundle", Toast.LENGTH_LONG).show();
            finish();
            return;
        }

        stemText = stemObj.optString("stem", "");
        tasks = stemObj.optJSONArray("tasks");
        if (tasks == null) tasks = new JSONArray();

        stemTitle.setText(stemText);

        if (getSupportActionBar() != null) {
            getSupportActionBar().setTitle(stemText);
        }

        approveBtn.setOnClickListener(v -> onDecide("approved"));
        rejectBtn.setOnClickListener(v -> onDecide("rejected"));
        prevBtn.setOnClickListener(v -> goPrevTask());
        nextBtn.setOnClickListener(v -> goNextTask());

        showNextPendingOrFirst();
    }

    @Override
    public boolean onSupportNavigateUp() {
        finish();
        return true;
    }

    private void onDecide(String decision) {
        if (currentTaskIndex < 0 || currentTaskIndex >= tasks.length()) {
            Toast.makeText(this, "No task selected", Toast.LENGTH_SHORT).show();
            return;
        }
        JSONObject t = tasks.optJSONObject(currentTaskIndex);
        if (t == null) return;
        String flag = t.optString("flag", "");
        if (flag.isEmpty()) return;

        String note = noteEdit.getText() == null ? "" : noteEdit.getText().toString();

        try {
            DecisionsStore.upsertDecision(this, stemText, flag, decision, note);
            decisionMap = DecisionsStore.loadDecisionStatusMap(this);
            noteEdit.setText("");
        } catch (Exception ex) {
            Toast.makeText(this, "Failed saving decision: " + ex, Toast.LENGTH_LONG).show();
            return;
        }

        if (BackupFolderStore.isConfigured(this)) {
            final String username = getUsernameFromBundle();
            new Thread(() -> {
                try {
                    JSONObject payload = DecisionsStore.buildExportPayload(ReviewActivity.this, bundleHeader == null ? null : bundleHeader.toUserJson());
                    DriveBackupWriter.writeDecisionsBackup(ReviewActivity.this, username, payload);
                } catch (Exception ex) {
                    runOnUiThread(() -> Toast.makeText(
                            ReviewActivity.this,
                            "Backup failed: " + ex.getMessage(),
                            Toast.LENGTH_LONG
                    ).show());
                }
            }).start();
        }

        Toast.makeText(this, decision.toUpperCase() + " saved", Toast.LENGTH_SHORT).show();

        // If this was the last pending flag for the stem, return to the queue.
        // (Avoid looping back to the first flag.)
        if (findNextPendingTaskIndex() < 0) {
            Toast.makeText(this, "Stem complete", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }

        showNextPendingOrFirst();
    }

    private String getUsernameFromBundle() {
        if (bundleHeader == null) return "reviewer";
        String u = bundleHeader.username;
        if (u == null || u.trim().isEmpty()) return "reviewer";
        return u.trim();
    }

    private void showNextPendingOrFirst() {
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
        descText.setText(desc);

        StringBuilder sb = new StringBuilder();
        if (examples != null) {
            for (int i = 0; i < examples.length(); i++) {
                String w = examples.optString(i, "");
                if (w == null || w.isEmpty()) continue;
                sb.append(w).append("\n");
            }
        }
        examplesText.setText(sb.toString().trim());

        // Preload note (if this task was already decided before)
        try {
            JSONObject row = DecisionsStore.findDecisionRow(this, stemText, flag);
            String note = row == null ? "" : row.optString("note", "");
            noteEdit.setText(note == null ? "" : note);
        } catch (Exception ex) {
            noteEdit.setText("");
        }

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

}
