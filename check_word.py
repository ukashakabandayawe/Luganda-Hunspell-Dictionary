from spylls.hunspell import Dictionary

# Loads Luganda.aff + Luganda.dic (same basename: "Lugnada")
d = Dictionary.from_files("Luganda")

words = ["luma", "baluma", "ziluma", "baziluma", "zibaluma"]
for w in words:
    print(f"{w}: {'OK' if d.lookup(w) else 'NO'}")

# for suggestion in d.suggest('spylls'):
#         print(sugestion)