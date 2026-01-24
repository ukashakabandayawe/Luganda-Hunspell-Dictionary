import argparse
import os
from pathlib import Path
import sys
from string import Template

# Utility to generate a cross-product script that hardcodes two PFX rule blocks
# and emits in-place update logic with descriptive comments.

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

DEFAULT_DESCRIPTIONS = {
    "yt": "Using the adverb yet in reflexive verbs",
    "YT": "Using the adverb yet",
    "yT": "Subject markers of adverb yet for relative pronouns",
    "ob": "Objects used in relative pronouns",
    "SC": "Subordinating conjunction when with subjects in present simple tense",
    "sc": "Subordinating conjunction when with negative subjects in present simple tense",
    "WN": "Subordinating conjunction when with subjects in near and distant past tense",
    "wn": "Subordinating conjunction when with negative subjects in near and distant past tense",
    "WM": "Subordinating conjunction when with subjects in near future tense",
    "wm": "Subordinating conjunction when with negative subjects in near future tense",
    "WF": "Subordinating conjunction when with subjects in far future tense",
    "wf": "Subordinating conjunction when with negative subjects in far future tense",
    "SB": "Permission subjunctive",
    "CC": "Counterfactual conditions",
    "St": "Adverb still",
}

TEMPLATE = Template("""import re
import os
from pathlib import Path

# Auto-generated cross-product script: $left_flag x $right_flag -> $out_flag
# Hardcoded rule blocks captured from Luganda.aff at generation time.

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

rule_left_raw = $rule_left_repr

rule_right_raw = $rule_right_repr

FLAG_DESCRIPTIONS = {
    "$left_flag": "$left_desc",
    "$right_flag": "$right_desc",
}

def parse_rules(raw_text):
    rules = []
    for line in raw_text.strip().split('\\n'):
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        s = s.split('#', 1)[0].strip()
        parts = s.split()
        if len(parts) < 4:
            continue
        if parts[2] == 'Y':
            continue
        cond = parts[4] if len(parts) > 4 else '.'
        rules.append({'strip': parts[2], 'add': parts[3], 'cond': cond})
    return rules

def generate_block():
    lefts = parse_rules(rule_left_raw)
    rights = parse_rules(rule_right_raw)
    new_rules = []

    for left in lefts:
        for right in rights:
            if left['strip'] != '0':
                if not right['add'].startswith(left['strip']):
                    continue
                combined = left['add'] + right['add'][len(left['strip']):]
            else:
                combined = left['add'] + right['add']

            if left['cond'] != '.':
                if not re.match(left['cond'], right['add']):
                    continue

            new_rules.append({'strip': right['strip'], 'add': combined, 'cond': right['cond']})

    out_flag = "$out_flag"
    left_desc = FLAG_DESCRIPTIONS.get("$left_flag", "$left_flag")
    right_desc = FLAG_DESCRIPTIONS.get("$right_flag", "$right_flag")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "$left_flag", left_desc, "$right_flag", right_desc, out_flag
    )

    output = ["PFX {} Y {}".format(out_flag, len(new_rules))]
    for r in new_rules:
        output.append("PFX {} {} {} {}".format(out_flag, r['strip'], r['add'], r['cond']))

    return (out_flag, "\\n".join([comment_line] + output) + "\\n")

def main():
    if not os.path.exists(AFF_FILE):
        print("Error: {} not found.".format(AFF_FILE))
        return

    out_flag, block = generate_block()

    with open(AFF_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    first_flag_idx = None
    last_flag_idx = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("PFX {} ".format(out_flag)):
            if first_flag_idx is None:
                first_flag_idx = i
            last_flag_idx = i

    if first_flag_idx is not None and first_flag_idx > 0:
        prev_line = lines[first_flag_idx - 1].strip()
        if prev_line.startswith("# Cross product"):
            start_idx = first_flag_idx - 1
        else:
            start_idx = first_flag_idx
    elif first_flag_idx is not None:
        start_idx = first_flag_idx
    else:
        start_idx = None

    if start_idx is not None and last_flag_idx is not None:
        new_lines = lines[:start_idx] + [block] + lines[last_flag_idx + 1:]
    else:
        new_lines = lines
        if new_lines and not new_lines[-1].endswith(chr(10)):
            new_lines[-1] += chr(10)
        new_lines.append(block)

    with open(AFF_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print("{}: updated in place.".format(out_flag))

if __name__ == '__main__':
    main()
""")

def extract_block(flag: str) -> str:
    if not AFF_FILE.exists():
        sys.exit("Error: {} not found".format(AFF_FILE))
    lines = AFF_FILE.read_text(encoding='utf-8').splitlines()
    block = [ln for ln in lines if ln.strip().startswith("PFX {} ".format(flag))]
    if not block:
        sys.exit("Error: flag {} not found in {}".format(flag, AFF_FILE))
    return "\n".join(block) + "\n"

def build_script(left_flag: str, right_flag: str, out_flag: str, out_path: Path, left_desc: str, right_desc: str) -> None:
    rule_left = extract_block(left_flag)
    rule_right = extract_block(right_flag)

    script_text = TEMPLATE.substitute(
        left_flag=left_flag,
        right_flag=right_flag,
        out_flag=out_flag,
        rule_left_repr=repr(rule_left.rstrip('\n')),
        rule_right_repr=repr(rule_right.rstrip('\n')),
        left_desc=left_desc,
        right_desc=right_desc,
    )

    out_path.write_text(script_text, encoding='utf-8')
    print("Wrote {}".format(out_path))

def main_cli():
    parser = argparse.ArgumentParser(description="Generate a cross-product script that hardcodes two PFX rule blocks.")
    parser.add_argument('--left', help='Left flag (e.g. SC)', dest='left')
    parser.add_argument('--right', help='Right flag (e.g. Ob)', dest='right')
    parser.add_argument('--out', help='Output flag (e.g. FD)', dest='out_flag')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing script')
    args = parser.parse_args()

    left = args.left or input("Enter left flag: ").strip()
    right = args.right or input("Enter right flag: ").strip()
    out_flag = args.out_flag or input("Enter output flag: ").strip()

    if not (left and right and out_flag):
        sys.exit("Error: all flags are required")

    left_desc = DEFAULT_DESCRIPTIONS.get(left, left)
    right_desc = DEFAULT_DESCRIPTIONS.get(right, right)

    filename = "update_aff_cross_{}_{}_to_{}.py".format(left, right, out_flag)
    out_path = Path(__file__).resolve().parent / filename

    if out_path.exists() and not args.overwrite:
        sys.exit("Error: {} already exists (use --overwrite to replace)".format(out_path))

    build_script(left, right, out_flag, out_path, left_desc, right_desc)

if __name__ == '__main__':
    main_cli()

