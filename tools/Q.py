import re
import os
from pathlib import Path

# Resolve New.aff from repository root
REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# Rule SE (Near-future Tense Subjects)
# Cleaned up duplicates and fixed formatting (added missing dots)
rule_k_raw = """
PFX SE 0 naa [^mn]
PFX SE 0 naa mu
PFX SE 0 munaa .
PFX SE 0 onoo .
PFX SE 0 onaa .
PFX SE 0 anaa .
PFX SE 0 tunaa .
PFX SE 0 banaa .
PFX SE 0 abanaa .
PFX SE 0 gunaa .
PFX SE 0 ogunaa .
PFX SE 0 ginaa .
PFX SE 0 eginaa .
PFX SE 0 enaa .
PFX SE 0 zinaa .
PFX SE 0 ezinaa .
PFX SE 0 kinaa .
PFX SE 0 ekinaa .
PFX SE 0 binaa .
PFX SE 0 ebinaa .
PFX SE 0 linaa .
PFX SE 0 elinaa .
PFX SE 0 ganaa .
PFX SE 0 aganaa .
PFX SE 0 kanaa .
PFX SE 0 akanaa .
PFX SE 0 bunaa .
PFX SE 0 obunaa .
PFX SE 0 lunaa .
PFX SE 0 olunaa .
PFX SE 0 kunaa .
PFX SE 0 okunaa .
PFX SE 0 otunaa .
"""

# Rule Ob (Objects)
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
            rules.append({
                'strip': parts[2],
                'add': parts[3],
                'cond': parts[4]
            })
    return rules

def generate_q_block():
    subjects = parse_rules(rule_k_raw)
    objects = parse_rules(rule_f_raw)
    new_rules = []

    for sub in subjects:
        for obj in objects:
            # Logic: Subject (K) attaches to Object (F).
            
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
                # The new rule Q applies to the STEM.
                # It inherits the Strip and Condition from the OBJECT rule (F).
                new_entry = {
                    'strip': obj['strip'],
                    'add': combined_prefix_start,
                    'cond': obj['cond']
                }
                new_rules.append(new_entry)

    output = []
    output.append(f"PFX QQ Y {len(new_rules)}")
    for r in new_rules:
        output.append(f"PFX QQ {r['strip']} {r['add']} {r['cond']}")
    return "\n".join(output) + "\n"

def main():
    if not os.path.exists(AFF_FILE):
        print(f"Error: {AFF_FILE} not found.")
        return

    print("Generating PFX Q rules...")
    q_block = generate_q_block()

    print(f"Reading {AFF_FILE}...")
    with open(AFF_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Remove existing PFX QQ lines to avoid duplicates
    new_lines = [line for line in lines if not line.strip().startswith("PFX QQ ")]

    # Ensure the file ends with a newline before appending
    if new_lines and not new_lines[-1].endswith('\n'):
        new_lines[-1] += '\n'

    # Append the new block
    new_lines.append(q_block)

    print(f"Writing updates to {AFF_FILE}...")
    with open(AFF_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"Success! Added {q_block.count(chr(10))} lines of rules.")

if __name__ == "__main__":
    main()
