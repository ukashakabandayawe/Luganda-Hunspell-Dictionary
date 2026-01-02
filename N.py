import re

# Raw content of Rule SD (Subjects) from your file
# I have removed duplicates and organized them
rule_e_raw = """
PFX SD 0 n [^bnmlhprxq]
PFX SD 0 m [b]
PFX SD 0 o .
PFX SD l nd [l]
PFX SD 0 a .
PFX SD 0 tu .
PFX SD 0 mu .
PFX SD 0 ba .
PFX SD 0 aba .
PFX SD 0 gu .
PFX SD 0 ogu .
PFX SD 0 gi .
PFX SD 0 egi .
PFX SD 0 e [^aeiou]
PFX SD 0 zi .
PFX SD 0 ezi .
PFX SD 0 ki .
PFX SD 0 eki .
PFX SD 0 bi .
PFX SD 0 ebi .
PFX SD 0 li .
PFX SD 0 eli .
PFX SD 0 ga .
PFX SD 0 aga .
PFX SD 0 ka .
PFX SD 0 aka .
PFX SD 0 bu .
PFX SD 0 obu .
PFX SD 0 lu .
PFX SD 0 olu .
PFX SD 0 ku .
PFX SD 0 oku .
PFX SD 0 otu .
"""

# Raw content of Rule Ob (Objects) from your file
rule_f_raw = """
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

subjects = parse_rules(rule_e_raw)
objects = parse_rules(rule_f_raw)

new_rules = []

for sub in subjects:
    for obj in objects:
        # Logic: Subject attaches to Object.
        # We need to check if Subject's condition allows attaching to Object's 'add' string.
        
        # 1. Check Strip/Add compatibility
        # If Subject strips a character (e.g., 'l'), Object 'add' must start with that character.
        if sub['strip'] != '0':
            if not obj['add'].startswith(sub['strip']):
                continue # Incompatible
            # Calculate the prefix added by subject
            # Remove the stripped char from object string, prepend subject add
            # e.g. Sub: l->nd, Obj: li.  li -> i -> ndi.
            combined_prefix_start = sub['add'] + obj['add'][len(sub['strip']):]
        else:
            combined_prefix_start = sub['add'] + obj['add']

        # 2. Check Condition compatibility
        # If Subject has a condition, it applies to the Object string
        valid_combination = True
        if sub['cond'] != '.':
            # Regex check
            # Convert hunspell condition to python regex
            # [^...] is compatible, [...] is compatible
            pattern = sub['cond']
            # Hunspell conditions match the beginning of the word (here, the object marker)
            if not re.match(pattern, obj['add']):
                valid_combination = False
        
        if valid_combination:
            # The new rule N applies to the STEM.
            # So it inherits the Strip and Condition from the OBJECT rule.
            # The Add part is the Combined Prefix.
            
            new_entry = {
                'strip': obj['strip'],
                'add': combined_prefix_start,
                'cond': obj['cond']
            }
            new_rules.append(new_entry)

# Output the result
print(f"PFX NN Y {len(new_rules)}")
for r in new_rules:
    print(f"PFX NN {r['strip']} {r['add']} {r['cond']}")
