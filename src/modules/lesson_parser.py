"""
Lesson Parser - Parse lesson files for fill-in-the-blank mode
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class BlankInfo:
    """Information about a blank (drop zone) in the lesson."""
    line_num: int
    blank_id: str
    expected_answer: str
    instruction: str = ""
    indentation: str = ""  # Indentation spaces for the blank line
    expected_answers: List[str] = field(default_factory=list)  # List of acceptable answers


@dataclass
class ParsedStep:
    """Parsed lesson step with blank information."""
    raw_content: str
    is_challenge: bool
    blank_map: Dict[str, BlankInfo] = field(default_factory=dict)
    display_lines: List[str] = field(default_factory=list)


def parse_step_file(file_path: str) -> ParsedStep:
    """
    Parse a lesson step file to extract blanks and instructions.
    
    Looks for patterns like:
    # __BLANK__ capture_camera = camera.Init_Camera()
    
    Args:
        file_path: Path to the lesson step file
        
    Returns:
        ParsedStep object with blank information
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        # Return empty parsed step if file not found
        return ParsedStep(raw_content="", is_challenge=True)
    
    lines = content.split('\n')
    blank_map = {}
    display_lines = []
    blank_counter = 0
    is_challenge = True  # Assume challenge unless we find blanks
    
    for line_num, line in enumerate(lines, start=1):
        # Check if this line has a __BLANK__ marker
        if '__BLANK__' in line:
            is_challenge = False  # Found a blank, so not a challenge
            blank_counter += 1
            blank_id = f"blank_{blank_counter}"
            
            # Extract indentation (leading spaces)
            indentation = line[:len(line) - len(line.lstrip())]
            
            # Extract the expected answer (the code after __BLANK__)
            # Pattern: # __BLANK__ <code>
            match = re.search(r'__BLANK__\s+(.+)$', line)
            if match:
                expected_answer = match.group(1).strip()
            else:
                expected_answer = ""
            
            # Extract function name from expected answer
            # Pattern: variable = module.Function_Name(...)
            func_match = re.search(r'\.([A-Za-z_]+)\(', expected_answer)
            if func_match:
                func_name = func_match.group(1)
                expected_answers = [func_name]  # Just the function name
            else:
                expected_answers = [expected_answer]  # Full line as fallback
            
            # Extract instruction from previous line if it starts with # ✏️
            instruction = ""
            if line_num > 1:
                prev_line = lines[line_num - 2]  # -2 because line_num is 1-indexed
                if '✏️' in prev_line:
                    # Extract text after ✏️
                    inst_match = re.search(r'✏️\s*(.+)$', prev_line)
                    if inst_match:
                        instruction = inst_match.group(1).strip()
            
            # Calculate the index where this blank will appear in display_lines
            # This is the current length of display_lines (0-indexed)
            display_line_index = len(display_lines)
            
            # Store blank info using display_line_index as key
            # GameLessonWidget uses enumerate(display_lines) which starts at 0
            blank_map[display_line_index] = BlankInfo(
                line_num=line_num,
                blank_id=blank_id,
                expected_answer=expected_answer,
                instruction=instruction,
                indentation=indentation,
                expected_answers=expected_answers
            )
            
            print(f"📝 Blank {blank_counter}: display_index={display_line_index}, expected={expected_answer}, func={expected_answers}")
            
            # Add display line with blank marker
            display_lines.append(f"# __BLANK_{blank_counter}__")
        else:
            display_lines.append(line)
    
    print(f"✅ Parsed step: {len(blank_map)} blanks found, is_challenge={is_challenge}")
    print(f"   Blank map keys: {list(blank_map.keys())}")
    
    return ParsedStep(
        raw_content=content,
        is_challenge=is_challenge,
        blank_map=blank_map,
        display_lines=display_lines
    )
