package com.lugandahunspelldictionary;
import morfologik.fsa.FSA;
import morfologik.fsa.builders.CFSA2Serializer;
import morfologik.fsa.builders.FSABuilder;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

public class ChunkedMorfologikBuilder {

    // 2 million lines per chunk.
    // Start conservatively because the PC has 16 GB RAM.
    private static final int CHUNK_SIZE = 2_000_000;

    // Number of files merged at once.
    private static final int MERGE_FAN_IN = 32;

    private static long inputLines = 0;
    private static long uniqueWords = 0;

    public static void main(String[] args) throws Exception {

        if (args.length != 3) {
            System.err.println(
                "Usage:"
            );
            System.err.println(
                "java ChunkedMorfologikBuilder <input> <output> <tempDir>"
            );
            System.exit(1);
        }

        Path input = Paths.get(args[0]);
        Path output = Paths.get(args[1]);
        Path tempDir = Paths.get(args[2]);

        Files.createDirectories(tempDir);

        System.out.println("========================================");
        System.out.println(" Chunked Morfologik Dictionary Builder");
        System.out.println("========================================");
        System.out.println("Input : " + input);
        System.out.println("Output: " + output);
        System.out.println("Temp  : " + tempDir);
        System.out.printf(
            Locale.ROOT,
            "Input size: %.2f GB%n",
            Files.size(input) / (1024.0 * 1024.0 * 1024.0)
        );
        System.out.printf(
            Locale.ROOT,
            "Chunk size: %,d lines%n",
            CHUNK_SIZE
        );

        List<Path> chunks;

        try {
            System.out.println();
            System.out.println("PHASE 1: Creating sorted chunks");

            chunks = createChunks(input, tempDir);

            System.out.printf(
                Locale.ROOT,
                "%nCreated %,d sorted chunks.%n",
                chunks.size()
            );

            System.out.println();
            System.out.println("PHASE 2: Multi-pass merge");

            while (chunks.size() > MERGE_FAN_IN) {
                chunks = mergePass(chunks, tempDir);
            }

            System.out.printf(
                Locale.ROOT,
                "Remaining sorted files: %,d%n",
                chunks.size()
            );

            System.out.println();
            System.out.println("PHASE 3: Building FSA");

            buildFSA(chunks, output);

            System.out.println();
            System.out.println("PHASE 4: Cleanup");

            for (Path p : chunks) {
                Files.deleteIfExists(p);
            }

            System.out.println();
            System.out.println("========================================");
            System.out.println(" SUCCESS");
            System.out.println("========================================");
            System.out.println("Dictionary: " + output);
            System.out.printf(
                Locale.ROOT,
                "Dictionary size: %.2f GB%n",
                Files.size(output) /
                    (1024.0 * 1024.0 * 1024.0)
            );

        } catch (Throwable t) {

            System.err.println();
            System.err.println("========================================");
            System.err.println(" BUILD FAILED");
            System.err.println("========================================");
            System.err.println(
                "Temporary files have NOT been deleted."
            );
            System.err.println(
                "They are in: " + tempDir
            );
            System.err.println();

            throw t;
        }
    }

    private static List<Path> createChunks(
            Path input,
            Path tempDir) throws IOException {

        List<Path> chunks = new ArrayList<>();

        ArrayList<String> words =
            new ArrayList<>(CHUNK_SIZE);

        long chunkNumber = 0;

        try (BufferedReader reader =
                Files.newBufferedReader(
                    input,
                    StandardCharsets.UTF_8
                )) {

            String line;

            while ((line = reader.readLine()) != null) {

                inputLines++;

                if (line.isEmpty()) {
                    continue;
                }

                words.add(line);

                if (words.size() >= CHUNK_SIZE) {

                    Path chunk =
                        writeSortedChunk(
                            words,
                            tempDir,
                            chunkNumber++
                        );

                    chunks.add(chunk);

                    words.clear();

                    showProgress(
                        inputLines,
                        "Reading"
                    );
                }
            }
        }

        if (!words.isEmpty()) {

            Path chunk =
                writeSortedChunk(
                    words,
                    tempDir,
                    chunkNumber
                );

            chunks.add(chunk);

            words.clear();
        }

        showProgress(inputLines, "Reading");
        System.out.println();

        return chunks;
    }

    private static Path writeSortedChunk(
            ArrayList<String> words,
            Path tempDir,
            long number) throws IOException {

        Collections.sort(words);

        Path file = tempDir.resolve(
            String.format(
                Locale.ROOT,
                "chunk-%06d.txt",
                number
            )
        );

        long unique = 0;

        try (BufferedWriter writer =
                Files.newBufferedWriter(
                    file,
                    StandardCharsets.UTF_8
                )) {

            String previous = null;

            for (String word : words) {

                if (!word.equals(previous)) {

                    writer.write(word);
                    writer.newLine();

                    previous = word;
                    unique++;
                }
            }
        }

        System.out.printf(
            Locale.ROOT,
            "\rCreated chunk %,d | %,d unique words",
            number,
            unique
        );

        return file;
    }

