import re
import os
from pathlib import Path

# Cross product generator: sc x Ob => FE
# Description:
# - Left block `sc`: Subordinating conjunction when with negative subjects in present simple tense
# - Right block `Ob`: Object markers
# - Output flag `FE`: Cross-product prefixes for sc x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX sc Y 173
PFX sc 0 wessi [^mn]
PFX sc 0 wessi mu
PFX sc 0 wetuta .
PFX sc 0 wemuta .
PFX sc 0 webata .
PFX sc 0 weguta .
PFX sc 0 wegita .
PFX sc 0 wezita .
PFX sc 0 wekita .
PFX sc 0 webita .
PFX sc 0 welita .
PFX sc 0 wegata .
PFX sc 0 wekata .
PFX sc 0 webuta .
PFX sc 0 weluta .
PFX sc 0 wekuta .
PFX sc 0 wetuta .
PFX sc 0 bwessi [^mn]
PFX sc 0 bwessi mu
PFX sc 0 bwetuta .
PFX sc 0 bwemuta .
PFX sc 0 bwebata .
PFX sc 0 bweguta .
PFX sc 0 bwegita .
PFX sc 0 bwezita .
PFX sc 0 bwekita .
PFX sc 0 bwebita .
PFX sc 0 bwelita .
PFX sc 0 bwegata .
PFX sc 0 bwekata .
PFX sc 0 bwebuta .
PFX sc 0 bweluta .
PFX sc 0 bwekuta .
PFX sc 0 bwetuta .
PFX sc 0 lwessi [^mn]
PFX sc 0 lwessi mu
PFX sc 0 lwetuta .
PFX sc 0 lwemuta .
PFX sc 0 lwebata .
PFX sc 0 lweguta .
PFX sc 0 lwegita .
PFX sc 0 lwezita .
PFX sc 0 lwekita .
PFX sc 0 lwebita .
PFX sc 0 lwelita .
PFX sc 0 lwegata .
PFX sc 0 lwekata .
PFX sc 0 lwebuta .
PFX sc 0 lweluta .
PFX sc 0 lwekuta .
PFX sc 0 lwetuta .
PFX sc 0 zessi [^mn]
PFX sc 0 zessi mu
PFX sc 0 zetuta .
PFX sc 0 zemuta .
PFX sc 0 zebata .
PFX sc 0 zeguta .
PFX sc 0 zegita .
PFX sc 0 zezita .
PFX sc 0 zekita .
PFX sc 0 zebita .
PFX sc 0 zelita .
PFX sc 0 zegata .
PFX sc 0 zekata .
PFX sc 0 zebuta .
PFX sc 0 zeluta .
PFX sc 0 zekuta .
PFX sc 0 zetuta .
PFX sc 0 gwessi [^mn]
PFX sc 0 gwessi mu
PFX sc 0 gwetuta .
PFX sc 0 gwemuta .
PFX sc 0 gwebata .
PFX sc 0 gweguta .
PFX sc 0 gwegita .
PFX sc 0 gwezita .
PFX sc 0 gwekita .
PFX sc 0 gwebita .
PFX sc 0 gwelita .
PFX sc 0 gwegata .
PFX sc 0 gwekata .
PFX sc 0 gwebuta .
PFX sc 0 gweluta .
PFX sc 0 gwekuta .
PFX sc 0 gwetuta .
PFX sc 0 gyessi [^mn]
PFX sc 0 gyessi mu
PFX sc 0 gyetuta .
PFX sc 0 gyemuta .
PFX sc 0 gyebata .
PFX sc 0 gyeguta .
PFX sc 0 gyegita .
PFX sc 0 gyezita .
PFX sc 0 gyekita .
PFX sc 0 gyebita .
PFX sc 0 gyelita .
PFX sc 0 gyegata .
PFX sc 0 gyekata .
PFX sc 0 gyebuta .
PFX sc 0 gyeluta .
PFX sc 0 gyekuta .
PFX sc 0 gyetuta .
PFX sc 0 kyessi [^mn]
PFX sc 0 kyessi mu
PFX sc 0 kyetuta .
PFX sc 0 kyemuta .
PFX sc 0 kyebata .
PFX sc 0 kyeguta .
PFX sc 0 kyegita .
PFX sc 0 kyezita .
PFX sc 0 kyekita .
PFX sc 0 kyebita .
PFX sc 0 kyelita .
PFX sc 0 kyegata .
PFX sc 0 kyekata .
PFX sc 0 kyebuta .
PFX sc 0 kyeluta .
PFX sc 0 kyekuta .
PFX sc 0 kyetuta .
PFX sc 0 byessi [^mn]
PFX sc 0 byessi mu
PFX sc 0 byetuta .
PFX sc 0 byemuta .
PFX sc 0 byebata .
PFX sc 0 byeguta .
PFX sc 0 byegita .
PFX sc 0 byezita .
PFX sc 0 byekita .
PFX sc 0 byebita .
PFX sc 0 byelita .
PFX sc 0 byegata .
PFX sc 0 byekata .
PFX sc 0 byebuta .
PFX sc 0 byeluta .
PFX sc 0 byekuta .
PFX sc 0 byetuta .
PFX sc 0 lyessi [^mn]
PFX sc 0 lyessi mu
PFX sc 0 lyetuta .
PFX sc 0 lyemuta .
PFX sc 0 lyebata .
PFX sc 0 lyeguta .
PFX sc 0 lyegita .
PFX sc 0 lyezita .
PFX sc 0 lyekita .
PFX sc 0 lyebita .
PFX sc 0 lyelita .
PFX sc 0 lyegata .
PFX sc 0 lyekata .
PFX sc 0 lyebuta .
PFX sc 0 lyeluta .
PFX sc 0 lyekuta .
PFX sc 0 lyetuta .
PFX sc 0 kessi [^mn]
PFX sc 0 kessi mu
PFX sc 0 ketuta .
PFX sc 0 kemuta .
PFX sc 0 kebata .
PFX sc 0 keguta .
PFX sc 0 kegita .
PFX sc 0 kezita .
PFX sc 0 kekita .
PFX sc 0 kebita .
PFX sc 0 kelita .
PFX sc 0 kegata .
PFX sc 0 kekata .
PFX sc 0 kebuta .
PFX sc 0 keluta .
PFX sc 0 kekuta .
PFX sc 0 ketuta .
PFX sc 0 oto .
PFX sc 0 ata .
PFX sc 0 ete ."""

rule_right_raw = """
PFX Ob Y 18
PFX Ob 0 n [^lmnb]
PFX Ob l nd l.[^mn][^u]
PFX Ob l nn l.[mn]
PFX Ob w mp [w]
PFX Ob 0 mu .
PFX Ob 0 ba .
PFX Ob 0 gu .
PFX Ob 0 gi .
PFX Ob 0 zi .
PFX Ob 0 ki .
PFX Ob 0 bi .
PFX Ob 0 li .
PFX Ob 0 ga .
PFX Ob 0 ka .
PFX Ob 0 bu .
PFX Ob 0 lu .
PFX Ob 0 ku .
PFX Ob 0 tu ."""

FLAG_DESCRIPTIONS = {
    "sc": "Subordinating conjunction when with negative subjects in present simple tense",
    "Ob": "Object markers",
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

    out_flag = "FE"
    left_desc = FLAG_DESCRIPTIONS.get("sc", "sc")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "sc", left_desc, "Ob", right_desc, out_flag
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
