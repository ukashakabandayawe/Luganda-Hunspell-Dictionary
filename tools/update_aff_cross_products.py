import re
import os
from pathlib import Path

# Resolve Luganda.aff from repository root
REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# Configuration for the cross products (FLAG long)
TRANSFORMATIONS = [
    # Source 1 (Subj), Source 2 (Obj), Target Flag, Filter Logic
    # a/b/c were negative subjects; F was object; H was special reflexive-object.
    # New long flags (see Luganda.aff comments):
    #   C->ps, a->np, b->nf, c->ff, E->SD, G->SB, J->SA, K->SE, L->SF, F->Ob, H->OR
    #   I->II, W->WW, T->TT, U->UU, V->VV, X->XX, Y->YY, Z->ZZ
    {'s': 'ps', 'o': 'Ob', 't': 'SS', 'filter': '1st_person'},
    {'s': 'np', 'o': 'Ob', 't': 'II', 'filter': '1st_person'},
    {'s': 'nf', 'o': 'Ob', 't': 'WW', 'filter': '1st_person'},
    {'s': 'ff', 'o': 'Ob', 't': 'TT', 'filter': '1st_person'},
    {'s': 'SD', 'o': 'OR', 't': 'UU', 'filter': None},
    {'s': 'SB', 'o': 'OR', 't': 'VV', 'filter': None},
    {'s': 'SA', 'o': 'OR', 't': 'XX', 'filter': None},
    {'s': 'SE', 'o': 'OR', 't': 'YY', 'filter': None},
    {'s': 'SF', 'o': 'OR', 't': 'ZZ', 'filter': None},
]

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
        # Exact match for flag to respect case sensitivity (e.g. 'a' vs 'A')
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
            break
            
    return rules

def is_1st_person_clash(subj_add, obj_add):
    """
    Checks for invalid combinations of 1st person subject and 1st person object.
    """
    # Common 1st person subject markers
    subj_1st = ['n', 'm', 'si', 'saa', 'sii', 'sili', 'ndi', 'nna']
    # Common 1st person object markers
    obj_1st = ['n', 'nd', 'nn', 'mp']
    
    if subj_add in subj_1st and obj_add in obj_1st:
        return True
    return False

def generate_rules(subj_rules, obj_rules, filter_type):
    new_rules = []
    for s in subj_rules:
        for o in obj_rules:
            # 1. Check Condition Compatibility
            # The subject attaches to the object string.
            # We must ensure the object string satisfies the subject's condition.
            if s['cond'] != '.':
                if not re.match(s['cond'], o['add']):
                    continue
            
            # 2. Check Strip/Add Compatibility
            # If subject strips characters, object must start with them.
            # (Note: Subject PFX usually has strip='0', but we check to be safe)
            if s['strip'] != '0':
                if not o['add'].startswith(s['strip']):
                    continue
                combined_add = s['add'] + o['add'][len(s['strip']):]
            else:
                combined_add = s['add'] + o['add']
            
            # 3. Apply Filters
            if filter_type == '1st_person':
                if is_1st_person_clash(s['add'], o['add']):
                    continue
            
            new_rules.append({
                'strip': o['strip'],
                'add': combined_add,
                'cond': o['cond']
            })
    return new_rules

def main():
    if not os.path.exists(AFF_FILE):
        print(f"Error: {AFF_FILE} not found.")
        return

    out_flag, block = generate_block()
    
    with open(AFF_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find existing block for this flag (comment + PFX lines)
    first_flag_idx = None
    last_flag_idx = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(f"PFX {out_flag} "):
            if first_flag_idx is None:
                first_flag_idx = i
            last_flag_idx = i
    
    # Check if there's a comment line right before the first flag line
    if first_flag_idx is not None and first_flag_idx > 0:
        prev_line = lines[first_flag_idx - 1].strip()
        if prev_line.startswith("# Cross product"):
            start_idx = first_flag_idx - 1
        else:
            start_idx = first_flag_idx
    elif first_flag_idx is not None:
        start_idx = first_flag_idx
    else:
        start_idx = None

    # Replace block in place or append at end
    if start_idx is not None and last_flag_idx is not None:
        # Replace existing block in place
        new_lines = lines[:start_idx] + [block] + lines[last_flag_idx + 1:]
    else:
        # Append at end
        new_lines = lines
        if new_lines and not new_lines[-1].endswith(chr(10)):
            new_lines[-1] += chr(10)
        new_lines.append(block)

    with open(AFF_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"{out_flag}: updated in place.")

if __name__ == '__main__':
    main()
