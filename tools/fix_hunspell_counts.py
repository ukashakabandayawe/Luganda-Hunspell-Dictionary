#!/usr/bin/env python3
"""
Fix Hunspell Dictionary Counts

This script corrects:
1. Wrong rule header counts in .aff files (PFX/SFX rule counts)
2. Wrong word counts in .dic files (first line count)
3. Duplicate flags on a single .dic entry (e.g. word/PSPS -> word/PS)

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
from typing import Optional


class HunspellCountFixer:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.corrections_made = []

    def _detect_flag_mode_from_aff(self, aff_path: Path) -> str:
        """Return Hunspell FLAG mode from .aff.

        Supported: short (default), long, num, UTF-8.
        """
        try:
            with open(aff_path, 'r', encoding='utf-8') as f:
                for raw_line in f:
                    line = raw_line.strip()
                    if not line or line.startswith('#'):
                        continue
                    m = re.match(r'^FLAG\s+(\S+)\s*$', line)
                    if m:
                        mode = m.group(1)
                        # Hunspell uses: long|num|UTF-8 (or absent => "short")
                        return mode
        except OSError:
            pass

        return 'short'

    def _split_dic_entry(self, line_no_newline: str) -> tuple[Optional[str], Optional[str], str, str]:
        """Split a .dic line into (word, flags, tail_ws_and_rest, leading_ws).

        - Only considers the first whitespace-delimited token for word/flags.
        - Returns (None, None, original_tail, leading_ws) for non-entry lines.
        """
        if not line_no_newline:
            return None, None, '', ''

        # Preserve any leading whitespace (rare in .dic, but keep it stable)
        leading_ws_match = re.match(r'^(\s*)', line_no_newline)
        leading_ws = leading_ws_match.group(1) if leading_ws_match else ''
        stripped_leading = line_no_newline[len(leading_ws):]
        if not stripped_leading or stripped_leading.startswith('#'):
            return None, None, '', leading_ws

        m = re.match(r'^(\S+)(\s+.*)?$', stripped_leading)
        if not m:
            return None, None, '', leading_ws

        token = m.group(1)
        tail = m.group(2) or ''

        # Find first unescaped '/'
        slash_index = None
        escaped = False
        for idx, ch in enumerate(token):
            if escaped:
                escaped = False
                continue
            if ch == '\\':
                escaped = True
                continue
            if ch == '/':
                slash_index = idx
                break

        if slash_index is None:
            return None, None, tail, leading_ws

        word = token[:slash_index]
        flags = token[slash_index + 1:]
        return word, flags, tail, leading_ws

    def _parse_flags(self, flags: str, flag_mode: str) -> Optional[list[str]]:
        """Parse the flags string into a list of flag tokens based on FLAG mode."""
        if flags is None:
            return None

        if flag_mode == 'num':
            # e.g. 12,13,4
            return [f for f in flags.split(',') if f]

        if flag_mode == 'long':
            # Two-character flags concatenated (e.g. PSObyy)
            if len(flags) % 2 != 0:
                return None
            return [flags[i:i + 2] for i in range(0, len(flags), 2)]

        if flag_mode == 'UTF-8':
            # Each Unicode codepoint is a flag
            return list(flags)

        # Default: "short" (single-byte flag chars)
        return list(flags)

    def _join_flags(self, tokens: list[str], flag_mode: str) -> str:
        if flag_mode == 'num':
            return ','.join(tokens)
        return ''.join(tokens)

    def _dedupe_preserve_order(self, tokens: list[str]) -> tuple[list[str], int]:
        seen: set[str] = set()
        deduped: list[str] = []
        removed = 0
        for token in tokens:
            if token in seen:
                removed += 1
                continue
            seen.add(token)
            deduped.append(token)
        return deduped, removed
        
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
    
    def fix_dic_file(
        self,
        dic_path: Path,
        *,
        flag_mode: str = 'short',
        fix_duplicate_flags: bool = True,
        max_duplicate_reports: int = 25,
    ) -> bool:
        """
        Fix issues in .dic file.
        - Fix word count (first line)
        - Optionally remove duplicate flags per entry

        Returns True if any correction was made.
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

        corrected_lines = list(lines)
        any_changes = False

        # Fix header word count
        if declared_count != actual_count:
            self.corrections_made.append({
                'type': 'DIC',
                'subtype': 'COUNT',
                'line_num': 1,
                'declared': declared_count,
                'actual': actual_count,
            })
            print(f"⚠️  Word count mismatch:")
            print(f"   Declared: {declared_count} words")
            print(f"   Actual:   {actual_count} words")
            print(f"   Difference: {actual_count - declared_count:+d}")
            print(f"   {'[DRY RUN] Would correct' if self.dry_run else '✅ CORRECTED'}\n")
            corrected_lines[0] = f"{actual_count}\n"
            any_changes = True

        # Fix duplicate flags per entry
        if fix_duplicate_flags:
            duplicate_fixes = 0
            duplicate_reports = 0
            for idx in range(1, len(corrected_lines)):
                original_line = corrected_lines[idx]
                line_wo_nl = original_line[:-1] if original_line.endswith('\n') else original_line
                nl = '\n' if original_line.endswith('\n') else ''

                word, flags, tail, leading_ws = self._split_dic_entry(line_wo_nl)
                if word is None or flags is None or flags == '':
                    continue

                tokens = self._parse_flags(flags, flag_mode)
                if tokens is None:
                    continue

                deduped_tokens, removed = self._dedupe_preserve_order(tokens)
                if removed <= 0:
                    continue

                new_flags = self._join_flags(deduped_tokens, flag_mode)
                new_token = f"{word}/{new_flags}"
                new_line = f"{leading_ws}{new_token}{tail}{nl}"
                corrected_lines[idx] = new_line
                any_changes = True
                duplicate_fixes += 1

                self.corrections_made.append({
                    'type': 'DIC',
                    'subtype': 'DUP_FLAGS',
                    'line_num': idx + 1,
                    'word': word,
                    'removed': removed,
                })

                if duplicate_reports < max_duplicate_reports:
                    duplicate_reports += 1
                    print(f"⚠️  Duplicate flags on '{word}' (line {idx + 1}): removed {removed}")
                    print(f"   {'[DRY RUN] Would rewrite' if self.dry_run else '✅ REWROTE'}: {word}/{flags} → {word}/{new_flags}\n")

            if duplicate_fixes and duplicate_reports >= max_duplicate_reports:
                remaining = duplicate_fixes - duplicate_reports
                if remaining > 0:
                    print(f"… and {remaining} more entries with duplicate flags were {'found' if self.dry_run else 'fixed'} (output truncated).\n")

        if any_changes:
            if self.dry_run:
                print(f"🔍 [DRY RUN] No changes written to {dic_path}\n")
            else:
                with open(dic_path, 'w', encoding='utf-8') as f:
                    f.writelines(corrected_lines)
                print(f"✅ Saved corrections to {dic_path}\n")
        else:
            print(f"✅ No corrections needed in {dic_path}\n")

        return any_changes
    
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
            count_fixes = [c for c in dic_corrections if c.get('subtype') == 'COUNT']
            dup_flag_fixes = [c for c in dic_corrections if c.get('subtype') == 'DUP_FLAGS']

            for corr in count_fixes:
                diff = corr['actual'] - corr['declared']
                print(f"   • Word count: {corr['declared']} → {corr['actual']} ({diff:+d})")

            if dup_flag_fixes:
                total_removed = sum(c.get('removed', 0) for c in dup_flag_fixes)
                print(f"   • Duplicate flags: fixed {len(dup_flag_fixes)} entries (removed {total_removed} duplicates)")
        
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

    parser.add_argument(
        '--no-fix-duplicate-flags',
        action='store_true',
        help='Disable removing duplicate flags on .dic entries'
    )
    
    args = parser.parse_args()
    
    # Default file paths
    if args.aff is None and args.dic is None:
        # If neither specified, use defaults
        args.aff = 'Luganda.aff'
        args.dic = 'Luganda.dic'
    
    fixer = HunspellCountFixer(dry_run=args.dry_run)
    
    any_corrections = False
    
    flag_mode = 'short'

    # Fix .aff file if specified
    if args.aff:
        aff_path = Path(args.aff)
        if fixer.fix_aff_file(aff_path):
            any_corrections = True
        if aff_path.exists():
            flag_mode = fixer._detect_flag_mode_from_aff(aff_path)
    
    # Fix .dic file if specified
    if args.dic:
        dic_path = Path(args.dic)

        # If no .aff provided but a sibling .aff exists, use it to detect flag mode.
        if not args.aff:
            sibling_aff = dic_path.with_suffix('.aff')
            if sibling_aff.exists():
                flag_mode = fixer._detect_flag_mode_from_aff(sibling_aff)

        if fixer.fix_dic_file(
            dic_path,
            flag_mode=flag_mode,
            fix_duplicate_flags=not args.no_fix_duplicate_flags,
        ):
            any_corrections = True
    
    # Print summary
    fixer.print_summary()
    
    # Exit code: 0 if corrections made or none needed, 1 if errors
    sys.exit(0)


if __name__ == '__main__':
    main()
