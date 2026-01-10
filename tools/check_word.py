from pathlib import Path
from spylls.hunspell import Dictionary

# Load from repo root regardless of CWD
REPO_ROOT = Path(__file__).resolve().parents[1]
d = Dictionary.from_files(str(REPO_ROOT / "Luganda"))

words = ["luma", "baluma", "ziluma", "baziluma", "zibaluma"]
for w in words:
    print(f"{w}: {'OK' if d.lookup(w) else 'NO'}")

# for suggestion in d.suggest('spylls'):
#         print(sugestion)