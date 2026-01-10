import re
import os
from pathlib import Path

# Resolve Luganda.aff from repository root
REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# Rule ob (Object Relative)
# Cleaned up duplicates
rule_ob_raw = """
PFX ob 0 be [^aeioun]
PFX ob 0 gwe [^aeioun]
PFX ob 0 gye [^aeioun]
PFX ob 0 ze [^aeioun]
PFX ob 0 kye [^aeioun]
PFX ob 0 bye [^aeioun]
PFX ob 0 lye [^aeioun]
PFX ob 0 ge [^aeioun]
PFX ob 0 ke [^aeioun]
PFX ob 0 bwe [^aeioun]
PFX ob 0 lwe [^aeioun]
PFX ob 0 kwe [^aeioun]
PFX ob 0 twe [^aeioun]
PFX ob 0 ben naa
PFX ob 0 gwen naa
PFX ob 0 gyen naa
PFX ob 0 zen naa
PFX ob 0 kyen naa
PFX ob 0 byen naa
PFX ob 0 lyen naa
PFX ob 0 gen naa
PFX ob 0 ken naa
PFX ob 0 bwen naa
PFX ob 0 lwen naa
PFX ob 0 kwen naa
PFX ob 0 twen naa
"""

# Rule NF (Subject markers (affirmative): near future)
# Cleaned up duplicates
rule_nf_raw = """
PFX NF 0 naa .
PFX NF 0 munaa .
PFX NF 0 onoo .
PFX NF 0 onaa .
PFX NF 0 anaa .
PFX NF 0 tunaa .
PFX NF 0 banaa .
PFX NF 0 abanaa .
PFX NF 0 gunaa .
PFX NF 0 ogunaa .
PFX NF 0 ginaa .
PFX NF 0 eginaa .
PFX NF 0 enaa .
PFX NF 0 zinaa .
PFX NF 0 ezinaa .
PFX NF 0 kinaa .
PFX NF 0 ekinaa .
PFX NF 0 binaa .
PFX NF 0 ebinaa .
PFX NF 0 linaa .
PFX NF 0 elinaa .
PFX NF 0 ganaa .
PFX NF 0 aganaa .
PFX NF 0 kanaa .
PFX NF 0 akanaa .
PFX NF 0 bunaa .
PFX NF 0 obunaa .
PFX NF 0 lunaa .
PFX NF 0 olunaa .
PFX NF 0 kunaa .
PFX NF 0 okunaa .
PFX NF 0 otunaa .
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

def generate_bh_block():
    ob_rules = parse_rules(rule_ob_raw)
    nf_rules = parse_rules(rule_nf_raw)
    new_rules = []
    
    for o in ob_rules:
        for p in nf_rules:
            # Logic: ob (outer) attaches to NF (inner).
            
            # 1. Check Strip/Add compatibility
            # If outer (ob) has a strip, the inner (NF) add must start with it.
            if o['strip'] != '0':
                if not p['add'].startswith(o['strip']):
                    continue
                combined_add = o['add'] + p['add'][len(o['strip']):]
            else:
                combined_add = o['add'] + p['add']
            
            # 2. Check Condition compatibility
            # The outer rule (ob) condition must be satisfied by the inner rule (NF) add.
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
    output.append(f"# Cross product ob (Object Relative) x NF (Subject markers (affirmative): near future) -> BH")
    output.append(f"PFX BH Y {len(new_rules)}")
    for r in new_rules:
        output.append(f"PFX BH {r['strip']} {r['add']} {r['cond']}")
    return "\n".join(output) + "\n"

def main():
    if not os.path.exists(AFF_FILE):
        print(f"Error: {AFF_FILE} not found.")
        return

    print("Generating PFX BH rules...")
    bh_block = generate_bh_block()
    
    print(f"Reading {AFF_FILE}...")
    with open(AFF_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Remove existing PFX BH lines to avoid duplicates
    new_lines = []
    for line in lines:
        if line.strip().startswith("PFX BH "):
            continue
        # Also remove the comment header if it exists to avoid duplication
        if line.strip().startswith("# Cross product ob (Object Relative) x NF"):
            continue
        new_lines.append(line)

    # Ensure the file ends with a newline before appending
    if new_lines and not new_lines[-1].endswith('\n'):
        new_lines[-1] += '\n'

    # Append the new block
    new_lines.append(bh_block)

    print(f"Writing updates to {AFF_FILE}...")
    with open(AFF_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"Success! Added {bh_block.count(chr(10))} lines of rules.")

if __name__ == "__main__":
    main()
