import re
import os
from pathlib import Path

# Cross product generator: ob x Rn => BN
# Description:
# - Left block `ob`: Objects used in relative pronouns
# - Right block `Rn`: Rn
# - Output flag `BN`: Cross-product prefixes for ob x Rn

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX ob Y 16
PFX ob 0 be [^aeiou]
PFX ob 0 gwe [^aeiou]
PFX ob 0 gye [^aeiou]
PFX ob 0 ze [^aeiou]
PFX ob 0 kye [^aeiou]
PFX ob 0 kye [^aeiou]
PFX ob 0 bye [^aeiou]
PFX ob 0 lye [^aeiou]
PFX ob 0 ge [^aeiou]
PFX ob 0 ke [^aeiou]
PFX ob 0 bwe [^aeiou]
PFX ob 0 lwe [^aeiou]
PFX ob 0 ze [^aeiou]
PFX ob 0 kwe [^aeiou]
PFX ob 0 ge [^aeiou]
PFX ob 0 twe [^aeiou]"""

rule_right_raw = """
PFX Rn Y 34
PFX Rn 0 nnee .
PFX Rn 0 onee .
PFX Rn 0 anee .
PFX Rn 0 tunee .
PFX Rn 0 munee .
PFX Rn 0 banee .
PFX Rn 0 gunee .
PFX Rn 0 ogunee .
PFX Rn 0 ginee .
PFX Rn 0 eginee .
PFX Rn 0 zinee .
PFX Rn 0 ezinee .
PFX Rn 0 kinee .
PFX Rn 0 ekinee .
PFX Rn 0 binee .
PFX Rn 0 ebinee .
PFX Rn 0 linee .
PFX Rn 0 elinee .
PFX Rn 0 ganee .
PFX Rn 0 aganee .
PFX Rn 0 kanee .
PFX Rn 0 akanee .
PFX Rn 0 bunee .
PFX Rn 0 obunee .
PFX Rn 0 lunee .
PFX Rn 0 olunee .
PFX Rn 0 zinee .
PFX Rn 0 ezinee .
PFX Rn 0 kunee .
PFX Rn 0 okunee .
PFX Rn 0 ganee .
PFX Rn 0 aganee .
PFX Rn 0 tunee .
PFX Rn 0 otunee ."""

FLAG_DESCRIPTIONS = {
    "ob": "Objects used in relative pronouns",
    "Rn": "Rn",
}

def parse_rules(raw_text):
    rules = []
    for line in raw_text.strip().split('\n'):
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

    out_flag = "BN"
    left_desc = FLAG_DESCRIPTIONS.get("ob", "ob")
    right_desc = FLAG_DESCRIPTIONS.get("Rn", "Rn")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "ob", left_desc, "Rn", right_desc, out_flag
    )

    output = ["PFX {} Y {}".format(out_flag, len(new_rules))]
    for r in new_rules:
        output.append("PFX {} {} {} {}".format(out_flag, r['strip'], r['add'], r['cond']))

    return (out_flag, "\n".join([comment_line] + output) + "\n")

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
        # Replace existing block in-place.
        new_lines = lines[:start_idx] + [block] + lines[last_flag_idx + 1:]
    else:
        # Insert before an anchor flag if requested; otherwise append.
        insert_idx = None
        if INSERT_BEFORE_FLAG:
            anchor_prefix = "PFX {} ".format(INSERT_BEFORE_FLAG)
            for i, line in enumerate(lines):
                if line.strip().startswith(anchor_prefix):
                    insert_idx = i
                    # If the anchor PFX block is preceded by one or more cross-product
                    # comment lines, insert before those comments to keep them attached
                    # to the anchor block.
                    while insert_idx > 0 and lines[insert_idx - 1].strip().startswith("# Cross product"):
                        insert_idx -= 1
                    break

        if insert_idx is not None:
            new_lines = lines[:insert_idx] + [block] + lines[insert_idx:]
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
