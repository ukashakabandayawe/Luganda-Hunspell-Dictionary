import re
import os

AFF_FILE = r"e:\Luganda Hunspell Dictionary\New.aff"

# Rule K (Future Tense Subjects)
# Cleaned up duplicates and fixed formatting (added missing dots)
rule_k_raw = """
PFX K 0 naa .
PFX K 0 munaa .
PFX K 0 onoo .
PFX K 0 onaa .
PFX K 0 anaa .
PFX K 0 tunaa .
PFX K 0 banaa .
PFX K 0 abanaa .
PFX K 0 gunaa .
PFX K 0 ogunaa .
PFX K 0 ginaa .
PFX K 0 eginaa .
PFX K 0 enaa .
PFX K 0 zinaa .
PFX K 0 ezinaa .
PFX K 0 kinaa .
PFX K 0 ekinaa .
PFX K 0 binaa .
PFX K 0 ebinaa .
PFX K 0 linaa .
PFX K 0 elinaa .
PFX K 0 ganaa .
PFX K 0 aganaa .
PFX K 0 kanaa .
PFX K 0 akanaa .
PFX K 0 bunaa .
PFX K 0 obunaa .
PFX K 0 lunaa .
PFX K 0 olunaa .
PFX K 0 kunaa .
PFX K 0 okunaa .
PFX K 0 otunaa .
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
    output.append(f"PFX Q Y {len(new_rules)}")
    for r in new_rules:
        output.append(f"PFX Q {r['strip']} {r['add']} {r['cond']}")
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

    # Remove existing PFX Q lines to avoid duplicates
    new_lines = [line for line in lines if not line.strip().startswith("PFX Q ")]

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
