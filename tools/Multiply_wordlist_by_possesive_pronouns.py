#!/usr/bin/env python3

import os
import sys
import time
import json
import shutil
import hashlib
import tempfile


# ============================================================
# DESCRIPTION
# ============================================================
# Processes a list of words and generates prefixed forms.
#
# IMPORTANT:
# This version is resumable.
#
# If the USB/external drive disappears, Windows sleeps, the
# process crashes, or the computer is shut down, run the same
# command again. The script resumes from the last durable
# checkpoint instead of starting from zero.
#
# Checkpoints are deliberately stored on the system drive by
# default, NOT beside the output on the external drive.
# ============================================================


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

BUFFER_SIZE = 1024 * 1024 * 16

# Stop before the destination filesystem becomes completely full.
MIN_FREE_SPACE = 5 * 1024 * 1024 * 1024

# How often to check free space.
DISK_CHECK_INTERVAL = 2.0

# How often to make a durable resume checkpoint.
# Smaller = less work lost after a crash, but more disk I/O.
CHECKPOINT_INTERVAL = 10.0

# Also checkpoint after this many input lines, regardless of time.
CHECKPOINT_LINES = 100_000

# Force Python/OS buffers to disk at every checkpoint.
# This makes recovery much safer, at the cost of some speed.
USE_FSYNC = True


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
    return shutil.disk_usage(path).free


def clear_terminal_line():
    print("\r\033[K", end="")


def checkpoint_path_for(input_path, output_path):
    """
    Store the checkpoint on the system drive rather than the USB.

    This is important: if F:\\ disappears, the resume information
    remains available on C:\\.
    """
    key = hashlib.sha256(
        (os.path.abspath(input_path) + "\0" + os.path.abspath(output_path))
        .encode("utf-8", errors="replace")
    ).hexdigest()[:20]

    base = os.environ.get("LOCALAPPDATA")

    if not base:
        base = tempfile.gettempdir()

    directory = os.path.join(base, "ExpandWordsCheckpoints")
    os.makedirs(directory, exist_ok=True)

    return os.path.join(directory, f"checkpoint_{key}.json")


def atomic_write_json(path, data):
    """
    Write checkpoint atomically.

    The old checkpoint remains intact if the program dies halfway
    through writing the new checkpoint.
    """
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)

    fd, temp_path = tempfile.mkstemp(
        prefix=".checkpoint_",
        suffix=".tmp",
        dir=directory,
        text=True
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_path, path)

    except Exception:
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise


def load_checkpoint(checkpoint_path):
    try:
        with open(checkpoint_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def delete_checkpoint(checkpoint_path):
    try:
        os.remove(checkpoint_path)
    except FileNotFoundError:
        pass
    except OSError as e:
        print(f"WARNING: Could not remove checkpoint: {e}")


def checkpoint_matches(cp, input_path, output_path):
    if not cp:
        return False

    try:
        return (
            os.path.abspath(cp.get("input_path", "")) ==
            os.path.abspath(input_path)
            and
            os.path.abspath(cp.get("output_path", "")) ==
            os.path.abspath(output_path)
            and
            os.path.getsize(input_path) == cp.get("input_size")
            and
            os.path.getmtime(input_path) == cp.get("input_mtime")
        )
    except OSError:
        return False


def sync_file(f):
    """
    Make all data written so far durable.

    flush() alone only pushes Python's buffer to the OS.
    fsync() additionally asks the OS to commit it to storage.
    """
    f.flush()

    if USE_FSYNC:
        os.fsync(f.fileno())


def safe_input_offset(f):
    """
    Return the byte position after the current complete input line.

    The input file is opened in binary mode for resumable processing,
    so offsets are exact byte offsets.
    """
    return f.tell()


def save_checkpoint(
    checkpoint_path,
    input_path,
    output_path,
    input_size,
    input_mtime,
    total_lines,
    processed_lines,
    original_words,
    generated_words,
    input_offset,
    output_offset,
    current_word,
):
    data = {
        "version": 2,
        "input_path": os.path.abspath(input_path),
        "output_path": os.path.abspath(output_path),
        "input_size": input_size,
        "input_mtime": input_mtime,
        "total_lines": total_lines,

        # These are the important recovery values.
        "input_offset": input_offset,
        "output_offset": output_offset,

        "processed_lines": processed_lines,
        "original_words": original_words,
        "generated_words": generated_words,
        "current_word": current_word,
        "saved_at": time.time(),
    }

    atomic_write_json(checkpoint_path, data)


def count_lines(path):
    print("First pass: counting input lines...")

    total = 0
    size = os.path.getsize(path)
    processed_bytes = 0
    last_display = time.monotonic()
    start = time.monotonic()

    with open(path, "rb", buffering=BUFFER_SIZE) as f:
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
                    flush=True,
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
    start_time,
):
    elapsed = time.monotonic() - start_time

    speed = processed_lines / elapsed if elapsed > 0 else 0

    percent = (
        processed_lines / total_lines * 100
        if total_lines
        else 100
    )

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
        flush=True,
    )


