import re
import os
from pathlib import Path

# Resolve New.aff from repository root
REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "New.aff"

# Rule ps (Present Tense Negative Subjects) (was flag C)
# Cleaned up duplicates and normalized
rule_c_raw = """
PFX ps 0 si .
PFX ps 0 to .
PFX ps 0 ta .
PFX ps 0 tetu .
PFX ps 0 temu .
PFX ps 0 teba .
PFX ps 0 abata .
PFX ps 0 tegu .
PFX ps 0 oguta .
PFX ps 0 tegi .
PFX ps 0 egita .
PFX ps 0 te .
PFX ps 0 ete .
PFX ps 0 tezi .
PFX ps 0 ezita .
PFX ps 0 teki .
PFX ps 0 ekita .
PFX ps 0 tebi .
PFX ps 0 ebita .
PFX ps 0 teli .
PFX ps 0 elita .
PFX ps 0 tega .
PFX ps 0 agata .
PFX ps 0 teka .
PFX ps 0 akata .
PFX ps 0 tebu .
PFX ps 0 obuta .
PFX ps 0 telu .
PFX ps 0 oluta .
PFX ps 0 teku .
PFX ps 0 okuta .
PFX ps 0 tetu .
PFX ps 0 otuta .
"""

# Rule Ob (Objects) (was flag F)
rule_f_raw = """
PFX Ob 0 n .
PFX Ob l nd l.[^mn]
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
PFX Ob 0 tu .
"""

def parse_rules(raw_text):
    rules = []
    for line in raw_text.strip().split('\n'):
        parts = line.split()
        if len(parts) >= 4:
            # Format: PFX Flag Strip Add Condition
            # Handle cases where condition might be implicit or missing (default to .)
            cond = parts[4] if len(parts) > 4 else '.'
            rules.append({
                'strip': parts[2],
                'add': parts[3],
                'cond': cond
            })
    return rules

def generate_s_block():
    subjects = parse_rules(rule_c_raw)
    objects = parse_rules(rule_f_raw)
    new_rules = []

    for sub in subjects:
        for obj in objects:
            # Logic: Subject (C) attaches to Object (F).
            
            # Prevent 1st person subject negative (si) combining with 1st person object (n, nd, nn, mp)
            if sub['add'] == 'si' and obj['add'] in ['n', 'nd', 'nn', 'mp']:
                continue
            
            # 1. Check Strip/Add compatibility
            if sub['strip'] != '0':
                if not obj['add'].startswith(sub['strip']):
                    continue 
                combined_prefix_start = sub['add'] + obj['add'][len(sub['strip']):]
            else:
                combined_prefix_start = sub['add'] + obj['add']

            # 2. Check Condition compatibility
            valid_combination = True
            if sub['cond'] != '.':
                pattern = sub['cond']
                if not re.match(pattern, obj['add']):
                    valid_combination = False
            
            if valid_combination:
                new_entry = {
                    'strip': obj['strip'],
                    'add': combined_prefix_start,
                    'cond': obj['cond']
                }
                new_rules.append(new_entry)

    output = []
    # SS is the long-flag replacement for S (ps x Ob)
    output.append(f"PFX SS Y {len(new_rules)}")
    for r in new_rules:
        output.append(f"PFX SS {r['strip']} {r['add']} {r['cond']}")
    return "\n".join(output) + "\n"

def main():
    if not os.path.exists(AFF_FILE):
        print(f"Error: {AFF_FILE} not found.")
        return

    print("Generating PFX S rules...")
    s_block = generate_s_block()

    print(f"Reading {AFF_FILE}...")
    with open(AFF_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Remove existing PFX SS lines to avoid duplicates
    new_lines = [line for line in lines if not line.strip().startswith("PFX SS ")]

    # Ensure the file ends with a newline before appending
    if new_lines and not new_lines[-1].endswith('\n'):
        new_lines[-1] += '\n'

    # Append the new block
    new_lines.append(s_block)

    print(f"Writing updates to {AFF_FILE}...")
    with open(AFF_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"Success! Added {s_block.count(chr(10))} lines of rules.")

if __name__ == "__main__":
    main()