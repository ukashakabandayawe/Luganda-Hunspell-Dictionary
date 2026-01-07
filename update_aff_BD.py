import re
import os

AFF_FILE = r"e:\Luganda Hunspell Dictionary\Luganda.aff"

# Rule ob (Object Relative)
# Cleaned up duplicates
rule_ob_raw = """
PFX ob 0 be [^aeiou]
PFX ob 0 gwe [^aeiou]
PFX ob 0 gye [^aeiou]
PFX ob 0 ze [^aeiou]
PFX ob 0 kye [^aeiou]
PFX ob 0 bye [^aeiou]
PFX ob 0 lye [^aeiou]
PFX ob 0 ge [^aeiou]
PFX ob 0 ke [^aeiou]
PFX ob 0 bwe [^aeiou]
PFX ob 0 lwe [^aeiou]
PFX ob 0 kwe [^aeiou]
PFX ob 0 twe [^aeiou]
PFX ob 0 ben nee
PFX ob 0 gwen nee
PFX ob 0 gyen nee
PFX ob 0 zen nee
PFX ob 0 kyen nee
PFX ob 0 byen nee
PFX ob 0 lyen nee
PFX ob 0 gen nee
PFX ob 0 ken nee
PFX ob 0 bwen nee
PFX ob 0 lwen nee
PFX ob 0 kwen nee
PFX ob 0 twen nee
"""

# Rule PS (Subject markers (affirmative): present simple + very near past)
rule_ps_raw = """
PFX PS j n jj
PFX PS 0 n [^jbnmlhprxq]
PFX PS 0 m [b]
PFX PS 0 o .
PFX PS l nd [l]
PFX PS 0 a .
PFX PS 0 tu .
PFX PS 0 mu .
PFX PS 0 ba .
PFX PS 0 aba .
PFX PS 0 gu .
PFX PS 0 ogu .
PFX PS 0 gi .
PFX PS 0 egi .
PFX PS 0 e [^aeiou]
PFX PS 0 zi .
PFX PS 0 ezi .
PFX PS 0 ki .
PFX PS 0 eki .
PFX PS 0 bi .
PFX PS 0 ebi .
PFX PS 0 li .
PFX PS 0 eli .
PFX PS 0 ga .
PFX PS 0 aga .
PFX PS 0 ka .
PFX PS 0 aka .
PFX PS 0 bu .
PFX PS 0 obu .
PFX PS 0 lu .
PFX PS 0 olu .
PFX PS 0 ku .
PFX PS 0 oku .
PFX PS 0 tu .
PFX PS 0 otu .
"""

def parse_rules(raw_text):
    rules = []
    for line in raw_text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) >= 4:
            # Format: PFX Flag Strip Add Condition
            cond = parts[4] if len(parts) > 4 else '.'
            rules.append({
                'strip': parts[2],
                'add': parts[3],
                'cond': cond
            })
    return rules

def generate_bd_block():
    ob_rules = parse_rules(rule_ob_raw)
    ps_rules = parse_rules(rule_ps_raw)
    new_rules = []
    
    for o in ob_rules:
        for p in ps_rules:
            # Logic: ob (outer) attaches to PS (inner).
            
            # 1. Check Strip/Add compatibility
            # If outer (ob) has a strip, the inner (PS) add must start with it.
            if o['strip'] != '0':
                if not p['add'].startswith(o['strip']):
                    continue
                combined_add = o['add'] + p['add'][len(o['strip']):]
            else:
                combined_add = o['add'] + p['add']
            
            # 2. Check Condition compatibility
            # The outer rule (ob) condition must be satisfied by the inner rule (PS) add.
            valid_combination = True
            if o['cond'] != '.':
                pattern = o['cond']
                if not re.match(pattern, p['add']):
                    valid_combination = False
            
            if valid_combination:
                # The new rule inherits the inner rule's strip and condition (applied to stem)
                new_entry = {
                    'strip': p['strip'],
                    'add': combined_add,
                    'cond': p['cond']
                }
                new_rules.append(new_entry)

    output = []
    output.append(f"# Cross product ob (These are objects as used in relative pronouns) x PS (Subject markers (affirmative): present simple + very near past) -> BD")
    output.append(f"PFX BD Y {len(new_rules)}")
    for r in new_rules:
        output.append(f"PFX BD {r['strip']} {r['add']} {r['cond']}")
    return "\n".join(output) + "\n"

def main():
    if not os.path.exists(AFF_FILE):
        print(f"Error: {AFF_FILE} not found.")
        return

    print("Generating PFX BD rules...")
    bd_block = generate_bd_block()
    
    print(f"Reading {AFF_FILE}...")
    with open(AFF_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Remove existing PFX BD lines to avoid duplicates
    new_lines = []
    for line in lines:
        if line.strip().startswith("PFX BD "):
            continue
        # Also remove the comment header if it exists to avoid duplication
        if line.strip().startswith("# Cross product ob (These are objects as used in relative pronouns) x PS"):
            continue
        new_lines.append(line)

    # Ensure the file ends with a newline before appending
    if new_lines and not new_lines[-1].endswith('\n'):
        new_lines[-1] += '\n'

    # Append the new block
    new_lines.append(bd_block)

    print(f"Writing updates to {AFF_FILE}...")
    with open(AFF_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"Success! Added {bd_block.count(chr(10))} lines of rules.")

if __name__ == "__main__":
    main()
