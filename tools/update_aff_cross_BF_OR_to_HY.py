import re
import os
from pathlib import Path

# Cross product generator: BF x OR => HY
# Description:
# - Left block `BF`: BF
# - Right block `OR`: Special reflexive object markers
# - Output flag `HY`: Cross-product prefixes for BF x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX BF Y 304
PFX BF 0 benna .
PFX BF 0 bewa .
PFX BF 0 beya .
PFX BF 0 betwa .
PFX BF 0 bemwa .
PFX BF 0 bebaa .
PFX BF 0 begwa .
PFX BF 0 begya .
PFX BF 0 bezaa .
PFX BF 0 bekyaa .
PFX BF 0 bebyaa .
PFX BF 0 belyaa .
PFX BF 0 begaa .
PFX BF 0 bekaa .
PFX BF 0 bebwa .
PFX BF 0 belwa .
PFX BF 0 bekwaa .
PFX BF 0 begaa .
PFX BF 0 betwaa .
PFX BF 0 gwenna .
PFX BF 0 gwewa .
PFX BF 0 gweya .
PFX BF 0 gwetwa .
PFX BF 0 gwemwa .
PFX BF 0 gwebaa .
PFX BF 0 gwegwa .
PFX BF 0 gwegya .
PFX BF 0 gwezaa .
PFX BF 0 gwekyaa .
PFX BF 0 gwebyaa .
PFX BF 0 gwelyaa .
PFX BF 0 gwegaa .
PFX BF 0 gwekaa .
PFX BF 0 gwebwa .
PFX BF 0 gwelwa .
PFX BF 0 gwekwaa .
PFX BF 0 gwegaa .
PFX BF 0 gwetwaa .
PFX BF 0 gyenna .
PFX BF 0 gyewa .
PFX BF 0 gyeya .
PFX BF 0 gyetwa .
PFX BF 0 gyemwa .
PFX BF 0 gyebaa .
PFX BF 0 gyegwa .
PFX BF 0 gyegya .
PFX BF 0 gyezaa .
PFX BF 0 gyekyaa .
PFX BF 0 gyebyaa .
PFX BF 0 gyelyaa .
PFX BF 0 gyegaa .
PFX BF 0 gyekaa .
PFX BF 0 gyebwa .
PFX BF 0 gyelwa .
PFX BF 0 gyekwaa .
PFX BF 0 gyegaa .
PFX BF 0 gyetwaa .
PFX BF 0 zenna .
PFX BF 0 zewa .
PFX BF 0 zeya .
PFX BF 0 zetwa .
PFX BF 0 zemwa .
PFX BF 0 zebaa .
PFX BF 0 zegwa .
PFX BF 0 zegya .
PFX BF 0 zezaa .
PFX BF 0 zekyaa .
PFX BF 0 zebyaa .
PFX BF 0 zelyaa .
PFX BF 0 zegaa .
PFX BF 0 zekaa .
PFX BF 0 zebwa .
PFX BF 0 zelwa .
PFX BF 0 zekwaa .
PFX BF 0 zegaa .
PFX BF 0 zetwaa .
PFX BF 0 kyenna .
PFX BF 0 kyewa .
PFX BF 0 kyeya .
PFX BF 0 kyetwa .
PFX BF 0 kyemwa .
PFX BF 0 kyebaa .
PFX BF 0 kyegwa .
PFX BF 0 kyegya .
PFX BF 0 kyezaa .
PFX BF 0 kyekyaa .
PFX BF 0 kyebyaa .
PFX BF 0 kyelyaa .
PFX BF 0 kyegaa .
PFX BF 0 kyekaa .
PFX BF 0 kyebwa .
PFX BF 0 kyelwa .
PFX BF 0 kyekwaa .
PFX BF 0 kyegaa .
PFX BF 0 kyetwaa .
PFX BF 0 kyenna .
PFX BF 0 kyewa .
PFX BF 0 kyeya .
PFX BF 0 kyetwa .
PFX BF 0 kyemwa .
PFX BF 0 kyebaa .
PFX BF 0 kyegwa .
PFX BF 0 kyegya .
PFX BF 0 kyezaa .
PFX BF 0 kyekyaa .
PFX BF 0 kyebyaa .
PFX BF 0 kyelyaa .
PFX BF 0 kyegaa .
PFX BF 0 kyekaa .
PFX BF 0 kyebwa .
PFX BF 0 kyelwa .
PFX BF 0 kyekwaa .
PFX BF 0 kyegaa .
PFX BF 0 kyetwaa .
PFX BF 0 byenna .
PFX BF 0 byewa .
PFX BF 0 byeya .
PFX BF 0 byetwa .
PFX BF 0 byemwa .
PFX BF 0 byebaa .
PFX BF 0 byegwa .
PFX BF 0 byegya .
PFX BF 0 byezaa .
PFX BF 0 byekyaa .
PFX BF 0 byebyaa .
PFX BF 0 byelyaa .
PFX BF 0 byegaa .
PFX BF 0 byekaa .
PFX BF 0 byebwa .
PFX BF 0 byelwa .
PFX BF 0 byekwaa .
PFX BF 0 byegaa .
PFX BF 0 byetwaa .
PFX BF 0 lyenna .
PFX BF 0 lyewa .
PFX BF 0 lyeya .
PFX BF 0 lyetwa .
PFX BF 0 lyemwa .
PFX BF 0 lyebaa .
PFX BF 0 lyegwa .
PFX BF 0 lyegya .
PFX BF 0 lyezaa .
PFX BF 0 lyekyaa .
PFX BF 0 lyebyaa .
PFX BF 0 lyelyaa .
PFX BF 0 lyegaa .
PFX BF 0 lyekaa .
PFX BF 0 lyebwa .
PFX BF 0 lyelwa .
PFX BF 0 lyekwaa .
PFX BF 0 lyegaa .
PFX BF 0 lyetwaa .
PFX BF 0 genna .
PFX BF 0 gewa .
PFX BF 0 geya .
PFX BF 0 getwa .
PFX BF 0 gemwa .
PFX BF 0 gebaa .
PFX BF 0 gegwa .
PFX BF 0 gegya .
PFX BF 0 gezaa .
PFX BF 0 gekyaa .
PFX BF 0 gebyaa .
PFX BF 0 gelyaa .
PFX BF 0 gegaa .
PFX BF 0 gekaa .
PFX BF 0 gebwa .
PFX BF 0 gelwa .
PFX BF 0 gekwaa .
PFX BF 0 gegaa .
PFX BF 0 getwaa .
PFX BF 0 kenna .
PFX BF 0 kewa .
PFX BF 0 keya .
PFX BF 0 ketwa .
PFX BF 0 kemwa .
PFX BF 0 kebaa .
PFX BF 0 kegwa .
PFX BF 0 kegya .
PFX BF 0 kezaa .
PFX BF 0 kekyaa .
PFX BF 0 kebyaa .
PFX BF 0 kelyaa .
PFX BF 0 kegaa .
PFX BF 0 kekaa .
PFX BF 0 kebwa .
PFX BF 0 kelwa .
PFX BF 0 kekwaa .
PFX BF 0 kegaa .
PFX BF 0 ketwaa .
PFX BF 0 bwenna .
PFX BF 0 bwewa .
PFX BF 0 bweya .
PFX BF 0 bwetwa .
PFX BF 0 bwemwa .
PFX BF 0 bwebaa .
PFX BF 0 bwegwa .
PFX BF 0 bwegya .
PFX BF 0 bwezaa .
PFX BF 0 bwekyaa .
PFX BF 0 bwebyaa .
PFX BF 0 bwelyaa .
PFX BF 0 bwegaa .
PFX BF 0 bwekaa .
PFX BF 0 bwebwa .
PFX BF 0 bwelwa .
PFX BF 0 bwekwaa .
PFX BF 0 bwegaa .
PFX BF 0 bwetwaa .
PFX BF 0 lwenna .
PFX BF 0 lwewa .
PFX BF 0 lweya .
PFX BF 0 lwetwa .
PFX BF 0 lwemwa .
PFX BF 0 lwebaa .
PFX BF 0 lwegwa .
PFX BF 0 lwegya .
PFX BF 0 lwezaa .
PFX BF 0 lwekyaa .
PFX BF 0 lwebyaa .
PFX BF 0 lwelyaa .
PFX BF 0 lwegaa .
PFX BF 0 lwekaa .
PFX BF 0 lwebwa .
PFX BF 0 lwelwa .
PFX BF 0 lwekwaa .
PFX BF 0 lwegaa .
PFX BF 0 lwetwaa .
PFX BF 0 zenna .
PFX BF 0 zewa .
PFX BF 0 zeya .
PFX BF 0 zetwa .
PFX BF 0 zemwa .
PFX BF 0 zebaa .
PFX BF 0 zegwa .
PFX BF 0 zegya .
PFX BF 0 zezaa .
PFX BF 0 zekyaa .
PFX BF 0 zebyaa .
PFX BF 0 zelyaa .
PFX BF 0 zegaa .
PFX BF 0 zekaa .
PFX BF 0 zebwa .
PFX BF 0 zelwa .
PFX BF 0 zekwaa .
PFX BF 0 zegaa .
PFX BF 0 zetwaa .
PFX BF 0 kwenna .
PFX BF 0 kwewa .
PFX BF 0 kweya .
PFX BF 0 kwetwa .
PFX BF 0 kwemwa .
PFX BF 0 kwebaa .
PFX BF 0 kwegwa .
PFX BF 0 kwegya .
PFX BF 0 kwezaa .
PFX BF 0 kwekyaa .
PFX BF 0 kwebyaa .
PFX BF 0 kwelyaa .
PFX BF 0 kwegaa .
PFX BF 0 kwekaa .
PFX BF 0 kwebwa .
PFX BF 0 kwelwa .
PFX BF 0 kwekwaa .
PFX BF 0 kwegaa .
PFX BF 0 kwetwaa .
PFX BF 0 genna .
PFX BF 0 gewa .
PFX BF 0 geya .
PFX BF 0 getwa .
PFX BF 0 gemwa .
PFX BF 0 gebaa .
PFX BF 0 gegwa .
PFX BF 0 gegya .
PFX BF 0 gezaa .
PFX BF 0 gekyaa .
PFX BF 0 gebyaa .
PFX BF 0 gelyaa .
PFX BF 0 gegaa .
PFX BF 0 gekaa .
PFX BF 0 gebwa .
PFX BF 0 gelwa .
PFX BF 0 gekwaa .
PFX BF 0 gegaa .
PFX BF 0 getwaa .
PFX BF 0 twenna .
PFX BF 0 twewa .
PFX BF 0 tweya .
PFX BF 0 twetwa .
PFX BF 0 twemwa .
PFX BF 0 twebaa .
PFX BF 0 twegwa .
PFX BF 0 twegya .
PFX BF 0 twezaa .
PFX BF 0 twekyaa .
PFX BF 0 twebyaa .
PFX BF 0 twelyaa .
PFX BF 0 twegaa .
PFX BF 0 twekaa .
PFX BF 0 twebwa .
PFX BF 0 twelwa .
PFX BF 0 twekwaa .
PFX BF 0 twegaa .
PFX BF 0 twetwaa ."""

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
    "BF": "BF",
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

    out_flag = "HY"
    left_desc = FLAG_DESCRIPTIONS.get("BF", "BF")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "BF", left_desc, "OR", right_desc, out_flag
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
