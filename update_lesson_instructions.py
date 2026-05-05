"""
Script to automatically add instructions to lesson files.
Reads instructions from tutorial markdown files and injects them as comments above __BLANK__ lines.
"""

import os
import re

def extract_instructions_from_tutorial(tutorial_path):
    """Extract numbered instructions from tutorial markdown file."""
    if not os.path.exists(tutorial_path):
        return []
    
    try:
        with open(tutorial_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract Instructions section
        instructions_match = re.search(r'## Instructions\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if not instructions_match:
            return []
        
        instructions_text = instructions_match.group(1).strip()
        
        # Parse numbered list items (1. 2. 3. etc.)
        instructions = []
        for line in instructions_text.split('\n'):
            # Match lines starting with number followed by dot
            match = re.match(r'^\d+\.\s+(.+)$', line.strip())
            if match:
                # Convert to uppercase
                instruction = match.group(1).upper()
                instructions.append(instruction)
        
        return instructions
    except Exception as e:
        print(f"Error reading {tutorial_path}: {e}")
        return []


def update_lesson_file(lesson_path, tutorial_path):
    """Update a lesson file by adding instructions above __BLANK__ lines."""
    if not os.path.exists(lesson_path):
        print(f"Lesson file not found: {lesson_path}")
        return False
    
    # Extract instructions from tutorial
    instructions = extract_instructions_from_tutorial(tutorial_path)
    if not instructions:
        print(f"No instructions found in {tutorial_path}")
        return False
    
    # Read lesson file
    try:
        with open(lesson_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {lesson_path}: {e}")
        return False
    
    # Process lines and inject instructions
    new_lines = []
    instruction_idx = 0
    
    for i, line in enumerate(lines):
        # Check if this line contains __BLANK__
        if '# __BLANK__' in line:
            # Check if previous line is already an instruction (starts with # ✏️)
            if new_lines and '# ✏️' in new_lines[-1]:
                # Already has instruction, skip
                new_lines.append(line)
            elif instruction_idx < len(instructions):
                # Get indentation from the blank line
                indentation = line[:len(line) - len(line.lstrip())]
                
                # Add instruction comment above the blank
                instruction_line = f"{indentation}# ✏️ {instructions[instruction_idx]}\n"
                new_lines.append(instruction_line)
                new_lines.append(line)
                instruction_idx += 1
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Write updated content
    try:
        with open(lesson_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"✅ Updated: {lesson_path}")
        return True
    except Exception as e:
        print(f"Error writing {lesson_path}: {e}")
        return False


def main():
    """Main function to update all lesson files."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define lesson mappings: (lesson_file, tutorial_file)
    lessons_to_update = [
        # Lesson 2
        ("lessons/en/lesson2_image_processing/step1_image_filters_lab.py", "tutorials/en/lesson2_step1.md"),
        ("lessons/en/lesson2_image_processing/step2_blur_effect.py", "tutorials/en/lesson2_step2.md"),
        ("lessons/en/lesson2_image_processing/step3_edge_detection.py", "tutorials/en/lesson2_step3.md"),
        ("lessons/en/lesson2_image_processing/step4_resize_image.py", "tutorials/en/lesson2_step4.md"),
        ("lessons/en/lesson2_image_processing/step5_filter_chain.py", "tutorials/en/lesson2_step5.md"),
        
        # Lesson 3
        ("lessons/en/lesson3_drawing_shapes/step1_draw_rectangle.py", "tutorials/en/lesson3_step1.md"),
        ("lessons/en/lesson3_drawing_shapes/step2_draw_circle.py", "tutorials/en/lesson3_step2.md"),
        ("lessons/en/lesson3_drawing_shapes/step3_multiple_shapes.py", "tutorials/en/lesson3_step3.md"),
        ("lessons/en/lesson3_drawing_shapes/step4_color_variations.py", "tutorials/en/lesson3_step4.md"),
    ]
    
    print("Starting lesson file updates...\n")
    
    success_count = 0
    for lesson_file, tutorial_file in lessons_to_update:
        lesson_path = os.path.join(base_dir, lesson_file)
        tutorial_path = os.path.join(base_dir, tutorial_file)
        
        if update_lesson_file(lesson_path, tutorial_path):
            success_count += 1
    
    print(f"\n✅ Successfully updated {success_count}/{len(lessons_to_update)} files")


if __name__ == "__main__":
    main()
