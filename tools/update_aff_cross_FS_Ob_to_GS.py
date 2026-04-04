import re
import os
from pathlib import Path

# Cross product generator: FS x Ob => GS
# Description:
# - Left block `FS`: FS
# - Right block `Ob`: Object markers
# - Output flag `GS`: Cross-product prefixes for FS x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX FS Y 283
PFX FS 0 wendiba .
PFX FS 0 wendigu .
PFX FS 0 wendigi .
PFX FS 0 wendizi .
PFX FS 0 wendiki .
PFX FS 0 wendibi .
PFX FS 0 wendili .
PFX FS 0 wendiga .
PFX FS 0 wendika .
PFX FS 0 wendibu .
PFX FS 0 wendilu .
PFX FS 0 wendiku .
PFX FS 0 wenditu .
PFX FS 0 wetulin [^lmnb]
PFX FS l wetulind l.[^mn]
PFX FS l wetulinn l.[mn]
PFX FS w wetulimp [w]
PFX FS 0 wetulimu .
PFX FS 0 wetuliba .
PFX FS 0 wetuligu .
PFX FS 0 wetuligi .
PFX FS 0 wetulizi .
PFX FS 0 wetuliki .
PFX FS 0 wetulibi .
PFX FS 0 wetulili .
PFX FS 0 wetuliga .
PFX FS 0 wetulika .
PFX FS 0 wetulibu .
PFX FS 0 wetulilu .
PFX FS 0 wetuliku .
PFX FS 0 wetulitu .
PFX FS 0 wemulin [^lmnb]
PFX FS l wemulind l.[^mn]
PFX FS l wemulinn l.[mn]
PFX FS w wemulimp [w]
PFX FS 0 wemulimu .
PFX FS 0 wemuliba .
PFX FS 0 wemuligu .
PFX FS 0 wemuligi .
PFX FS 0 wemulizi .
PFX FS 0 wemuliki .
PFX FS 0 wemulibi .
PFX FS 0 wemulili .
PFX FS 0 wemuliga .
PFX FS 0 wemulika .
PFX FS 0 wemulibu .
PFX FS 0 wemulilu .
PFX FS 0 wemuliku .
PFX FS 0 wemulitu .
PFX FS 0 webalin [^lmnb]
PFX FS l webalind l.[^mn]
PFX FS l webalinn l.[mn]
PFX FS w webalimp [w]
PFX FS 0 webalimu .
PFX FS 0 webaliba .
PFX FS 0 webaligu .
PFX FS 0 webaligi .
PFX FS 0 webalizi .
PFX FS 0 webaliki .
PFX FS 0 webalibi .
PFX FS 0 webalili .
PFX FS 0 webaliga .
PFX FS 0 webalika .
PFX FS 0 webalibu .
PFX FS 0 webalilu .
PFX FS 0 webaliku .
PFX FS 0 webalitu .
PFX FS 0 wegulin [^lmnb]
PFX FS l wegulind l.[^mn]
PFX FS l wegulinn l.[mn]
PFX FS w wegulimp [w]
PFX FS 0 wegulimu .
PFX FS 0 weguliba .
PFX FS 0 weguligu .
PFX FS 0 weguligi .
PFX FS 0 wegulizi .
PFX FS 0 weguliki .
PFX FS 0 wegulibi .
PFX FS 0 wegulili .
PFX FS 0 weguliga .
PFX FS 0 wegulika .
PFX FS 0 wegulibu .
PFX FS 0 wegulilu .
PFX FS 0 weguliku .
PFX FS 0 wegulitu .
PFX FS 0 wegilin [^lmnb]
PFX FS l wegilind l.[^mn]
PFX FS l wegilinn l.[mn]
PFX FS w wegilimp [w]
PFX FS 0 wegilimu .
PFX FS 0 wegiliba .
PFX FS 0 wegiligu .
PFX FS 0 wegiligi .
PFX FS 0 wegilizi .
PFX FS 0 wegiliki .
PFX FS 0 wegilibi .
PFX FS 0 wegilili .
PFX FS 0 wegiliga .
PFX FS 0 wegilika .
PFX FS 0 wegilibu .
PFX FS 0 wegililu .
PFX FS 0 wegiliku .
PFX FS 0 wegilitu .
PFX FS 0 wezilin [^lmnb]
PFX FS l wezilind l.[^mn]
PFX FS l wezilinn l.[mn]
PFX FS w wezilimp [w]
PFX FS 0 wezilimu .
PFX FS 0 weziliba .
PFX FS 0 weziligu .
PFX FS 0 weziligi .
PFX FS 0 wezilizi .
PFX FS 0 weziliki .
PFX FS 0 wezilibi .
PFX FS 0 wezilili .
PFX FS 0 weziliga .
PFX FS 0 wezilika .
PFX FS 0 wezilibu .
PFX FS 0 wezililu .
PFX FS 0 weziliku .
PFX FS 0 wezilitu .
PFX FS 0 wekilin [^lmnb]
PFX FS l wekilind l.[^mn]
PFX FS l wekilinn l.[mn]
PFX FS w wekilimp [w]
PFX FS 0 wekilimu .
PFX FS 0 wekiliba .
PFX FS 0 wekiligu .
PFX FS 0 wekiligi .
PFX FS 0 wekilizi .
PFX FS 0 wekiliki .
PFX FS 0 wekilibi .
PFX FS 0 wekilili .
PFX FS 0 wekiliga .
PFX FS 0 wekilika .
PFX FS 0 wekilibu .
PFX FS 0 wekililu .
PFX FS 0 wekiliku .
PFX FS 0 wekilitu .
PFX FS 0 webilin [^lmnb]
PFX FS l webilind l.[^mn]
PFX FS l webilinn l.[mn]
PFX FS w webilimp [w]
PFX FS 0 webilimu .
PFX FS 0 webiliba .
PFX FS 0 webiligu .
PFX FS 0 webiligi .
PFX FS 0 webilizi .
PFX FS 0 webiliki .
PFX FS 0 webilibi .
PFX FS 0 webilili .
PFX FS 0 webiliga .
PFX FS 0 webilika .
PFX FS 0 webilibu .
PFX FS 0 webililu .
PFX FS 0 webiliku .
PFX FS 0 webilitu .
PFX FS 0 welilin [^lmnb]
PFX FS l welilind l.[^mn]
PFX FS l welilinn l.[mn]
PFX FS w welilimp [w]
PFX FS 0 welilimu .
PFX FS 0 weliliba .
PFX FS 0 weliligu .
PFX FS 0 weliligi .
PFX FS 0 welilizi .
PFX FS 0 weliliki .
PFX FS 0 welilibi .
PFX FS 0 welilili .
PFX FS 0 weliliga .
PFX FS 0 welilika .
PFX FS 0 welilibu .
PFX FS 0 welililu .
PFX FS 0 weliliku .
PFX FS 0 welilitu .
PFX FS 0 wegalin [^lmnb]
PFX FS l wegalind l.[^mn]
PFX FS l wegalinn l.[mn]
PFX FS w wegalimp [w]
PFX FS 0 wegalimu .
PFX FS 0 wegaliba .
PFX FS 0 wegaligu .
PFX FS 0 wegaligi .
PFX FS 0 wegalizi .
PFX FS 0 wegaliki .
PFX FS 0 wegalibi .
PFX FS 0 wegalili .
PFX FS 0 wegaliga .
PFX FS 0 wegalika .
PFX FS 0 wegalibu .
PFX FS 0 wegalilu .
PFX FS 0 wegaliku .
PFX FS 0 wegalitu .
PFX FS 0 wekalin [^lmnb]
PFX FS l wekalind l.[^mn]
PFX FS l wekalinn l.[mn]
PFX FS w wekalimp [w]
PFX FS 0 wekalimu .
PFX FS 0 wekaliba .
PFX FS 0 wekaligu .
PFX FS 0 wekaligi .
PFX FS 0 wekalizi .
PFX FS 0 wekaliki .
PFX FS 0 wekalibi .
PFX FS 0 wekalili .
PFX FS 0 wekaliga .
PFX FS 0 wekalika .
PFX FS 0 wekalibu .
PFX FS 0 wekalilu .
PFX FS 0 wekaliku .
PFX FS 0 wekalitu .
PFX FS 0 webulin [^lmnb]
PFX FS l webulind l.[^mn]
PFX FS l webulinn l.[mn]
PFX FS w webulimp [w]
PFX FS 0 webulimu .
PFX FS 0 webuliba .
PFX FS 0 webuligu .
PFX FS 0 webuligi .
PFX FS 0 webulizi .
PFX FS 0 webuliki .
PFX FS 0 webulibi .
PFX FS 0 webulili .
PFX FS 0 webuliga .
PFX FS 0 webulika .
PFX FS 0 webulibu .
PFX FS 0 webulilu .
PFX FS 0 webuliku .
PFX FS 0 webulitu .
PFX FS 0 welulin [^lmnb]
PFX FS l welulind l.[^mn]
PFX FS l welulinn l.[mn]
PFX FS w welulimp [w]
PFX FS 0 welulimu .
PFX FS 0 weluliba .
PFX FS 0 weluligu .
PFX FS 0 weluligi .
PFX FS 0 welulizi .
PFX FS 0 weluliki .
PFX FS 0 welulibi .
PFX FS 0 welulili .
PFX FS 0 weluliga .
PFX FS 0 welulika .
PFX FS 0 welulibu .
PFX FS 0 welulilu .
PFX FS 0 weluliku .
PFX FS 0 welulitu .
PFX FS 0 wekulin [^lmnb]
PFX FS l wekulind l.[^mn]
PFX FS l wekulinn l.[mn]
PFX FS w wekulimp [w]
PFX FS 0 wekulimu .
PFX FS 0 wekuliba .
PFX FS 0 wekuligu .
PFX FS 0 wekuligi .
PFX FS 0 wekulizi .
PFX FS 0 wekuliki .
PFX FS 0 wekulibi .
PFX FS 0 wekulili .
PFX FS 0 wekuliga .
PFX FS 0 wekulika .
PFX FS 0 wekulibu .
PFX FS 0 wekulilu .
PFX FS 0 wekuliku .
PFX FS 0 wekulitu .
PFX FS 0 wetulin [^lmnb]
PFX FS l wetulind l.[^mn]
PFX FS l wetulinn l.[mn]
PFX FS w wetulimp [w]
PFX FS 0 wetulimu .
PFX FS 0 wetuliba .
PFX FS 0 wetuligu .
PFX FS 0 wetuligi .
PFX FS 0 wetulizi .
PFX FS 0 wetuliki .
PFX FS 0 wetulibi .
PFX FS 0 wetulili .
PFX FS 0 wetuliga .
PFX FS 0 wetulika .
PFX FS 0 wetulibu .
PFX FS 0 wetulilu .
PFX FS 0 wetuliku .
PFX FS 0 wetulitu ."""

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
    "FS": "FS",
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

    out_flag = "GS"
    left_desc = FLAG_DESCRIPTIONS.get("FS", "FS")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "FS", left_desc, "Ob", right_desc, out_flag
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
