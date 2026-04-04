import re
import os
from pathlib import Path

# Cross product generator: BE x OR => HM
# Description:
# - Left block `BE`: BE
# - Right block `OR`: Special reflexive object markers
# - Output flag `HM`: Cross-product prefixes for BE x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX BE Y 320
PFX BE j ben jj
PFX BE 0 ben [^jbnmlhprxq]
PFX BE 0 bem [b]
PFX BE l bend [l]
PFX BE 0 betu .
PFX BE 0 bemu .
PFX BE 0 beba .
PFX BE 0 beba .
PFX BE 0 begu .
PFX BE 0 begi .
PFX BE 0 bezi .
PFX BE 0 beki .
PFX BE 0 bebi .
PFX BE 0 beli .
PFX BE 0 bega .
PFX BE 0 beka .
PFX BE 0 bebu .
PFX BE 0 belu .
PFX BE 0 beku .
PFX BE 0 betu .
PFX BE j gwen jj
PFX BE 0 gwen [^jbnmlhprxq]
PFX BE 0 gwem [b]
PFX BE l gwend [l]
PFX BE 0 gwetu .
PFX BE 0 gwemu .
PFX BE 0 gweba .
PFX BE 0 gweba .
PFX BE 0 gwegu .
PFX BE 0 gwegi .
PFX BE 0 gwezi .
PFX BE 0 gweki .
PFX BE 0 gwebi .
PFX BE 0 gweli .
PFX BE 0 gwega .
PFX BE 0 gweka .
PFX BE 0 gwebu .
PFX BE 0 gwelu .
PFX BE 0 gweku .
PFX BE 0 gwetu .
PFX BE j gyen jj
PFX BE 0 gyen [^jbnmlhprxq]
PFX BE 0 gyem [b]
PFX BE l gyend [l]
PFX BE 0 gyetu .
PFX BE 0 gyemu .
PFX BE 0 gyeba .
PFX BE 0 gyeba .
PFX BE 0 gyegu .
PFX BE 0 gyegi .
PFX BE 0 gyezi .
PFX BE 0 gyeki .
PFX BE 0 gyebi .
PFX BE 0 gyeli .
PFX BE 0 gyega .
PFX BE 0 gyeka .
PFX BE 0 gyebu .
PFX BE 0 gyelu .
PFX BE 0 gyeku .
PFX BE 0 gyetu .
PFX BE j zen jj
PFX BE 0 zen [^jbnmlhprxq]
PFX BE 0 zem [b]
PFX BE l zend [l]
PFX BE 0 zetu .
PFX BE 0 zemu .
PFX BE 0 zeba .
PFX BE 0 zeba .
PFX BE 0 zegu .
PFX BE 0 zegi .
PFX BE 0 zezi .
PFX BE 0 zeki .
PFX BE 0 zebi .
PFX BE 0 zeli .
PFX BE 0 zega .
PFX BE 0 zeka .
PFX BE 0 zebu .
PFX BE 0 zelu .
PFX BE 0 zeku .
PFX BE 0 zetu .
PFX BE j kyen jj
PFX BE 0 kyen [^jbnmlhprxq]
PFX BE 0 kyem [b]
PFX BE l kyend [l]
PFX BE 0 kyetu .
PFX BE 0 kyemu .
PFX BE 0 kyeba .
PFX BE 0 kyeba .
PFX BE 0 kyegu .
PFX BE 0 kyegi .
PFX BE 0 kyezi .
PFX BE 0 kyeki .
PFX BE 0 kyebi .
PFX BE 0 kyeli .
PFX BE 0 kyega .
PFX BE 0 kyeka .
PFX BE 0 kyebu .
PFX BE 0 kyelu .
PFX BE 0 kyeku .
PFX BE 0 kyetu .
PFX BE j kyen jj
PFX BE 0 kyen [^jbnmlhprxq]
PFX BE 0 kyem [b]
PFX BE l kyend [l]
PFX BE 0 kyetu .
PFX BE 0 kyemu .
PFX BE 0 kyeba .
PFX BE 0 kyeba .
PFX BE 0 kyegu .
PFX BE 0 kyegi .
PFX BE 0 kyezi .
PFX BE 0 kyeki .
PFX BE 0 kyebi .
PFX BE 0 kyeli .
PFX BE 0 kyega .
PFX BE 0 kyeka .
PFX BE 0 kyebu .
PFX BE 0 kyelu .
PFX BE 0 kyeku .
PFX BE 0 kyetu .
PFX BE j byen jj
PFX BE 0 byen [^jbnmlhprxq]
PFX BE 0 byem [b]
PFX BE l byend [l]
PFX BE 0 byetu .
PFX BE 0 byemu .
PFX BE 0 byeba .
PFX BE 0 byeba .
PFX BE 0 byegu .
PFX BE 0 byegi .
PFX BE 0 byezi .
PFX BE 0 byeki .
PFX BE 0 byebi .
PFX BE 0 byeli .
PFX BE 0 byega .
PFX BE 0 byeka .
PFX BE 0 byebu .
PFX BE 0 byelu .
PFX BE 0 byeku .
PFX BE 0 byetu .
PFX BE j lyen jj
PFX BE 0 lyen [^jbnmlhprxq]
PFX BE 0 lyem [b]
PFX BE l lyend [l]
PFX BE 0 lyetu .
PFX BE 0 lyemu .
PFX BE 0 lyeba .
PFX BE 0 lyeba .
PFX BE 0 lyegu .
PFX BE 0 lyegi .
PFX BE 0 lyezi .
PFX BE 0 lyeki .
PFX BE 0 lyebi .
PFX BE 0 lyeli .
PFX BE 0 lyega .
PFX BE 0 lyeka .
PFX BE 0 lyebu .
PFX BE 0 lyelu .
PFX BE 0 lyeku .
PFX BE 0 lyetu .
PFX BE j gen jj
PFX BE 0 gen [^jbnmlhprxq]
PFX BE 0 gem [b]
PFX BE l gend [l]
PFX BE 0 getu .
PFX BE 0 gemu .
PFX BE 0 geba .
PFX BE 0 geba .
PFX BE 0 gegu .
PFX BE 0 gegi .
PFX BE 0 gezi .
PFX BE 0 geki .
PFX BE 0 gebi .
PFX BE 0 geli .
PFX BE 0 gega .
PFX BE 0 geka .
PFX BE 0 gebu .
PFX BE 0 gelu .
PFX BE 0 geku .
PFX BE 0 getu .
PFX BE j ken jj
PFX BE 0 ken [^jbnmlhprxq]
PFX BE 0 kem [b]
PFX BE l kend [l]
PFX BE 0 ketu .
PFX BE 0 kemu .
PFX BE 0 keba .
PFX BE 0 keba .
PFX BE 0 kegu .
PFX BE 0 kegi .
PFX BE 0 kezi .
PFX BE 0 keki .
PFX BE 0 kebi .
PFX BE 0 keli .
PFX BE 0 kega .
PFX BE 0 keka .
PFX BE 0 kebu .
PFX BE 0 kelu .
PFX BE 0 keku .
PFX BE 0 ketu .
PFX BE j bwen jj
PFX BE 0 bwen [^jbnmlhprxq]
PFX BE 0 bwem [b]
PFX BE l bwend [l]
PFX BE 0 bwetu .
PFX BE 0 bwemu .
PFX BE 0 bweba .
PFX BE 0 bweba .
PFX BE 0 bwegu .
PFX BE 0 bwegi .
PFX BE 0 bwezi .
PFX BE 0 bweki .
PFX BE 0 bwebi .
PFX BE 0 bweli .
PFX BE 0 bwega .
PFX BE 0 bweka .
PFX BE 0 bwebu .
PFX BE 0 bwelu .
PFX BE 0 bweku .
PFX BE 0 bwetu .
PFX BE j lwen jj
PFX BE 0 lwen [^jbnmlhprxq]
PFX BE 0 lwem [b]
PFX BE l lwend [l]
PFX BE 0 lwetu .
PFX BE 0 lwemu .
PFX BE 0 lweba .
PFX BE 0 lweba .
PFX BE 0 lwegu .
PFX BE 0 lwegi .
PFX BE 0 lwezi .
PFX BE 0 lweki .
PFX BE 0 lwebi .
PFX BE 0 lweli .
PFX BE 0 lwega .
PFX BE 0 lweka .
PFX BE 0 lwebu .
PFX BE 0 lwelu .
PFX BE 0 lweku .
PFX BE 0 lwetu .
PFX BE j zen jj
PFX BE 0 zen [^jbnmlhprxq]
PFX BE 0 zem [b]
PFX BE l zend [l]
PFX BE 0 zetu .
PFX BE 0 zemu .
PFX BE 0 zeba .
PFX BE 0 zeba .
PFX BE 0 zegu .
PFX BE 0 zegi .
PFX BE 0 zezi .
PFX BE 0 zeki .
PFX BE 0 zebi .
PFX BE 0 zeli .
PFX BE 0 zega .
PFX BE 0 zeka .
PFX BE 0 zebu .
PFX BE 0 zelu .
PFX BE 0 zeku .
PFX BE 0 zetu .
PFX BE j kwen jj
PFX BE 0 kwen [^jbnmlhprxq]
PFX BE 0 kwem [b]
PFX BE l kwend [l]
PFX BE 0 kwetu .
PFX BE 0 kwemu .
PFX BE 0 kweba .
PFX BE 0 kweba .
PFX BE 0 kwegu .
PFX BE 0 kwegi .
PFX BE 0 kwezi .
PFX BE 0 kweki .
PFX BE 0 kwebi .
PFX BE 0 kweli .
PFX BE 0 kwega .
PFX BE 0 kweka .
PFX BE 0 kwebu .
PFX BE 0 kwelu .
PFX BE 0 kweku .
PFX BE 0 kwetu .
PFX BE j gen jj
PFX BE 0 gen [^jbnmlhprxq]
PFX BE 0 gem [b]
PFX BE l gend [l]
PFX BE 0 getu .
PFX BE 0 gemu .
PFX BE 0 geba .
PFX BE 0 geba .
PFX BE 0 gegu .
PFX BE 0 gegi .
PFX BE 0 gezi .
PFX BE 0 geki .
PFX BE 0 gebi .
PFX BE 0 geli .
PFX BE 0 gega .
PFX BE 0 geka .
PFX BE 0 gebu .
PFX BE 0 gelu .
PFX BE 0 geku .
PFX BE 0 getu .
PFX BE j twen jj
PFX BE 0 twen [^jbnmlhprxq]
PFX BE 0 twem [b]
PFX BE l twend [l]
PFX BE 0 twetu .
PFX BE 0 twemu .
PFX BE 0 tweba .
PFX BE 0 tweba .
PFX BE 0 twegu .
PFX BE 0 twegi .
PFX BE 0 twezi .
PFX BE 0 tweki .
PFX BE 0 twebi .
PFX BE 0 tweli .
PFX BE 0 twega .
PFX BE 0 tweka .
PFX BE 0 twebu .
PFX BE 0 twelu .
PFX BE 0 tweku .
PFX BE 0 twetu ."""

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
    "BE": "BE",
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

    out_flag = "HM"
    left_desc = FLAG_DESCRIPTIONS.get("BE", "BE")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "BE", left_desc, "OR", right_desc, out_flag
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
