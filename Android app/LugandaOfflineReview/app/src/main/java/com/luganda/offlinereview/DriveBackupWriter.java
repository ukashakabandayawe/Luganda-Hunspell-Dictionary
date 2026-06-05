package com.luganda.offlinereview;

import android.content.Context;
import android.net.Uri;

import androidx.documentfile.provider.DocumentFile;

import org.json.JSONObject;

import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import android.content.SharedPreferences;

public final class DriveBackupWriter {
    private DriveBackupWriter() {}

    public interface ProgressListener {
        void onProgress(int percent, String label);
    }

    private static final String PREFS_NAME = "drive_backup";
    private static final String LAST_BACKUP_MS_PREFIX = "lastBackupMs_";
    private static final String LAST_AUTO_DIC_BACKUP_MS_PREFIX = "lastAutoDicBackupMs_";

    private static String safeUser(String username) {
        if (username == null) return "reviewer";
        String trimmed = username.trim();
        return trimmed.isEmpty() ? "reviewer" : trimmed;
    }

    public static long getLastBackupTimeMillis(Context context, String username) {
        String user = safeUser(username);
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        return prefs.getLong(LAST_BACKUP_MS_PREFIX + user, 0L);
    }

    public static long getLastAutoDicBackupTimeMillis(Context context, String username) {
        String user = safeUser(username);
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        return prefs.getLong(LAST_AUTO_DIC_BACKUP_MS_PREFIX + user, 0L);
    }

    public static void recordBackupCompletedNow(Context context, String username) {
        String user = safeUser(username);
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        prefs.edit().putLong(LAST_BACKUP_MS_PREFIX + user, System.currentTimeMillis()).apply();
    }

    public static void recordAutoDicBackupCompletedNow(Context context, String username) {
        String user = safeUser(username);
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        prefs.edit().putLong(LAST_AUTO_DIC_BACKUP_MS_PREFIX + user, System.currentTimeMillis()).apply();
    }

    public static void writeDecisionsBackup(Context context, String username, JSONObject decisionsPayload) throws Exception {
        if (decisionsPayload == null) {
            throw new IllegalArgumentException("decisionsPayload is required");
        }

        DocumentFile folder = BackupFolderStore.getFolder(context);
        if (folder == null || !folder.exists() || !folder.isDirectory()) {
            throw new IllegalStateException("Backup folder not configured");
        }

        String user = safeUser(username);
        String fileName = "decisions_" + user + ".json";

        // Use active account subfolder when available.
        String acct = AccountManager.getActiveAccountId(context);
        DocumentFile targetFolder = folder;
        if (acct != null) {
            DocumentFile sub = folder.findFile(acct);
            if (sub == null || !sub.isDirectory()) {
                try { sub = folder.createDirectory(acct); } catch (Throwable ignored) { sub = null; }
            }
            if (sub != null && sub.isDirectory()) targetFolder = sub;
        }

        // Find or create file.
        DocumentFile file = targetFolder.findFile(fileName);
        if (file == null) {
            file = targetFolder.createFile("application/json", fileName);
        }
        if (file == null) {
            throw new IllegalStateException("Could not create backup file");
        }

        Uri outUri = file.getUri();
        try (OutputStream os = context.getContentResolver().openOutputStream(outUri, "w")) {
            if (os == null) {
                throw new IllegalStateException("Could not open backup output stream");
            }
            os.write(decisionsPayload.toString().getBytes(StandardCharsets.UTF_8));
        }
    }

    public static void writeWorkingDicBackup(Context context, String username, JSONObject decisionsPayload) throws Exception {
        writeWorkingDicBackup(context, username, decisionsPayload, null);
    }

    public static void writeWorkingDicBackup(Context context, String username, JSONObject decisionsPayload, ProgressListener progress) throws Exception {
        if (decisionsPayload == null) {
            throw new IllegalArgumentException("decisionsPayload is required");
        }

        DocumentFile folder = BackupFolderStore.getFolder(context);
        if (folder == null || !folder.exists() || !folder.isDirectory()) {
            throw new IllegalStateException("Backup folder not configured");
        }

        String user = safeUser(username);
        String fileName = "Luganda_" + user + ".dic";

        String acct = AccountManager.getActiveAccountId(context);
        DocumentFile targetFolder = folder;
        if (acct != null) {
            DocumentFile sub = folder.findFile(acct);
            if (sub == null || !sub.isDirectory()) {
                try { sub = folder.createDirectory(acct); } catch (Throwable ignored) { sub = null; }
            }
            if (sub != null && sub.isDirectory()) targetFolder = sub;
        }

        // Find or create file.
        DocumentFile file = targetFolder.findFile(fileName);
        if (file == null) {
            file = targetFolder.createFile("text/plain", fileName);
        }
        if (file == null) {
            throw new IllegalStateException("Could not create .dic backup file");
        }

        Uri outUri = file.getUri();
        try (OutputStream os = context.getContentResolver().openOutputStream(outUri, "w")) {
            if (os == null) {
                throw new IllegalStateException("Could not open .dic backup output stream");
            }
            DicExporter.exportWorkingDic(context, os, decisionsPayload, (done, total) -> {
                if (progress == null) return;
                if (total > 0) {
                    int pct = (int) Math.round((done * 100.0) / total);
                    if (pct < 0) pct = 0;
                    if (pct > 100) pct = 100;
                    progress.onProgress(pct, "Saving .dic");
                } else {
                    progress.onProgress(0, "Saving .dic");
                }
            });
        }
    }

    public static void writeAllBackups(Context context, String username, JSONObject decisionsPayload) throws Exception {
        writeAllBackups(context, username, decisionsPayload, null);
    }

    public static void writeAllBackups(Context context, String username, JSONObject decisionsPayload, ProgressListener progress) throws Exception {
        if (progress != null) progress.onProgress(0, "Starting backup");

        writeDecisionsBackup(context, username, decisionsPayload);
        if (progress != null) progress.onProgress(50, "Saved decisions");

        writeWorkingDicBackup(context, username, decisionsPayload, (pct, label) -> {
            if (progress == null) return;
            // Map .dic 0-100 -> overall 50-100
            int mapped = 50 + (int) Math.round((pct / 100.0) * 50.0);
            if (mapped < 50) mapped = 50;
            if (mapped > 100) mapped = 100;
            progress.onProgress(mapped, label);
        });

        recordBackupCompletedNow(context, username);
        if (progress != null) progress.onProgress(100, "Backup complete");
    }
}
