import re
import os
from pathlib import Path

# Cross product generator: BG x OR => IJ
# Description:
# - Left block `BG`: BG
# - Right block `OR`: Special reflexive object markers
# - Output flag `IJ`: Cross-product prefixes for BG x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX BG Y 320
PFX BG 0 benna .
PFX BG 0 bewa .
PFX BG 0 beya .
PFX BG 0 betwa .
PFX BG 0 bemwa .
PFX BG 0 bebaa .
PFX BG 0 begwa .
PFX BG 0 begya .
PFX BG 0 bezaa .
PFX BG 0 bekya .
PFX BG 0 bebya .
PFX BG 0 belya .
PFX BG 0 begaa .
PFX BG 0 bekaa .
PFX BG 0 bebwa .
PFX BG 0 belwaa .
PFX BG 0 bezaa .
PFX BG 0 bekwaa .
PFX BG 0 begaa .
PFX BG 0 betwa .
PFX BG 0 gwenna .
PFX BG 0 gwewa .
PFX BG 0 gweya .
PFX BG 0 gwetwa .
PFX BG 0 gwemwa .
PFX BG 0 gwebaa .
PFX BG 0 gwegwa .
PFX BG 0 gwegya .
PFX BG 0 gwezaa .
PFX BG 0 gwekya .
PFX BG 0 gwebya .
PFX BG 0 gwelya .
PFX BG 0 gwegaa .
PFX BG 0 gwekaa .
PFX BG 0 gwebwa .
PFX BG 0 gwelwaa .
PFX BG 0 gwezaa .
PFX BG 0 gwekwaa .
PFX BG 0 gwegaa .
PFX BG 0 gwetwa .
PFX BG 0 gyenna .
PFX BG 0 gyewa .
PFX BG 0 gyeya .
PFX BG 0 gyetwa .
PFX BG 0 gyemwa .
PFX BG 0 gyebaa .
PFX BG 0 gyegwa .
PFX BG 0 gyegya .
PFX BG 0 gyezaa .
PFX BG 0 gyekya .
PFX BG 0 gyebya .
PFX BG 0 gyelya .
PFX BG 0 gyegaa .
PFX BG 0 gyekaa .
PFX BG 0 gyebwa .
PFX BG 0 gyelwaa .
PFX BG 0 gyezaa .
PFX BG 0 gyekwaa .
PFX BG 0 gyegaa .
PFX BG 0 gyetwa .
PFX BG 0 zenna .
PFX BG 0 zewa .
PFX BG 0 zeya .
PFX BG 0 zetwa .
PFX BG 0 zemwa .
PFX BG 0 zebaa .
PFX BG 0 zegwa .
PFX BG 0 zegya .
PFX BG 0 zezaa .
PFX BG 0 zekya .
PFX BG 0 zebya .
PFX BG 0 zelya .
PFX BG 0 zegaa .
PFX BG 0 zekaa .
PFX BG 0 zebwa .
PFX BG 0 zelwaa .
PFX BG 0 zezaa .
PFX BG 0 zekwaa .
PFX BG 0 zegaa .
PFX BG 0 zetwa .
PFX BG 0 kyenna .
PFX BG 0 kyewa .
PFX BG 0 kyeya .
PFX BG 0 kyetwa .
PFX BG 0 kyemwa .
PFX BG 0 kyebaa .
PFX BG 0 kyegwa .
PFX BG 0 kyegya .
PFX BG 0 kyezaa .
PFX BG 0 kyekya .
PFX BG 0 kyebya .
PFX BG 0 kyelya .
PFX BG 0 kyegaa .
PFX BG 0 kyekaa .
PFX BG 0 kyebwa .
PFX BG 0 kyelwaa .
PFX BG 0 kyezaa .
PFX BG 0 kyekwaa .
PFX BG 0 kyegaa .
PFX BG 0 kyetwa .
PFX BG 0 kyenna .
PFX BG 0 kyewa .
PFX BG 0 kyeya .
PFX BG 0 kyetwa .
PFX BG 0 kyemwa .
PFX BG 0 kyebaa .
PFX BG 0 kyegwa .
PFX BG 0 kyegya .
PFX BG 0 kyezaa .
PFX BG 0 kyekya .
PFX BG 0 kyebya .
PFX BG 0 kyelya .
PFX BG 0 kyegaa .
PFX BG 0 kyekaa .
PFX BG 0 kyebwa .
PFX BG 0 kyelwaa .
PFX BG 0 kyezaa .
PFX BG 0 kyekwaa .
PFX BG 0 kyegaa .
PFX BG 0 kyetwa .
PFX BG 0 byenna .
PFX BG 0 byewa .
PFX BG 0 byeya .
PFX BG 0 byetwa .
PFX BG 0 byemwa .
PFX BG 0 byebaa .
PFX BG 0 byegwa .
PFX BG 0 byegya .
PFX BG 0 byezaa .
PFX BG 0 byekya .
PFX BG 0 byebya .
PFX BG 0 byelya .
PFX BG 0 byegaa .
PFX BG 0 byekaa .
PFX BG 0 byebwa .
PFX BG 0 byelwaa .
PFX BG 0 byezaa .
PFX BG 0 byekwaa .
PFX BG 0 byegaa .
PFX BG 0 byetwa .
PFX BG 0 lyenna .
PFX BG 0 lyewa .
PFX BG 0 lyeya .
PFX BG 0 lyetwa .
PFX BG 0 lyemwa .
PFX BG 0 lyebaa .
PFX BG 0 lyegwa .
PFX BG 0 lyegya .
PFX BG 0 lyezaa .
PFX BG 0 lyekya .
PFX BG 0 lyebya .
PFX BG 0 lyelya .
PFX BG 0 lyegaa .
PFX BG 0 lyekaa .
PFX BG 0 lyebwa .
PFX BG 0 lyelwaa .
PFX BG 0 lyezaa .
PFX BG 0 lyekwaa .
PFX BG 0 lyegaa .
PFX BG 0 lyetwa .
PFX BG 0 genna .
PFX BG 0 gewa .
PFX BG 0 geya .
PFX BG 0 getwa .
PFX BG 0 gemwa .
PFX BG 0 gebaa .
PFX BG 0 gegwa .
PFX BG 0 gegya .
PFX BG 0 gezaa .
PFX BG 0 gekya .
PFX BG 0 gebya .
PFX BG 0 gelya .
PFX BG 0 gegaa .
PFX BG 0 gekaa .
PFX BG 0 gebwa .
PFX BG 0 gelwaa .
PFX BG 0 gezaa .
PFX BG 0 gekwaa .
PFX BG 0 gegaa .
PFX BG 0 getwa .
PFX BG 0 kenna .
PFX BG 0 kewa .
PFX BG 0 keya .
PFX BG 0 ketwa .
PFX BG 0 kemwa .
PFX BG 0 kebaa .
PFX BG 0 kegwa .
PFX BG 0 kegya .
PFX BG 0 kezaa .
PFX BG 0 kekya .
PFX BG 0 kebya .
PFX BG 0 kelya .
PFX BG 0 kegaa .
PFX BG 0 kekaa .
PFX BG 0 kebwa .
PFX BG 0 kelwaa .
PFX BG 0 kezaa .
PFX BG 0 kekwaa .
PFX BG 0 kegaa .
PFX BG 0 ketwa .
PFX BG 0 bwenna .
PFX BG 0 bwewa .
PFX BG 0 bweya .
PFX BG 0 bwetwa .
PFX BG 0 bwemwa .
PFX BG 0 bwebaa .
PFX BG 0 bwegwa .
PFX BG 0 bwegya .
PFX BG 0 bwezaa .
PFX BG 0 bwekya .
PFX BG 0 bwebya .
PFX BG 0 bwelya .
PFX BG 0 bwegaa .
PFX BG 0 bwekaa .
PFX BG 0 bwebwa .
PFX BG 0 bwelwaa .
PFX BG 0 bwezaa .
PFX BG 0 bwekwaa .
PFX BG 0 bwegaa .
PFX BG 0 bwetwa .
PFX BG 0 lwenna .
PFX BG 0 lwewa .
PFX BG 0 lweya .
PFX BG 0 lwetwa .
PFX BG 0 lwemwa .
PFX BG 0 lwebaa .
PFX BG 0 lwegwa .
PFX BG 0 lwegya .
PFX BG 0 lwezaa .
PFX BG 0 lwekya .
PFX BG 0 lwebya .
PFX BG 0 lwelya .
PFX BG 0 lwegaa .
PFX BG 0 lwekaa .
PFX BG 0 lwebwa .
PFX BG 0 lwelwaa .
PFX BG 0 lwezaa .
PFX BG 0 lwekwaa .
PFX BG 0 lwegaa .
PFX BG 0 lwetwa .
PFX BG 0 zenna .
PFX BG 0 zewa .
PFX BG 0 zeya .
PFX BG 0 zetwa .
PFX BG 0 zemwa .
PFX BG 0 zebaa .
PFX BG 0 zegwa .
PFX BG 0 zegya .
PFX BG 0 zezaa .
PFX BG 0 zekya .
PFX BG 0 zebya .
PFX BG 0 zelya .
PFX BG 0 zegaa .
PFX BG 0 zekaa .
PFX BG 0 zebwa .
PFX BG 0 zelwaa .
PFX BG 0 zezaa .
PFX BG 0 zekwaa .
PFX BG 0 zegaa .
PFX BG 0 zetwa .
PFX BG 0 kwenna .
PFX BG 0 kwewa .
PFX BG 0 kweya .
PFX BG 0 kwetwa .
PFX BG 0 kwemwa .
PFX BG 0 kwebaa .
PFX BG 0 kwegwa .
PFX BG 0 kwegya .
PFX BG 0 kwezaa .
PFX BG 0 kwekya .
PFX BG 0 kwebya .
PFX BG 0 kwelya .
PFX BG 0 kwegaa .
PFX BG 0 kwekaa .
PFX BG 0 kwebwa .
PFX BG 0 kwelwaa .
PFX BG 0 kwezaa .
PFX BG 0 kwekwaa .
PFX BG 0 kwegaa .
PFX BG 0 kwetwa .
PFX BG 0 genna .
PFX BG 0 gewa .
PFX BG 0 geya .
PFX BG 0 getwa .
PFX BG 0 gemwa .
PFX BG 0 gebaa .
PFX BG 0 gegwa .
PFX BG 0 gegya .
PFX BG 0 gezaa .
PFX BG 0 gekya .
PFX BG 0 gebya .
PFX BG 0 gelya .
PFX BG 0 gegaa .
PFX BG 0 gekaa .
PFX BG 0 gebwa .
PFX BG 0 gelwaa .
PFX BG 0 gezaa .
PFX BG 0 gekwaa .
PFX BG 0 gegaa .
PFX BG 0 getwa .
PFX BG 0 twenna .
PFX BG 0 twewa .
PFX BG 0 tweya .
PFX BG 0 twetwa .
PFX BG 0 twemwa .
PFX BG 0 twebaa .
PFX BG 0 twegwa .
PFX BG 0 twegya .
PFX BG 0 twezaa .
PFX BG 0 twekya .
PFX BG 0 twebya .
PFX BG 0 twelya .
PFX BG 0 twegaa .
PFX BG 0 twekaa .
PFX BG 0 twebwa .
PFX BG 0 twelwaa .
PFX BG 0 twezaa .
PFX BG 0 twekwaa .
PFX BG 0 twegaa .
PFX BG 0 twetwa ."""

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
    "BG": "BG",
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

    out_flag = "IJ"
    left_desc = FLAG_DESCRIPTIONS.get("BG", "BG")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "BG", left_desc, "OR", right_desc, out_flag
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
