import re
import os
from pathlib import Path

# Cross product generator: wm x Ob => FP
# Description:
# - Left block `wm`: Subordinating conjunction when with negative subjects in near future tense
# - Right block `Ob`: Object markers
# - Output flag `FP`: Cross-product prefixes for wm x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX wm Y 204
PFX wm 0 w'otoo .
PFX wm 0 w'ataa .
PFX wm 0 w'etaa .
PFX wm 0 wessii [^mn]
PFX wm 0 wessii mu
PFX wm 0 wetutaa .
PFX wm 0 wemutaa .
PFX wm 0 webataa .
PFX wm 0 wegutaa .
PFX wm 0 wegitaa .
PFX wm 0 wezitaa .
PFX wm 0 wekitaa .
PFX wm 0 webitaa .
PFX wm 0 welitaa .
PFX wm 0 wegataa .
PFX wm 0 wekataa .
PFX wm 0 webutaa .
PFX wm 0 welutaa .
PFX wm 0 wekutaa .
PFX wm 0 wetutaa .
PFX wm 0 bw'otoo .
PFX wm 0 bw'ataa .
PFX wm 0 bw'etaa .
PFX wm 0 bwessii [^mn]
PFX wm 0 bwessii mu
PFX wm 0 bwetutaa .
PFX wm 0 bwemutaa .
PFX wm 0 bwebataa .
PFX wm 0 bwegutaa .
PFX wm 0 bwegitaa .
PFX wm 0 bwezitaa .
PFX wm 0 bwekitaa .
PFX wm 0 bwebitaa .
PFX wm 0 bwelitaa .
PFX wm 0 bwegataa .
PFX wm 0 bwekataa .
PFX wm 0 bwebutaa .
PFX wm 0 bwelutaa .
PFX wm 0 bwekutaa .
PFX wm 0 bwetutaa .
PFX wm 0 bwessii [^mn]
PFX wm 0 bwessii mu
PFX wm 0 lw'otoo .
PFX wm 0 lw'ataa .
PFX wm 0 lw'etaa .
PFX wm 0 lwessii [^mn]
PFX wm 0 lwessii mu
PFX wm 0 lwetutaa .
PFX wm 0 lwemutaa .
PFX wm 0 lwebataa .
PFX wm 0 lwegutaa .
PFX wm 0 lwegitaa .
PFX wm 0 lwezitaa .
PFX wm 0 lwekitaa .
PFX wm 0 lwebitaa .
PFX wm 0 lwelitaa .
PFX wm 0 lwegataa .
PFX wm 0 lwekataa .
PFX wm 0 lwebutaa .
PFX wm 0 lwelutaa .
PFX wm 0 lwekutaa .
PFX wm 0 lwetutaa .
PFX wm 0 lwessii [^mn]
PFX wm 0 lwessii mu
PFX wm 0 z'otoo .
PFX wm 0 z'ataa .
PFX wm 0 z'etaa .
PFX wm 0 zetutaa .
PFX wm 0 zemutaa .
PFX wm 0 zebataa .
PFX wm 0 zegutaa .
PFX wm 0 zegitaa .
PFX wm 0 zezitaa .
PFX wm 0 zekitaa .
PFX wm 0 zebitaa .
PFX wm 0 zelitaa .
PFX wm 0 zegataa .
PFX wm 0 zekataa .
PFX wm 0 zebutaa .
PFX wm 0 zelutaa .
PFX wm 0 zekutaa .
PFX wm 0 zetutaa .
PFX wm 0 gw'otoo .
PFX wm 0 gw'ataa .
PFX wm 0 gw'etaa .
PFX wm 0 gwessii [^mn]
PFX wm 0 gwessii mu
PFX wm 0 gwetutaa .
PFX wm 0 gwemutaa .
PFX wm 0 gwebataa .
PFX wm 0 gwegutaa .
PFX wm 0 gwegitaa .
PFX wm 0 gwezitaa .
PFX wm 0 gwekitaa .
PFX wm 0 gwebitaa .
PFX wm 0 gwelitaa .
PFX wm 0 gwegataa .
PFX wm 0 gwekataa .
PFX wm 0 gwebutaa .
PFX wm 0 gwelutaa .
PFX wm 0 gwekutaa .
PFX wm 0 gwetutaa .
PFX wm 0 gy'otoo .
PFX wm 0 gy'ataa .
PFX wm 0 gy'etaa .
PFX wm 0 gyessii [^mn]
PFX wm 0 gyessii mu
PFX wm 0 gyetutaa .
PFX wm 0 gyemutaa .
PFX wm 0 gyebataa .
PFX wm 0 gyegutaa .
PFX wm 0 gyegitaa .
PFX wm 0 gyezitaa .
PFX wm 0 gyekitaa .
PFX wm 0 gyebitaa .
PFX wm 0 gyelitaa .
PFX wm 0 gyegataa .
PFX wm 0 gyekataa .
PFX wm 0 gyebutaa .
PFX wm 0 gyelutaa .
PFX wm 0 gyekutaa .
PFX wm 0 gyetutaa .
PFX wm 0 ky'otoo .
PFX wm 0 ky'ataa .
PFX wm 0 ky'etaa .
PFX wm 0 kyessii [^mn]
PFX wm 0 kyessii mu
PFX wm 0 kyetutaa .
PFX wm 0 kyemutaa .
PFX wm 0 kyebataa .
PFX wm 0 kyegutaa .
PFX wm 0 kyegitaa .
PFX wm 0 kyezitaa .
PFX wm 0 kyekitaa .
PFX wm 0 kyebitaa .
PFX wm 0 kyelitaa .
PFX wm 0 kyegataa .
PFX wm 0 kyekataa .
PFX wm 0 kyebutaa .
PFX wm 0 kyelutaa .
PFX wm 0 kyekutaa .
PFX wm 0 kyetutaa .
PFX wm 0 by'otoo .
PFX wm 0 by'ataa .
PFX wm 0 by'etaa .
PFX wm 0 byessii [^mn]
PFX wm 0 byessii mu
PFX wm 0 byetutaa .
PFX wm 0 byemutaa .
PFX wm 0 byebataa .
PFX wm 0 byegutaa .
PFX wm 0 byegitaa .
PFX wm 0 byezitaa .
PFX wm 0 byekitaa .
PFX wm 0 byebitaa .
PFX wm 0 byelitaa .
PFX wm 0 byegataa .
PFX wm 0 byekataa .
PFX wm 0 byebutaa .
PFX wm 0 byelutaa .
PFX wm 0 byekutaa .
PFX wm 0 byetutaa .
PFX wm 0 ly'otoo .
PFX wm 0 ly'ataa .
PFX wm 0 ly'etaa .
PFX wm 0 lyessii [^mn]
PFX wm 0 lyessii mu
PFX wm 0 lyetutaa .
PFX wm 0 lyemutaa .
PFX wm 0 lyebataa .
PFX wm 0 lyegutaa .
PFX wm 0 lyegitaa .
PFX wm 0 lyezitaa .
PFX wm 0 lyekitaa .
PFX wm 0 lyebitaa .
PFX wm 0 lyelitaa .
PFX wm 0 lyegataa .
PFX wm 0 lyekataa .
PFX wm 0 lyebutaa .
PFX wm 0 lyelutaa .
PFX wm 0 lyekutaa .
PFX wm 0 lyetutaa .
PFX wm 0 k'otoo .
PFX wm 0 k'ataa .
PFX wm 0 k'etaa .
PFX wm 0 kessii [^mn]
PFX wm 0 kessii mu
PFX wm 0 kessii [^mn]
PFX wm 0 kessii mu
PFX wm 0 ketutaa .
PFX wm 0 kemutaa .
PFX wm 0 kebataa .
PFX wm 0 kegutaa .
PFX wm 0 kegitaa .
PFX wm 0 kezitaa .
PFX wm 0 kekitaa .
PFX wm 0 kebitaa .
PFX wm 0 kelitaa .
PFX wm 0 kegataa .
PFX wm 0 kekataa .
PFX wm 0 kebutaa .
PFX wm 0 kelutaa .
PFX wm 0 kekutaa .
PFX wm 0 ketutaa ."""

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
    "wm": "Subordinating conjunction when with negative subjects in near future tense",
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

    out_flag = "FP"
    left_desc = FLAG_DESCRIPTIONS.get("wm", "wm")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "wm", left_desc, "Ob", right_desc, out_flag
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
