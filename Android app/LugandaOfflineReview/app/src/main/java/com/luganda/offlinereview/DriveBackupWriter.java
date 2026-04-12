package com.luganda.offlinereview;

import android.content.Context;
import android.net.Uri;

import androidx.documentfile.provider.DocumentFile;

import org.json.JSONObject;

import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

public final class DriveBackupWriter {
    private DriveBackupWriter() {}

    public static void writeDecisionsBackup(Context context, String username, JSONObject decisionsPayload) throws Exception {
        if (decisionsPayload == null) {
            throw new IllegalArgumentException("decisionsPayload is required");
        }

        DocumentFile folder = BackupFolderStore.getFolder(context);
        if (folder == null || !folder.exists() || !folder.isDirectory()) {
            throw new IllegalStateException("Backup folder not configured");
        }

        String safeUser = (username == null || username.trim().isEmpty()) ? "reviewer" : username.trim();
        String fileName = "decisions_" + safeUser + ".json";

        // Find or create file.
        DocumentFile file = folder.findFile(fileName);
        if (file == null) {
            file = folder.createFile("application/json", fileName);
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
}
