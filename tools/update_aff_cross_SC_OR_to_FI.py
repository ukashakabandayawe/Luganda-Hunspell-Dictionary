import re
import os
from pathlib import Path

# Cross product generator: SC x OR => FI
# Description:
# - Left block `SC`: Subordinating conjunction when with subjects in present simple tense
# - Right block `OR`: Special reflexive object markers
# - Output flag `FI`: Cross-product prefixes for SC x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX SC Y 190
PFX SC j wenzi jj # It creates wenzija from stem "jja"
PFX SC 0 wen [^jbnmlhprxq] # Person marker
PFX SC 0 wem [b] # Person marker
PFX SC l wend [l] # Person marker
PFX SC 0 wetu . # Person marker
PFX SC 0 wemu . # Person marker
PFX SC 0 weba . # Person marker
PFX SC 0 wegu .
PFX SC 0 wegi .
PFX SC 0 wezi .
PFX SC 0 weki .
PFX SC 0 webi .
PFX SC 0 weli .
PFX SC 0 wega .
PFX SC 0 weka .
PFX SC 0 webu .
PFX SC 0 welu .
PFX SC 0 weku .
PFX SC 0 wetu .
PFX SC j bwenzi jj # It creates bwenzija from stem "jja"
PFX SC 0 bwen [^jbnmlhprxq] # Person marker
PFX SC 0 bwem [b] # Person marker
PFX SC l bwend [l] # Person marker
PFX SC 0 bwetu . # Person marker
PFX SC 0 bwemu . # Person marker
PFX SC 0 bweba . # Person marker
PFX SC 0 bwegu .
PFX SC 0 bwegi .
PFX SC 0 bwezi .
PFX SC 0 bweki .
PFX SC 0 bwebi .
PFX SC 0 bweli .
PFX SC 0 bwega .
PFX SC 0 bweka .
PFX SC 0 bwebu .
PFX SC 0 bwelu .
PFX SC 0 bweku .
PFX SC 0 bwetu .
PFX SC j lwenzi jj # It creates lwenzija from stem "jja"
PFX SC 0 lwen [^jbnmlhprxq] # Person marker
PFX SC 0 lwem [b] # Person marker
PFX SC l lwend [l] # Person marker
PFX SC 0 lwetu . # Person marker
PFX SC 0 lwemu . # Person marker
PFX SC 0 lweba . # Person marker
PFX SC 0 lwegu .
PFX SC 0 lwegi .
PFX SC 0 lwezi .
PFX SC 0 lweki .
PFX SC 0 lwebi .
PFX SC 0 lweli .
PFX SC 0 lwega .
PFX SC 0 lweka .
PFX SC 0 lwebu .
PFX SC 0 lwelu .
PFX SC 0 lweku .
PFX SC 0 lwetu .
PFX SC j zenzi jj # It creates zenzija from stem "jja"
PFX SC 0 zen [^jbnmlhprxq] # Person marker
PFX SC 0 zem [b] # Person marker
PFX SC l zend [l] # Person marker
PFX SC 0 zetu . # Person marker
PFX SC 0 zemu . # Person marker
PFX SC 0 zeba . # Person marker
PFX SC 0 zegu .
PFX SC 0 zegi .
PFX SC 0 zezi .
PFX SC 0 zeki .
PFX SC 0 zebi .
PFX SC 0 zeli .
PFX SC 0 zega .
PFX SC 0 zeka .
PFX SC 0 zebu .
PFX SC 0 zelu .
PFX SC 0 zeku .
PFX SC 0 zetu .
PFX SC j gwenzi jj # It creates gwenzija from stem "jja"
PFX SC 0 gwen [^jbnmlhprxq] # Person marker
PFX SC 0 gwem [b] # Person marker
PFX SC l gwend [l] # Person marker
PFX SC 0 gwetu . # Person marker
PFX SC 0 gwemu . # Person marker
PFX SC 0 gweba . # Person marker
PFX SC 0 gwegu .
PFX SC 0 gwegi .
PFX SC 0 gwezi .
PFX SC 0 gweki .
PFX SC 0 gwebi .
PFX SC 0 gweli .
PFX SC 0 gwega .
PFX SC 0 gweka .
PFX SC 0 gwebu .
PFX SC 0 gwelu .
PFX SC 0 gweku .
PFX SC 0 gwetu .
PFX SC j gyenzi jj # It creates gyenzija from stem "jja"
PFX SC 0 gyen [^jbnmlhprxq] # Person marker
PFX SC 0 gyem [b] # Person marker
PFX SC l gyend [l] # Person marker
PFX SC 0 gyetu . # Person marker
PFX SC 0 gyemu . # Person marker
PFX SC 0 gyeba . # Person marker
PFX SC 0 gyegu .
PFX SC 0 gyegi .
PFX SC 0 gyezi .
PFX SC 0 gyeki .
PFX SC 0 gyebi .
PFX SC 0 gyeli .
PFX SC 0 gyega .
PFX SC 0 gyeka .
PFX SC 0 gyebu .
PFX SC 0 gyelu .
PFX SC 0 gyeku .
PFX SC 0 gyetu .
PFX SC j kyenzi jj # It creates kyenzija from stem "jja"
PFX SC 0 kyen [^jbnmlhprxq] # Person marker
PFX SC 0 kyem [b] # Person marker
PFX SC l kyend [l] # Person marker
PFX SC 0 kyetu . # Person marker
PFX SC 0 kyemu . # Person marker
PFX SC 0 kyeba . # Person marker
PFX SC 0 kyegu .
PFX SC 0 kyegi .
PFX SC 0 kyezi .
PFX SC 0 kyeki .
PFX SC 0 kyebi .
PFX SC 0 kyeli .
PFX SC 0 kyega .
PFX SC 0 kyeka .
PFX SC 0 kyebu .
PFX SC 0 kyelu .
PFX SC 0 kyeku .
PFX SC 0 kyetu .
PFX SC j byenzi jj # It creates byenzija from stem "jja"
PFX SC 0 byen [^jbnmlhprxq] # Person marker
PFX SC 0 byem [b] # Person marker
PFX SC l byend [l] # Person marker
PFX SC 0 byetu . # Person marker
PFX SC 0 byemu . # Person marker
PFX SC 0 byeba . # Person marker
PFX SC 0 byegu .
PFX SC 0 byegi .
PFX SC 0 byezi .
PFX SC 0 byeki .
PFX SC 0 byebi .
PFX SC 0 byeli .
PFX SC 0 byega .
PFX SC 0 byeka .
PFX SC 0 byebu .
PFX SC 0 byelu .
PFX SC 0 byeku .
PFX SC 0 byetu .
PFX SC j lyenzi jj # It creates lyenzija from stem "jja"
PFX SC 0 lyen [^jbnmlhprxq] # Person marker
PFX SC 0 lyem [b] # Person marker
PFX SC l lyend [l] # Person marker
PFX SC 0 lyetu . # Person marker
PFX SC 0 lyemu . # Person marker
PFX SC 0 lyeba . # Person marker
PFX SC 0 lyegu .
PFX SC 0 lyegi .
PFX SC 0 lyezi .
PFX SC 0 lyeki .
PFX SC 0 lyebi .
PFX SC 0 lyeli .
PFX SC 0 lyega .
PFX SC 0 lyeka .
PFX SC 0 lyebu .
PFX SC 0 lyelu .
PFX SC 0 lyeku .
PFX SC 0 lyetu .
PFX SC j kenzi jj # It creates kenzija from stem "jja"
PFX SC 0 ken [^jbnmlhprxq] # Person marker
PFX SC 0 kem [b] # Person marker
PFX SC l kend [l] # Person marker
PFX SC 0 ketu . # Person marker
PFX SC 0 kemu . # Person marker
PFX SC 0 keba . # Person marker
PFX SC 0 kegu .
PFX SC 0 kegi .
PFX SC 0 kezi .
PFX SC 0 keki .
PFX SC 0 kebi .
PFX SC 0 keli .
PFX SC 0 kega .
PFX SC 0 keka .
PFX SC 0 kebu .
PFX SC 0 kelu .
PFX SC 0 keku .
PFX SC 0 ketu ."""

rule_right_raw = """
PFX OR Y 16
PFX OR 0 mwe .
PFX OR 0 bee .
PFX OR 0 gwe .
PFX OR 0 gye .
PFX OR 0 zee .
PFX OR 0 kye .
PFX OR 0 bye .
PFX OR 0 lye .
PFX OR 0 gee .
PFX OR 0 kee .
PFX OR 0 bwe .
PFX OR 0 lwe .
PFX OR 0 zee .
PFX OR 0 kwe .
PFX OR 0 gee .
PFX OR 0 twe ."""

FLAG_DESCRIPTIONS = {
    "SC": "Subordinating conjunction when with subjects in present simple tense",
    "OR": "Special reflexive object markers",
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

    out_flag = "FI"
    left_desc = FLAG_DESCRIPTIONS.get("SC", "SC")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "SC", left_desc, "OR", right_desc, out_flag
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
