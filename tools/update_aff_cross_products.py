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
        print(f"Error: {AFF_FILE} not found")
        return
        
    print(f"Reading {AFF_FILE}...")
    lines = read_aff(AFF_FILE)
    
    # --- 1. Generate all new blocks and store them in a dictionary ---
    parsed_cache = {}
    new_blocks = {}
    all_target_flags = {t['t'] for t in TRANSFORMATIONS}

    for t in TRANSFORMATIONS:
        s_flag, o_flag, target = t['s'], t['o'], t['t']
        
        if s_flag not in parsed_cache: parsed_cache[s_flag] = parse_pfx_block(lines, s_flag)
        if o_flag not in parsed_cache: parsed_cache[o_flag] = parse_pfx_block(lines, o_flag)
        s_rules = parsed_cache[s_flag]
        o_rules = parsed_cache[o_flag]
        
        if not s_rules or not o_rules:
            print(f"Skipping {target} ({s_flag} x {o_flag}): Source rules not found.")
            continue
            
        print(f"Generating {target} from {s_flag} ({len(s_rules)}) x {o_flag} ({len(o_rules)})...")
        new_rules = generate_rules(s_rules, o_rules, t['filter'])
        
        block_content = []
        block_content.append(f"PFX {target} Y {len(new_rules)}\n")
        for r in new_rules:
            block_content.append(f"PFX {target} {r['strip']} {r['add']} {r['cond']}\n")
        new_blocks[target] = block_content

    # --- 2. Build the new file content by replacing blocks in-place ---
    final_lines = []
    line_idx = 0
    processed_flags = set()

    while line_idx < len(lines):
        line = lines[line_idx]
        stripped = line.strip()
        
        is_header = False
        target_flag = None
        old_rule_count = 0
        if stripped.startswith("PFX"):
            parts = stripped.split()
            if len(parts) >= 4 and parts[1] in new_blocks and parts[2] in ['Y', 'N']:
                is_header = True
                target_flag = parts[1]
                old_rule_count = int(parts[3])

        if is_header:
            # Found a block to replace. Add the new block content.
            final_lines.extend(new_blocks[target_flag])
            processed_flags.add(target_flag)
            
            # Advance line_idx to skip the old block's PFX lines
            line_idx += 1 # Skip the header
            rules_found = 0
            while line_idx < len(lines) and rules_found < old_rule_count:
                current_line = lines[line_idx].strip()
                if not current_line or current_line.startswith('#'):
                    line_idx += 1
                    continue
                
                if current_line.startswith(f"PFX {target_flag} "):
                    rules_found += 1
                else:
                    break
                line_idx += 1
        else:
            # Not a header to replace, just copy the line
            final_lines.append(line)
            line_idx += 1

    # --- 3. Append any completely new blocks that weren't found for replacement ---
    for target, block_lines in new_blocks.items():
        if target not in processed_flags:
            s_flag = [t['s'] for t in TRANSFORMATIONS if t['t'] == target][0]
            o_flag = [t['o'] for t in TRANSFORMATIONS if t['t'] == target][0]
            final_lines.append(f"\n# Cross product {s_flag} x {o_flag}\n")
            final_lines.extend(block_lines)

    # --- 4. Write the final content ---
    print("Updating file content...")
    with open(AFF_FILE, 'w', encoding='utf-8') as f:
        f.writelines(final_lines)
            
    print("Done! Luganda.aff updated.")

if __name__ == "__main__":
    main()