    private static List<Path> mergePass(
            List<Path> chunks,
            Path tempDir) throws IOException {

        List<Path> next = new ArrayList<>();

        int groups =
            (chunks.size() + MERGE_FAN_IN - 1)
            / MERGE_FAN_IN;

        for (int start = 0; start < chunks.size();
             start += MERGE_FAN_IN) {

            int end =
                Math.min(
                    start + MERGE_FAN_IN,
                    chunks.size()
                );

            List<Path> group =
                new ArrayList<>(
                    chunks.subList(start, end)
                );

            Path merged =
                tempDir.resolve(
                    "merge-" +
                    System.nanoTime() +
                    ".txt"
                );

            mergeFiles(group, merged);

            for (Path p : group) {
                Files.deleteIfExists(p);
            }

            next.add(merged);

            System.out.printf(
                Locale.ROOT,
                "\rMerge groups: %d / %d",
                Math.min(
                    (start / MERGE_FAN_IN) + 1,
                    groups
                ),
                groups
            );
        }

        System.out.println();

        return next;
    }

    private static void mergeFiles(
            List<Path> files,
            Path output) throws IOException {

        List<BufferedReader> readers =
            new ArrayList<>();

        PriorityQueue<Entry> queue =
            new PriorityQueue<>(
                Comparator.comparing(e -> e.word)
            );

        try {

            for (int i = 0; i < files.size(); i++) {

                BufferedReader reader =
                    Files.newBufferedReader(
                        files.get(i),
                        StandardCharsets.UTF_8
                    );

                readers.add(reader);

                String word = reader.readLine();

                if (word != null) {
                    queue.add(
                        new Entry(word, i)
                    );
                }
            }

            try (BufferedWriter writer =
                    Files.newBufferedWriter(
                        output,
                        StandardCharsets.UTF_8
                    )) {

                String previous = null;

                while (!queue.isEmpty()) {

                    Entry entry =
                        queue.poll();

                    if (!entry.word.equals(previous)) {

                        writer.write(entry.word);
                        writer.newLine();

                        previous =
                            entry.word;
                    }

                    String nextWord =
                        readers
                            .get(entry.reader)
                            .readLine();

                    if (nextWord != null) {

                        queue.add(
                            new Entry(
                                nextWord,
                                entry.reader
                            )
                        );
                    }
                }
            }

        } finally {

            for (BufferedReader reader :
                    readers) {

                try {
                    reader.close();
                } catch (IOException ignored) {
                }
            }
        }
    }

    private static void buildFSA(
            List<Path> files,
            Path output) throws Exception {

        FSABuilder builder =
            new FSABuilder();

        List<BufferedReader> readers =
            new ArrayList<>();

        PriorityQueue<Entry> queue =
            new PriorityQueue<>(
                Comparator.comparing(e -> e.word)
            );

        try {

            for (int i = 0; i < files.size(); i++) {

                BufferedReader reader =
                    Files.newBufferedReader(
                        files.get(i),
                        StandardCharsets.UTF_8
                    );

                readers.add(reader);

                String word =
                    reader.readLine();

                if (word != null) {

                    queue.add(
                        new Entry(word, i)
                    );
                }
            }

            String previous = null;

            while (!queue.isEmpty()) {

                Entry entry =
                    queue.poll();

                if (!entry.word.equals(previous)) {

                    byte[] bytes =
                        entry.word.getBytes(
                            StandardCharsets.UTF_8
                        );

                    builder.add(
                        bytes,
                        0,
                        bytes.length
                    );

                    uniqueWords++;

                    previous =
                        entry.word;

                    if (
                        uniqueWords % 100_000 == 0
                    ) {

                        showFSAProgress(
                            uniqueWords
                        );
                    }
                }

                String nextWord =
                    readers
                        .get(entry.reader)
                        .readLine();

                if (nextWord != null) {

                    queue.add(
                        new Entry(
                            nextWord,
                            entry.reader
                        )
                    );
                }
            }

        } finally {

            for (BufferedReader reader :
                    readers) {

                try {
                    reader.close();
                } catch (IOException ignored) {
                }
            }
        }

        System.out.println();
        System.out.println();
        System.out.println("Completing FSA...");
        System.out.println(
            "This is the memory-intensive stage."
        );

        FSA fsa = builder.complete();

        System.out.println(
            "FSA completed. Serializing CFSA2..."
        );

        try (OutputStream outputStream =
                new BufferedOutputStream(
                    Files.newOutputStream(
                        output,
                        StandardOpenOption.CREATE,
                        StandardOpenOption.TRUNCATE_EXISTING
                    ),
                    1024 * 1024
                )) {

            new CFSA2Serializer()
                .serialize(
                    fsa,
                    outputStream
                );
        }
    }

    private static void showProgress(
            long count,
            String phase) {

        Runtime runtime =
            Runtime.getRuntime();

        long used =
            runtime.totalMemory()
            - runtime.freeMemory();

        System.out.printf(
            Locale.ROOT,
            "\r%-10s %,d lines | RAM %.2f GB",
            phase,
            count,
            used /
                (1024.0 *
                 1024.0 *
                 1024.0)
        );
    }

    private static void showFSAProgress(
            long count) {

        Runtime runtime =
            Runtime.getRuntime();

        long used =
            runtime.totalMemory()
            - runtime.freeMemory();

        System.out.printf(
            Locale.ROOT,
            "\rFSA: %,d words | RAM %.2f GB",
            count,
            used /
                (1024.0 *
                 1024.0 *
                 1024.0)
        );
    }

    private static class Entry {

        final String word;
        final int reader;

        Entry(
                String word,
                int reader) {

            this.word = word;
            this.reader = reader;
        }
    }
}