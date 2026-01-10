import re
import os
from pathlib import Path

# Resolve Luganda.aff from repository root
REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

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

# Rule nP (Negative Subject markers for the near past and distant past to be used in the combination [object]+[subject]+[stem])
rule_np_raw = """
PFX nP 0 saa .
PFX nP 0 otoo .
PFX nP 0 otaa .
PFX nP 0 ataa .
PFX nP 0 etaa .
PFX nP 0 mutaa .
PFX nP 0 bataa .
PFX nP 0 gutaa .
PFX nP 0 gitaa .
PFX nP 0 zitaa .
PFX nP 0 kitaa .
PFX nP 0 bitaa .
PFX nP 0 litaa .
PFX nP 0 gataa .
PFX nP 0 kataa .
PFX nP 0 butaa .
PFX nP 0 lutaa .
PFX nP 0 zitaa .
PFX nP 0 kutaa .
PFX nP 0 gataa .
PFX nP 0 tutaa .
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

def generate_bx_block():
    ob_rules = parse_rules(rule_ob_raw)
    np_rules = parse_rules(rule_np_raw)
    new_rules = []
    
    for o in ob_rules:
        for p in np_rules:
            # Logic: ob (outer) attaches to nP (inner).
            
            # 1. Check Strip/Add compatibility
            if o['strip'] != '0':
                if not p['add'].startswith(o['strip']):
                    continue
                combined_add = o['add'] + p['add'][len(o['strip']):]
            else:
                combined_add = o['add'] + p['add']
            
            # 2. Check Condition compatibility
            valid_combination = True
            if o['cond'] != '.':
                pattern = o['cond']
                if not re.match(pattern, p['add']):
                    valid_combination = False
            
            if valid_combination:
                new_entry = {
                    'strip': p['strip'],
                    'add': combined_add,
                    'cond': p['cond']
                }
                new_rules.append(new_entry)

    output = []
    output.append(f"# Cross product ob (Object Relative) x nP (Negative Past Relative Subject) -> BX")
    output.append(f"PFX BX Y {len(new_rules)}")
    for r in new_rules:
        output.append(f"PFX BX {r['strip']} {r['add']} {r['cond']}")
    return "\n".join(output) + "\n"

def main():
    if not os.path.exists(AFF_FILE):
        print(f"Error: {AFF_FILE} not found.")
        return

    print("Generating PFX BX rules...")
    bx_block = generate_bx_block()
    
    print(f"Reading {AFF_FILE}...")
    with open(AFF_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Remove existing PFX BX lines to avoid duplicates
    new_lines = []
    for line in lines:
        if line.strip().startswith("PFX BX "):
            continue
        # Also remove the comment header if it exists to avoid duplication
        if line.strip().startswith("# Cross product ob (Object Relative) x nP"):
            continue
        new_lines.append(line)

    # Ensure the file ends with a newline before appending
    if new_lines and not new_lines[-1].endswith('\n'):
        new_lines[-1] += '\n'

    # Append the new block
    new_lines.append(bx_block)

    print(f"Writing updates to {AFF_FILE}...")
    with open(AFF_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"Success! Added {bx_block.count(chr(10))} lines of rules.")

if __name__ == "__main__":
    main()