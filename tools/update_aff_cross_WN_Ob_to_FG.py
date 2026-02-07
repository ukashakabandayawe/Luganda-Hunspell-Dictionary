import re
import os
from pathlib import Path

# Cross product generator: WN x Ob => FG
# Description:
# - Left block `WN`: Subordinating conjunction when with subjects in near and distant past tense
# - Right block `Ob`: Object markers
# - Output flag `FG`: Cross-product prefixes for WN x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX WN Y 196
PFX WN 0 wenna .
PFX WN 0 wewa .
PFX WN 0 weya .
PFX WN 0 wetwa .
PFX WN 0 wemwa .
PFX WN 0 webaa .
PFX WN 0 wegwa .
PFX WN 0 wegya .
PFX WN 0 wezaa .
PFX WN 0 wekyaa .
PFX WN 0 webyaa .
PFX WN 0 welyaa .
PFX WN 0 wegaa .
PFX WN 0 wekaa .
PFX WN 0 webwa .
PFX WN 0 welwa .
PFX WN 0 wekwa .
PFX WN 0 wegaa .
PFX WN 0 wetwa .
PFX WN 0 bwenna .
PFX WN 0 bwewa .
PFX WN 0 bweya .
PFX WN 0 bwetwa .
PFX WN 0 bwemwa .
PFX WN 0 bwebaa .
PFX WN 0 bwegwa .
PFX WN 0 bwegya .
PFX WN 0 bwezaa .
PFX WN 0 bwekyaa .
PFX WN 0 bwebyaa .
PFX WN 0 bwelyaa .
PFX WN 0 bwegaa .
PFX WN 0 bwekaa .
PFX WN 0 bwebwa .
PFX WN 0 bwelwa .
PFX WN 0 bwekwa .
PFX WN 0 bwegaa .
PFX WN 0 bwetwa .
PFX WN 0 bwenna .
PFX WN 0 bwewa .
PFX WN 0 bweya .
PFX WN 0 lwenna .
PFX WN 0 lwewa .
PFX WN 0 lweya .
PFX WN 0 lwetwa .
PFX WN 0 lwemwa .
PFX WN 0 lwebaa .
PFX WN 0 lwegwa .
PFX WN 0 lwegya .
PFX WN 0 lwezaa .
PFX WN 0 lwekyaa .
PFX WN 0 lwebyaa .
PFX WN 0 lwelyaa .
PFX WN 0 lwegaa .
PFX WN 0 lwekaa .
PFX WN 0 lwebwa .
PFX WN 0 lwelwa .
PFX WN 0 lwekwa .
PFX WN 0 lwegaa .
PFX WN 0 lwetwa .
PFX WN 0 lwenna .
PFX WN 0 lwewa .
PFX WN 0 lweya .
PFX WN 0 zenna .
PFX WN 0 zewa .
PFX WN 0 zeya .
PFX WN 0 zetwa .
PFX WN 0 zemwa .
PFX WN 0 zebaa .
PFX WN 0 zegwa .
PFX WN 0 zegya .
PFX WN 0 zezaa .
PFX WN 0 zekyaa .
PFX WN 0 zebyaa .
PFX WN 0 zelyaa .
PFX WN 0 zegaa .
PFX WN 0 zekaa .
PFX WN 0 zebwa .
PFX WN 0 zelwa .
PFX WN 0 zekwa .
PFX WN 0 zegaa .
PFX WN 0 zetwa .
PFX WN 0 gwenna .
PFX WN 0 gwewa .
PFX WN 0 gweya .
PFX WN 0 gwetwa .
PFX WN 0 gwemwa .
PFX WN 0 gwebaa .
PFX WN 0 gwegwa .
PFX WN 0 gwegya .
PFX WN 0 gwezaa .
PFX WN 0 gwekyaa .
PFX WN 0 gwebyaa .
PFX WN 0 gwelyaa .
PFX WN 0 gwegaa .
PFX WN 0 gwekaa .
PFX WN 0 gwebwa .
PFX WN 0 gwelwa .
PFX WN 0 gwekwa .
PFX WN 0 gwegaa .
PFX WN 0 gwetwa .
PFX WN 0 gyenna .
PFX WN 0 gyewa .
PFX WN 0 gyeya .
PFX WN 0 gyetwa .
PFX WN 0 gyemwa .
PFX WN 0 gyebaa .
PFX WN 0 gyegwa .
PFX WN 0 gyegya .
PFX WN 0 gyezaa .
PFX WN 0 gyekyaa .
PFX WN 0 gyebyaa .
PFX WN 0 gyelyaa .
PFX WN 0 gyegaa .
PFX WN 0 gyekaa .
PFX WN 0 gyebwa .
PFX WN 0 gyelwa .
PFX WN 0 gyekwa .
PFX WN 0 gyegaa .
PFX WN 0 gyetwa .
PFX WN 0 kyenna .
PFX WN 0 kyewa .
PFX WN 0 kyeya .
PFX WN 0 kyetwa .
PFX WN 0 kyemwa .
PFX WN 0 kyebaa .
PFX WN 0 kyegwa .
PFX WN 0 kyegya .
PFX WN 0 kyezaa .
PFX WN 0 kyekyaa .
PFX WN 0 kyebyaa .
PFX WN 0 kyelyaa .
PFX WN 0 kyegaa .
PFX WN 0 kyekaa .
PFX WN 0 kyebwa .
PFX WN 0 kyelwa .
PFX WN 0 kyekwa .
PFX WN 0 kyegaa .
PFX WN 0 kyetwa .
PFX WN 0 byenna .
PFX WN 0 byewa .
PFX WN 0 byeya .
PFX WN 0 byetwa .
PFX WN 0 byemwa .
PFX WN 0 byebaa .
PFX WN 0 byegwa .
PFX WN 0 byegya .
PFX WN 0 byezaa .
PFX WN 0 byekyaa .
PFX WN 0 byebyaa .
PFX WN 0 byelyaa .
PFX WN 0 byegaa .
PFX WN 0 byekaa .
PFX WN 0 byebwa .
PFX WN 0 byelwa .
PFX WN 0 byekwa .
PFX WN 0 byegaa .
PFX WN 0 byetwa .
PFX WN 0 lyenna .
PFX WN 0 lyewa .
PFX WN 0 lyeya .
PFX WN 0 lyetwa .
PFX WN 0 lyemwa .
PFX WN 0 lyebaa .
PFX WN 0 lyegwa .
PFX WN 0 lyegya .
PFX WN 0 lyezaa .
PFX WN 0 lyekyaa .
PFX WN 0 lyebyaa .
PFX WN 0 lyelyaa .
PFX WN 0 lyegaa .
PFX WN 0 lyekaa .
PFX WN 0 lyebwa .
PFX WN 0 lyelwa .
PFX WN 0 lyekwa .
PFX WN 0 lyegaa .
PFX WN 0 lyetwa .
PFX WN 0 kenna .
PFX WN 0 kewa .
PFX WN 0 keya .
PFX WN 0 ketwa .
PFX WN 0 kemwa .
PFX WN 0 kebaa .
PFX WN 0 kegwa .
PFX WN 0 kegya .
PFX WN 0 kezaa .
PFX WN 0 kekyaa .
PFX WN 0 kebyaa .
PFX WN 0 kelyaa .
PFX WN 0 kegaa .
PFX WN 0 kekaa .
PFX WN 0 kebwa .
PFX WN 0 kelwa .
PFX WN 0 kekwa .
PFX WN 0 kegaa .
PFX WN 0 ketwa ."""

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
    "WN": "Subordinating conjunction when with subjects in near and distant past tense",
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

    out_flag = "FG"
    left_desc = FLAG_DESCRIPTIONS.get("WN", "WN")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "WN", left_desc, "Ob", right_desc, out_flag
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
