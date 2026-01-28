#!/usr/bin/env python3
"""
Fix Hunspell Dictionary Counts

This script corrects:
1. Wrong rule header counts in .aff files (PFX/SFX rule counts)
2. Wrong word counts in .dic files (first line count)

Usage:
    python fix_hunspell_counts.py [--aff AFFFILE] [--dic DICFILE] [--dry-run]

Examples:
    python fix_hunspell_counts.py --aff Luganda.aff --dic Luganda.dic
    python fix_hunspell_counts.py --dry-run  # Test without making changes
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Dict


class HunspellCountFixer:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.corrections_made = []
        
    def fix_aff_file(self, aff_path: Path) -> bool:
        """
        Fix rule counts in .aff file.
        Returns True if any corrections were made.
        """
        print(f"\n{'='*70}")
        print(f"Checking .aff file: {aff_path}")
        print(f"{'='*70}\n")
        
        if not aff_path.exists():
            print(f"❌ Error: File not found: {aff_path}")
            return False
        
        with open(aff_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        corrected_lines = []
        corrections = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            corrected_lines.append(line)
            
            # Match PFX or SFX header: "PFX PS Y 41"
            match = re.match(r'^(PFX|SFX)\s+(\S+)\s+([YN])\s+(\d+)', line)
            
            if match:
                rule_type = match.group(1)  # PFX or SFX
                flag_name = match.group(2)  # e.g., PS, gg, ko
                cross_flag = match.group(3)  # Y or N
                declared_count = int(match.group(4))
                
                # Count actual rules following this header
                actual_count = 0
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    # Check if this is a rule line for the current flag
                    if re.match(rf'^{rule_type}\s+{re.escape(flag_name)}\s+', next_line):
                        actual_count += 1
                        j += 1
                    else:
                        # Stop when we hit a different rule or empty line
                        break
                
                # Check if count matches
                if declared_count != actual_count:
                    correction = {
                        'type': 'AFF',
                        'rule_type': rule_type,
                        'flag': flag_name,
                        'line_num': i + 1,
                        'declared': declared_count,
                        'actual': actual_count
                    }
                    corrections.append(correction)
                    
                    # Update the line with correct count
                    corrected_line = re.sub(
                        r'^(PFX|SFX)\s+(\S+)\s+([YN])\s+\d+',
                        f'{rule_type} {flag_name} {cross_flag} {actual_count}',
                        line
                    )
                    corrected_lines[-1] = corrected_line
                    
                    print(f"⚠️  {rule_type} {flag_name} (line {i+1}):")
                    print(f"   Declared: {declared_count} rules")
                    print(f"   Actual:   {actual_count} rules")
                    print(f"   {'[DRY RUN] Would correct' if self.dry_run else '✅ CORRECTED'}\n")
            
            i += 1
        
        # Write corrected file if not dry run and corrections were made
        if corrections and not self.dry_run:
            with open(aff_path, 'w', encoding='utf-8') as f:
                f.writelines(corrected_lines)
            print(f"✅ Saved corrections to {aff_path}\n")
        elif corrections and self.dry_run:
            print(f"🔍 [DRY RUN] No changes written to {aff_path}\n")
        else:
            print(f"✅ No corrections needed in {aff_path}\n")
        
        self.corrections_made.extend(corrections)
        return len(corrections) > 0
    
    def fix_dic_file(self, dic_path: Path) -> bool:
        """
        Fix word count in .dic file.
        Returns True if correction was made.
        """
        print(f"\n{'='*70}")
        print(f"Checking .dic file: {dic_path}")
        print(f"{'='*70}\n")
        
        if not dic_path.exists():
            print(f"❌ Error: File not found: {dic_path}")
            return False
        
        with open(dic_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            print(f"❌ Error: Empty file: {dic_path}")
            return False
        
        # First line should be the word count
        first_line = lines[0].strip()
        
        try:
            declared_count = int(first_line)
        except ValueError:
            print(f"❌ Error: First line is not a number: '{first_line}'")
            return False
        
        # Count actual words (excluding first line, blank lines, and comments)
        actual_count = 0
        for line in lines[1:]:  # Skip first line (the count)
            stripped = line.strip()
            # Skip blank lines and comments (lines starting with #)
            if stripped and not stripped.startswith('#'):
                actual_count += 1
        
        correction_made = False
        
        if declared_count != actual_count:
            correction = {
                'type': 'DIC',
                'line_num': 1,
                'declared': declared_count,
                'actual': actual_count
            }
            self.corrections_made.append(correction)
            
            print(f"⚠️  Word count mismatch:")
            print(f"   Declared: {declared_count} words")
            print(f"   Actual:   {actual_count} words")
            print(f"   Difference: {actual_count - declared_count:+d}")
            print(f"   {'[DRY RUN] Would correct' if self.dry_run else '✅ CORRECTED'}\n")
            
            if not self.dry_run:
                lines[0] = f"{actual_count}\n"
                with open(dic_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                print(f"✅ Saved corrections to {dic_path}\n")
            else:
                print(f"🔍 [DRY RUN] No changes written to {dic_path}\n")
            
            correction_made = True
        else:
            print(f"✅ No corrections needed in {dic_path}\n")
        
        return correction_made
    
    def print_summary(self):
        """Print summary of all corrections made."""
        print(f"\n{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}\n")
        
        if not self.corrections_made:
            print("✅ No corrections needed. All counts are accurate!")
            return
        
        aff_corrections = [c for c in self.corrections_made if c['type'] == 'AFF']
        dic_corrections = [c for c in self.corrections_made if c['type'] == 'DIC']
        
        if aff_corrections:
            print(f"📝 .aff file corrections: {len(aff_corrections)}")
            for corr in aff_corrections:
                diff = corr['actual'] - corr['declared']
                print(f"   • {corr['rule_type']} {corr['flag']}: "
                      f"{corr['declared']} → {corr['actual']} ({diff:+d})")
        
        if dic_corrections:
            print(f"\n📝 .dic file corrections: {len(dic_corrections)}")
            for corr in dic_corrections:
                diff = corr['actual'] - corr['declared']
                print(f"   • Word count: {corr['declared']} → {corr['actual']} ({diff:+d})")
        
        print(f"\n{'Total corrections: ' + str(len(self.corrections_made))}")
        
        if self.dry_run:
            print("\n🔍 DRY RUN MODE: No files were modified")
        else:
            print("\n✅ All corrections have been applied")


def main():
    parser = argparse.ArgumentParser(
        description='Fix Hunspell dictionary and affix file counts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fix both files in current directory
  python fix_hunspell_counts.py --aff Luganda.aff --dic Luganda.dic
  
  # Test without making changes
  python fix_hunspell_counts.py --aff Luganda.aff --dic Luganda.dic --dry-run
  
  # Fix only .aff file
  python fix_hunspell_counts.py --aff Luganda.aff
  
  # Fix only .dic file
  python fix_hunspell_counts.py --dic Luganda.dic
        """
    )
    
    parser.add_argument(
        '--aff',
        type=str,
        help='Path to .aff file (default: Luganda.aff in current directory)'
    )
    
    parser.add_argument(
        '--dic',
        type=str,
        help='Path to .dic file (default: Luganda.dic in current directory)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test mode - show what would be changed without modifying files'
    )
    
    args = parser.parse_args()
    
    # Default file paths
    if args.aff is None and args.dic is None:
        # If neither specified, use defaults
        args.aff = 'Luganda.aff'
        args.dic = 'Luganda.dic'
    
    fixer = HunspellCountFixer(dry_run=args.dry_run)
    
    any_corrections = False
    
    # Fix .aff file if specified
    if args.aff:
        aff_path = Path(args.aff)
        if fixer.fix_aff_file(aff_path):
            any_corrections = True
    
    # Fix .dic file if specified
    if args.dic:
        dic_path = Path(args.dic)
        if fixer.fix_dic_file(dic_path):
            any_corrections = True
    
    # Print summary
    fixer.print_summary()
    
    # Exit code: 0 if corrections made or none needed, 1 if errors
    sys.exit(0)


if __name__ == '__main__':
    main()
