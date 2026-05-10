import re
import os
from pathlib import Path

# Cross product generator: ob x PS => BD
# Description:
# - Left block `ob`: Objects used in relative pronouns
# - Right block `PS`: Present simple tense subject markers
# - Output flag `BD`: Cross-product prefixes for ob x PS

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
PFX PS Y 30
PFX PS j nzi jj # It creates nzija from stem "jja"
PFX PS z nzi zze # It creates nzize
PFX PS j n   jj # It handles the word "nja" (the singular of tujja) so, Luganda.dic should have "jja" entry with NEEDAFFIX flag plus other flags
PFX PS y nj  y.[^mn] # yiga-->njiga
PFX PS 0 n   [^jbnmlhprxq] # Person marker
PFX PS 0 m   b # Person marker: buuka-->mbuuka
PFX PS b mm  banja
PFX PS 0 o   . # Person marker
PFX PS l nd  l.[^mn] # Person marker: lya-->ndya
PFX PS l nn  l.[mn][^u] # Person marker: luma-->nnuma
PFX PS w mp  w # Person marker: wandiika --> mpandiika
PFX PS 0 a   . # Person marker
PFX PS 0 tu  . # Person marker
PFX PS 0 mu  . # Person marker
PFX PS 0 ba  . # Person marker
PFX PS 0 a   [^aeiou]
PFX PS 0 ba  . MORPH:tense=present MORPH:number=plural MORPH:pos=verb MORPH:class=1 MORPH:polarity=negative
PFX PS 0 gu  .
PFX PS 0 gi  .
PFX PS 0 e   [^aeiou]
PFX PS 0 zi  .
PFX PS 0 ki  .
PFX PS 0 bi  .
PFX PS 0 li  .
PFX PS 0 ga  .
PFX PS 0 ka  .
PFX PS 0 bu  .
PFX PS 0 lu  .
PFX PS 0 ku  .
PFX PS 0 tu  ."""

FLAG_DESCRIPTIONS = {
    "ob": "Objects used in relative pronouns",
    "PS": "Present simple tense subject markers",
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

    out_flag = "BD"
    left_desc = FLAG_DESCRIPTIONS.get("ob", "ob")
    right_desc = FLAG_DESCRIPTIONS.get("PS", "PS")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "ob", left_desc, "PS", right_desc, out_flag
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
