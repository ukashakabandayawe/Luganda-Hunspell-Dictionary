package com.luganda.offlinereview;

import android.content.Context;
import android.net.Uri;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.util.zip.GZIPInputStream;
import java.util.zip.GZIPOutputStream;

public final class BundleStore {
    private static final String BUNDLE_FILE_NAME = "review_bundle.json.gz";

    private BundleStore() {}

    public static File getBundleFile(Context context) {
        return new File(context.getFilesDir(), BUNDLE_FILE_NAME);
    }

    public static boolean hasBundle(Context context) {
        return getBundleFile(context).exists();
    }

    public static void importBundle(Context context, Uri uri) throws Exception {
        if (uri == null) {
            throw new IllegalArgumentException("uri is required");
        }

        byte[] data;
        try (InputStream is = context.getContentResolver().openInputStream(uri)) {
            if (is == null) {
                throw new IllegalStateException("Could not open selected file");
            }
            data = readAllBytes(is);
        }

        if (data.length == 0) {
            throw new IllegalStateException("Selected file is empty");
        }

        // If file is already gzip (magic 1F 8B), store as-is.
        boolean isGz = data.length >= 2 && (data[0] == (byte) 0x1f) && (data[1] == (byte) 0x8b);
        File outFile = getBundleFile(context);

        if (isGz) {
            try (FileOutputStream fos = new FileOutputStream(outFile, false)) {
                fos.write(data);
            }
        } else {
            // Assume JSON, gzip it to keep storage small.
            try (FileOutputStream fos = new FileOutputStream(outFile, false);
                 GZIPOutputStream gz = new GZIPOutputStream(fos)) {
                gz.write(data);
            }
        }

        // Validate parse.
        JSONObject obj = loadBundleJson(context);
        int schema = obj.optInt("schema", 0);
        if (schema != 1) {
            throw new IllegalStateException("Unsupported bundle schema: " + schema);
        }
        if (!obj.has("stems")) {
            throw new IllegalStateException("Invalid bundle: missing 'stems'");
        }

        // New assignment => clear any previous decisions.
        File decisions = DecisionsStore.getDecisionsFile(context);
        if (decisions.exists()) {
            // noinspection ResultOfMethodCallIgnored
            decisions.delete();
        }
    }

    public static JSONObject loadBundleJson(Context context) throws Exception {
        File f = getBundleFile(context);
        if (!f.exists()) {
            throw new IllegalStateException("Bundle not found");
        }
        try (FileInputStream fis = new FileInputStream(f);
             GZIPInputStream gis = new GZIPInputStream(fis)) {
            byte[] bytes = readAllBytes(gis);
            String json = new String(bytes, "UTF-8");
            return new JSONObject(json);
        }
    }

    private static byte[] readAllBytes(InputStream is) throws Exception {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buf = new byte[8192];
        while (true) {
            int n = is.read(buf);
            if (n < 0) break;
            if (n > 0) out.write(buf, 0, n);
        }
        return out.toByteArray();
    }
}
