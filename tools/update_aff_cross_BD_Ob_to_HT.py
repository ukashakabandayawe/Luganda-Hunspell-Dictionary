import re
import os
from pathlib import Path

# Cross product generator: BD x Ob => HT
# Description:
# - Left block `BD`: BD
# - Right block `Ob`: Object markers
# - Output flag `HT`: Cross-product prefixes for BD x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX BD Y 247
PFX BD j ben jj
PFX BD 0 ben [^jbnmlhprxq]
PFX BD 0 bem [b]
PFX BD l bend [l]
PFX BD 0 betu .
PFX BD 0 bemu .
PFX BD 0 beba .
PFX BD 0 begu .
PFX BD 0 begi .
PFX BD 0 bezi .
PFX BD 0 beki .
PFX BD 0 bebi .
PFX BD 0 beli .
PFX BD 0 bega .
PFX BD 0 beka .
PFX BD 0 bebu .
PFX BD 0 belu .
PFX BD 0 beku .
PFX BD 0 betu .
PFX BD j gwen jj
PFX BD 0 gwen [^jbnmlhprxq]
PFX BD 0 gwem [b]
PFX BD l gwend [l]
PFX BD 0 gwetu .
PFX BD 0 gwemu .
PFX BD 0 gweba .
PFX BD 0 gwegu .
PFX BD 0 gwegi .
PFX BD 0 gwezi .
PFX BD 0 gweki .
PFX BD 0 gwebi .
PFX BD 0 gweli .
PFX BD 0 gwega .
PFX BD 0 gweka .
PFX BD 0 gwebu .
PFX BD 0 gwelu .
PFX BD 0 gweku .
PFX BD 0 gwetu .
PFX BD j gyen jj
PFX BD 0 gyen [^jbnmlhprxq]
PFX BD 0 gyem [b]
PFX BD l gyend [l]
PFX BD 0 gyetu .
PFX BD 0 gyemu .
PFX BD 0 gyeba .
PFX BD 0 gyegu .
PFX BD 0 gyegi .
PFX BD 0 gyezi .
PFX BD 0 gyeki .
PFX BD 0 gyebi .
PFX BD 0 gyeli .
PFX BD 0 gyega .
PFX BD 0 gyeka .
PFX BD 0 gyebu .
PFX BD 0 gyelu .
PFX BD 0 gyeku .
PFX BD 0 gyetu .
PFX BD j zen jj
PFX BD 0 zen [^jbnmlhprxq]
PFX BD 0 zem [b]
PFX BD l zend [l]
PFX BD 0 zetu .
PFX BD 0 zemu .
PFX BD 0 zeba .
PFX BD 0 zegu .
PFX BD 0 zegi .
PFX BD 0 zezi .
PFX BD 0 zeki .
PFX BD 0 zebi .
PFX BD 0 zeli .
PFX BD 0 zega .
PFX BD 0 zeka .
PFX BD 0 zebu .
PFX BD 0 zelu .
PFX BD 0 zeku .
PFX BD 0 zetu .
PFX BD j kyen jj
PFX BD 0 kyen [^jbnmlhprxq]
PFX BD 0 kyem [b]
PFX BD l kyend [l]
PFX BD 0 kyetu .
PFX BD 0 kyemu .
PFX BD 0 kyeba .
PFX BD 0 kyegu .
PFX BD 0 kyegi .
PFX BD 0 kyezi .
PFX BD 0 kyeki .
PFX BD 0 kyebi .
PFX BD 0 kyeli .
PFX BD 0 kyega .
PFX BD 0 kyeka .
PFX BD 0 kyebu .
PFX BD 0 kyelu .
PFX BD 0 kyeku .
PFX BD 0 kyetu .
PFX BD j byen jj
PFX BD 0 byen [^jbnmlhprxq]
PFX BD 0 byem [b]
PFX BD l byend [l]
PFX BD 0 byetu .
PFX BD 0 byemu .
PFX BD 0 byeba .
PFX BD 0 byegu .
PFX BD 0 byegi .
PFX BD 0 byezi .
PFX BD 0 byeki .
PFX BD 0 byebi .
PFX BD 0 byeli .
PFX BD 0 byega .
PFX BD 0 byeka .
PFX BD 0 byebu .
PFX BD 0 byelu .
PFX BD 0 byeku .
PFX BD 0 byetu .
PFX BD j lyen jj
PFX BD 0 lyen [^jbnmlhprxq]
PFX BD 0 lyem [b]
PFX BD l lyend [l]
PFX BD 0 lyetu .
PFX BD 0 lyemu .
PFX BD 0 lyeba .
PFX BD 0 lyegu .
PFX BD 0 lyegi .
PFX BD 0 lyezi .
PFX BD 0 lyeki .
PFX BD 0 lyebi .
PFX BD 0 lyeli .
PFX BD 0 lyega .
PFX BD 0 lyeka .
PFX BD 0 lyebu .
PFX BD 0 lyelu .
PFX BD 0 lyeku .
PFX BD 0 lyetu .
PFX BD j gen jj
PFX BD 0 gen [^jbnmlhprxq]
PFX BD 0 gem [b]
PFX BD l gend [l]
PFX BD 0 getu .
PFX BD 0 gemu .
PFX BD 0 geba .
PFX BD 0 gegu .
PFX BD 0 gegi .
PFX BD 0 gezi .
PFX BD 0 geki .
PFX BD 0 gebi .
PFX BD 0 geli .
PFX BD 0 gega .
PFX BD 0 geka .
PFX BD 0 gebu .
PFX BD 0 gelu .
PFX BD 0 geku .
PFX BD 0 getu .
PFX BD j ken jj
PFX BD 0 ken [^jbnmlhprxq]
PFX BD 0 kem [b]
PFX BD l kend [l]
PFX BD 0 ketu .
PFX BD 0 kemu .
PFX BD 0 keba .
PFX BD 0 kegu .
PFX BD 0 kegi .
PFX BD 0 kezi .
PFX BD 0 keki .
PFX BD 0 kebi .
PFX BD 0 keli .
PFX BD 0 kega .
PFX BD 0 keka .
PFX BD 0 kebu .
PFX BD 0 kelu .
PFX BD 0 keku .
PFX BD 0 ketu .
PFX BD j bwen jj
PFX BD 0 bwen [^jbnmlhprxq]
PFX BD 0 bwem [b]
PFX BD l bwend [l]
PFX BD 0 bwetu .
PFX BD 0 bwemu .
PFX BD 0 bweba .
PFX BD 0 bwegu .
PFX BD 0 bwegi .
PFX BD 0 bwezi .
PFX BD 0 bweki .
PFX BD 0 bwebi .
PFX BD 0 bweli .
PFX BD 0 bwega .
PFX BD 0 bweka .
PFX BD 0 bwebu .
PFX BD 0 bwelu .
PFX BD 0 bweku .
PFX BD 0 bwetu .
PFX BD j lwen jj
PFX BD 0 lwen [^jbnmlhprxq]
PFX BD 0 lwem [b]
PFX BD l lwend [l]
PFX BD 0 lwetu .
PFX BD 0 lwemu .
PFX BD 0 lweba .
PFX BD 0 lwegu .
PFX BD 0 lwegi .
PFX BD 0 lwezi .
PFX BD 0 lweki .
PFX BD 0 lwebi .
PFX BD 0 lweli .
PFX BD 0 lwega .
PFX BD 0 lweka .
PFX BD 0 lwebu .
PFX BD 0 lwelu .
PFX BD 0 lweku .
PFX BD 0 lwetu .
PFX BD j kwen jj
PFX BD 0 kwen [^jbnmlhprxq]
PFX BD 0 kwem [b]
PFX BD l kwend [l]
PFX BD 0 kwetu .
PFX BD 0 kwemu .
PFX BD 0 kweba .
PFX BD 0 kwegu .
PFX BD 0 kwegi .
PFX BD 0 kwezi .
PFX BD 0 kweki .
PFX BD 0 kwebi .
PFX BD 0 kweli .
PFX BD 0 kwega .
PFX BD 0 kweka .
PFX BD 0 kwebu .
PFX BD 0 kwelu .
PFX BD 0 kweku .
PFX BD 0 kwetu .
PFX BD j twen jj
PFX BD 0 twen [^jbnmlhprxq]
PFX BD 0 twem [b]
PFX BD l twend [l]
PFX BD 0 twetu .
PFX BD 0 twemu .
PFX BD 0 tweba .
PFX BD 0 twegu .
PFX BD 0 twegi .
PFX BD 0 twezi .
PFX BD 0 tweki .
PFX BD 0 twebi .
PFX BD 0 tweli .
PFX BD 0 twega .
PFX BD 0 tweka .
PFX BD 0 twebu .
PFX BD 0 twelu .
PFX BD 0 tweku .
PFX BD 0 twetu ."""

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
    "BD": "BD",
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

    out_flag = "HT"
    left_desc = FLAG_DESCRIPTIONS.get("BD", "BD")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "BD", left_desc, "Ob", right_desc, out_flag
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
