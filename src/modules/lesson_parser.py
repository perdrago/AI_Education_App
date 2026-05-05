"""
Lesson Parser Module

Parses lesson step files containing # __BLANK__ markers and produces
display-ready content with blank slot metadata for the fill-in-the-blank
lesson system.
"""

from dataclasses import dataclass, field
from pathlib import Path


BLANK_MARKER = "# __BLANK__"


@dataclass
class BlankInfo:
    """Metadata for a single blank slot."""
    line_number: int            # 0-based line index in display code
    indentation: str            # Leading whitespace preserved from marker line
    expected_answers: list[str] = field(default_factory=list)  # One or more valid answers


@dataclass
class ParsedStep:
    """Result of parsing a step file."""
    display_lines: list[str] = field(default_factory=list)    # Lines shown in editor
    blank_map: dict[int, BlankInfo] = field(default_factory=dict)  # line_number → BlankInfo
    is_challenge: bool = False   # True if no blanks found (free-form mode)
    raw_content: str = ""        # Original file content for challenge fallback


def _parse_blank_line(line: str, line_number: int) -> "BlankInfo | None":
    """Extract BlankInfo from a single line if it contains BLANK_MARKER.

    Args:
        line: A single line from the step file (without trailing newline).
        line_number: The 0-based line index.

    Returns:
        BlankInfo if the line contains a blank marker, None otherwise.
    """
    stripped = line.lstrip()
    if not stripped.startswith(BLANK_MARKER):
        return None

    # Preserve original indentation (leading whitespace before the marker)
    indentation = line[: len(line) - len(stripped)]

    # Extract the answer portion after "# __BLANK__"
    marker_end = stripped[len(BLANK_MARKER):]

    # Remove the leading space after the marker if present
    if marker_end.startswith(" "):
        answer_text = marker_end[1:]
    else:
        answer_text = marker_end

    # Parse pipe-separated alternatives
    if answer_text:
        expected_answers = [ans.strip() for ans in answer_text.split("|")]
    else:
        expected_answers = [""]

    return BlankInfo(
        line_number=line_number,
        indentation=indentation,
        expected_answers=expected_answers,
    )


def parse_step_file(file_path: str) -> ParsedStep:
    """Parse a step file, extract blank markers, return display-ready content.

    Reads the file, scans each line for the # __BLANK__ prefix, and builds
    a ParsedStep with display lines (blanks replaced with indentation-only
    empty lines), a blank_map of line metadata, and challenge detection.

    Args:
        file_path: Path to the step file to parse.

    Returns:
        ParsedStep with display_lines, blank_map, is_challenge, and raw_content.
    """
    path = Path(file_path)
    raw_content = path.read_text(encoding="utf-8", errors="replace")

    lines = raw_content.splitlines()
    display_lines: list[str] = []
    blank_map: dict[int, BlankInfo] = {}

    for line_number, line in enumerate(lines):
        blank_info = _parse_blank_line(line, line_number)
        if blank_info is not None:
            # Replace blank marker line with indentation-only empty line
            display_lines.append(blank_info.indentation)
            blank_map[line_number] = blank_info
        else:
            display_lines.append(line)

    is_challenge = len(blank_map) == 0

    return ParsedStep(
        display_lines=display_lines,
        blank_map=blank_map,
        is_challenge=is_challenge,
        raw_content=raw_content,
    )


def inject_instructions_into_code(display_lines: list[str], instructions: list[str]) -> list[str]:
    """Inject instruction comments into code at appropriate positions.
    
    Args:
        display_lines: The parsed code lines from ParsedStep
        instructions: List of instruction strings to inject
        
    Returns:
        Modified display_lines with instructions injected as bold comments
    """
    if not instructions:
        return display_lines
    
    result_lines = []
    instruction_idx = 0
    
    for i, line in enumerate(display_lines):
        # Check if this is a blank line (empty or only whitespace after indentation)
        stripped = line.strip()
        
        # If we find a blank marker position and have instructions left
        if not stripped and instruction_idx < len(instructions):
            # Get the indentation from the line
            indentation = line[:len(line) - len(line.lstrip())]
            
            # Add the instruction as a bold comment above the blank
            instruction_text = instructions[instruction_idx]
            comment_line = f"{indentation}# ✏️ {instruction_text}"
            result_lines.append(comment_line)
            instruction_idx += 1
        
        result_lines.append(line)
    
    return result_lines


def extract_instructions_from_tutorial(tutorial_file_path: str) -> list[str]:
    """Extract numbered instructions from tutorial markdown file.
    
    Args:
        tutorial_file_path: Path to the tutorial markdown file
        
    Returns:
        List of instruction strings (without numbers)
    """
    import re
    import os
    
    if not os.path.exists(tutorial_file_path):
        return []
    
    try:
        with open(tutorial_file_path, 'r', encoding='utf-8') as f:
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
                instructions.append(match.group(1))
        
        return instructions
    except Exception:
        return []
