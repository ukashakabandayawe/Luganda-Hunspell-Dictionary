package com.luganda.offlinereview;

import android.content.Context;
import android.content.SharedPreferences;
import android.net.Uri;

import org.json.JSONObject;

import java.io.File;
import java.io.FileWriter;
import java.io.FileReader;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.zip.ZipInputStream;
import java.util.zip.ZipOutputStream;
import java.util.zip.ZipEntry;

public final class AccountManager {
    private static final String PREFS = "luganda_accounts_prefs";
    private static final String PREF_ACTIVE = "active_account";
    private static final String ACCOUNTS_DIR = "accounts";
    private static final String ACCOUNT_META = "account.json";

    private AccountManager() {}

    public static File getAccountsDir(Context context) {
        File d = new File(context.getFilesDir(), ACCOUNTS_DIR);
        if (!d.exists()) d.mkdirs();
        return d;
    }

    public static File getAccountDir(Context context, String accountId) {
        if (accountId == null) return null;
        File d = new File(getAccountsDir(context), sanitizeId(accountId));
        if (!d.exists()) d.mkdirs();
        return d;
    }

    public static File getActiveAccountDir(Context context) {
        String id = getActiveAccountId(context);
        if (id == null) return null;
        File dir = getAccountDir(context, id);
        if (!dir.exists()) return null;
        return dir;
    }

    public static String getActiveAccountId(Context context) {
        SharedPreferences p = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        return p.getString(PREF_ACTIVE, null);
    }

    public static void setActiveAccountId(Context context, String id) {
        SharedPreferences p = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        p.edit().putString(PREF_ACTIVE, id).apply();
        if (id != null) {
            File d = getAccountDir(context, id);
            if (!d.exists()) d.mkdirs();
        }
    }

    public static String createAccount(Context context, String displayName) throws Exception {
        String id = UUID.randomUUID().toString();
        File d = getAccountDir(context, id);
        if (!d.exists() && !d.mkdirs()) {
            throw new IllegalStateException("Could not create account dir");
        }
        JSONObject meta = new JSONObject();
        meta.put("id", id);
        meta.put("display_name", displayName == null ? "" : displayName);
        try (FileWriter w = new FileWriter(new File(d, ACCOUNT_META), false)) {
            w.write(meta.toString());
        }
        return id;
    }

    public static List<JSONObject> listAccounts(Context context) {
        File ads = getAccountsDir(context);
        List<JSONObject> out = new ArrayList<>();
        if (!ads.exists() || !ads.isDirectory()) return out;
        File[] children = ads.listFiles();
        if (children == null) return out;
        for (File c : children) {
            if (!c.isDirectory()) continue;
            File m = new File(c, ACCOUNT_META);
            if (!m.exists()) continue;
            try (FileReader r = new FileReader(m)) {
                char[] buf = new char[(int) Math.min(4096, m.length())];
                int n = r.read(buf);
                if (n > 0) {
                    String s = new String(buf, 0, n);
                    JSONObject jo = new JSONObject(s);
                    out.add(jo);
                }
            } catch (Throwable ignored) {}
        }
        return out;
    }

    public static String getActiveAccountDisplayName(Context context) {
        String id = getActiveAccountId(context);
        if (id == null) return null;
        File m = new File(getAccountDir(context, id), ACCOUNT_META);
        if (!m.exists()) return null;
        try (FileReader r = new FileReader(m)) {
            char[] buf = new char[(int) Math.min(4096, m.length())];
            int n = r.read(buf);
            if (n > 0) {
                String s = new String(buf, 0, n);
                JSONObject jo = new JSONObject(s);
                return jo.optString("display_name", null);
            }
        } catch (Throwable ignored) {}
        return null;
    }

    public static String sanitizeId(String raw) {
        if (raw == null) return "default";
        String s = raw.trim();
        if (s.isEmpty()) return "default";
        s = s.replaceAll("[^A-Za-z0-9_.-]", "_");
        if (s.length() > 64) s = s.substring(0, 64);
        return s;
    }

    public static File exportAccount(Context context, String accountId) throws Exception {
        File acc = getAccountDir(context, accountId);
        File out = new File(context.getCacheDir(), "account_export_" + sanitizeId(accountId) + ".zip");
        try (FileOutputStream fos = new FileOutputStream(out);
             ZipOutputStream zos = new ZipOutputStream(fos)) {
            addDirToZip(zos, acc, acc.getName() + "/");
        }
        return out;
    }

    private static void addDirToZip(ZipOutputStream zos, File dir, String base) throws Exception {
        File[] children = dir.listFiles();
        if (children == null) return;
        byte[] buf = new byte[8192];
        for (File f : children) {
            if (f.isDirectory()) {
                addDirToZip(zos, f, base + f.getName() + "/");
            } else {
                ZipEntry e = new ZipEntry(base + f.getName());
                zos.putNextEntry(e);
                try (FileInputStream fis = new FileInputStream(f)) {
                    int r;
                    while ((r = fis.read(buf)) > 0) zos.write(buf, 0, r);
                }
                zos.closeEntry();
            }
        }
    }

    public static File importAccountFromUri(Context context, Uri uri, String desiredAccountId) throws Exception {
        if (uri == null) throw new IllegalArgumentException("uri required");

        String accountId = (desiredAccountId == null || desiredAccountId.trim().isEmpty())
                ? "imported_" + System.currentTimeMillis()
                : sanitizeId(desiredAccountId);

        File acc = getAccountDir(context, accountId);

        try (InputStream is = context.getContentResolver().openInputStream(uri);
             ZipInputStream zis = new ZipInputStream(is)) {
            java.util.zip.ZipEntry e;
            byte[] buf = new byte[8192];
            while ((e = zis.getNextEntry()) != null) {
                if (e.isDirectory()) {
                    File d = new File(acc, e.getName());
                    d.mkdirs();
                    zis.closeEntry();
                    continue;
                }
                File out = new File(acc, e.getName());
                File parent = out.getParentFile();
                if (parent != null && !parent.exists()) parent.mkdirs();
                try (FileOutputStream fos = new FileOutputStream(out, false)) {
                    int r;
                    while ((r = zis.read(buf)) > 0) fos.write(buf, 0, r);
                }
                zis.closeEntry();
            }
        }

        // Set the newly imported account as active
        setActiveAccountId(context, accountId);
        return acc;
    }
}
