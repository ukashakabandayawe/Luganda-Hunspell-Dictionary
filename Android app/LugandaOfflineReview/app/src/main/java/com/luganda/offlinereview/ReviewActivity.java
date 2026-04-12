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

    private JSONObject bundle;
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

        stemIndex = getIntent().getIntExtra(QueueActivity.EXTRA_STEM_INDEX, -1);
        if (stemIndex < 0) {
            Toast.makeText(this, "Missing stem index", Toast.LENGTH_LONG).show();
            finish();
            return;
        }

        try {
            bundle = BundleStore.loadBundleJson(this);
            decisionMap = DecisionsStore.loadDecisionStatusMap(this);
        } catch (Exception ex) {
            Toast.makeText(this, "Failed to load bundle/decisions: " + ex, Toast.LENGTH_LONG).show();
            finish();
            return;
        }

        JSONObject stemObj = safeStemAt(stemIndex);
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
                    JSONObject payload = DecisionsStore.buildExportPayload(ReviewActivity.this, bundle);
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
        showNextPendingOrFirst();
    }

    private String getUsernameFromBundle() {
        if (bundle == null) return "reviewer";
        JSONObject user = bundle.optJSONObject("user");
        if (user == null) return "reviewer";
        String u = user.optString("username", "");
        if (u == null || u.trim().isEmpty()) return "reviewer";
        return u.trim();
    }

    private void showNextPendingOrFirst() {
        int pendingIdx = findNextPendingTaskIndex();
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
        int pendingCount = 0;
        for (int i = 0; i < tasks.length(); i++) {
            JSONObject t = tasks.optJSONObject(i);
            if (t == null) continue;
            String flag = t.optString("flag", "");
            String baseStatus = t.optString("status", "pending");
            String effective = effectiveStatus(stemText, flag, baseStatus);
            if ("pending".equals(effective)) {
                pendingCount++;
                return i;
            }
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

    private JSONObject safeStemAt(int index) {
        JSONArray stems = bundle.optJSONArray("stems");
        if (stems == null) return null;
        return stems.optJSONObject(index);
    }
}
