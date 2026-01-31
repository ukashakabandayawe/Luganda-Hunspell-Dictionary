import re
import os
from pathlib import Path

# Cross product generator: LT x Ob => EH
# Left: LT (recent past tense markers "nzze..." etc.)
# Right: Ob (basic object markers)
# Output flag: EH

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

rule_left_raw = """
PFX LT Y 53
PFX LT j bwenzi jj 
PFX LT z bwenzi zze
PFX LT j bwen jj 
PFX LT 0 bwen [^jbnmlhprxq]  
PFX LT 0 bwem b
PFX LT 0 o . 
PFX LT l bwend l.[^mn] 
PFX LT l bwenn l.[mn] 
PFX LT l bwend li
PFX LT w bwemp w 
PFX LT 0 a .  
PFX LT 0 bwetu . 
PFX LT 0 bwemu . 
PFX LT 0 bweba . 
PFX LT 0 bweba .
PFX LT 0 bwegu .
PFX LT 0 bwegi .
PFX LT 0 e [^aeiou]
PFX LT 0 bwezi .
PFX LT 0 bweki .
PFX LT 0 bwebi .
PFX LT 0 bweli .
PFX LT 0 bwega .
PFX LT 0 bweka .
PFX LT 0 bwebu .
PFX LT 0 bwelu .
PFX LT 0 bweku .
PFX LT 0 bwetu .    
PFX LT j wenzi jj 
PFX LT z wenzi zze 
PFX LT j wen jj 
PFX LT 0 wen [^jbnmlhprxq] 
PFX LT 0 wem b 
PFX LT l wend l.[^mn] 
PFX LT l wenn l.[mn] 
PFX LT l wend li
PFX LT w wemp w 
PFX LT 0 wetu .
PFX LT 0 wemu . 
PFX LT 0 weba . 
PFX LT 0 weba .
PFX LT 0 wegu .
PFX LT 0 wegi .
PFX LT 0 wezi .
PFX LT 0 weki .
PFX LT 0 webi .
PFX LT 0 weli .
PFX LT 0 wega .
PFX LT 0 weka .
PFX LT 0 webu .
PFX LT 0 welu .
PFX LT 0 weku .
PFX LT 0 wetu .
"""

rule_right_raw = """
PFX Ob Y 18
PFX Ob 0 n [^lmnb]
PFX Ob l nd l.[^mn]
PFX Ob l nn l.[mn]
PFX Ob w mp w
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
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        s = s.split('#', 1)[0].strip()
        parts = s.split()
        if len(parts) < 4:
            continue
        if parts[2] == 'Y':
            continue
        cond = parts[4] if len(parts) > 4 else '.'
        rules.append({'strip': parts[2], 'add': parts[3], 'cond': cond})
    return rules

def generate_block():
    lefts = parse_rules(rule_left_raw)
    rights = parse_rules(rule_right_raw)
    new_rules = []
    for left in lefts:
        for right in rights:
            if left['strip'] != '0':
                if not right['add'].startswith(left['strip']):
                    continue
                combined = left['add'] + right['add'][len(left['strip']):]
            else:
                combined = left['add'] + right['add']
            if left['cond'] != '.':
                if not re.match(left['cond'], right['add']):
                    continue
            new_rules.append({'strip': right['strip'], 'add': combined, 'cond': right['cond']})

    out_flag = 'EH'
    file_parts = Path(__file__).stem.split('_')
    desc_left = file_parts[3] if len(file_parts) >= 7 else '?'
    desc_right = file_parts[4] if len(file_parts) >= 7 else '?'
    flag_from_name = file_parts[6] if len(file_parts) >= 7 else out_flag
    
    flag_descriptions = {
        'yt': 'Using the adverb yet in reflexive verbs',
        'YT': 'Using the adverb yet',
        'yT': 'Subject markers of adverb yet for relative pronouns',
        'ob': 'Objects used in relative pronouns',
        'SC': 'Subordinating conjunction when with subjects in present simple tense',
        'sc': 'Subordinating conjunction when with negative subjects in present simple tense',
        'WN': 'Subordinating conjunction when with subjects in near and distant past tense',
        'wn': 'Subordinating conjunction when with negative subjects in near and distant past tense',
        'WM': 'Subordinating conjunction when with subjects in near future tense',
        'wm': 'Subordinating conjunction when with negative subjects in near future tense',
        'WF': 'Subordinating conjunction when with subjects in far future tense',
        'wf': 'Subordinating conjunction when with negative subjects in far future tense',
        'SB': 'Permission subjunctive',
        'CC': 'Counterfactual conditions',
        'St': 'Adverb still',
        'st': 'Negating adverb still to no longer',
        'LT': 'Adverbs like this and like that in present simple tense',
        'Ob': 'Object markers',
        'OR': 'Special reflexive object markers',
    }
    
    left_desc = flag_descriptions.get(desc_left, desc_left)
    right_desc = flag_descriptions.get(desc_right, desc_right)
    comment_line = f"# Cross product of {desc_left} ({left_desc}) and {desc_right} ({right_desc}) to {flag_from_name}"

    output = [comment_line, f"PFX {out_flag} Y {len(new_rules)}"]
    for r in new_rules:
        output.append(f"PFX {out_flag} {r['strip']} {r['add']} {r['cond']}")
    return (out_flag, "\n".join(output) + "\n")

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
