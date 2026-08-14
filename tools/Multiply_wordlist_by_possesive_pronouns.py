#!/usr/bin/env python3

import os
import sys
import time

# ============================================================
# DESCRIPTION
# This script processes a list of words and generates prefixed forms.
# ============================================================
# CONFIGURATION
# ============================================================

PREFIXES = (
    "ow'",
    "ab'",
    "ogw'",
    "egy'",
    "ey'",
    "ez'",
    "eky'",
    "eby'",
    "ely'",
    "ag'",
    "ak'",
    "obw'",
    "olw'",
    "okw'",
    "otw'",
    "w'",
    "b'",
    "gw'",
    "gy'",
    "y'",
    "z'",
    "ky'",
    "by'",
    "ly'",
    "g'",
    "k'",
    "bw'",
    "lw'",
    "z'",
    "kw'",
    "g'",
    "tw'",
    "n'"
)

VOWELS = "aeiouAEIOU"

BUFFER_SIZE = 1024 * 1024 * 16   # 16 MB


# ============================================================
# HELPERS
# ============================================================

def format_number(n):
    return f"{n:,}"


def format_bytes(n):
    units = ("B", "KB", "MB", "GB", "TB")
    value = float(n)

    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}"

        value /= 1024


def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.1f}s"

    minutes, seconds = divmod(seconds, 60)

    if minutes < 60:
        return f"{int(minutes)}m {int(seconds)}s"

    hours, minutes = divmod(minutes, 60)

    return f"{int(hours)}h {int(minutes)}m"


def same_file(path1, path2):
    try:
        return os.path.samefile(path1, path2)
    except (FileNotFoundError, OSError):
        return os.path.abspath(path1) == os.path.abspath(path2)


# ============================================================
# COUNT LINES
# ============================================================

def count_lines(path):

    print("First pass: counting input lines...")

    total = 0
    size = os.path.getsize(path)

    processed_bytes = 0
    last_display = time.monotonic()

    start = time.monotonic()

    with open(
        path,
        "rb",
        buffering=BUFFER_SIZE
    ) as f:

        while True:

            chunk = f.read(BUFFER_SIZE)

            if not chunk:
                break

            total += chunk.count(b"\n")
            processed_bytes += len(chunk)

            now = time.monotonic()

            if now - last_display >= 1:

                percent = (
                    processed_bytes / size * 100
                    if size
                    else 100
                )

                print(
                    f"\rCounting: {percent:6.2f}% | "
                    f"{format_bytes(processed_bytes)} / "
                    f"{format_bytes(size)} | "
                    f"{format_number(total)} lines",
                    end="",
                    flush=True
                )

                last_display = now

    # Account for a final line without a newline.
    if size > 0:

        with open(path, "rb") as f:

            f.seek(-1, os.SEEK_END)

            if f.read(1) != b"\n":
                total += 1

    elapsed = time.monotonic() - start

    print()

    print(
        f"Total input lines: {format_number(total)} "
        f"({format_time(elapsed)})"
    )

    return total


# ============================================================
# MAIN PROCESSING
# ============================================================

def process(input_path, output_path, total_lines):

    input_size = os.path.getsize(input_path)

    processed_lines = 0
    original_words = 0
    generated_words = 0

    start_time = time.monotonic()
    last_display = start_time

    current_word = ""

    print()
    print("Second pass: generating word list...")
    print(f"Prefixes: {len(PREFIXES)}")
    print(f"Input:    {input_path}")
    print(f"Output:   {output_path}")
    print()

    with open(
        input_path,
        "r",
        encoding="utf-8",
        errors="replace",
        buffering=BUFFER_SIZE
    ) as inp, open(
        output_path,
        "w",
        encoding="utf-8",
        buffering=BUFFER_SIZE
    ) as out:

        for line in inp:

            word = line.rstrip("\r\n")

            processed_lines += 1
            original_words += 1

            # Preserve original word.
            out.write(word)
            out.write("\n")

            # Generate prefixed forms.
            if word and word[0] in VOWELS:

                for prefix in PREFIXES:

                    generated = prefix + word

                    out.write(generated)
                    out.write("\n")

                    generated_words += 1

                    # Update terminal immediately for the current word.
                    now = time.monotonic()

                    if now - last_display >= 0.05:

                        elapsed = now - start_time

                        if elapsed > 0:
                            speed = (
                                processed_lines / elapsed
                            )
                        else:
                            speed = 0

                        percent = (
                            processed_lines / total_lines * 100
                            if total_lines
                            else 100
                        )

                        status = (
                            f"Progress: {percent:6.2f}% | "
                            f"Lines: "
                            f"{format_number(processed_lines)} / "
                            f"{format_number(total_lines)} | "
                            f"Generated: "
                            f"{format_number(generated_words)} | "
                            f"Speed: "
                            f"{format_number(int(speed))} lines/s | "
                            f"Current: {generated}"
                        )

                        # \r returns to the beginning of the same line.
                        # \033[K clears anything remaining from the
                        # previous, longer status line.
                        print(
                            "\r\033[K" + status,
                            end="",
                            flush=True
                        )

                        last_display = now

            # Update status for non-vowel words too.
            now = time.monotonic()

            if now - last_display >= 0.05:

                elapsed = now - start_time

                if elapsed > 0:
                    speed = (
                        processed_lines / elapsed
                    )
                else:
                    speed = 0

                percent = (
                    processed_lines / total_lines * 100
                    if total_lines
                    else 100
                )

                status = (
                    f"Progress: {percent:6.2f}% | "
                    f"Lines: "
                    f"{format_number(processed_lines)} / "
                    f"{format_number(total_lines)} | "
                    f"Generated: "
                    f"{format_number(generated_words)} | "
                    f"Speed: "
                    f"{format_number(int(speed))} lines/s | "
                    f"Current: {word}"
                )

                print(
                    "\r\033[K" + status,
                    end="",
                    flush=True
                )

                last_display = now

    elapsed = time.monotonic() - start_time

    # Move to a new line after the in-place progress display.
    print()

    print()
    print("Finished.")
    print("-" * 60)
    print(
        f"Original words:  "
        f"{format_number(original_words)}"
    )
    print(
        f"Generated words: "
        f"{format_number(generated_words)}"
    )
    print(
        f"Total output:    "
        f"{format_number(original_words + generated_words)}"
    )
    print(
        f"Input size:      "
        f"{format_bytes(input_size)}"
    )
    print(
        f"Output size:     "
        f"{format_bytes(os.path.getsize(output_path))}"
    )
    print(
        f"Time:            "
        f"{format_time(elapsed)}"
    )
    print(
        f"Output:          "
        f"{output_path}"
    )


# ============================================================
# COMMAND LINE
# ============================================================

def usage():

    print(
        "Usage:\n"
        "  python expand_words.py INPUT.txt OUTPUT.txt\n\n"
        "Example:\n"
        "  python expand_words.py huge_words.txt expanded.txt"
    )


def main():

    if len(sys.argv) != 3:

        usage()
        sys.exit(1)

    input_path = os.path.abspath(sys.argv[1])
    output_path = os.path.abspath(sys.argv[2])

    if not os.path.isfile(input_path):

        print(
            f"ERROR: Input file does not exist:\n"
            f"{input_path}"
        )

        sys.exit(1)

    if same_file(input_path, output_path):

        print(
            "ERROR: Input and output must be different files.\n"
            "The input file cannot safely be modified in-place."
        )

        sys.exit(1)

    total_lines = count_lines(input_path)

    process(
        input_path,
        output_path,
        total_lines
    )


if __name__ == "__main__":
    main()