#!/usr/bin/env python3

import os
import sys
import time
import shutil


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
    "n'",
    "ew'"
)

VOWELS = "aeiouAEIOU"

# 16 MB file buffers
BUFFER_SIZE = 1024 * 1024 * 16

# Stop when less than this amount of free space remains.
# 5 GB = 5 * 1024^3
MIN_FREE_SPACE = 5 * 1024 * 1024 * 1024

# How often to check disk space.
DISK_CHECK_INTERVAL = 2.0


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

    return f"{value:.2f} TB"


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


def get_free_space(path):
    """
    Return free space in bytes on the filesystem containing path.
    """
    return shutil.disk_usage(path).free


def clear_terminal_line():
    """
    Move to the beginning of the current terminal line and
    clear the entire line.
    """
    print("\r\033[K", end="")


# ============================================================
# COUNT INPUT LINES
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
                    f"\r\033[K"
                    f"Counting: {percent:6.2f}% | "
                    f"{format_bytes(processed_bytes)} / "
                    f"{format_bytes(size)} | "
                    f"{format_number(total)} lines",
                    end="",
                    flush=True
                )

                last_display = now

    # Handle a final line without a newline.
    if size > 0:

        with open(path, "rb") as f:

            f.seek(-1, os.SEEK_END)

            if f.read(1) != b"\n":
                total += 1

    elapsed = time.monotonic() - start

    clear_terminal_line()

    print(
        f"Total input lines: {format_number(total)} "
        f"({format_time(elapsed)})"
    )

    return total


# ============================================================
# STATUS DISPLAY
# ============================================================

def display_status(
    processed_lines,
    total_lines,
    generated_words,
    current_word,
    free_space,
    start_time
):

    elapsed = time.monotonic() - start_time

    if elapsed > 0:
        speed = processed_lines / elapsed
    else:
        speed = 0

    if total_lines:
        percent = processed_lines / total_lines * 100
    else:
        percent = 100

    status = (
        f"Progress: {percent:6.2f}% | "
        f"Lines: {format_number(processed_lines)} / "
        f"{format_number(total_lines)} | "
        f"Generated: {format_number(generated_words)} | "
        f"Speed: {format_number(int(speed))} lines/s | "
        f"Free: {format_bytes(free_space)} | "
        f"Current: {current_word}"
    )

    print(
        "\r\033[K" + status,
        end="",
        flush=True
    )


# ============================================================
# PROCESSING
# ============================================================

def process(input_path, output_path, total_lines):

    input_size = os.path.getsize(input_path)

    processed_lines = 0
    original_words = 0
    generated_words = 0

    start_time = time.monotonic()
    last_display = start_time
    last_disk_check = start_time

    current_word = ""

    # Track whether we successfully reached the end.
    completed = False

    print()
    print("Second pass: generating word list...")
    print(f"Prefixes: {len(PREFIXES)}")
    print(f"Input:    {input_path}")
    print(f"Output:   {output_path}")
    print(f"Safety margin: {format_bytes(MIN_FREE_SPACE)}")
    print()

    output_file = None

    try:

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

            output_file = out

            for line in inp:

                word = line.rstrip("\r\n")

                processed_lines += 1
                original_words += 1

                # ------------------------------------------------
                # Check disk space periodically.
                # ------------------------------------------------

                now = time.monotonic()

                if now - last_disk_check >= DISK_CHECK_INTERVAL:

                    free_space = get_free_space(output_path)

                    if free_space <= MIN_FREE_SPACE:

                        # Flush anything currently held in Python's
                        # output buffer before stopping.
                        try:
                            out.flush()
                        except OSError:
                            pass

                        clear_terminal_line()

                        print(
                            "ERROR: Output storage is almost full."
                        )

                        print(
                            f"Free space remaining: "
                            f"{format_bytes(free_space)}"
                        )

                        print(
                            f"Safety threshold: "
                            f"{format_bytes(MIN_FREE_SPACE)}"
                        )

                        print(
                            "Stopping safely before the drive "
                            "becomes completely full."
                        )

                        return (
                            False,
                            processed_lines,
                            original_words,
                            generated_words
                        )

                    last_disk_check = now

                # ------------------------------------------------
                # Preserve original word.
                # ------------------------------------------------

                try:

                    out.write(word)
                    out.write("\n")

                except OSError as e:

                    if getattr(e, "errno", None) == 28:

                        try:
                            out.flush()
                        except OSError:
                            pass

                        clear_terminal_line()

                        print(
                            "ERROR: Output storage is full."
                        )

                        return (
                            False,
                            processed_lines,
                            original_words,
                            generated_words
                        )

                    raise

                # ------------------------------------------------
                # Generate prefixed forms.
                # ------------------------------------------------

                if word and word[0] in VOWELS:

                    for prefix in PREFIXES:

                        generated = prefix + word

                        try:

                            out.write(generated)
                            out.write("\n")

                        except OSError as e:

                            if getattr(e, "errno", None) == 28:

                                try:
                                    out.flush()
                                except OSError:
                                    pass

                                clear_terminal_line()

                                print(
                                    "ERROR: Output storage is full."
                                )

                                return (
                                    False,
                                    processed_lines,
                                    original_words,
                                    generated_words
                                )

                            raise

                        generated_words += 1

                        current_word = generated

                        # Update display frequently, but not for
                        # every single generated word.
                        now = time.monotonic()

                        if now - last_display >= 0.05:

                            free_space = get_free_space(
                                output_path
                            )

                            display_status(
                                processed_lines,
                                total_lines,
                                generated_words,
                                current_word,
                                free_space,
                                start_time
                            )

                            last_display = now

                else:

                    current_word = word

                # ------------------------------------------------
                # Regular status update.
                # ------------------------------------------------

                now = time.monotonic()

                if now - last_display >= 0.05:

                    free_space = get_free_space(
                        output_path
                    )

                    display_status(
                        processed_lines,
                        total_lines,
                        generated_words,
                        current_word,
                        free_space,
                        start_time
                    )

                    last_display = now

            # Flush the remaining output buffer.
            out.flush()

            completed = True

    except OSError as e:

        clear_terminal_line()

        if getattr(e, "errno", None) == 28:

            print(
                "ERROR: Output storage is full."
            )

        else:

            print(
                f"ERROR: File operation failed:\n{e}"
            )

        return (
            False,
            processed_lines,
            original_words,
            generated_words
        )

    finally:

        # Nothing else needed here; the with-statement closes files.
        pass

    # ============================================================
    # FINAL REPORT
    # ============================================================

    elapsed = time.monotonic() - start_time

    clear_terminal_line()

    print()

    if completed:

        print("Finished successfully.")

    else:

        print("Processing stopped.")

    print("-" * 70)

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

    # The output file should exist even if processing stopped.
    if os.path.exists(output_path):

        output_size = os.path.getsize(output_path)

        print(
            f"Output written:  "
            f"{format_bytes(output_size)}"
        )

        free_space = get_free_space(output_path)

        print(
            f"Free space:      "
            f"{format_bytes(free_space)}"
        )

    print(
        f"Time:            "
        f"{format_time(elapsed)}"
    )

    print(
        f"Output:          "
        f"{output_path}"
    )

    if not completed:

        print()
        print(
            "The partial output file has been preserved."
        )

    return (
        completed,
        processed_lines,
        original_words,
        generated_words
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

    result = process(
        input_path,
        output_path,
        total_lines
    )

    completed = result[0]

    if completed:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()