import re
import os
from pathlib import Path

# Resolve Luganda.aff from repository root
REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

def read_aff(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def parse_pfx_block(lines, flag):
    """
    Parses a PFX block for a specific flag.
    Returns a list of rule dictionaries.
    """
    rules = []
    header_index = -1
    count = 0

    # Find the header line for the specified flag
    for i, line in enumerate(lines):
        line = line.strip()
        parts = line.split()
        if len(parts) >= 4 and parts[0] == 'PFX' and parts[1] == flag and parts[2] in ['Y', 'N']:
            header_index = i
            count = int(parts[3])
            break
    
    if header_index == -1:
        print(f"Warning: PFX flag '{flag}' header not found.")
        return []

    # Find the rules that belong to this block
    rules_found = 0
    for i in range(header_index + 1, len(lines)):
        if rules_found >= count:
            break
        
        line = lines[i].strip()
        if not line or line.startswith('#'):
            continue
        
        parts = line.split()
        if len(parts) >= 4 and parts[0] == 'PFX' and parts[1] == flag:
            rules.append({
                'strip': parts[2],
                'add': parts[3],
                'cond': parts[4] if len(parts) > 4 else '.'
            })
            rules_found += 1
        else:
            # The block ended unexpectedly (e.g., another directive was found)
            break
            
    return rules

def generate_cross_product(g_rules, f_rules):
    """
    Generates combined rules where g (infinitive) attaches to F (object).
    """
    new_rules = []
    for g in g_rules:
        # We only want to combine simple infinitive prefixes like 'oku'
        if g['strip'] != '0':
            continue
        
        for f in f_rules:
            combined_add = g['add'] + f['add']
            new_rules.append({
                'strip': f['strip'],
                'add': combined_add,
                'cond': f['cond']
            })
    return new_rules

def main():
    if not os.path.exists(AFF_FILE):
        print(f"Error: {AFF_FILE} not found")
        return
        
    print(f"Reading {AFF_FILE}...")
    lines = read_aff(AFF_FILE)
    
    # Long-flag mode mappings:
    #   g -> gg (infinitive)
    #   F -> Ob (object)
    g_rules = parse_pfx_block(lines, 'gg')
    f_rules = parse_pfx_block(lines, 'Ob')
    
    print(f"Found {len(g_rules)} rules for g (Infinitive) and {len(f_rules)} for F (Object).")
    
    new_rules = generate_cross_product(g_rules, f_rules)
    new_flag = 'MM'
    
    print(f"Generated {len(new_rules)} combined rules under new flag '{new_flag}'.")
    
    with open(AFF_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n# Cross product of Infinitive (gg) and Object (Ob)\n")
        f.write(f"PFX {new_flag} Y {len(new_rules)}\n")
        for r in new_rules:
            f.write(f"PFX {new_flag} {r['strip']} {r['add']} {r['cond']}\n")
            
    print(f"Success! Appended new PFX {new_flag} block to {AFF_FILE}")

if __name__ == "__main__":
    main()