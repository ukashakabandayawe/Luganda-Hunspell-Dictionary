package com.luganda.offlinereview;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;

import java.io.File;
import java.io.FileWriter;
import java.io.Writer;
import java.util.Map;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class Watchdog {

    private static final int DEFAULT_THRESHOLD_MS = 5000; // 5s
    private static ScheduledExecutorService executor;
    private static Handler mainHandler = new Handler(Looper.getMainLooper());
    private static Context appContext;

    public static synchronized void start(Context ctx) {
        if (executor != null) return;
        appContext = ctx.getApplicationContext();
        executor = Executors.newSingleThreadScheduledExecutor();
        executor.scheduleAtFixedRate(() -> {
            final CountDownLatch latch = new CountDownLatch(1);
            try {
                mainHandler.post(latch::countDown);
                boolean responded = latch.await(DEFAULT_THRESHOLD_MS, TimeUnit.MILLISECONDS);
                if (!responded) {
                    captureStacks();
                }
            } catch (InterruptedException ignored) {
                // ignore
            }
        }, DEFAULT_THRESHOLD_MS, DEFAULT_THRESHOLD_MS, TimeUnit.MILLISECONDS);
    }

    public static synchronized void stop() {
        if (executor != null) {
            executor.shutdownNow();
            executor = null;
        }
    }

    private static void captureStacks() {
        try {
            Map<Thread, StackTraceElement[]> traces = Thread.getAllStackTraces();
            File dir = null;
            try {
                if (appContext != null) {
                    File base = appContext.getExternalFilesDir(null);
                    if (base != null) dir = new File(base, "anr");
                }
            } catch (Throwable ignored) {
            }
            if (dir == null) dir = new File("files_anr");
            if (!dir.exists()) dir.mkdirs();

            File out = new File(dir, "anr_" + System.currentTimeMillis() + ".txt");
            try (Writer w = new FileWriter(out)) {
                for (Map.Entry<Thread, StackTraceElement[]> e : traces.entrySet()) {
                    Thread t = e.getKey();
                    w.write("Thread: " + t.getName() + " state=" + t.getState() + "\n");
                    for (StackTraceElement ste : e.getValue()) {
                        w.write("\t" + ste.toString() + "\n");
                    }
                    w.write("\n");
                }
            }
        } catch (Throwable ignored) {
            // Best-effort; don't crash the app for instrumentation.
        }
    }
}