# ============================================================
# PROCESSING
# ============================================================

def process(
    input_path,
    output_path,
    total_lines,
    checkpoint_path,
    resume=None,
):
    input_size = os.path.getsize(input_path)
    input_mtime = os.path.getmtime(input_path)

    # --------------------------------------------------------
    # Recovery state.
    # --------------------------------------------------------

    if resume:
        processed_lines = int(resume["processed_lines"])
        original_words = int(resume["original_words"])
        generated_words = int(resume["generated_words"])
        input_offset = int(resume["input_offset"])
        output_offset = int(resume["output_offset"])
        current_word = resume.get("current_word", "")

        print()
        print("RESUMING PREVIOUS RUN")
        print("-" * 70)
        print(f"Input offset:      {format_bytes(input_offset)}")
        print(f"Output offset:     {format_bytes(output_offset)}")
        print(f"Processed lines:   {format_number(processed_lines)}")
        print(f"Generated words:   {format_number(generated_words)}")
        print(f"Checkpoint:        {checkpoint_path}")
        print()

        # Very important:
        # Never append blindly. The output is truncated to the last
        # checkpoint that was known to be durable.
        if not os.path.exists(output_path):
            print(
                "ERROR: The output drive/file is not currently "
                "available. Reconnect it and run the same command again."
            )
            return False, processed_lines, original_words, generated_words

        actual_output_size = os.path.getsize(output_path)

        if actual_output_size < output_offset:
            print(
                "ERROR: Output file is smaller than the checkpoint."
            )
            print(
                f"Checkpoint expects: {format_bytes(output_offset)}"
            )
            print(
                f"Actual output:     {format_bytes(actual_output_size)}"
            )
            print(
                "The output appears to have been replaced or damaged."
            )
            return False, processed_lines, original_words, generated_words

        if actual_output_size > output_offset:
            print(
                "Recovering output: removing "
                f"{format_bytes(actual_output_size - output_offset)} "
                "of uncheckpointed data..."
            )

            with open(output_path, "r+b") as out:
                out.truncate(output_offset)

    else:
        processed_lines = 0
        original_words = 0
        generated_words = 0
        input_offset = 0
        output_offset = 0
        current_word = ""

    start_time = time.monotonic()
    last_display = start_time
    last_disk_check = start_time
    last_checkpoint = start_time
    lines_since_checkpoint = 0

    completed = False

    print()
    print("Generating word list...")
    print(f"Prefixes: {len(PREFIXES)}")
    print(f"Input:    {input_path}")
    print(f"Output:   {output_path}")
    print(f"Checkpoint: {checkpoint_path}")
    print(f"Safety margin: {format_bytes(MIN_FREE_SPACE)}")
    print()

    try:
        # Binary mode is intentional. It gives us exact byte offsets
        # that can be used with seek() after a restart.
        with open(
            input_path,
            "rb",
            buffering=BUFFER_SIZE,
        ) as inp, open(
            output_path,
            "a+",
            encoding="utf-8",
            buffering=BUFFER_SIZE,
            newline="",
        ) as out:

            # Seek to the exact place recorded in the checkpoint.
            if input_offset:
                inp.seek(input_offset)

            # Ensure output is positioned at the durable checkpoint.
            out.seek(output_offset)

            while True:
                raw_line = inp.readline()

                if not raw_line:
                    break

                # We have consumed a complete line.
                new_input_offset = inp.tell()

                word = raw_line.rstrip(b"\r\n").decode(
                    "utf-8",
                    errors="replace",
                )

                processed_lines += 1
                original_words += 1
                lines_since_checkpoint += 1

                # ------------------------------------------------
                # Check disk space periodically.
                # ------------------------------------------------

                now = time.monotonic()

                if now - last_disk_check >= DISK_CHECK_INTERVAL:
                    try:
                        free_space = get_free_space(output_path)
                    except OSError as e:
                        raise OSError(
                            getattr(e, "errno", None),
                            f"Destination drive unavailable: {e}",
                        ) from e

                    if free_space <= MIN_FREE_SPACE:
                        sync_file(out)

                        # Since the output is now durable, save the
                        # checkpoint at this exact input position.
                        durable_output_offset = out.tell()

                        save_checkpoint(
                            checkpoint_path,
                            input_path,
                            output_path,
                            input_size,
                            input_mtime,
                            total_lines,
                            processed_lines,
                            original_words,
                            generated_words,
                            new_input_offset,
                            durable_output_offset,
                            current_word,
                        )

                        clear_terminal_line()

                        print("ERROR: Output storage is almost full.")
                        print(
                            f"Free space remaining: "
                            f"{format_bytes(free_space)}"
                        )
                        print(
                            f"Safety threshold: "
                            f"{format_bytes(MIN_FREE_SPACE)}"
                        )
                        print(
                            "Stopped safely. Run the same command "
                            "after freeing space to continue."
                        )

                        return (
                            False,
                            processed_lines,
                            original_words,
                            generated_words,
                        )

                    last_disk_check = now

                # ------------------------------------------------
                # Preserve original word.
                # ------------------------------------------------

                try:
                    out.write(word)
                    out.write("\n")

                except OSError:
                    # Do not delete the checkpoint. The existing
                    # checkpoint points to the last known durable data.
                    raise

                # ------------------------------------------------
                # Generate prefixed forms.
                # ------------------------------------------------

                if word and word[0] in VOWELS:
                    for prefix in PREFIXES:
                        generated = prefix + word

                        out.write(generated)
                        out.write("\n")

                        generated_words += 1
                        current_word = generated

                else:
                    current_word = word

                # ------------------------------------------------
                # Durable checkpoint.
                # ------------------------------------------------
                #
                # The order matters:
                #
                # 1. Write output.
                # 2. flush/fsync output.
                # 3. Record input offset and output offset.
                #
                # Therefore a checkpoint never claims that data is
                # safely processed before that output is durable.
                # ------------------------------------------------

                now = time.monotonic()

                if (
                    now - last_checkpoint >= CHECKPOINT_INTERVAL
                    or lines_since_checkpoint >= CHECKPOINT_LINES
                ):
                    sync_file(out)

                    durable_output_offset = out.tell()

                    save_checkpoint(
                        checkpoint_path,
                        input_path,
                        output_path,
                        input_size,
                        input_mtime,
                        total_lines,
                        processed_lines,
                        original_words,
                        generated_words,
                        new_input_offset,
                        durable_output_offset,
                        current_word,
                    )

                    input_offset = new_input_offset
                    output_offset = durable_output_offset

                    last_checkpoint = now
                    lines_since_checkpoint = 0

                # ------------------------------------------------
                # Status display.
                # ------------------------------------------------

                if now - last_display >= 0.05:
                    try:
                        free_space = get_free_space(output_path)
                    except OSError:
                        free_space = 0

                    display_status(
                        processed_lines,
                        total_lines,
                        generated_words,
                        current_word,
                        free_space,
                        start_time,
                    )

                    last_display = now

            # ----------------------------------------------------
            # Successful end.
            # ----------------------------------------------------

            # Make absolutely everything durable before declaring
            # completion.
            sync_file(out)

            final_input_offset = inp.tell()
            final_output_offset = out.tell()

            # Save a final checkpoint too. This protects the state
            # until we have successfully finished the function.
            save_checkpoint(
                checkpoint_path,
                input_path,
                output_path,
                input_size,
                input_mtime,
                total_lines,
                processed_lines,
                original_words,
                generated_words,
                final_input_offset,
                final_output_offset,
                current_word,
            )

            completed = True

    except OSError as e:
        clear_terminal_line()

        print()
        print("=" * 70)
        print("UNEXPECTED FILE/DRIVE ERROR")
        print("=" * 70)
        print(f"{e}")
        print()

        # The last checkpoint is deliberately preserved.
        print("The last durable checkpoint has been preserved.")
        print()
        print("If the USB/external drive was disconnected:")
        print("  1. Reconnect the drive.")
        print("  2. Make sure the same drive letter is assigned.")
        print("  3. Run the exact same command again.")
        print()
        print("The script will resume from the checkpoint.")
        print()

        return (
            False,
            processed_lines,
            original_words,
            generated_words,
        )

    except KeyboardInterrupt:
        clear_terminal_line()

        print()
        print("Interrupted by user.")

        # We do NOT try to create a checkpoint here because doing
        # so would require knowing exactly how much output is durable.
        # The previous checkpoint remains the safe recovery point.
        print("The previous durable checkpoint has been preserved.")
        print("Run the same command again to resume.")

        return (
            False,
            processed_lines,
            original_words,
            generated_words,
        )

    elapsed = time.monotonic() - start_time

    clear_terminal_line()
    print()
    print("Finished successfully.")
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

    # Only remove the checkpoint after successful completion.
    delete_checkpoint(checkpoint_path)

    return (
        completed,
        processed_lines,
        original_words,
        generated_words,
    )


