import re
import os
from pathlib import Path

# Cross product generator: BW x OR => HU
# Description:
# - Left block `BW`: BW
# - Right block `OR`: Special reflexive object markers
# - Output flag `HU`: Cross-product prefixes for BW x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX BW Y 304
PFX BW 0 bendimuku .
PFX BW 0 betulimuku .
PFX BW 0 bemulimuku .
PFX BW 0 bebalimuku .
PFX BW 0 bebalimuku .
PFX BW 0 begulimuku .
PFX BW 0 begilimuku .
PFX BW 0 bezilimuku .
PFX BW 0 bekilimuku .
PFX BW 0 bebilimuku .
PFX BW 0 belilimuku .
PFX BW 0 begalimuku .
PFX BW 0 bekalimuku .
PFX BW 0 bebulimuku .
PFX BW 0 belulimuku .
PFX BW 0 bezilimuku .
PFX BW 0 bekulimuku .
PFX BW 0 begalimuku .
PFX BW 0 betulimuku .
PFX BW 0 gwendimuku .
PFX BW 0 gwetulimuku .
PFX BW 0 gwemulimuku .
PFX BW 0 gwebalimuku .
PFX BW 0 gwebalimuku .
PFX BW 0 gwegulimuku .
PFX BW 0 gwegilimuku .
PFX BW 0 gwezilimuku .
PFX BW 0 gwekilimuku .
PFX BW 0 gwebilimuku .
PFX BW 0 gwelilimuku .
PFX BW 0 gwegalimuku .
PFX BW 0 gwekalimuku .
PFX BW 0 gwebulimuku .
PFX BW 0 gwelulimuku .
PFX BW 0 gwezilimuku .
PFX BW 0 gwekulimuku .
PFX BW 0 gwegalimuku .
PFX BW 0 gwetulimuku .
PFX BW 0 gyendimuku .
PFX BW 0 gyetulimuku .
PFX BW 0 gyemulimuku .
PFX BW 0 gyebalimuku .
PFX BW 0 gyebalimuku .
PFX BW 0 gyegulimuku .
PFX BW 0 gyegilimuku .
PFX BW 0 gyezilimuku .
PFX BW 0 gyekilimuku .
PFX BW 0 gyebilimuku .
PFX BW 0 gyelilimuku .
PFX BW 0 gyegalimuku .
PFX BW 0 gyekalimuku .
PFX BW 0 gyebulimuku .
PFX BW 0 gyelulimuku .
PFX BW 0 gyezilimuku .
PFX BW 0 gyekulimuku .
PFX BW 0 gyegalimuku .
PFX BW 0 gyetulimuku .
PFX BW 0 zendimuku .
PFX BW 0 zetulimuku .
PFX BW 0 zemulimuku .
PFX BW 0 zebalimuku .
PFX BW 0 zebalimuku .
PFX BW 0 zegulimuku .
PFX BW 0 zegilimuku .
PFX BW 0 zezilimuku .
PFX BW 0 zekilimuku .
PFX BW 0 zebilimuku .
PFX BW 0 zelilimuku .
PFX BW 0 zegalimuku .
PFX BW 0 zekalimuku .
PFX BW 0 zebulimuku .
PFX BW 0 zelulimuku .
PFX BW 0 zezilimuku .
PFX BW 0 zekulimuku .
PFX BW 0 zegalimuku .
PFX BW 0 zetulimuku .
PFX BW 0 kyendimuku .
PFX BW 0 kyetulimuku .
PFX BW 0 kyemulimuku .
PFX BW 0 kyebalimuku .
PFX BW 0 kyebalimuku .
PFX BW 0 kyegulimuku .
PFX BW 0 kyegilimuku .
PFX BW 0 kyezilimuku .
PFX BW 0 kyekilimuku .
PFX BW 0 kyebilimuku .
PFX BW 0 kyelilimuku .
PFX BW 0 kyegalimuku .
PFX BW 0 kyekalimuku .
PFX BW 0 kyebulimuku .
PFX BW 0 kyelulimuku .
PFX BW 0 kyezilimuku .
PFX BW 0 kyekulimuku .
PFX BW 0 kyegalimuku .
PFX BW 0 kyetulimuku .
PFX BW 0 kyendimuku .
PFX BW 0 kyetulimuku .
PFX BW 0 kyemulimuku .
PFX BW 0 kyebalimuku .
PFX BW 0 kyebalimuku .
PFX BW 0 kyegulimuku .
PFX BW 0 kyegilimuku .
PFX BW 0 kyezilimuku .
PFX BW 0 kyekilimuku .
PFX BW 0 kyebilimuku .
PFX BW 0 kyelilimuku .
PFX BW 0 kyegalimuku .
PFX BW 0 kyekalimuku .
PFX BW 0 kyebulimuku .
PFX BW 0 kyelulimuku .
PFX BW 0 kyezilimuku .
PFX BW 0 kyekulimuku .
PFX BW 0 kyegalimuku .
PFX BW 0 kyetulimuku .
PFX BW 0 byendimuku .
PFX BW 0 byetulimuku .
PFX BW 0 byemulimuku .
PFX BW 0 byebalimuku .
PFX BW 0 byebalimuku .
PFX BW 0 byegulimuku .
PFX BW 0 byegilimuku .
PFX BW 0 byezilimuku .
PFX BW 0 byekilimuku .
PFX BW 0 byebilimuku .
PFX BW 0 byelilimuku .
PFX BW 0 byegalimuku .
PFX BW 0 byekalimuku .
PFX BW 0 byebulimuku .
PFX BW 0 byelulimuku .
PFX BW 0 byezilimuku .
PFX BW 0 byekulimuku .
PFX BW 0 byegalimuku .
PFX BW 0 byetulimuku .
PFX BW 0 lyendimuku .
PFX BW 0 lyetulimuku .
PFX BW 0 lyemulimuku .
PFX BW 0 lyebalimuku .
PFX BW 0 lyebalimuku .
PFX BW 0 lyegulimuku .
PFX BW 0 lyegilimuku .
PFX BW 0 lyezilimuku .
PFX BW 0 lyekilimuku .
PFX BW 0 lyebilimuku .
PFX BW 0 lyelilimuku .
PFX BW 0 lyegalimuku .
PFX BW 0 lyekalimuku .
PFX BW 0 lyebulimuku .
PFX BW 0 lyelulimuku .
PFX BW 0 lyezilimuku .
PFX BW 0 lyekulimuku .
PFX BW 0 lyegalimuku .
PFX BW 0 lyetulimuku .
PFX BW 0 gendimuku .
PFX BW 0 getulimuku .
PFX BW 0 gemulimuku .
PFX BW 0 gebalimuku .
PFX BW 0 gebalimuku .
PFX BW 0 gegulimuku .
PFX BW 0 gegilimuku .
PFX BW 0 gezilimuku .
PFX BW 0 gekilimuku .
PFX BW 0 gebilimuku .
PFX BW 0 gelilimuku .
PFX BW 0 gegalimuku .
PFX BW 0 gekalimuku .
PFX BW 0 gebulimuku .
PFX BW 0 gelulimuku .
PFX BW 0 gezilimuku .
PFX BW 0 gekulimuku .
PFX BW 0 gegalimuku .
PFX BW 0 getulimuku .
PFX BW 0 kendimuku .
PFX BW 0 ketulimuku .
PFX BW 0 kemulimuku .
PFX BW 0 kebalimuku .
PFX BW 0 kebalimuku .
PFX BW 0 kegulimuku .
PFX BW 0 kegilimuku .
PFX BW 0 kezilimuku .
PFX BW 0 kekilimuku .
PFX BW 0 kebilimuku .
PFX BW 0 kelilimuku .
PFX BW 0 kegalimuku .
PFX BW 0 kekalimuku .
PFX BW 0 kebulimuku .
PFX BW 0 kelulimuku .
PFX BW 0 kezilimuku .
PFX BW 0 kekulimuku .
PFX BW 0 kegalimuku .
PFX BW 0 ketulimuku .
PFX BW 0 bwendimuku .
PFX BW 0 bwetulimuku .
PFX BW 0 bwemulimuku .
PFX BW 0 bwebalimuku .
PFX BW 0 bwebalimuku .
PFX BW 0 bwegulimuku .
PFX BW 0 bwegilimuku .
PFX BW 0 bwezilimuku .
PFX BW 0 bwekilimuku .
PFX BW 0 bwebilimuku .
PFX BW 0 bwelilimuku .
PFX BW 0 bwegalimuku .
PFX BW 0 bwekalimuku .
PFX BW 0 bwebulimuku .
PFX BW 0 bwelulimuku .
PFX BW 0 bwezilimuku .
PFX BW 0 bwekulimuku .
PFX BW 0 bwegalimuku .
PFX BW 0 bwetulimuku .
PFX BW 0 lwendimuku .
PFX BW 0 lwetulimuku .
PFX BW 0 lwemulimuku .
PFX BW 0 lwebalimuku .
PFX BW 0 lwebalimuku .
PFX BW 0 lwegulimuku .
PFX BW 0 lwegilimuku .
PFX BW 0 lwezilimuku .
PFX BW 0 lwekilimuku .
PFX BW 0 lwebilimuku .
PFX BW 0 lwelilimuku .
PFX BW 0 lwegalimuku .
PFX BW 0 lwekalimuku .
PFX BW 0 lwebulimuku .
PFX BW 0 lwelulimuku .
PFX BW 0 lwezilimuku .
PFX BW 0 lwekulimuku .
PFX BW 0 lwegalimuku .
PFX BW 0 lwetulimuku .
PFX BW 0 zendimuku .
PFX BW 0 zetulimuku .
PFX BW 0 zemulimuku .
PFX BW 0 zebalimuku .
PFX BW 0 zebalimuku .
PFX BW 0 zegulimuku .
PFX BW 0 zegilimuku .
PFX BW 0 zezilimuku .
PFX BW 0 zekilimuku .
PFX BW 0 zebilimuku .
PFX BW 0 zelilimuku .
PFX BW 0 zegalimuku .
PFX BW 0 zekalimuku .
PFX BW 0 zebulimuku .
PFX BW 0 zelulimuku .
PFX BW 0 zezilimuku .
PFX BW 0 zekulimuku .
PFX BW 0 zegalimuku .
PFX BW 0 zetulimuku .
PFX BW 0 kwendimuku .
PFX BW 0 kwetulimuku .
PFX BW 0 kwemulimuku .
PFX BW 0 kwebalimuku .
PFX BW 0 kwebalimuku .
PFX BW 0 kwegulimuku .
PFX BW 0 kwegilimuku .
PFX BW 0 kwezilimuku .
PFX BW 0 kwekilimuku .
PFX BW 0 kwebilimuku .
PFX BW 0 kwelilimuku .
PFX BW 0 kwegalimuku .
PFX BW 0 kwekalimuku .
PFX BW 0 kwebulimuku .
PFX BW 0 kwelulimuku .
PFX BW 0 kwezilimuku .
PFX BW 0 kwekulimuku .
PFX BW 0 kwegalimuku .
PFX BW 0 kwetulimuku .
PFX BW 0 gendimuku .
PFX BW 0 getulimuku .
PFX BW 0 gemulimuku .
PFX BW 0 gebalimuku .
PFX BW 0 gebalimuku .
PFX BW 0 gegulimuku .
PFX BW 0 gegilimuku .
PFX BW 0 gezilimuku .
PFX BW 0 gekilimuku .
PFX BW 0 gebilimuku .
PFX BW 0 gelilimuku .
PFX BW 0 gegalimuku .
PFX BW 0 gekalimuku .
PFX BW 0 gebulimuku .
PFX BW 0 gelulimuku .
PFX BW 0 gezilimuku .
PFX BW 0 gekulimuku .
PFX BW 0 gegalimuku .
PFX BW 0 getulimuku .
PFX BW 0 twendimuku .
PFX BW 0 twetulimuku .
PFX BW 0 twemulimuku .
PFX BW 0 twebalimuku .
PFX BW 0 twebalimuku .
PFX BW 0 twegulimuku .
PFX BW 0 twegilimuku .
PFX BW 0 twezilimuku .
PFX BW 0 twekilimuku .
PFX BW 0 twebilimuku .
PFX BW 0 twelilimuku .
PFX BW 0 twegalimuku .
PFX BW 0 twekalimuku .
PFX BW 0 twebulimuku .
PFX BW 0 twelulimuku .
PFX BW 0 twezilimuku .
PFX BW 0 twekulimuku .
PFX BW 0 twegalimuku .
PFX BW 0 twetulimuku ."""

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
    "BW": "BW",
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

    out_flag = "HU"
    left_desc = FLAG_DESCRIPTIONS.get("BW", "BW")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "BW", left_desc, "OR", right_desc, out_flag
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
