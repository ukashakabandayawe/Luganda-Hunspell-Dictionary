package com.luganda.offlinereview;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.os.Bundle;
import android.text.InputType;
import android.content.Intent;
import java.io.File;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

public class AccountsActivity extends AppCompatActivity {

    private ListView listView;
    private ArrayAdapter<String> adapter;
    private List<String> ids = new ArrayList<>();
    private static final int REQ_EXPORT_ACCOUNT = 2001;
    private String pendingExportAccountId = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_accounts);

        listView = findViewById(R.id.accountsList);
        adapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, new ArrayList<>());
        listView.setAdapter(adapter);

        Button btnNew = findViewById(R.id.btnNewAccount);
        btnNew.setOnClickListener(v -> createNewAccount());

        listView.setOnItemClickListener((parent, view, position, id) -> {
            if (position < 0 || position >= ids.size()) return;
            String acctId = ids.get(position);
            AccountManager.setActiveAccountId(AccountsActivity.this, acctId);
            Toast.makeText(AccountsActivity.this, "Switched account", Toast.LENGTH_SHORT).show();
            finish();
        });

        listView.setOnItemLongClickListener((parent, view, position, id) -> {
            if (position < 0 || position >= ids.size()) return false;
            String acctId = ids.get(position);
            pendingExportAccountId = acctId;
            Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
            intent.addCategory(Intent.CATEGORY_OPENABLE);
            intent.setType("application/zip");
            intent.putExtra(Intent.EXTRA_TITLE, "account_" + acctId + ".zip");
            startActivityForResult(intent, REQ_EXPORT_ACCOUNT);
            return true;
        });

        refreshList();
    }

    private void refreshList() {
        adapter.clear();
        ids.clear();
        try {
            java.util.List<JSONObject> list = AccountManager.listAccounts(this);
            for (JSONObject jo : list) {
                String id = jo.optString("id", "");
                String dn = jo.optString("display_name", "");
                ids.add(id);
                adapter.add(dn == null || dn.isEmpty() ? id : dn + " (" + id.substring(0, Math.min(8, id.length())) + ")");
            }
        } catch (Throwable ignored) {}
        adapter.notifyDataSetChanged();
    }

    private void createNewAccount() {
        final EditText input = new EditText(this);
        input.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_CAP_WORDS);
        new AlertDialog.Builder(this)
                .setTitle("New account")
                .setMessage("Enter reviewer display name:")
                .setView(input)
                .setPositiveButton("Create", (dialog, which) -> {
                    String name = input.getText() == null ? "" : input.getText().toString().trim();
                    try {
                        String id = AccountManager.createAccount(AccountsActivity.this, name);
                        AccountManager.setActiveAccountId(AccountsActivity.this, id);
                        Toast.makeText(AccountsActivity.this, "Account created", Toast.LENGTH_SHORT).show();
                        refreshList();
                    } catch (Exception ex) {
                        Toast.makeText(AccountsActivity.this, "Failed to create account: " + ex.getMessage(), Toast.LENGTH_LONG).show();
                    }
                })
                .setNegativeButton("Cancel", (dialog, which) -> dialog.dismiss())
                .show();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, android.content.Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQ_EXPORT_ACCOUNT) {
            if (resultCode != RESULT_OK || data == null) return;
            android.net.Uri uri = data.getData();
            if (uri == null || pendingExportAccountId == null) return;
            // Zip account directory and write to uri
            try (java.io.OutputStream os = getContentResolver().openOutputStream(uri)) {
                if (os == null) throw new IllegalStateException("Could not open output");
                File acctDir = AccountManager.getAccountDir(this, pendingExportAccountId);
                if (acctDir == null || !acctDir.exists()) throw new IllegalStateException("Account data missing");
                zipDirectoryToStream(acctDir, os, acctDir.getName());
                Toast.makeText(this, "Account exported", Toast.LENGTH_SHORT).show();
            } catch (Exception ex) {
                Toast.makeText(this, "Export failed: " + ex.getMessage(), Toast.LENGTH_LONG).show();
            } finally {
                pendingExportAccountId = null;
            }
        }
    }

    private void zipDirectoryToStream(File dir, java.io.OutputStream out, String baseName) throws Exception {
        try (java.util.zip.ZipOutputStream zos = new java.util.zip.ZipOutputStream(out)) {
            byte[] buf = new byte[8192];
            java.util.List<File> files = new java.util.ArrayList<>();
            collectFiles(dir, files, dir);
            for (File f : files) {
                String rel = dir.toPath().relativize(f.toPath()).toString().replace('\\', '/');
                java.util.zip.ZipEntry e = new java.util.zip.ZipEntry(rel);
                zos.putNextEntry(e);
                try (java.io.FileInputStream fis = new java.io.FileInputStream(f)) {
                    int n;
                    while ((n = fis.read(buf)) >= 0) {
                        if (n == 0) continue;
                        zos.write(buf, 0, n);
                    }
                }
                zos.closeEntry();
            }
            zos.finish();
        }
    }

    private void collectFiles(File root, List<File> out, File dir) {
        File[] children = dir.listFiles();
        if (children == null) return;
        for (File c : children) {
            if (c.isDirectory()) collectFiles(root, out, c);
            else out.add(c);
        }
    }
}
