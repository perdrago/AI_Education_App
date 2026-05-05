"""
Script to fix indentation errors in lesson files by adding 'pass' after while/for loops with only blank lines.
"""

import os
import re

def fix_lesson_file(file_path):
    """Fix indentation errors in a lesson file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file has while True: followed by only comments/blanks
        lines = content.split('\n')
        new_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            new_lines.append(line)
            
            # Check if this is a while or for statement
            if line.strip().startswith('while ') and line.strip().endswith(':'):
                # Check if next non-empty line is not indented code
                j = i + 1
                has_code = False
                while j < len(lines):
                    next_line = lines[j]
                    # If we hit a non-indented line (not comment), break
                    if next_line.strip() and not next_line.strip().startswith('#') and not next_line.startswith('    '):
                        break
                    # If we find indented code (not comment), we have code
                    if next_line.strip() and not next_line.strip().startswith('#') and next_line.startswith('    '):
                        has_code = True
                        break
                    j += 1
                
                # If no code found, add pass
                if not has_code:
                    # Get indentation of while line
                    indent = len(line) - len(line.lstrip())
                    # Look ahead to find where to insert pass
                    # Insert pass after all comments/blanks
                    insert_pos = i + 1
                    while insert_pos < len(lines) and (not lines[insert_pos].strip() or lines[insert_pos].strip().startswith('#')):
                        new_lines.append(lines[insert_pos])
                        insert_pos += 1
                    # Add pass with proper indentation
                    new_lines.append(' ' * (indent + 4) + 'pass  # Placeholder for blank lines')
                    i = insert_pos - 1
            
            i += 1
        
        # Write back
        new_content = '\n'.join(new_lines)
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Fixed: {file_path}")
            return True
        else:
            print(f"⏭️  No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def main():
    """Fix all lesson files."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    lessons_dir = os.path.join(base_dir, "lessons", "en")
    
    fixed_count = 0
    total_count = 0
    
    # Walk through all lesson directories
    for root, dirs, files in os.walk(lessons_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                total_count += 1
                if fix_lesson_file(file_path):
                    fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count}/{total_count} files")


if __name__ == "__main__":
    main()