# ============================================================
# COMMAND LINE
# ============================================================

def usage():
    print(
        "Usage:\n"
        "  python expand_words.py INPUT.txt OUTPUT.txt\n\n"
        "Example:\n"
        "  python expand_words.py huge_words.txt expanded.txt\n\n"
        "Resume behavior:\n"
        "  Run the exact same command again after an interruption.\n"
        "  The script automatically finds the checkpoint."
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

    checkpoint_path = checkpoint_path_for(
        input_path,
        output_path,
    )

    input_size = os.path.getsize(input_path)
    input_mtime = os.path.getmtime(input_path)

    checkpoint = load_checkpoint(checkpoint_path)

    resume = None

    if checkpoint:
        if checkpoint_matches(
            checkpoint,
            input_path,
            output_path,
        ):
            print()
            print("A previous checkpoint was found.")
            print(
                f"Checkpoint: {checkpoint_path}"
            )
            print(
                f"Saved progress: "
                f"{format_number(checkpoint.get('processed_lines', 0))} "
                f"input lines"
            )
            print()

            resume = checkpoint

        else:
            print(
                "WARNING: Existing checkpoint does not match "
                "the current input/output files."
            )
            print(
                "Starting a new run instead."
            )

            delete_checkpoint(checkpoint_path)

    # The total line count is expensive for a huge input, so save it
    # in the checkpoint and reuse it on subsequent restarts.
    if resume:
        total_lines = int(resume["total_lines"])
    else:
        total_lines = count_lines(input_path)

    result = process(
        input_path,
        output_path,
        total_lines,
        checkpoint_path,
        resume,
    )

    completed = result[0]

    if completed:
        sys.exit(0)

    sys.exit(1)


if __name__ == "__main__":
    main()