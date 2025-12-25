import re

# Raw content of Rule E (Subjects) from your file
# I have removed duplicates and organized them
rule_e_raw = """
PFX E 0 n [^bnmlhprxq]
PFX E 0 m [b]
PFX E 0 o .
PFX E l nd [l]
PFX E 0 a .
PFX E 0 tu .
PFX E 0 mu .
PFX E 0 ba .
PFX E 0 aba .
PFX E 0 gu .
PFX E 0 ogu .
PFX E 0 gi .
PFX E 0 egi .
PFX E 0 e [^aeiou]
PFX E 0 zi .
PFX E 0 ezi .
PFX E 0 ki .
PFX E 0 eki .
PFX E 0 bi .
PFX E 0 ebi .
PFX E 0 li .
PFX E 0 eli .
PFX E 0 ga .
PFX E 0 aga .
PFX E 0 ka .
PFX E 0 aka .
PFX E 0 bu .
PFX E 0 obu .
PFX E 0 lu .
PFX E 0 olu .
PFX E 0 ku .
PFX E 0 oku .
PFX E 0 otu .
"""

# Raw content of Rule F (Objects) from your file
rule_f_raw = """
PFX F 0 n .
PFX F l nd l.[^mn]
PFX F l nn l.[mn]
PFX F w mp [w]
PFX F 0 mu .
PFX F 0 ba .
PFX F 0 gu .
PFX F 0 gi .
PFX F 0 zi . 
PFX F 0 ki .
PFX F 0 bi .
PFX F 0 li .
PFX F 0 ga .
PFX F 0 ka .
PFX F 0 bu .
PFX F 0 lu .
PFX F 0 ku .
PFX F 0 tu .
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
print(f"PFX N Y {len(new_rules)}")
for r in new_rules:
    print(f"PFX N {r['strip']} {r['add']} {r['cond']}")
