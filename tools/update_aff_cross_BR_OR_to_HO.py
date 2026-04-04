import re
import os
from pathlib import Path

# Cross product generator: BR x OR => HO
# Description:
# - Left block `BR`: BR
# - Right block `OR`: Special reflexive object markers
# - Output flag `HO`: Cross-product prefixes for BR x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX BR Y 256
PFX BR 0 bessi .
PFX BR 0 betuta .
PFX BR 0 bemuta .
PFX BR 0 bebata .
PFX BR 0 beguta .
PFX BR 0 begita .
PFX BR 0 bezita .
PFX BR 0 bekita .
PFX BR 0 bebita .
PFX BR 0 belita .
PFX BR 0 begata .
PFX BR 0 bekata .
PFX BR 0 bebuta .
PFX BR 0 beluta .
PFX BR 0 bekuta .
PFX BR 0 betuta .
PFX BR 0 gwessi .
PFX BR 0 gwetuta .
PFX BR 0 gwemuta .
PFX BR 0 gwebata .
PFX BR 0 gweguta .
PFX BR 0 gwegita .
PFX BR 0 gwezita .
PFX BR 0 gwekita .
PFX BR 0 gwebita .
PFX BR 0 gwelita .
PFX BR 0 gwegata .
PFX BR 0 gwekata .
PFX BR 0 gwebuta .
PFX BR 0 gweluta .
PFX BR 0 gwekuta .
PFX BR 0 gwetuta .
PFX BR 0 gyessi .
PFX BR 0 gyetuta .
PFX BR 0 gyemuta .
PFX BR 0 gyebata .
PFX BR 0 gyeguta .
PFX BR 0 gyegita .
PFX BR 0 gyezita .
PFX BR 0 gyekita .
PFX BR 0 gyebita .
PFX BR 0 gyelita .
PFX BR 0 gyegata .
PFX BR 0 gyekata .
PFX BR 0 gyebuta .
PFX BR 0 gyeluta .
PFX BR 0 gyekuta .
PFX BR 0 gyetuta .
PFX BR 0 zessi .
PFX BR 0 zetuta .
PFX BR 0 zemuta .
PFX BR 0 zebata .
PFX BR 0 zeguta .
PFX BR 0 zegita .
PFX BR 0 zezita .
PFX BR 0 zekita .
PFX BR 0 zebita .
PFX BR 0 zelita .
PFX BR 0 zegata .
PFX BR 0 zekata .
PFX BR 0 zebuta .
PFX BR 0 zeluta .
PFX BR 0 zekuta .
PFX BR 0 zetuta .
PFX BR 0 kyessi .
PFX BR 0 kyetuta .
PFX BR 0 kyemuta .
PFX BR 0 kyebata .
PFX BR 0 kyeguta .
PFX BR 0 kyegita .
PFX BR 0 kyezita .
PFX BR 0 kyekita .
PFX BR 0 kyebita .
PFX BR 0 kyelita .
PFX BR 0 kyegata .
PFX BR 0 kyekata .
PFX BR 0 kyebuta .
PFX BR 0 kyeluta .
PFX BR 0 kyekuta .
PFX BR 0 kyetuta .
PFX BR 0 kyessi .
PFX BR 0 kyetuta .
PFX BR 0 kyemuta .
PFX BR 0 kyebata .
PFX BR 0 kyeguta .
PFX BR 0 kyegita .
PFX BR 0 kyezita .
PFX BR 0 kyekita .
PFX BR 0 kyebita .
PFX BR 0 kyelita .
PFX BR 0 kyegata .
PFX BR 0 kyekata .
PFX BR 0 kyebuta .
PFX BR 0 kyeluta .
PFX BR 0 kyekuta .
PFX BR 0 kyetuta .
PFX BR 0 byessi .
PFX BR 0 byetuta .
PFX BR 0 byemuta .
PFX BR 0 byebata .
PFX BR 0 byeguta .
PFX BR 0 byegita .
PFX BR 0 byezita .
PFX BR 0 byekita .
PFX BR 0 byebita .
PFX BR 0 byelita .
PFX BR 0 byegata .
PFX BR 0 byekata .
PFX BR 0 byebuta .
PFX BR 0 byeluta .
PFX BR 0 byekuta .
PFX BR 0 byetuta .
PFX BR 0 lyessi .
PFX BR 0 lyetuta .
PFX BR 0 lyemuta .
PFX BR 0 lyebata .
PFX BR 0 lyeguta .
PFX BR 0 lyegita .
PFX BR 0 lyezita .
PFX BR 0 lyekita .
PFX BR 0 lyebita .
PFX BR 0 lyelita .
PFX BR 0 lyegata .
PFX BR 0 lyekata .
PFX BR 0 lyebuta .
PFX BR 0 lyeluta .
PFX BR 0 lyekuta .
PFX BR 0 lyetuta .
PFX BR 0 gessi .
PFX BR 0 getuta .
PFX BR 0 gemuta .
PFX BR 0 gebata .
PFX BR 0 geguta .
PFX BR 0 gegita .
PFX BR 0 gezita .
PFX BR 0 gekita .
PFX BR 0 gebita .
PFX BR 0 gelita .
PFX BR 0 gegata .
PFX BR 0 gekata .
PFX BR 0 gebuta .
PFX BR 0 geluta .
PFX BR 0 gekuta .
PFX BR 0 getuta .
PFX BR 0 kessi .
PFX BR 0 ketuta .
PFX BR 0 kemuta .
PFX BR 0 kebata .
PFX BR 0 keguta .
PFX BR 0 kegita .
PFX BR 0 kezita .
PFX BR 0 kekita .
PFX BR 0 kebita .
PFX BR 0 kelita .
PFX BR 0 kegata .
PFX BR 0 kekata .
PFX BR 0 kebuta .
PFX BR 0 keluta .
PFX BR 0 kekuta .
PFX BR 0 ketuta .
PFX BR 0 bwessi .
PFX BR 0 bwetuta .
PFX BR 0 bwemuta .
PFX BR 0 bwebata .
PFX BR 0 bweguta .
PFX BR 0 bwegita .
PFX BR 0 bwezita .
PFX BR 0 bwekita .
PFX BR 0 bwebita .
PFX BR 0 bwelita .
PFX BR 0 bwegata .
PFX BR 0 bwekata .
PFX BR 0 bwebuta .
PFX BR 0 bweluta .
PFX BR 0 bwekuta .
PFX BR 0 bwetuta .
PFX BR 0 lwessi .
PFX BR 0 lwetuta .
PFX BR 0 lwemuta .
PFX BR 0 lwebata .
PFX BR 0 lweguta .
PFX BR 0 lwegita .
PFX BR 0 lwezita .
PFX BR 0 lwekita .
PFX BR 0 lwebita .
PFX BR 0 lwelita .
PFX BR 0 lwegata .
PFX BR 0 lwekata .
PFX BR 0 lwebuta .
PFX BR 0 lweluta .
PFX BR 0 lwekuta .
PFX BR 0 lwetuta .
PFX BR 0 zessi .
PFX BR 0 zetuta .
PFX BR 0 zemuta .
PFX BR 0 zebata .
PFX BR 0 zeguta .
PFX BR 0 zegita .
PFX BR 0 zezita .
PFX BR 0 zekita .
PFX BR 0 zebita .
PFX BR 0 zelita .
PFX BR 0 zegata .
PFX BR 0 zekata .
PFX BR 0 zebuta .
PFX BR 0 zeluta .
PFX BR 0 zekuta .
PFX BR 0 zetuta .
PFX BR 0 kwessi .
PFX BR 0 kwetuta .
PFX BR 0 kwemuta .
PFX BR 0 kwebata .
PFX BR 0 kweguta .
PFX BR 0 kwegita .
PFX BR 0 kwezita .
PFX BR 0 kwekita .
PFX BR 0 kwebita .
PFX BR 0 kwelita .
PFX BR 0 kwegata .
PFX BR 0 kwekata .
PFX BR 0 kwebuta .
PFX BR 0 kweluta .
PFX BR 0 kwekuta .
PFX BR 0 kwetuta .
PFX BR 0 gessi .
PFX BR 0 getuta .
PFX BR 0 gemuta .
PFX BR 0 gebata .
PFX BR 0 geguta .
PFX BR 0 gegita .
PFX BR 0 gezita .
PFX BR 0 gekita .
PFX BR 0 gebita .
PFX BR 0 gelita .
PFX BR 0 gegata .
PFX BR 0 gekata .
PFX BR 0 gebuta .
PFX BR 0 geluta .
PFX BR 0 gekuta .
PFX BR 0 getuta .
PFX BR 0 twessi .
PFX BR 0 twetuta .
PFX BR 0 twemuta .
PFX BR 0 twebata .
PFX BR 0 tweguta .
PFX BR 0 twegita .
PFX BR 0 twezita .
PFX BR 0 twekita .
PFX BR 0 twebita .
PFX BR 0 twelita .
PFX BR 0 twegata .
PFX BR 0 twekata .
PFX BR 0 twebuta .
PFX BR 0 tweluta .
PFX BR 0 twekuta .
PFX BR 0 twetuta ."""

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
    "BR": "BR",
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

    out_flag = "HO"
    left_desc = FLAG_DESCRIPTIONS.get("BR", "BR")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "BR", left_desc, "OR", right_desc, out_flag
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
