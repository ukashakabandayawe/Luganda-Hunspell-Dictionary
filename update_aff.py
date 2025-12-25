import re
import os

AFF_FILE = r"e:\Luganda Hunspell Dictionary\New.aff"

# Rule G (Near Past Subjects)
rule_g_raw = """
PFX G 0 nna .
PFX G 0 wa .
PFX G 0 ya .
PFX G 0 eya .
PFX G 0 twa .
PFX G 0 mwa .
PFX G 0 baa .
PFX G 0 abaa .
PFX G 0 gwa .
PFX G 0 ogwa .
PFX G 0 gya .
PFX G 0 egya .
PFX G 0 zaa .
PFX G 0 ezaa .
PFX G 0 kyaa .
PFX G 0 ekyaa .
PFX G 0 byaa .
PFX G 0 ebyaa .
PFX G 0 lyaa .
PFX G 0 elyaa .
PFX G 0 gaa .
PFX G 0 agaa .
PFX G 0 kaa .
PFX G 0 akaa .
PFX G 0 bwa .
PFX G 0 obwa .
PFX G 0 lwa .
PFX G 0 olwa .
PFX G 0 kwaa .
PFX G 0 okwaa .
PFX G 0 twaa .
PFX G 0 otwaa .
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

def generate_p_block():
    subjects = parse_rules(rule_g_raw)
    objects = parse_rules(rule_f_raw)
    new_rules = []

    for sub in subjects:
        for obj in objects:
            # Logic: Subject (G) attaches to Object (F).
            
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
    output.append(f"PFX P Y {len(new_rules)}")
    for r in new_rules:
        output.append(f"PFX P {r['strip']} {r['add']} {r['cond']}")
    return "\n".join(output) + "\n"

def main():
    if not os.path.exists(AFF_FILE):
        print(f"Error: {AFF_FILE} not found.")
        return

    print("Generating PFX P rules...")
    p_block = generate_p_block()

    print(f"Reading {AFF_FILE}...")
    with open(AFF_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Remove existing PFX P lines to avoid duplicates
    # This removes the placeholder or any previous PFX P definitions
    new_lines = [line for line in lines if not line.strip().startswith("PFX P ")]

    # Ensure the file ends with a newline before appending
    if new_lines and not new_lines[-1].endswith('\n'):
        new_lines[-1] += '\n'

    # Append the new block
    new_lines.append(p_block)

    print(f"Writing updates to {AFF_FILE}...")
    with open(AFF_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"Success! Added {p_block.count(chr(10))} lines of rules.")

if __name__ == "__main__":
    main()