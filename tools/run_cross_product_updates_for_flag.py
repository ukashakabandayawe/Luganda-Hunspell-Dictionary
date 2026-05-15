"""Run cross-product update scripts impacted by an updated Hunspell flag.

Usage:
  python tools/run_cross_product_updates_for_flag.py
  python tools/run_cross_product_updates_for_flag.py --flag Ob
  python tools/run_cross_product_updates_for_flag.py --flag Ob --dry-run
    python tools/run_cross_product_updates_for_flag.py --flag Ob --sync-only

What it does:
- Discovers scripts named: tools/update_aff_cross_<LEFT>_<RIGHT>_to_<OUT>.py
- Asks for an updated flag (unless --flag is provided)
- Runs every discovered cross-product script where LEFT or RIGHT matches the updated flag,
  and then continues transitively (if a script generates OUT, any scripts that use OUT
  as LEFT/RIGHT are also run), so dependent cross-products stay in sync.

Notes:
- Matching is case-sensitive (Hunspell flags are case-sensitive in this repo).
- By default, the runner will sync the updated flag's hard-coded `rule_left_raw`/
    `rule_right_raw` blocks inside impacted cross scripts from the current `Luganda.aff`
    before executing them. Use `--no-sync-scripts` to disable.

Sync behavior:
- The sync is *delta-based* by default: it updates matching rules in-place (keyed by
    `strip+add`) and adds missing `PFX <flag> ...` rule lines found in `Luganda.aff`.
- If you want deletions synchronized too, use `--sync-mode add-delete`.
- To protect hand-tweaked lines from deletion when using `add-delete`, add a keep marker
    like `# keep` at the end of that line inside the script's raw block.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Set, Tuple


@dataclass(frozen=True)
class CrossScript:
    path: Path
    left: str
    right: str
    out: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _aff_path() -> Path:
    return _repo_root() / "Luganda.aff"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_pfx_block_from_aff(aff_text: str, flag: str) -> Optional[str]:
    """Extract the PFX block (header + rule lines) for `flag` from Luganda.aff.

    Returns a normalized block string with '\n' newlines and no trailing whitespace.
    """
    lines = aff_text.splitlines()

    header_idx = None
    header_parts: Optional[list[str]] = None
    for i, raw in enumerate(lines):
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if len(parts) >= 4 and parts[0] == "PFX" and parts[1] == flag and parts[2] in ("Y", "N"):
            header_idx = i
            header_parts = parts
            break

    if header_idx is None or header_parts is None:
        return None

    rules: List[str] = []
    for j in range(header_idx + 1, len(lines)):
        s = lines[j].strip()
        if not s or s.startswith("#"):
            continue

        parts = s.split()
        # Rule lines look like: PFX <flag> <strip> <add> <cond>
        if len(parts) >= 4 and parts[0] == "PFX" and parts[1] == flag and parts[2] not in ("Y", "N"):
            rules.append(s)
        else:
            # Stop if we hit something that isn't part of the flag's PFX rules.
            break

    # Recompute the count from the rules we actually found.
    # This makes the sync resilient when Luganda.aff's header count wasn't updated.
    allow = header_parts[2]
    header_line = f"PFX {flag} {allow} {len(rules)}"
    return "\n".join([header_line] + rules)


def _normalize_rule_identity(line: str) -> str:
    """Normalize a PFX rule line for comparison.

    - Strips trailing inline comments (anything after '#')
    - Collapses whitespace
    """
    base = line.split("#", 1)[0].strip()
    return " ".join(base.split())


def _is_header_line_for_flag(line: str, flag: str) -> bool:
    s = _normalize_rule_identity(line)
    parts = s.split()
    return (
        len(parts) >= 4
        and parts[0] == "PFX"
        and parts[1] == flag
        and parts[2] in ("Y", "N")
    )


def _is_rule_line_for_flag(line: str, flag: str) -> bool:
    s = _normalize_rule_identity(line)
    parts = s.split()
    return (
        len(parts) >= 4
        and parts[0] == "PFX"
        and parts[1] == flag
        and parts[2] not in ("Y", "N")
    )


def _parse_aff_rules(block: str, flag: str) -> List[str]:
    """Parse a `PFX <flag> ...` block text into rule lines (excluding header)."""
    rules: List[str] = []
    for raw in block.splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        if _is_header_line_for_flag(s, flag):
            continue
        if _is_rule_line_for_flag(s, flag):
            rules.append(_normalize_rule_identity(s))
    return rules


def _parse_rule_fields(line: str, flag: str) -> Optional[tuple[str, str, str, str]]:
    """Parse a single rule line into (strip, add, cond, comment).

    Returns None if line doesn't look like a PFX rule line for this flag.
    """
    if not _is_rule_line_for_flag(line, flag):
        return None

    before, hashmark, after = line.partition("#")
    comment = (hashmark + after).rstrip() if hashmark else ""

    parts = before.strip().split()
    if len(parts) < 4:
        return None

    # Format: PFX <flag> <strip> <add> <cond>
    strip = parts[2]
    add = parts[3]
    cond = parts[4] if len(parts) > 4 else "."
    return strip, add, cond, comment


def _sig(strip: str, add: str) -> tuple[str, str]:
    return (strip, add)


_RAW_BLOCK_RE = re.compile(
    r"(?P<prefix>\brule_(?P<side>left|right)_raw\s*=\s*\"\"\")(?P<body>.*?)(?P<suffix>\"\"\")",
    re.DOTALL,
)


def sync_cross_script_raw_blocks_from_aff(
    script_path: Path,
    *,
    updated_flags: Sequence[str],
    aff_blocks: dict[str, str],
    left_flag: str,
    right_flag: str,
    sync_mode: str,
    keep_marker: str,
) -> bool:
    """Sync hard-coded rule raw blocks for updated flags from aff.

    Returns True if the file was modified.
    """
    text = read_text(script_path)
    original = text

    def replace_match(m: re.Match) -> str:
        side = m.group("side")
        current_body = m.group("body")
        flag_for_side = left_flag if side == "left" else right_flag

        if flag_for_side not in updated_flags:
            return m.group(0)

        aff_block = aff_blocks.get(flag_for_side)
        if not aff_block:
            return m.group(0)

        return _sync_raw_block_delta(
            prefix=m.group("prefix"),
            body=current_body,
            suffix=m.group("suffix"),
            flag=flag_for_side,
            aff_block=aff_block,
            sync_mode=sync_mode,
            keep_marker=keep_marker,
        )

    text = _RAW_BLOCK_RE.sub(replace_match, text)

    if text != original:
        script_path.write_text(text, encoding="utf-8")
        return True

    return False


def _sync_raw_block_delta(
    *,
    prefix: str,
    body: str,
    suffix: str,
    flag: str,
    aff_block: str,
    sync_mode: str,
    keep_marker: str,
) -> str:
    """Return updated triple-quoted raw block (prefix+body+suffix) with delta sync."""

    # Sync mode meanings:
    # - add-only: only append missing rules from aff
    # - add-update: update matching rules in-place (by strip+add) and append missing
    # - add-delete: add-update + delete rules missing from aff (unless protected by keep_marker)

    body_lines = body.splitlines()

    # Find header + rule lines in the script body.
    header_idx: Optional[int] = None
    allow: Optional[str] = None
    for i, line in enumerate(body_lines):
        if _is_header_line_for_flag(line, flag):
            header_idx = i
            parts = _normalize_rule_identity(line).split()
            allow = parts[2]
            break

    if header_idx is None or allow is None:
        # If the raw block isn't in the expected format, don't touch it.
        return prefix + body + suffix

    # Collect indices of rule lines.
    rule_indices: List[int] = []
    script_rule_identities: List[str] = []
    script_rule_identity_set: Set[str] = set()

    for i, line in enumerate(body_lines):
        if _is_rule_line_for_flag(line, flag):
            ident = _normalize_rule_identity(line)
            rule_indices.append(i)
            script_rule_identities.append(ident)
            script_rule_identity_set.add(ident)

    aff_rules = _parse_aff_rules(aff_block, flag)
    aff_rule_set = set(aff_rules)

    # Build aff signature map: (strip, add) -> full normalized rule line.
    aff_sig_map: dict[tuple[str, str], str] = {}
    for r in aff_rules:
        # r is normalized like: "PFX Ob 0 n [^lmnbp]"
        parts = r.split()
        if len(parts) < 4:
            continue
        if parts[0] != "PFX" or parts[1] != flag:
            continue
        strip = parts[2]
        add = parts[3]
        aff_sig_map[_sig(strip, add)] = r

    # Update-in-place: if a script rule has the same (strip, add) signature but differs,
    # replace it with the aff version (preserving trailing comments), unless protected.
    if sync_mode in ("add-update", "add-delete"):
        keep_marker_l = keep_marker.lower()
        for i, line in enumerate(body_lines):
            parsed = _parse_rule_fields(line, flag)
            if not parsed:
                continue
            strip, add, _cond, comment = parsed
            replacement = aff_sig_map.get(_sig(strip, add))
            if not replacement:
                continue
            if keep_marker_l in line.lower():
                continue

            current_norm = _normalize_rule_identity(line)
            if current_norm == replacement:
                continue

            # Preserve any existing comment/trailing notes.
            body_lines[i] = (replacement + ("  " + comment if comment else "")).rstrip()

    # Optionally delete rules that no longer exist in aff.
    if sync_mode == "add-delete" and rule_indices:
        keep_marker_l = keep_marker.lower()
        new_body_lines: List[str] = []
        for line in body_lines:
            if _is_rule_line_for_flag(line, flag):
                ident = _normalize_rule_identity(line)
                protected = keep_marker_l in line.lower()
                if (ident not in aff_rule_set) and not protected:
                    continue
            new_body_lines.append(line)
        body_lines = new_body_lines

    # Recompute rules after deletion to determine what's missing.
    script_rule_identity_set = set()
    for line in body_lines:
        if _is_rule_line_for_flag(line, flag):
            script_rule_identity_set.add(_normalize_rule_identity(line))

    missing_rules = [r for r in aff_rules if r not in script_rule_identity_set]

    if missing_rules:
        # Append missing rules at the end of the block.
        # (Rule ordering is not critical, and this preserves any hand-tweaked ordering.)
        # Ensure body has at least one newline separation (we're inside triple quotes).
        if body_lines and body_lines[-1].strip() != "":
            body_lines.append("")
        body_lines.extend(missing_rules)

    # Update header count to match the number of rule lines currently present.
    rule_count = sum(1 for line in body_lines if _is_rule_line_for_flag(line, flag))
    body_lines[header_idx] = f"PFX {flag} {allow} {rule_count}"

    # Preserve leading/trailing newline behavior inside triple quotes.
    new_body = "\n" + "\n".join(body_lines).strip("\n") + "\n"
    return prefix + new_body + suffix


def discover_cross_scripts(tools_dir: Path) -> List[CrossScript]:
    scripts: List[CrossScript] = []
    for path in sorted(tools_dir.glob("update_aff_cross_*.py")):
        stem = path.stem
        parts = stem.split("_")
        # Expected: update aff cross <LEFT> <RIGHT> to <OUT>
        if len(parts) < 7:
            continue
        if parts[0] != "update" or parts[1] != "aff" or parts[2] != "cross":
            continue
        if parts[5] != "to":
            continue
        left = parts[3]
        right = parts[4]
        out = parts[6]
        scripts.append(CrossScript(path=path, left=left, right=right, out=out))
    return scripts


def parse_flag_list(raw: str) -> List[str]:
    # Allow: "Ob" or "Ob,OR" or "Ob OR" etc.
    items: List[str] = []
    for chunk in raw.replace(",", " ").split():
        s = chunk.strip()
        if s:
            items.append(s)
    return items


def compute_impacted_scripts(
    scripts: Sequence[CrossScript], updated_flags: Sequence[str]
) -> Tuple[List[CrossScript], Set[str]]:
    """Return (scripts_to_run_in_order, all_flags_seen_as_impacted)."""

    remaining = list(scripts)
    to_run: List[CrossScript] = []
    seen_scripts: Set[Path] = set()

    seen_flags: Set[str] = set(updated_flags)
    queue: List[str] = list(updated_flags)

    # Discovery order: as new outputs are produced, we enqueue them and continue.
    while queue:
        flag = queue.pop(0)

        for script in remaining:
            if script.path in seen_scripts:
                continue
            if script.left == flag or script.right == flag:
                seen_scripts.add(script.path)
                to_run.append(script)
                if script.out not in seen_flags:
                    seen_flags.add(script.out)
                    queue.append(script.out)

    return to_run, seen_flags


def collect_known_flags(scripts: Sequence[CrossScript]) -> Set[str]:
    flags: Set[str] = set()
    for s in scripts:
        flags.add(s.left)
        flags.add(s.right)
        flags.add(s.out)
    return flags


def run_scripts(
    scripts: Sequence[CrossScript], *, python_exe: str, cwd: Path
) -> int:
    failures = 0
    for idx, s in enumerate(scripts, start=1):
        rel = s.path.relative_to(cwd)
        print(f"[{idx}/{len(scripts)}] Running {rel} ({s.left} x {s.right} => {s.out})")
        completed = subprocess.run(
            [python_exe, str(s.path)],
            cwd=str(cwd),
            capture_output=True,
            text=True,
        )
        if completed.stdout.strip():
            print(completed.stdout.rstrip())
        if completed.returncode != 0:
            failures += 1
            if completed.stderr.strip():
                print(completed.stderr.rstrip(), file=sys.stderr)
            else:
                print(f"ERROR: {rel} exited with code {completed.returncode}", file=sys.stderr)
        elif completed.stderr.strip():
            # Some scripts may write warnings to stderr.
            print(completed.stderr.rstrip(), file=sys.stderr)

    if failures:
        print(f"Done with {failures} failure(s).", file=sys.stderr)
        return 1

    print("Done.")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run all cross-product update scripts impacted by an updated Hunspell flag."
    )
    parser.add_argument(
        "--flag",
        help="Updated flag name (case-sensitive). If omitted, you'll be prompted.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print which scripts would run.",
    )
    parser.add_argument(
        "--no-sync-scripts",
        action="store_true",
        help="Do not sync hard-coded raw blocks inside cross scripts from Luganda.aff.",
    )
    parser.add_argument(
        "--sync-only",
        action="store_true",
        help="Only sync impacted scripts (no execution).",
    )
    parser.add_argument(
        "--sync-mode",
        choices=("add-only", "add-update", "add-delete"),
        default="add-update",
        help=(
            "How to sync script raw blocks from Luganda.aff. "
            "'add-only' adds missing lines; 'add-update' also updates matching rules in-place (by strip+add); "
            "'add-delete' does add-update plus deletes lines missing from aff unless protected by --keep-marker."
        ),
    )
    parser.add_argument(
        "--keep-marker",
        default="# keep",
        help="Substring to protect a line from deletion in 'add-delete' mode (case-insensitive).",
    )

    args = parser.parse_args(argv)

    tools_dir = Path(__file__).resolve().parent
    scripts = discover_cross_scripts(tools_dir)

    if not scripts:
        print(f"No cross-product scripts found in {tools_dir}.", file=sys.stderr)
        return 2

    raw_flag = (args.flag or "").strip() or input("Enter updated flag (e.g. Ob): ").strip()
    updated_flags = parse_flag_list(raw_flag)
    if not updated_flags:
        print("No updated flag provided.", file=sys.stderr)
        return 2

    known = collect_known_flags(scripts)
    for f in updated_flags:
        if f not in known:
            # Keep going, but provide a hint.
            near = sorted([k for k in known if k.lower() == f.lower()])
            if near:
                print(
                    f"Warning: flag '{f}' not found exactly; case variants exist: {', '.join(near)}",
                    file=sys.stderr,
                )
            else:
                print(
                    f"Warning: flag '{f}' not found in any discovered script inputs/outputs.",
                    file=sys.stderr,
                )

    to_run, impacted_flags = compute_impacted_scripts(scripts, updated_flags)

    if not to_run:
        print("No cross-product scripts matched the updated flag(s).")
        return 0

    print(f"Updated flag(s): {', '.join(updated_flags)}")
    print(f"Impacted scripts: {len(to_run)}")

    for s in to_run:
        rel = s.path.relative_to(_repo_root())
        print(f"- {rel} ({s.left} x {s.right} => {s.out})")

    if args.dry_run:
        return 0

    # Sync the updated flag's hard-coded blocks in impacted scripts before executing.
    if not args.no_sync_scripts:
        aff_file = _aff_path()
        if not aff_file.exists():
            print(f"Warning: {aff_file} not found; skipping script sync.", file=sys.stderr)
        else:
            aff_text = read_text(aff_file)
            aff_blocks: dict[str, str] = {}
            for f in updated_flags:
                block = extract_pfx_block_from_aff(aff_text, f)
                if block is None:
                    print(f"Warning: PFX block for '{f}' not found in Luganda.aff; skipping sync for that flag.", file=sys.stderr)
                else:
                    aff_blocks[f] = block

            changed = 0
            for s in to_run:
                if not (s.left in updated_flags or s.right in updated_flags):
                    continue
                did_change = sync_cross_script_raw_blocks_from_aff(
                    s.path,
                    updated_flags=updated_flags,
                    aff_blocks=aff_blocks,
                    left_flag=s.left,
                    right_flag=s.right,
                    sync_mode=args.sync_mode,
                    keep_marker=args.keep_marker,
                )
                if did_change:
                    changed += 1

            print(f"Synced scripts from Luganda.aff: {changed} file(s) updated.")

    if args.sync_only:
        return 0

    return run_scripts(to_run, python_exe=sys.executable, cwd=_repo_root())


if __name__ == "__main__":
    raise SystemExit(main())
