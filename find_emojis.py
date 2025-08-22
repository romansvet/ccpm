#!/usr/bin/env python3
"""Find all emoji characters in Python files."""

import re
from pathlib import Path

# Emoji ranges based on Unicode standards
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002600-\U000027BF"  # Miscellaneous symbols
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U00002300-\U000023FF"  # Miscellaneous Technical
    "\U00002B50-\U00002B55"  # stars
    "\U00002700-\U000027BF"  # Dingbats
    "\U0001F004-\U0001F0CF"  # Mahjong/playing cards
    "\U00002194-\U000021AA"  # arrows
    "\U00002139"             # info
    "\U00002714"             # check mark
    "\U0000274C"             # cross mark
    "\U00002705"             # white check mark
    "\U000026A0-\U000026A1"  # warning sign
    "\U0001F194-\U0001F19A"  # squared letters
    "]+", 
    flags=re.UNICODE
)

def find_emojis_in_file(filepath):
    """Find all emojis in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        emojis_found = []
        for line_num, line in enumerate(content.splitlines(), 1):
            matches = EMOJI_PATTERN.findall(line)
            if matches:
                for emoji in matches:
                    emojis_found.append({
                        'file': str(filepath),
                        'line': line_num,
                        'emoji': emoji,
                        'context': line.strip()
                    })
        return emojis_found
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

def main():
    """Find all emojis in Python files."""
    # Search in ccpm directory
    ccpm_path = Path(__file__).parent / 'ccpm'
    
    all_emojis = []
    
    # Find all Python files
    for py_file in ccpm_path.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
        emojis = find_emojis_in_file(py_file)
        all_emojis.extend(emojis)
    
    # Also check shell scripts
    claude_scripts = Path(__file__).parent / '.claude'
    if claude_scripts.exists():
        for sh_file in claude_scripts.rglob('*.sh'):
            emojis = find_emojis_in_file(sh_file)
            all_emojis.extend(emojis)
    
    # Print results
    if all_emojis:
        print(f"Found {len(all_emojis)} emoji occurrences:\n")
        
        # Group by file
        files = {}
        for emoji_info in all_emojis:
            file = emoji_info['file']
            if file not in files:
                files[file] = []
            files[file].append(emoji_info)
        
        for file, emojis in files.items():
            print(f"\n{file}:")
            for emoji_info in emojis:
                print(f"  Line {emoji_info['line']}: {emoji_info['emoji']} -> {emoji_info['context'][:80]}")
    else:
        print("No emojis found in Python files!")

if __name__ == "__main__":
    main()