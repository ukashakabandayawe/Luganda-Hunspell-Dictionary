# Fix Hunspell Counts Script

## Overview

`fix_hunspell_counts.py` is a utility script that automatically validates and corrects count mismatches in Hunspell dictionary files.

## What It Does

### .aff File (Affix Rules)
- Validates that each PFX/SFX rule header declares the correct number of rules
- Counts actual rules following each header
- Updates mismatched counts automatically
- Example: If `PFX PS Y 41` is declared but only 37 rules exist, it corrects to `PFX PS Y 37`

### .dic File (Word List)
- Validates that the first line (total word count) matches the actual number of words
- Counts all words in the file (excluding the first line)
- Updates the count if mismatched
- Example: If first line says `3007` but file has 3042 words, it corrects to `3042`

## Usage

### Basic Usage

```bash
# Fix both files (using defaults: Luganda.aff and Luganda.dic)
python tools/fix_hunspell_counts.py

# Fix specific files
python tools/fix_hunspell_counts.py --aff Luganda.aff --dic Luganda.dic

# Fix only .aff file
python tools/fix_hunspell_counts.py --aff Luganda.aff

# Fix only .dic file
python tools/fix_hunspell_counts.py --dic Luganda.dic
```

### Dry Run (Test Mode)

Preview what would be corrected without making changes:

```bash
python tools/fix_hunspell_counts.py --dry-run
```

### With PowerShell

```powershell
# Using virtual environment
& "E:/Luganda Hunspell Dictionary/.venv/Scripts/python.exe" tools\fix_hunspell_counts.py --dry-run

# Apply corrections
& "E:/Luganda Hunspell Dictionary/.venv/Scripts/python.exe" tools\fix_hunspell_counts.py
```

## Output Example

### Finding Issues

```
======================================================================
Checking .aff file: Luganda.aff
======================================================================

⚠️  PFX PS (line 1234):
   Declared: 41 rules
   Actual:   37 rules
   ✅ CORRECTED

======================================================================
Checking .dic file: Luganda.dic
======================================================================

⚠️  Word count mismatch:
   Declared: 3007 words
   Actual:   3042 words
   Difference: +35
   ✅ CORRECTED

✅ Saved corrections to Luganda.dic
```

### Summary

```
======================================================================
SUMMARY
======================================================================

📝 .aff file corrections: 1
   • PFX PS: 41 → 37 (-4)

📝 .dic file corrections: 1
   • Word count: 3007 → 3042 (+35)

Total corrections: 2

✅ All corrections have been applied
```

## When to Use This Script

Use this script whenever:
- ✅ You've manually edited the .aff file and added/removed rules
- ✅ You've added or removed words from the .dic file
- ✅ You get Hunspell errors about rule counts
- ✅ You want to validate dictionary integrity
- ✅ Before committing changes to version control
- ✅ After running automated dictionary generation scripts

## Command Line Options

| Option | Description |
|--------|-------------|
| `--aff FILE` | Path to .aff file (default: Luganda.aff) |
| `--dic FILE` | Path to .dic file (default: Luganda.dic) |
| `--dry-run` | Test mode - shows what would be changed without modifying files |
| `-h, --help` | Show help message |

## Exit Codes

- `0` - Success (corrections made or none needed)
- Non-zero - Error occurred

## Examples

### Example 1: Check Both Files Before Commit

```bash
# First, dry-run to see what needs fixing
python tools/fix_hunspell_counts.py --dry-run

# If corrections needed, apply them
python tools/fix_hunspell_counts.py

# Add to git
git add Luganda.aff Luganda.dic
git commit -m "Fixed dictionary counts"
```

### Example 2: After Bulk Edits

```bash
# After adding 50 new words to Luganda.dic
python tools/fix_hunspell_counts.py --dic Luganda.dic
```

### Example 3: After Generating New Rules

```bash
# After running update_aff_*.py scripts
python tools/fix_hunspell_counts.py --aff Luganda.aff
```

## Integration with Other Tools

This script works well with:
- `check_hunspell_counts.py` - Validates counts (read-only)
- `update_aff_*.py` scripts - Generate affix rules
- `clean_dict.py` - Clean and organize dictionary files

## Technical Details

### .aff File Format
```
PFX PS Y 41      ← Header: PFX [flag] [crossproduct] [count]
PFX PS 0 n .     ← Rule 1
PFX PS 0 o .     ← Rule 2
...              ← More rules
```

### .dic File Format
```
3042             ← First line: total word count
word1/FLAGS      ← Word 1
word2/FLAGS      ← Word 2
...              ← More words
```

## Troubleshooting

### "File not found"
Make sure you're running the script from the correct directory or use absolute paths.

### "First line is not a number"
The .dic file may be corrupted. The first line must contain only a number.

### Script doesn't find any issues
Great! Your dictionary counts are already correct.

## Contributing

If you find bugs or want to add features to this script, please:
1. Fork the repository
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

This script is part of the Luganda Hunspell Dictionary project and is licensed under GPL v3.
