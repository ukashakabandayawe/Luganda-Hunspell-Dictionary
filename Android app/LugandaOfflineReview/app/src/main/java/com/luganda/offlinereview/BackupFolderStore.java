package com.luganda.offlinereview;

import android.content.Context;
import android.content.SharedPreferences;
import android.net.Uri;

import androidx.documentfile.provider.DocumentFile;

public final class BackupFolderStore {
    private static final String PREFS = "luganda_offline_review";
    private static final String KEY_TREE_URI = "backup_tree_uri";

    private BackupFolderStore() {}

    public static void setTreeUri(Context context, Uri treeUri) {
        SharedPreferences sp = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        sp.edit().putString(KEY_TREE_URI, treeUri == null ? "" : treeUri.toString()).apply();
    }

    public static Uri getTreeUri(Context context) {
        SharedPreferences sp = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        String raw = sp.getString(KEY_TREE_URI, "");
        if (raw == null || raw.trim().isEmpty()) return null;
        try {
            return Uri.parse(raw);
        } catch (Exception ex) {
            return null;
        }
    }

    public static boolean isConfigured(Context context) {
        Uri uri = getTreeUri(context);
        return uri != null;
    }

    public static String describe(Context context) {
        Uri uri = getTreeUri(context);
        if (uri == null) return "(not set)";
        return uri.toString();
    }

    public static DocumentFile getFolder(Context context) {
        Uri uri = getTreeUri(context);
        if (uri == null) return null;
        return DocumentFile.fromTreeUri(context, uri);
    }
}
