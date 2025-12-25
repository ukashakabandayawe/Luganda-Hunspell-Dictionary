import re
import os

AFF_FILE = r"e:\Luganda Hunspell Dictionary\New.aff"

# Rule L (Far Future Tense Subjects)
# Cleaned up duplicates and normalized
rule_l_raw = """
PFX L 0 ndi .
PFX L 0 oli .
PFX L 0 ali .
PFX L 0 tuli .
PFX L 0 muli .
PFX L 0 bali .
PFX L 0 abali .
PFX L 0 guli .
PFX L 0 oguli .
PFX L 0 gili .
PFX L 0 egili .
PFX L 0 eli .
PFX L 0 zili .
PFX L 0 ezili .
PFX L 0 kili .
PFX L 0 ekili .
PFX L 0 bili .
PFX L 0 ebili .
PFX L 0 lili .
PFX L 0 elili .
PFX L 0 gali .
PFX L 0 agali .
PFX L 0 kali .
PFX L 0 akali .
PFX L 0 buli .
PFX L 0 obuli .
PFX L 0 luli .
PFX L 0 oluli .
PFX L 0 kuli .
PFX L 0 okuli .
PFX L 0 otuli .
"""

# Rule F (Objects)
rule_f_raw = """
PFX F 0 n .
PFX F l nd l.[^mn]
PFX F l nn l.[mn]
PFX F w mp [w]
PFX F 0 mu .
PFX F 0 ba .
PFX F 0 gu .
PFX F 0 gi .
PFX F 0 zi . 
PFX F 0 ki .
PFX F 0 bi .
PFX F 0 li .
PFX F 0 ga .
PFX F 0 ka .
PFX F 0 bu .
PFX F 0 lu .
PFX F 0 ku .
PFX F 0 tu .
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

def generate_r_block():
    subjects = parse_rules(rule_l_raw)
    objects = parse_rules(rule_f_raw)
    new_rules = []

    for sub in subjects:
        for obj in objects:
            # Logic: Subject (L) attaches to Object (F).
            
            # Prevent 1st person subject (ndi) combining with 1st person object (n, nd, nn, mp)
            # This prevents "ndinnuma" (ndi+nn), "ndinduma" (ndi+nd), etc. which should be reflexive
            if sub['add'] == 'ndi' and obj['add'] in ['n', 'nd', 'nn', 'mp']:
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
    output.append(f"PFX R Y {len(new_rules)}")
    for r in new_rules:
        output.append(f"PFX R {r['strip']} {r['add']} {r['cond']}")
    return "\n".join(output) + "\n"

def main():
    if not os.path.exists(AFF_FILE):
        print(f"Error: {AFF_FILE} not found.")
        return

    print("Generating PFX R rules...")
    r_block = generate_r_block()

    print(f"Reading {AFF_FILE}...")
    with open(AFF_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Remove existing PFX R lines to avoid duplicates
    new_lines = [line for line in lines if not line.strip().startswith("PFX R ")]

    # Ensure the file ends with a newline before appending
    if new_lines and not new_lines[-1].endswith('\n'):
        new_lines[-1] += '\n'

    # Append the new block
    new_lines.append(r_block)

    print(f"Writing updates to {AFF_FILE}...")
    with open(AFF_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"Success! Added {r_block.count(chr(10))} lines of rules.")

if __name__ == "__main__":
    main()