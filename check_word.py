from spylls.hunspell import Dictionary

# Loads New.aff + New.dic (same basename: "New")
d = Dictionary.from_files("New")

words = ["luma", "baluma", "ziluma", "baziluma", "zibaluma"]
for w in words:
    print(f"{w}: {'OK' if d.lookup(w) else 'NO'}")