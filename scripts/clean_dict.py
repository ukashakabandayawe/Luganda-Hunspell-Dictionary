import os
import re
import shutil

src = os.path.join(os.path.dirname(__file__), '..', 'Luganda.dic')
src = os.path.abspath(src)
backup = src + '.bak'
clean_out = os.path.join(os.path.dirname(__file__), '..', 'Luganda.cleaned.dic')
report_out = os.path.join(os.path.dirname(__file__), '..', 'Luganda_removed_report.txt')

# copy backup
shutil.copyfile(src, backup)

word_order = []
seen = set()
removed_lines = []

# pattern to strip non-letter/apostrophe/hyphen from ends
edge_strip = re.compile(r"(^[^A-Za-zÀ-ÖØ-öø-ÿ'-]+|[^A-Za-zÀ-ÖØ-öø-ÿ'-]+$)")

with open(src, 'r', encoding='utf-8', errors='replace') as f:
    for lineno, raw in enumerate(f, start=1):
        line = raw.strip()
        if not line:
            continue
        if line.startswith('#'):
            continue
        tokens = line.split()
        if not tokens:
            continue
        # find index of metadata token like 'noun' etc
        meta_idx = len(tokens)
        for i, t in enumerate(tokens):
            if 'noun' in t.lower() or t.lower() in ('also:', 'also', 'pronounced:'):
                meta_idx = i
                break
        head_tokens = tokens[:meta_idx]
        kept = []
        removed = []
        for tok in head_tokens:
            # remove parenthetical markers like (2), commas etc
            tok2 = edge_strip.sub('', tok)
            # strip surrounding punctuation remnants like parentheses, brackets, commas
            tok2 = tok2.strip('()[]{}.,;:"')
            # remove trailing ordinal markers
            tok2 = re.sub(r"\(\d+\)", "", tok2)
            # skip single-letter markers like 'I' 'II' 'III' or pure roman numerals
            if re.fullmatch(r"[IVXLCMivxlcm]+", tok2):
                removed.append((tok, 'pos/Morph marker'))
                continue
            # normalize interior punctuation: allow apostrophes and hyphens
            cleaned = edge_strip.sub('', tok2)
            cleaned_core = cleaned.replace("'", "").replace("-", "")
            if not cleaned_core:
                removed.append((tok, 'empty after strip'))
                continue
            # must contain only letters (unicode) after removing apostrophe/hyphen
            if cleaned_core.isalpha() and len(cleaned_core) >= 2:
                word = cleaned.lower()
                if word not in seen:
                    seen.add(word)
                    word_order.append(word)
                kept.append((tok, word))
            else:
                removed.append((tok, 'non-alpha or too short'))
        if removed:
            removed_lines.append((lineno, line, kept, removed))

with open(clean_out, 'w', encoding='utf-8') as out:
    out.write('# Cleaned Luganda dictionary — one word per line\n')
    for w in word_order:
        out.write(w + '\n')

with open(report_out, 'w', encoding='utf-8') as rep:
    rep.write('Backup of original: {}\n'.format(backup))
    rep.write('Total kept words: {}\n'.format(len(word_order)))
    rep.write('\nRemoved/flagged lines (samples):\n')
    for item in removed_lines[:500]:
        lineno, line, kept, removed = item
        rep.write(f'Line {lineno}: {line}\n')
        if kept:
            rep.write('  Kept: ' + ', '.join(k[1] for k in kept) + '\n')
        rep.write('  Removed: ' + ', '.join(f'{r[0]} ({r[1]})' for r in removed) + '\n\n')

print('Wrote', clean_out)
print('Wrote report', report_out)
print('Backup created at', backup)
