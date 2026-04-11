package com.luganda.offlinereview;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.google.android.material.appbar.MaterialToolbar;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.OutputStream;

public class MainActivity extends AppCompatActivity {

    private static final int REQ_IMPORT_BUNDLE = 1001;
    private static final int REQ_EXPORT_DECISIONS = 1002;
    private static final int REQ_EXPORT_DIC = 1003;

    private TextView status;
    private TextView progress;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home);

        MaterialToolbar toolbar = findViewById(R.id.homeToolbar);
        setSupportActionBar(toolbar);

        status = findViewById(R.id.homeStatus);
        progress = findViewById(R.id.homeProgress);
        Button btnImport = findViewById(R.id.btnImportBundle);
        Button btnQueue = findViewById(R.id.btnOpenQueue);
        Button btnExportDecisions = findViewById(R.id.btnExportDecisions);
        Button btnExportDic = findViewById(R.id.btnExportDic);

        btnImport.setOnClickListener(v -> startImportBundle());
        btnQueue.setOnClickListener(v -> openQueue());
        btnExportDecisions.setOnClickListener(v -> startExportDecisions());
        btnExportDic.setOnClickListener(v -> startExportDic());

        refreshUi();
    }

    @Override
    protected void onResume() {
        super.onResume();
        refreshUi();
    }

    private void refreshUi() {
        boolean hasBundle = BundleStore.hasBundle(this);
        String dicOk;
        try {
            String firstLine = new java.io.BufferedReader(
                    new java.io.InputStreamReader(getAssets().open("Luganda.dic"), java.nio.charset.StandardCharsets.UTF_8)
            ).readLine();
            dicOk = "Embedded Luganda.dic OK (first line: " + firstLine + ")";
        } catch (Exception ex) {
            dicOk = "Missing embedded Luganda.dic: " + ex;
        }

        if (!hasBundle) {
            status.setText(dicOk + "\n\nNo review bundle imported yet.");
            progress.setText("Progress: (import a bundle)");
            return;
        }

        try {
            JSONObject bundle = BundleStore.loadBundleJson(this);
            JSONObject user = bundle.optJSONObject("user");
            String username = user != null ? user.optString("username", "") : "";
            status.setText(dicOk + "\n\nBundle loaded for: " + (username.isEmpty() ? "(unknown)" : username));

            JSONArray stems = bundle.optJSONArray("stems");
            int stemsCount = stems == null ? 0 : stems.length();
            int totalTasks = 0;
            int pending = 0;
            int decided = 0;

            java.util.Map<String, java.util.Map<String, String>> decisionMap = DecisionsStore.loadDecisionStatusMap(this);

            if (stems != null) {
                for (int i = 0; i < stems.length(); i++) {
                    JSONObject s = stems.optJSONObject(i);
                    if (s == null) continue;
                    String stemText = s.optString("stem", "");
                    JSONArray tasks = s.optJSONArray("tasks");
                    if (tasks == null) continue;
                    for (int j = 0; j < tasks.length(); j++) {
                        JSONObject t = tasks.optJSONObject(j);
                        if (t == null) continue;
                        totalTasks++;
                        String flag = t.optString("flag", "");
                        String baseStatus = t.optString("status", "pending");
                        String eff = baseStatus;
                        java.util.Map<String, String> byFlag = decisionMap.get(stemText);
                        if (byFlag != null) {
                            String d = byFlag.get(flag);
                            if (d != null) {
                                String dl = d.trim().toLowerCase();
                                if (dl.equals("approved") || dl.equals("approve")) eff = "approved";
                                else if (dl.equals("rejected") || dl.equals("reject")) eff = "rejected";
                            }
                        }
                        if ("pending".equals(eff)) pending++;
                        else decided++;
                    }
                }
            }

            progress.setText(
                    "Progress:\n" +
                    "Stems: " + stemsCount + "\n" +
                    "Tasks: " + totalTasks + "\n" +
                    "Pending: " + pending + "\n" +
                    "Decided: " + decided
            );
        } catch (Exception ex) {
            status.setText(dicOk + "\n\nFailed to load bundle: " + ex);
            progress.setText("Progress: error");
        }
    }

    private void startImportBundle() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        String[] mimeTypes = new String[]{"application/gzip", "application/x-gzip", "application/json", "application/octet-stream"};
        intent.putExtra(Intent.EXTRA_MIME_TYPES, mimeTypes);
        startActivityForResult(intent, REQ_IMPORT_BUNDLE);
    }

    private void openQueue() {
        if (!BundleStore.hasBundle(this)) {
            Toast.makeText(this, "Import a bundle first", Toast.LENGTH_SHORT).show();
            return;
        }
        startActivity(new Intent(this, QueueActivity.class));
    }

    private void startExportDecisions() {
        if (!BundleStore.hasBundle(this)) {
            Toast.makeText(this, "Import a bundle first", Toast.LENGTH_SHORT).show();
            return;
        }
        String username = "reviewer";
        try {
            JSONObject bundle = BundleStore.loadBundleJson(this);
            JSONObject user = bundle.optJSONObject("user");
            if (user != null) {
                String u = user.optString("username", "");
                if (!u.isEmpty()) username = u;
            }
        } catch (Exception ignored) {}

        Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("application/json");
        intent.putExtra(Intent.EXTRA_TITLE, "decisions_" + username + ".json");
        startActivityForResult(intent, REQ_EXPORT_DECISIONS);
    }

    private void startExportDic() {
        if (!BundleStore.hasBundle(this)) {
            Toast.makeText(this, "Import a bundle first", Toast.LENGTH_SHORT).show();
            return;
        }
        String username = "reviewer";
        try {
            JSONObject bundle = BundleStore.loadBundleJson(this);
            JSONObject user = bundle.optJSONObject("user");
            if (user != null) {
                String u = user.optString("username", "");
                if (!u.isEmpty()) username = u;
            }
        } catch (Exception ignored) {}

        Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("text/plain");
        intent.putExtra(Intent.EXTRA_TITLE, "Luganda_" + username + ".dic");
        startActivityForResult(intent, REQ_EXPORT_DIC);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (resultCode != RESULT_OK || data == null) return;

        Uri uri = data.getData();
        if (uri == null) return;

        try {
            if (requestCode == REQ_IMPORT_BUNDLE) {
                BundleStore.importBundle(this, uri);
                Toast.makeText(this, "Bundle imported", Toast.LENGTH_SHORT).show();
                refreshUi();
            } else if (requestCode == REQ_EXPORT_DECISIONS) {
                JSONObject bundle = BundleStore.loadBundleJson(this);
                JSONObject payload = DecisionsStore.buildExportPayload(this, bundle);
                try (OutputStream os = getContentResolver().openOutputStream(uri)) {
                    if (os == null) throw new IllegalStateException("Could not open output");
                    os.write(payload.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
                }
                Toast.makeText(this, "Decisions exported", Toast.LENGTH_SHORT).show();
            } else if (requestCode == REQ_EXPORT_DIC) {
                JSONObject bundle = BundleStore.loadBundleJson(this);
                JSONObject payload = DecisionsStore.buildExportPayload(this, bundle);
                try (OutputStream os = getContentResolver().openOutputStream(uri)) {
                    if (os == null) throw new IllegalStateException("Could not open output");
                    DicExporter.exportWorkingDic(this, os, payload);
                }
                Toast.makeText(this, "Working .dic exported", Toast.LENGTH_SHORT).show();
            }
        } catch (Exception ex) {
            Toast.makeText(this, "Operation failed: " + ex, Toast.LENGTH_LONG).show();
        }
    }
}
