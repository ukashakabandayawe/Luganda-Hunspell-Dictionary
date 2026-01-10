import re
import os
from pathlib import Path

# Resolve Luganda.aff from repository root
REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

def read_aff(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def parse_pfx_block(lines, start_index):
    """
    Parses a PFX block starting at start_index.
    Returns the list of rules and the index of the line following the block.
    """
    header = lines[start_index].strip().split()
    flag = header[1]
    count = int(header[3])
    
    rules = []
    current_idx = start_index + 1
    found = 0
    
    while found < count and current_idx < len(lines):
        line = lines[current_idx].strip()
        # Skip comments and empty lines within the block count
        if not line or line.startswith('#'):
            current_idx += 1
            continue
            
        if line.startswith(f"PFX {flag}"):
            parts = line.split()
            # Format: PFX flag strip add cond
            if len(parts) >= 4:
                rules.append({
                    'line_idx': current_idx,
                    'strip': parts[2],
                    'add': parts[3],
                    'cond': parts[4] if len(parts) > 4 else '.'
                })
                found += 1
        current_idx += 1
        
    return rules, current_idx

def get_y_rules(lines):
    """Extracts all rules for the impersonal prefix (PFX y)."""
    y_rules = []
    for i, line in enumerate(lines):
        # Long-flag mode: y -> yy
        if line.strip().startswith("PFX yy Y"):
            rules, _ = parse_pfx_block(lines, i)
            for r in rules:
                y_rules.append({'add': r['add'], 'cond': r['cond']})
            break
    return y_rules

def update_noun_rules(lines, y_rules):
    """
    Iterates through noun class rules (n-x), generates cross-product rules with y,
    and updates the file content.
    """
    # Long-flag mode mappings (see Luganda.aff comments):
    #   n..x -> Na..Nj
    #   g/h  -> gg/hh
    noun_flags = ['Na', 'Nb', 'Nc', 'Nd', 'Ne', 'Nf', 'Ng', 'Nh', 'Ni', 'Nj', 'gg', 'hh']
    
    # First pass: Parse existing noun blocks
    blocks = {}
    for i, line in enumerate(lines):
        if line.strip().startswith("PFX"):
            parts = line.strip().split()
            # Check if it's a PFX header for one of our noun flags
            if len(parts) >= 4 and parts[2] in ['Y', 'N']:
                flag = parts[1]
                if flag in noun_flags:
                    rules, end_idx = parse_pfx_block(lines, i)
                    blocks[flag] = {'start': i, 'end': end_idx, 'rules': rules}

    # Second pass: Generate new rules for each block
    new_blocks_content = {}
    
    for flag, block in blocks.items():
        original_rules = block['rules']
        generated_rules = []
        
        for n_rule in original_rules:
            n_strip = n_rule['strip']
            n_add = n_rule['add']
            n_cond = n_rule['cond']
            
            # Handle '0' which means empty string in Hunspell
            eff_n_add = "" if n_add == "0" else n_add
            
            for y_rule in y_rules:
                y_add = y_rule['add']
                y_cond = y_rule['cond']
                
                # Logic: The possessive prefix (y) attaches to the output of the noun rule (n).
                # Therefore, the output of n (eff_n_add) must satisfy the condition of y (y_cond).
                # e.g., y requires [aeiou], so n must produce a string starting with a vowel.
                
                if not eff_n_add:
                    continue
                
                try:
                    if re.match(y_cond, eff_n_add):
                        # Combine: Strip remains same, Add becomes y_add + n_add
                        combined_add = y_add + eff_n_add
                        generated_rules.append(f"PFX {flag} {n_strip} {combined_add} {n_cond}\n")
                except re.error:
                    continue
        
        new_blocks_content[flag] = generated_rules

    # Third pass: Reconstruct the file content
    output_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        is_noun_header = False
        target_flag = None
        
        if stripped.startswith("PFX"):
            parts = stripped.split()
            if len(parts) >= 4 and parts[2] in ['Y', 'N']:
                flag = parts[1]
                if flag in noun_flags and flag in new_blocks_content:
                    is_noun_header = True
                    target_flag = flag
        
        if is_noun_header:
            block = blocks[target_flag]
            original_rules = block['rules']
            new_rules = new_blocks_content[target_flag]
            
            # Update the count in the header
            total_count = len(original_rules) + len(new_rules)
            header_parts = stripped.split()
            header_parts[3] = str(total_count)
            new_header = " ".join(header_parts) + "\n"
            output_lines.append(new_header)
            
            # Copy original block content (preserving comments/formatting)
            for k in range(block['start'] + 1, block['end']):
                output_lines.append(lines[k])
            
            # Append new generated rules
            output_lines.extend(new_rules)
            
            # Move index to end of this block
            i = block['end']
        else:
            output_lines.append(line)
            i += 1
            
    return output_lines

def main():
    if not os.path.exists(AFF_FILE):
        print(f"Error: {AFF_FILE} not found")
        return
        
    print(f"Reading {AFF_FILE}...")
    lines = read_aff(AFF_FILE)
    
    y_rules = get_y_rules(lines)
    if not y_rules:
        print("No PFX y rules found.")
        return
        
    print(f"Found {len(y_rules)} impersonal prefix rules (PFX y).")
    
    new_lines = update_noun_rules(lines, y_rules)
    
    print(f"Writing updates to {AFF_FILE}...")
    with open(AFF_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        
    print("Done. Noun class rules have been updated with possessive prefixes.")

if __name__ == "__main__":
    main()
