import re
import os

AFF_FILE = r"e:\Luganda Hunspell Dictionary\New.aff"

# Rule SB (Near Past Subjects) (was flag G)
rule_g_raw = """\
PFX SB 0 nna .
PFX SB 0 wa .
PFX SB 0 ya .
PFX SB 0 eya .
PFX SB 0 twa .
PFX SB 0 mwa .
PFX SB 0 baa .
PFX SB 0 abaa .
PFX SB 0 gwa .
PFX SB 0 ogwa .
PFX SB 0 gya .
PFX SB 0 egya .
PFX SB 0 zaa .
PFX SB 0 ezaa .
PFX SB 0 kyaa .
PFX SB 0 ekyaa .
PFX SB 0 byaa .
PFX SB 0 ebyaa .
PFX SB 0 lyaa .
PFX SB 0 elyaa .
PFX SB 0 gaa .
PFX SB 0 agaa .
PFX SB 0 kaa .
PFX SB 0 akaa .
PFX SB 0 bwa .
PFX SB 0 obwa .
PFX SB 0 lwa .
PFX SB 0 olwa .
PFX SB 0 kwaa .
PFX SB 0 okwaa .
PFX SB 0 twaa .
PFX SB 0 otwaa .
"""

# Rule Ob (Objects) (was flag F)
rule_f_raw = """\
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
    # GG is the long-flag replacement for P (SB x Ob)
    output.append(f"PFX GG Y {len(new_rules)}")
    for r in new_rules:
        output.append(f"PFX GG {r['strip']} {r['add']} {r['cond']}")
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

    # Remove existing PFX GG lines to avoid duplicates
    new_lines = [line for line in lines if not line.strip().startswith("PFX GG ")]

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