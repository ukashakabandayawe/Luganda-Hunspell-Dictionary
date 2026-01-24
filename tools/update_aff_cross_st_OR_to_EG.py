import re
import os
from pathlib import Path

# Cross product generator: st x OR => EG
# Left: st (lower case - near future subject markers "nnaaba...")
# Right: OR (special reflexive object markers)
# Output flag: EG

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

rule_left_raw = """
PFX st Y 34
PFX st 0 sikya .
PFX st 0 tokya .
PFX st 0 takya .
PFX st 0 atakya .
PFX st 0 tetukya .
PFX st 0 temukya .
PFX st 0 tebakya .
PFX st 0 abatakya .
PFX st 0 tegukya .
PFX st 0 ogutakya .
PFX st 0 tegikya .
PFX st 0 egitakya .
PFX st 0 tekya .
PFX st 0 etekya .
PFX st 0 tezikya .
PFX st 0 ezitakya .
PFX st 0 tekikya .
PFX st 0 ekitakya .
PFX st 0 tebikya .
PFX st 0 ebitakya .
PFX st 0 telikya .
PFX st 0 elitakya .
PFX st 0 tegakya .
PFX st 0 agatakya .
PFX st 0 tekakya .
PFX st 0 akatakya .
PFX st 0 tebukya .
PFX st 0 obutakya .
PFX st 0 telukya .
PFX st 0 olutakya .
PFX st 0 tekukya .
PFX st 0 okutakya .
PFX st 0 tetukya .
PFX st 0 otutakya .
"""

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
PFX OR 0 twe .
"""

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

    out_flag = 'EG'
    file_parts = Path(__file__).stem.split('_')
    desc_left = file_parts[3] if len(file_parts) >= 7 else '?'
    desc_right = file_parts[4] if len(file_parts) >= 7 else '?'
    flag_from_name = file_parts[6] if len(file_parts) >= 7 else out_flag
    
    flag_descriptions = {
        'yt': 'Using the adverb yet in reflexive verbs',
        'YT': 'Using the adverb yet',
        'yT': 'Subject markers of adverb yet for relative pronouns',
        'ob': 'Objects used in relative pronouns',
        'SC': 'Subordinating conjunction when with subjects in present simple tense',
        'sc': 'Subordinating conjunction when with negative subjects in present simple tense',
        'WN': 'Subordinating conjunction when with subjects in near and distant past tense',
        'wn': 'Subordinating conjunction when with negative subjects in near and distant past tense',
        'WM': 'Subordinating conjunction when with subjects in near future tense',
        'wm': 'Subordinating conjunction when with negative subjects in near future tense',
        'WF': 'Subordinating conjunction when with subjects in far future tense',
        'wf': 'Subordinating conjunction when with negative subjects in far future tense',
        'SB': 'Permission subjunctive',
        'CC': 'Counterfactual conditions',
        'St': 'Adverb still',
        'st': 'Negating adverb still to no longer',
        'LT': 'Adverbs like this and like that in present simple tense',
        'Ob': 'Object markers',
        'OR': 'Special reflexive object markers',
    }
    
    left_desc = flag_descriptions.get(desc_left, desc_left)
    right_desc = flag_descriptions.get(desc_right, desc_right)
    comment_line = f"# Cross product of {desc_left} ({left_desc}) and {desc_right} ({right_desc}) to {flag_from_name}"

    output = [comment_line, f"PFX {out_flag} Y {len(new_rules)}"]
    for r in new_rules:
        output.append(f"PFX {out_flag} {r['strip']} {r['add']} {r['cond']}")
    return (out_flag, "\n".join(output) + "\n")

def main():
    if not os.path.exists(AFF_FILE):
        print(f"Error: {AFF_FILE} not found.")
        return

    out_flag, block = generate_block()
    
    with open(AFF_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find existing block for this flag (comment + PFX lines)
    first_flag_idx = None
    last_flag_idx = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(f"PFX {out_flag} "):
            if first_flag_idx is None:
                first_flag_idx = i
            last_flag_idx = i
    
    # Check if there's a comment line right before the first flag line
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

    # Replace block in place or append at end
    if start_idx is not None and last_flag_idx is not None:
        # Replace existing block in place
        new_lines = lines[:start_idx] + [block] + lines[last_flag_idx + 1:]
    else:
        # Append at end
        new_lines = lines
        if new_lines and not new_lines[-1].endswith(chr(10)):
            new_lines[-1] += chr(10)
        new_lines.append(block)

    with open(AFF_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"{out_flag}: updated in place.")

if __name__ == '__main__':
    main()
