import re
import os
from pathlib import Path

# Cross product generator: BK x Ob => ID
# Description:
# - Left block `BK`: BK
# - Right block `Ob`: Object markers
# - Output flag `ID`: Cross-product prefixes for BK x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX BK Y 320
PFX BK 0 bennaaka .
PFX BK 0 bewaaka .
PFX BK 0 beyaaka .
PFX BK 0 betwaka .
PFX BK 0 bemwaka .
PFX BK 0 bebaaka .
PFX BK 0 begwaka .
PFX BK 0 begyaka .
PFX BK 0 bezaaka .
PFX BK 0 bekyaka .
PFX BK 0 bebyaka .
PFX BK 0 belyaka .
PFX BK 0 begaaka .
PFX BK 0 bekaaka .
PFX BK 0 bebwaka .
PFX BK 0 belwaaka .
PFX BK 0 bezaaka .
PFX BK 0 bekwaaka .
PFX BK 0 begaaka .
PFX BK 0 betwaka .
PFX BK 0 gwennaaka .
PFX BK 0 gwewaaka .
PFX BK 0 gweyaaka .
PFX BK 0 gwetwaka .
PFX BK 0 gwemwaka .
PFX BK 0 gwebaaka .
PFX BK 0 gwegwaka .
PFX BK 0 gwegyaka .
PFX BK 0 gwezaaka .
PFX BK 0 gwekyaka .
PFX BK 0 gwebyaka .
PFX BK 0 gwelyaka .
PFX BK 0 gwegaaka .
PFX BK 0 gwekaaka .
PFX BK 0 gwebwaka .
PFX BK 0 gwelwaaka .
PFX BK 0 gwezaaka .
PFX BK 0 gwekwaaka .
PFX BK 0 gwegaaka .
PFX BK 0 gwetwaka .
PFX BK 0 gyennaaka .
PFX BK 0 gyewaaka .
PFX BK 0 gyeyaaka .
PFX BK 0 gyetwaka .
PFX BK 0 gyemwaka .
PFX BK 0 gyebaaka .
PFX BK 0 gyegwaka .
PFX BK 0 gyegyaka .
PFX BK 0 gyezaaka .
PFX BK 0 gyekyaka .
PFX BK 0 gyebyaka .
PFX BK 0 gyelyaka .
PFX BK 0 gyegaaka .
PFX BK 0 gyekaaka .
PFX BK 0 gyebwaka .
PFX BK 0 gyelwaaka .
PFX BK 0 gyezaaka .
PFX BK 0 gyekwaaka .
PFX BK 0 gyegaaka .
PFX BK 0 gyetwaka .
PFX BK 0 zennaaka .
PFX BK 0 zewaaka .
PFX BK 0 zeyaaka .
PFX BK 0 zetwaka .
PFX BK 0 zemwaka .
PFX BK 0 zebaaka .
PFX BK 0 zegwaka .
PFX BK 0 zegyaka .
PFX BK 0 zezaaka .
PFX BK 0 zekyaka .
PFX BK 0 zebyaka .
PFX BK 0 zelyaka .
PFX BK 0 zegaaka .
PFX BK 0 zekaaka .
PFX BK 0 zebwaka .
PFX BK 0 zelwaaka .
PFX BK 0 zezaaka .
PFX BK 0 zekwaaka .
PFX BK 0 zegaaka .
PFX BK 0 zetwaka .
PFX BK 0 kyennaaka .
PFX BK 0 kyewaaka .
PFX BK 0 kyeyaaka .
PFX BK 0 kyetwaka .
PFX BK 0 kyemwaka .
PFX BK 0 kyebaaka .
PFX BK 0 kyegwaka .
PFX BK 0 kyegyaka .
PFX BK 0 kyezaaka .
PFX BK 0 kyekyaka .
PFX BK 0 kyebyaka .
PFX BK 0 kyelyaka .
PFX BK 0 kyegaaka .
PFX BK 0 kyekaaka .
PFX BK 0 kyebwaka .
PFX BK 0 kyelwaaka .
PFX BK 0 kyezaaka .
PFX BK 0 kyekwaaka .
PFX BK 0 kyegaaka .
PFX BK 0 kyetwaka .
PFX BK 0 kyennaaka .
PFX BK 0 kyewaaka .
PFX BK 0 kyeyaaka .
PFX BK 0 kyetwaka .
PFX BK 0 kyemwaka .
PFX BK 0 kyebaaka .
PFX BK 0 kyegwaka .
PFX BK 0 kyegyaka .
PFX BK 0 kyezaaka .
PFX BK 0 kyekyaka .
PFX BK 0 kyebyaka .
PFX BK 0 kyelyaka .
PFX BK 0 kyegaaka .
PFX BK 0 kyekaaka .
PFX BK 0 kyebwaka .
PFX BK 0 kyelwaaka .
PFX BK 0 kyezaaka .
PFX BK 0 kyekwaaka .
PFX BK 0 kyegaaka .
PFX BK 0 kyetwaka .
PFX BK 0 byennaaka .
PFX BK 0 byewaaka .
PFX BK 0 byeyaaka .
PFX BK 0 byetwaka .
PFX BK 0 byemwaka .
PFX BK 0 byebaaka .
PFX BK 0 byegwaka .
PFX BK 0 byegyaka .
PFX BK 0 byezaaka .
PFX BK 0 byekyaka .
PFX BK 0 byebyaka .
PFX BK 0 byelyaka .
PFX BK 0 byegaaka .
PFX BK 0 byekaaka .
PFX BK 0 byebwaka .
PFX BK 0 byelwaaka .
PFX BK 0 byezaaka .
PFX BK 0 byekwaaka .
PFX BK 0 byegaaka .
PFX BK 0 byetwaka .
PFX BK 0 lyennaaka .
PFX BK 0 lyewaaka .
PFX BK 0 lyeyaaka .
PFX BK 0 lyetwaka .
PFX BK 0 lyemwaka .
PFX BK 0 lyebaaka .
PFX BK 0 lyegwaka .
PFX BK 0 lyegyaka .
PFX BK 0 lyezaaka .
PFX BK 0 lyekyaka .
PFX BK 0 lyebyaka .
PFX BK 0 lyelyaka .
PFX BK 0 lyegaaka .
PFX BK 0 lyekaaka .
PFX BK 0 lyebwaka .
PFX BK 0 lyelwaaka .
PFX BK 0 lyezaaka .
PFX BK 0 lyekwaaka .
PFX BK 0 lyegaaka .
PFX BK 0 lyetwaka .
PFX BK 0 gennaaka .
PFX BK 0 gewaaka .
PFX BK 0 geyaaka .
PFX BK 0 getwaka .
PFX BK 0 gemwaka .
PFX BK 0 gebaaka .
PFX BK 0 gegwaka .
PFX BK 0 gegyaka .
PFX BK 0 gezaaka .
PFX BK 0 gekyaka .
PFX BK 0 gebyaka .
PFX BK 0 gelyaka .
PFX BK 0 gegaaka .
PFX BK 0 gekaaka .
PFX BK 0 gebwaka .
PFX BK 0 gelwaaka .
PFX BK 0 gezaaka .
PFX BK 0 gekwaaka .
PFX BK 0 gegaaka .
PFX BK 0 getwaka .
PFX BK 0 kennaaka .
PFX BK 0 kewaaka .
PFX BK 0 keyaaka .
PFX BK 0 ketwaka .
PFX BK 0 kemwaka .
PFX BK 0 kebaaka .
PFX BK 0 kegwaka .
PFX BK 0 kegyaka .
PFX BK 0 kezaaka .
PFX BK 0 kekyaka .
PFX BK 0 kebyaka .
PFX BK 0 kelyaka .
PFX BK 0 kegaaka .
PFX BK 0 kekaaka .
PFX BK 0 kebwaka .
PFX BK 0 kelwaaka .
PFX BK 0 kezaaka .
PFX BK 0 kekwaaka .
PFX BK 0 kegaaka .
PFX BK 0 ketwaka .
PFX BK 0 bwennaaka .
PFX BK 0 bwewaaka .
PFX BK 0 bweyaaka .
PFX BK 0 bwetwaka .
PFX BK 0 bwemwaka .
PFX BK 0 bwebaaka .
PFX BK 0 bwegwaka .
PFX BK 0 bwegyaka .
PFX BK 0 bwezaaka .
PFX BK 0 bwekyaka .
PFX BK 0 bwebyaka .
PFX BK 0 bwelyaka .
PFX BK 0 bwegaaka .
PFX BK 0 bwekaaka .
PFX BK 0 bwebwaka .
PFX BK 0 bwelwaaka .
PFX BK 0 bwezaaka .
PFX BK 0 bwekwaaka .
PFX BK 0 bwegaaka .
PFX BK 0 bwetwaka .
PFX BK 0 lwennaaka .
PFX BK 0 lwewaaka .
PFX BK 0 lweyaaka .
PFX BK 0 lwetwaka .
PFX BK 0 lwemwaka .
PFX BK 0 lwebaaka .
PFX BK 0 lwegwaka .
PFX BK 0 lwegyaka .
PFX BK 0 lwezaaka .
PFX BK 0 lwekyaka .
PFX BK 0 lwebyaka .
PFX BK 0 lwelyaka .
PFX BK 0 lwegaaka .
PFX BK 0 lwekaaka .
PFX BK 0 lwebwaka .
PFX BK 0 lwelwaaka .
PFX BK 0 lwezaaka .
PFX BK 0 lwekwaaka .
PFX BK 0 lwegaaka .
PFX BK 0 lwetwaka .
PFX BK 0 zennaaka .
PFX BK 0 zewaaka .
PFX BK 0 zeyaaka .
PFX BK 0 zetwaka .
PFX BK 0 zemwaka .
PFX BK 0 zebaaka .
PFX BK 0 zegwaka .
PFX BK 0 zegyaka .
PFX BK 0 zezaaka .
PFX BK 0 zekyaka .
PFX BK 0 zebyaka .
PFX BK 0 zelyaka .
PFX BK 0 zegaaka .
PFX BK 0 zekaaka .
PFX BK 0 zebwaka .
PFX BK 0 zelwaaka .
PFX BK 0 zezaaka .
PFX BK 0 zekwaaka .
PFX BK 0 zegaaka .
PFX BK 0 zetwaka .
PFX BK 0 kwennaaka .
PFX BK 0 kwewaaka .
PFX BK 0 kweyaaka .
PFX BK 0 kwetwaka .
PFX BK 0 kwemwaka .
PFX BK 0 kwebaaka .
PFX BK 0 kwegwaka .
PFX BK 0 kwegyaka .
PFX BK 0 kwezaaka .
PFX BK 0 kwekyaka .
PFX BK 0 kwebyaka .
PFX BK 0 kwelyaka .
PFX BK 0 kwegaaka .
PFX BK 0 kwekaaka .
PFX BK 0 kwebwaka .
PFX BK 0 kwelwaaka .
PFX BK 0 kwezaaka .
PFX BK 0 kwekwaaka .
PFX BK 0 kwegaaka .
PFX BK 0 kwetwaka .
PFX BK 0 gennaaka .
PFX BK 0 gewaaka .
PFX BK 0 geyaaka .
PFX BK 0 getwaka .
PFX BK 0 gemwaka .
PFX BK 0 gebaaka .
PFX BK 0 gegwaka .
PFX BK 0 gegyaka .
PFX BK 0 gezaaka .
PFX BK 0 gekyaka .
PFX BK 0 gebyaka .
PFX BK 0 gelyaka .
PFX BK 0 gegaaka .
PFX BK 0 gekaaka .
PFX BK 0 gebwaka .
PFX BK 0 gelwaaka .
PFX BK 0 gezaaka .
PFX BK 0 gekwaaka .
PFX BK 0 gegaaka .
PFX BK 0 getwaka .
PFX BK 0 twennaaka .
PFX BK 0 twewaaka .
PFX BK 0 tweyaaka .
PFX BK 0 twetwaka .
PFX BK 0 twemwaka .
PFX BK 0 twebaaka .
PFX BK 0 twegwaka .
PFX BK 0 twegyaka .
PFX BK 0 twezaaka .
PFX BK 0 twekyaka .
PFX BK 0 twebyaka .
PFX BK 0 twelyaka .
PFX BK 0 twegaaka .
PFX BK 0 twekaaka .
PFX BK 0 twebwaka .
PFX BK 0 twelwaaka .
PFX BK 0 twezaaka .
PFX BK 0 twekwaaka .
PFX BK 0 twegaaka .
PFX BK 0 twetwaka ."""

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
    "BK": "BK",
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

    out_flag = "ID"
    left_desc = FLAG_DESCRIPTIONS.get("BK", "BK")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "BK", left_desc, "Ob", right_desc, out_flag
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
