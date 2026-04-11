package com.luganda.offlinereview;

import android.content.Intent;
import android.os.Bundle;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.appbar.MaterialToolbar;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class QueueActivity extends AppCompatActivity {

    public static final String EXTRA_STEM_INDEX = "stem_index";

    private JSONObject bundle;
    private Map<String, Map<String, String>> decisionMap;

    private TextView title;
    private RecyclerView rv;
    private StemAdapter adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_queue);

        MaterialToolbar toolbar = findViewById(R.id.queueToolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }

        title = findViewById(R.id.queueTitle);
        rv = findViewById(R.id.queueRecycler);
        rv.setLayoutManager(new LinearLayoutManager(this));

        adapter = new StemAdapter(new ArrayList<>(), row -> {
            Intent intent = new Intent(this, ReviewActivity.class);
            intent.putExtra(EXTRA_STEM_INDEX, row.index);
            startActivity(intent);
        });
        rv.setAdapter(adapter);

        loadAndRender();
    }

    @Override
    protected void onResume() {
        super.onResume();
        // Returning from ReviewActivity: reload decisions and recompute counts.
        loadAndRender();
    }

    private void loadAndRender() {
        try {
            bundle = BundleStore.loadBundleJson(this);
            decisionMap = DecisionsStore.loadDecisionStatusMap(this);
        } catch (Exception ex) {
            title.setText("No bundle loaded. Go back and import a bundle.\n\n" + ex);
            if (adapter != null) {
                adapter.setItems(new ArrayList<>());
            }
            return;
        }

        JSONObject user = bundle.optJSONObject("user");
        String username = user != null ? user.optString("username", "") : "";
        title.setText(username.isEmpty() ? "My Queue" : ("My Queue (" + username + ")"));

        JSONArray stems = bundle.optJSONArray("stems");
        List<StemRow> rows = new ArrayList<>();
        if (stems != null) {
            for (int i = 0; i < stems.length(); i++) {
                JSONObject s = stems.optJSONObject(i);
                if (s == null) continue;
                String stemText = s.optString("stem", "");
                JSONArray tasks = s.optJSONArray("tasks");
                int pending = 0;
                int done = 0;
                if (tasks != null) {
                    for (int j = 0; j < tasks.length(); j++) {
                        JSONObject t = tasks.optJSONObject(j);
                        if (t == null) continue;
                        String flag = t.optString("flag", "");
                        String baseStatus = t.optString("status", "pending");
                        String effective = effectiveStatus(stemText, flag, baseStatus);
                        if ("pending".equals(effective)) pending++;
                        else done++;
                    }
                }
                rows.add(new StemRow(i, stemText, pending, done));
            }
        }

        adapter.setItems(rows);
    }

    @Override
    public boolean onSupportNavigateUp() {
        finish();
        return true;
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

    static final class StemRow {
        final int index;
        final String stem;
        final int pending;
        final int done;

        StemRow(int index, String stem, int pending, int done) {
            this.index = index;
            this.stem = stem;
            this.pending = pending;
            this.done = done;
        }
    }

    interface OnStemClick {
        void onClick(StemRow row);
    }

    static final class StemAdapter extends RecyclerView.Adapter<StemViewHolder> {
        private final List<StemRow> items;
        private final OnStemClick onClick;

        StemAdapter(List<StemRow> items, OnStemClick onClick) {
            this.items = items;
            this.onClick = onClick;
        }

        void setItems(List<StemRow> newItems) {
            items.clear();
            if (newItems != null) {
                items.addAll(newItems);
            }
            notifyDataSetChanged();
        }

        @Override
        public StemViewHolder onCreateViewHolder(android.view.ViewGroup parent, int viewType) {
            android.view.View v = android.view.LayoutInflater.from(parent.getContext())
                    .inflate(R.layout.row_stem, parent, false);
            return new StemViewHolder(v);
        }

        @Override
        public void onBindViewHolder(StemViewHolder holder, int position) {
            StemRow row = items.get(position);
            holder.bind(row, onClick);
        }

        @Override
        public int getItemCount() {
            return items.size();
        }
    }

    static final class StemViewHolder extends RecyclerView.ViewHolder {
        private final TextView stemText;
        private final TextView countsText;

        StemViewHolder(android.view.View itemView) {
            super(itemView);
            stemText = itemView.findViewById(R.id.rowStemText);
            countsText = itemView.findViewById(R.id.rowCountsText);
        }

        void bind(StemRow row, OnStemClick onClick) {
            stemText.setText(row.stem);
            countsText.setText("Pending: " + row.pending + "   Done: " + row.done);
            itemView.setOnClickListener(v -> onClick.onClick(row));
        }
    }
}
