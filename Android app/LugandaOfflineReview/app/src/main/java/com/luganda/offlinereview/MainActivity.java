package com.luganda.offlinereview;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.progressindicator.LinearProgressIndicator;
import com.luganda.offlinereview.ui.DonutProgressView;
import org.json.JSONObject;

import java.text.DateFormat;
import java.util.Date;

import java.io.OutputStream;

public class MainActivity extends AppCompatActivity {

    private static final int REQ_IMPORT_BUNDLE = 1001;
    private static final int REQ_EXPORT_DECISIONS = 1002;
    private static final int REQ_EXPORT_DIC = 1003;
    private static final int REQ_PICK_BACKUP_FOLDER = 1004;

    private TextView status;
    private TextView progress;
    private TextView backupStatus;
    private LinearProgressIndicator backupProgressBar;
    private TextView backupProgressText;
    private TextView userName;
    private TextView statStems;
    private TextView statPending;
    private TextView statDecided;

    private View headerLoader;

    private DonutProgressView progressDonut;
    private TextView legendActiveValue;
    private TextView legendInactiveValue;
    private TextView legendDraftsValue;

    private String lastHandledIncomingUri;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home);
        Watchdog.start(this);

        if (savedInstanceState != null) {
            lastHandledIncomingUri = savedInstanceState.getString("lastHandledIncomingUri", null);
        }

        MaterialToolbar toolbar = findViewById(R.id.homeToolbar);
        setSupportActionBar(toolbar);

        status = findViewById(R.id.homeStatus);
        progress = findViewById(R.id.homeProgress);
        backupStatus = findViewById(R.id.homeBackupStatus);
        backupProgressBar = findViewById(R.id.homeBackupProgressBar);
        backupProgressText = findViewById(R.id.homeBackupProgressText);
        userName = findViewById(R.id.homeUserName);
        statStems = findViewById(R.id.homeStatStems);
        statPending = findViewById(R.id.homeStatPending);
        statDecided = findViewById(R.id.homeStatDecided);

        headerLoader = findViewById(R.id.homeHeaderLoader);

        progressDonut = findViewById(R.id.homeProgressDonut);
        legendActiveValue = findViewById(R.id.homeLegendActiveValue);
        legendInactiveValue = findViewById(R.id.homeLegendInactiveValue);
        legendDraftsValue = findViewById(R.id.homeLegendDraftsValue);

        android.view.View btnImport = findViewById(R.id.btnImportBundle);
        android.view.View btnQueue = findViewById(R.id.btnOpenQueue);
        android.view.View btnExportDecisions = findViewById(R.id.btnExportDecisions);
        android.view.View btnExportDic = findViewById(R.id.btnExportDic);
        android.view.View btnSetBackupFolder = findViewById(R.id.btnSetBackupFolder);
        android.view.View btnBackupNow = findViewById(R.id.btnBackupNow);

        btnImport.setOnClickListener(v -> startImportBundle());
        btnQueue.setOnClickListener(v -> openQueue());
        btnExportDecisions.setOnClickListener(v -> startExportDecisions());
        btnExportDic.setOnClickListener(v -> startExportDic());
        btnSetBackupFolder.setOnClickListener(v -> pickBackupFolder());
        if (btnBackupNow != null) btnBackupNow.setOnClickListener(v -> runManualBackupNow());

        refreshUi();

        // If the app was opened from WhatsApp/Files with a bundle, import it automatically.
        handleIncomingIntent(getIntent());
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        handleIncomingIntent(intent);
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        outState.putString("lastHandledIncomingUri", lastHandledIncomingUri);
        super.onSaveInstanceState(outState);
    }

    @Override
    protected void onResume() {
        super.onResume();
        refreshUi();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        Watchdog.stop();
    }

    private void handleIncomingIntent(Intent intent) {
        if (intent == null) return;

        final String action = intent.getAction();
        Uri tempUri = null;

        if (Intent.ACTION_VIEW.equals(action)) {
            tempUri = intent.getData();
        } else if (Intent.ACTION_SEND.equals(action)) {
            try {
                tempUri = intent.getParcelableExtra(Intent.EXTRA_STREAM);
            } catch (Throwable ignored) {
                tempUri = null;
            }
        }

        if (tempUri == null) return;
        final Uri uri = tempUri;

        final String uriKey = uri.toString();
        if (uriKey.equals(lastHandledIncomingUri)) return;
        lastHandledIncomingUri = uriKey;

        Toast.makeText(this, "Importing bundle...", Toast.LENGTH_SHORT).show();
        new Thread(() -> {
            try {
                BundleStore.importBundle(MainActivity.this, uri);
                runOnUiThread(() -> {
                    Toast.makeText(MainActivity.this, "Bundle imported", Toast.LENGTH_SHORT).show();
                    refreshUi();
                });
            } catch (Throwable ex) {
                runOnUiThread(() -> Toast.makeText(
                        MainActivity.this,
                        "Import failed: " + (ex.getMessage() == null ? ex.toString() : ex.getMessage()),
                        Toast.LENGTH_LONG
                ).show());
            }
        }).start();
    }

    private void refreshUi() {
        boolean hasBundle = BundleStore.hasBundle(this);
        final String dicProblem = getEmbeddedDicProblem();

        if (userName != null) userName.setText("Reviewer");
        if (statStems != null) statStems.setText("-");
        if (statPending != null) statPending.setText("-");
        if (statDecided != null) statDecided.setText("-");

        if (progressDonut != null) progressDonut.setValues(0, 0, 0);
        if (legendActiveValue != null) legendActiveValue.setText("-");
        if (legendInactiveValue != null) legendInactiveValue.setText("-");
        if (legendDraftsValue != null) legendDraftsValue.setText("-");

        setHeaderLoading(false);
        setHeaderStatusText(null);

        if (!hasBundle) {
            setHeaderLoading(false);
            if (dicProblem != null) {
                setHeaderStatusText("No review bundle imported yet.\n" + dicProblem);
            } else {
                setHeaderStatusText("No review bundle imported yet.");
            }
            progress.setText("Import a bundle to see progress.");
            refreshBackupUi();
            return;
        }

        // Keep the dashboard visible without a loading message; refresh happens in the background.
        setHeaderLoading(false);
        if (dicProblem != null) {
            setHeaderStatusText(dicProblem);
        } else {
            setHeaderStatusText(null);
        }

        progress.setText(" ");
        refreshBackupUi();

        new Thread(() -> {
            try {
                BundleStore.BundleHeader header = BundleStore.readBundleHeader(MainActivity.this);
                java.util.Map<String, java.util.Map<String, String>> decisionMap = DecisionsStore.loadDecisionStatusMap(MainActivity.this);
                BundleStore.ProgressSummary sum = BundleStore.computeProgress(MainActivity.this, decisionMap);

                String username = header.username == null ? "" : header.username;
                String who = username.isEmpty() ? "(unknown)" : username;

                int active = sum.approved;
                int inactive = sum.rejected;
                int drafts = sum.pending;

                runOnUiThread(() -> {
                    if (userName != null) userName.setText(who);

                    if (dicProblem != null) {
                        setHeaderStatusText(dicProblem);
                    } else {
                        setHeaderStatusText(null);
                    }
                    setHeaderLoading(false);

                    if (statStems != null) statStems.setText(String.valueOf(sum.stems));
                    if (statPending != null) statPending.setText(String.valueOf(sum.pending));
                    if (statDecided != null) statDecided.setText(String.valueOf(sum.decided));

                        if (progressDonut != null) progressDonut.setValues(active, inactive, drafts);
                        if (legendActiveValue != null) legendActiveValue.setText(String.valueOf(active));
                        if (legendInactiveValue != null) legendInactiveValue.setText(String.valueOf(inactive));
                        if (legendDraftsValue != null) legendDraftsValue.setText(String.valueOf(drafts));

                        progress.setText("Tasks: " + sum.decided + "/" + sum.tasks);
                    refreshBackupUi();
                });
            } catch (Throwable ex) {
                runOnUiThread(() -> {
                    setHeaderLoading(false);
                    if (dicProblem != null) {
                        setHeaderStatusText("Failed to load bundle: " + ex + "\n" + dicProblem);
                    } else {
                        setHeaderStatusText("Failed to load bundle: " + ex);
                    }
                    progress.setText("Progress: error");
                    refreshBackupUi();
                });
            }
        }).start();
    }

    private String getEmbeddedDicProblem() {
        try {
            String firstLine;
            try (java.io.BufferedReader reader = new java.io.BufferedReader(
                    new java.io.InputStreamReader(getAssets().open("Luganda.dic"), java.nio.charset.StandardCharsets.UTF_8)
            )) {
                firstLine = reader.readLine();
            }
            if (firstLine == null || firstLine.trim().isEmpty()) {
                return "Embedded Luganda.dic is empty";
            }
            return null;
        } catch (Exception ex) {
            return "Missing embedded Luganda.dic: " + ex;
        }
    }

    private void setHeaderLoading(boolean isLoading) {
        if (headerLoader != null) {
            headerLoader.setVisibility(isLoading ? View.VISIBLE : View.GONE);
        }
    }

    private void setHeaderStatusText(String text) {
        if (status == null) return;
        if (text == null || text.trim().isEmpty()) {
            status.setText("");
            status.setVisibility(View.GONE);
            return;
        }

        status.setText(text);
        status.setVisibility(View.VISIBLE);
    }

    private void refreshBackupUi() {
        if (backupStatus == null) return;
        if (!BackupFolderStore.isConfigured(this)) {
            backupStatus.setText("Auto-backup: OFF");
            return;
        }

        String username = "reviewer";
        if (BundleStore.hasBundle(this)) {
            try {
                BundleStore.BundleHeader header = BundleStore.readBundleHeader(this);
                if (header != null && header.username != null && !header.username.trim().isEmpty()) {
                    username = header.username.trim();
                }
            } catch (Exception ignored) {
                // Keep default.
            }
        }

        long lastMs = DriveBackupWriter.getLastBackupTimeMillis(this, username);
        String lastText;
        if (lastMs <= 0L) {
            lastText = "Last backup: —";
        } else {
            DateFormat df = DateFormat.getDateTimeInstance(DateFormat.MEDIUM, DateFormat.SHORT);
            lastText = "Last backup: " + df.format(new Date(lastMs));
        }

        backupStatus.setText("Auto-backup: ON (decisions + .dic)\n" + lastText);
    }

    private void runManualBackupNow() {
        if (!BackupFolderStore.isConfigured(this)) {
            Toast.makeText(this, "Set a backup folder first", Toast.LENGTH_SHORT).show();
            return;
        }
        if (!BundleStore.hasBundle(this)) {
            Toast.makeText(this, "Import a bundle first", Toast.LENGTH_SHORT).show();
            return;
        }

        if (backupProgressBar != null) {
            backupProgressBar.setIndeterminate(false);
            backupProgressBar.setProgressCompat(0, false);
            backupProgressBar.setVisibility(View.VISIBLE);
        }
        if (backupProgressText != null) {
            backupProgressText.setText("Backup: 0%");
            backupProgressText.setVisibility(View.VISIBLE);
        }

        new Thread(() -> {
            try {
                BundleStore.BundleHeader header = BundleStore.readBundleHeader(MainActivity.this);
                String username = (header == null || header.username == null) ? "reviewer" : header.username.trim();
                if (username.isEmpty()) username = "reviewer";

                JSONObject payload = DecisionsStore.buildExportPayload(MainActivity.this, header == null ? null : header.toUserJson());
                DriveBackupWriter.writeAllBackups(MainActivity.this, username, payload, (percent, label) -> {
                    runOnUiThread(() -> {
                        if (backupProgressBar != null) {
                            backupProgressBar.setIndeterminate(false);
                            backupProgressBar.setProgressCompat(percent, true);
                        }
                        if (backupProgressText != null) {
                            if (label == null || label.trim().isEmpty()) {
                                backupProgressText.setText("Backup: " + percent + "%");
                            } else {
                                backupProgressText.setText(label + ": " + percent + "%");
                            }
                        }
                    });
                });

                runOnUiThread(() -> {
                    Toast.makeText(MainActivity.this, "Backup complete", Toast.LENGTH_SHORT).show();
                    if (backupProgressBar != null) backupProgressBar.setVisibility(View.GONE);
                    if (backupProgressText != null) backupProgressText.setVisibility(View.GONE);
                    refreshBackupUi();
                });
            } catch (Exception ex) {
                runOnUiThread(() -> {
                    if (backupProgressBar != null) backupProgressBar.setVisibility(View.GONE);
                    if (backupProgressText != null) backupProgressText.setVisibility(View.GONE);
                    Toast.makeText(MainActivity.this, "Backup failed: " + ex.getMessage(), Toast.LENGTH_LONG).show();
                });
            }
        }, "manual-backup").start();
    }

    private void startImportBundle() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        String[] mimeTypes = new String[]{"application/zip", "application/gzip", "application/x-gzip", "application/json", "application/octet-stream"};
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
            BundleStore.BundleHeader header = BundleStore.readBundleHeader(this);
            if (header.username != null && !header.username.trim().isEmpty()) username = header.username.trim();
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
            BundleStore.BundleHeader header = BundleStore.readBundleHeader(this);
            if (header.username != null && !header.username.trim().isEmpty()) username = header.username.trim();
        } catch (Exception ignored) {}

        Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("text/plain");
        intent.putExtra(Intent.EXTRA_TITLE, "Luganda_" + username + ".dic");
        startActivityForResult(intent, REQ_EXPORT_DIC);
    }

    private void pickBackupFolder() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        intent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
        intent.addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
        intent.addFlags(Intent.FLAG_GRANT_PREFIX_URI_PERMISSION);
        startActivityForResult(intent, REQ_PICK_BACKUP_FOLDER);
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
                BundleStore.BundleHeader header = BundleStore.readBundleHeader(this);
                JSONObject payload = DecisionsStore.buildExportPayload(this, header.toUserJson());
                try (OutputStream os = getContentResolver().openOutputStream(uri)) {
                    if (os == null) throw new IllegalStateException("Could not open output");
                    os.write(payload.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
                }
                Toast.makeText(this, "Decisions exported", Toast.LENGTH_SHORT).show();
            } else if (requestCode == REQ_EXPORT_DIC) {
                BundleStore.BundleHeader header = BundleStore.readBundleHeader(this);
                JSONObject payload = DecisionsStore.buildExportPayload(this, header.toUserJson());
                try (OutputStream os = getContentResolver().openOutputStream(uri)) {
                    if (os == null) throw new IllegalStateException("Could not open output");
                    DicExporter.exportWorkingDic(this, os, payload);
                }
                Toast.makeText(this, "Working .dic exported", Toast.LENGTH_SHORT).show();
            } else if (requestCode == REQ_PICK_BACKUP_FOLDER) {
                int flags = data.getFlags();
                int takeFlags = flags & (Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
                try {
                    getContentResolver().takePersistableUriPermission(uri, takeFlags);
                } catch (SecurityException ex) {
                    // Continue anyway; if persist fails, backup may stop working after reboot.
                }
                BackupFolderStore.setTreeUri(this, uri);
                Toast.makeText(this, "Backup folder set", Toast.LENGTH_SHORT).show();
                refreshBackupUi();
            }
        } catch (Exception ex) {
            Toast.makeText(this, "Operation failed: " + ex, Toast.LENGTH_LONG).show();
        }
    }
}

