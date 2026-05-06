import re
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QScrollArea, QWidget, QSizePolicy, QSpacerItem, QPushButton
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QDragEnterEvent, QDropEvent

from src.modules.library.definitions import LIBRARY_FUNCTIONS


class BlankTextBox(QLineEdit):
    """Custom QLineEdit with drag-and-drop support for game lessons."""
    text_changed_signal = pyqtSignal()

    def __init__(self, expected_answers, indentation="", is_small=False, parent=None):
        super().__init__(parent)
        self.expected_answers = expected_answers
        self.indentation = indentation
        self._is_small = is_small
        self.setAcceptDrops(True)
        
        self.setPlaceholderText("Drop function here..." if is_small else "Drop function here or type...")
        
        _fs = 7 if is_small else 10
        self.setFont(QFont("Consolas", _fs))
        
        # Style - Changed to gray with gradient
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 2px dashed #94a3b8;
                border-radius: 8px;
                padding: {4 if is_small else 8}px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(248, 250, 252, 1),
                    stop:1 rgba(241, 245, 249, 1));
                color: #1e293b;
            }}
            QLineEdit:focus {{
                border: 2px solid #64748b;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff,
                    stop:1 #f8fafc);
            }}
        """)
        
        self.textChanged.connect(lambda: self.text_changed_signal.emit())

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        func_id = event.mimeData().text().strip()
        usage_snippet = self._find_usage_snippet(func_id)
        
        if usage_snippet:
            snippet_cleaned = usage_snippet.strip()
            self.setText(snippet_cleaned)
            event.acceptProposedAction()
        else:
            self.setText(func_id)
            event.acceptProposedAction()

    def _find_usage_snippet(self, func_id):
        for category, data in LIBRARY_FUNCTIONS.items():
            if func_id in data["functions"]:
                return data["functions"][func_id]["usage"]
            for f_name, f_info in data["functions"].items():
                if f_name.lower() == func_id.lower():
                    return f_info["usage"]
        return None

    def set_feedback(self, is_correct):
        _pad = 6 if self._is_small else 10
        if is_correct:
            self.setStyleSheet(f"""
                QLineEdit {{
                    border: 3px solid #22c55e;
                    border-radius: 8px;
                    padding: {_pad}px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(220, 252, 231, 1),
                        stop:1 rgba(187, 247, 208, 1));
                    color: #166534;
                    font-weight: bold;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QLineEdit {{
                    border: 3px solid #ef4444;
                    border-radius: 8px;
                    padding: {_pad}px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(254, 226, 226, 1),
                        stop:1 rgba(254, 202, 202, 1));
                    color: #991b1b;
                }}
            """)

    def clear_feedback(self):
        _pad = 5 if self._is_small else 8
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 2px dashed #94a3b8;
                border-radius: 8px;
                padding: {_pad}px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(248, 250, 252, 1),
                    stop:1 rgba(241, 245, 249, 1));
                color: #1e293b;
            }}
            QLineEdit:focus {{
                border: 2px solid #64748b;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff,
                    stop:1 #f8fafc);
            }}
        """)


class GameLessonWidget(QFrame):
    """Visual drag-and-drop game round layout for fill-in-the-blank lessons."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._blank_boxes = {}  # line_num -> BlankTextBox
        self._parsed_step = None
        self._is_small = False
        self._instruction_labels = {}  # Store instruction labels for toggle
        
        self.setObjectName("gameLessonWidget")
        self.setStyleSheet("""
            QFrame#gameLessonWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border-radius: 16px;
                border: 2px solid #e2e8f0;
            }
        """)
        
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.NoFrame)
        self._scroll_area.setStyleSheet("QScrollArea { background: transparent; }")
        
        self._content_widget = QWidget()
        self._content_widget.setStyleSheet("background: transparent;")
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(8, 8, 8, 8)
        self._content_layout.setSpacing(8)
        
        self._scroll_area.setWidget(self._content_widget)
        self._main_layout.addWidget(self._scroll_area)

    def set_small_mode(self, is_small):
        """Update sizing for screen resolutions and redraw content."""
        self._is_small = is_small
        if self._is_small:
            self._content_layout.setContentsMargins(8, 8, 8, 8)
            self._content_layout.setSpacing(8)
        else:
            self._content_layout.setContentsMargins(20, 20, 20, 20)
            self._content_layout.setSpacing(15)
            
        if self._parsed_step:
            self.set_blank_mode(self._parsed_step)

    def set_blank_mode(self, parsed_step):
        self._parsed_step = parsed_step
        self._blank_boxes.clear()
        self._instruction_labels.clear()
        
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        lines = parsed_step.display_lines
        blank_map = parsed_step.blank_map
        
        current_code_block = []
        pending_instruction = None  # Store instruction to add with next blank
        
        skip_patterns = [
            r"^#\s*={3,}",
            r"^#\s*LESSON",
            r"^#\s*TITLE",
            r"^#\s*NHIỆM VỤ",
            r"^#\s*TASK",
            r"^#\s*HƯỚNG DẪN",
            r"^#\s*INSTRUCTIONS"
        ]
        
        def should_skip(l):
            return any(re.search(pat, l, re.I) for pat in skip_patterns)
        
        def is_instruction_line(l):
            """Check if line is an instruction (starts with # ✏️)"""
            return l.strip().startswith("# ✏️")

        for line_num, line in enumerate(lines):
            if line_num in blank_map:
                if current_code_block:
                    self._add_code_block(current_code_block)
                    current_code_block = []
                    
                blank_info = blank_map[line_num]
                self._add_blank_block(line_num, blank_info, pending_instruction)
                pending_instruction = None  # Reset after adding
            else:
                stripped = line.strip()
                if should_skip(line):
                    continue
                
                # Check if this is an instruction line
                if is_instruction_line(line):
                    # Extract instruction text (remove # ✏️ prefix)
                    instruction_text = stripped.replace("# ✏️", "").strip()
                    pending_instruction = instruction_text
                    continue  # Don't add to code block
                
                if stripped.startswith("#"):
                    if current_code_block:
                        self._add_code_block(current_code_block)
                        current_code_block = []
                        
                    title_text = stripped.lstrip("#").strip()
                    if title_text:
                        self._add_title_block(title_text)
                elif stripped:
                    current_code_block.append(line)
                else:
                    if current_code_block:
                        self._add_code_block(current_code_block)
                        current_code_block = []

        if current_code_block:
            self._add_code_block(current_code_block)

        self._content_layout.addStretch()

    def _add_title_block(self, text):
        label = QLabel(text)
        label.setWordWrap(True)
        _fs = 8 if self._is_small else 10
        label.setFont(QFont("Inter", _fs, QFont.Bold))
        label.setStyleSheet(f"""
            QLabel {{
                color: #1e3a8a;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #dbeafe, stop:1 #bfdbfe);
                border-left: 5px solid #3b82f6;
                padding: {5 if self._is_small else 10}px {8 if self._is_small else 15}px;
                border-radius: 8px;
                border: 2px solid #93c5fd;
            }}
        """)
        self._content_layout.addWidget(label)

    def _add_code_block(self, code_lines):
        label = QLabel("\n".join(code_lines))
        _fs = 6 if self._is_small else 9
        label.setFont(QFont("Consolas", _fs))
        label.setStyleSheet(f"""
            QLabel {{
                color: #1e293b;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fafc, stop:1 #f1f5f9);
                border: 2px solid #cbd5e1;
                padding: {4 if self._is_small else 10}px;
                border-radius: 8px;
            }}
        """)
        self._content_layout.addWidget(label)

    def _add_blank_block(self, line_num, blank_info, instruction_text=None):
        # Container for blank + instruction
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(4)
        
        # Blank input row
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        indent_spaces = len(blank_info.indentation)
        if indent_spaces > 0:
            pixel_indent = (indent_spaces // 4) * (15 if self._is_small else 30)
            h_layout.addSpacing(pixel_indent)
            
        textbox = BlankTextBox(blank_info.expected_answers, blank_info.indentation, is_small=self._is_small)
        self._blank_boxes[line_num] = textbox
        
        h_layout.addWidget(textbox)
        
        # Add toggle button if there's an instruction
        if instruction_text:
            # Get color for this instruction based on function name
            bg_color, text_color = self._get_instruction_colors(instruction_text)
            
            # Toggle button - gradient gray/purple
            toggle_btn = QPushButton("▼")
            toggle_btn.setFixedSize(24 if self._is_small else 32, 24 if self._is_small else 32)
            toggle_btn.setCursor(Qt.PointingHandCursor)
            toggle_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #94a3b8, stop:1 #64748b);
                    color: white;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #64748b, stop:1 #475569);
                    border: 2px solid rgba(255, 255, 255, 0.5);
                }
            """)
            h_layout.addWidget(toggle_btn)
            
            # Create instruction label (hidden by default) with category colors
            instruction_label = QLabel(f"✏️ {instruction_text}")
            instruction_label.setWordWrap(True)
            _fs = 7 if self._is_small else 9
            instruction_label.setFont(QFont("Inter", _fs))
            instruction_label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color};
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {bg_color},
                        stop:1 rgba(255, 255, 255, 0.8));
                    border-left: 4px solid {text_color};
                    border: 2px solid {text_color};
                    padding: {4 if self._is_small else 8}px;
                    border-radius: 8px;
                    margin-left: {pixel_indent if indent_spaces > 0 else 0}px;
                }}
            """)
            instruction_label.setVisible(False)  # Hidden by default
            
            # Store reference
            self._instruction_labels[line_num] = {
                'label': instruction_label,
                'button': toggle_btn,
                'visible': False
            }
            
            # Connect toggle
            toggle_btn.clicked.connect(lambda checked, ln=line_num: self._toggle_instruction(ln))
            
            # Add to container
            blank_widget = QWidget()
            blank_widget.setLayout(h_layout)
            container_layout.addWidget(blank_widget)
            container_layout.addWidget(instruction_label)
        else:
            blank_widget = QWidget()
            blank_widget.setLayout(h_layout)
            container_layout.addWidget(blank_widget)
        
        self._content_layout.addWidget(container)
    
    def _get_instruction_colors(self, instruction_text):
        """Extract function name from instruction and return matching category colors.
        Returns (background_color, text_color) tuple."""
        
        # Default colors (orange - for unknown functions)
        default_bg = "rgba(254, 243, 199, 1)"  # Light yellow/orange
        default_text = "#f97316"  # Orange
        
        # Extract function name from instruction text
        # Pattern: USE 'FUNCTION_NAME()' or USE `FUNCTION_NAME()` or USE "FUNCTION_NAME()"
        import re
        match = re.search(r"['\"`]([A-Za-z_]+)\(", instruction_text, re.IGNORECASE)
        if not match:
            return (default_bg, default_text)
        
        func_name = match.group(1)
        
        # Map function names to categories and their colors
        # Camera functions - Orange #f97316
        camera_funcs = ["Init_Camera", "Get_Camera_Frame", "Close_Camera", "Save_Frame", 
                       "Load_Image", "Set_Camera_Resolution", "Capture_Snapshot"]
        
        # Image Processing functions - Green #10b981
        image_funcs = ["convert_to_gray", "resize_image", "apply_blur", "detect_edges",
                      "flip_image", "adjust_brightness", "rotate_image", "crop_image",
                      "draw_text", "convert_to_hsv", "threshold_image", "blend_images",
                      "split_channels", "equalize_histogram", "detect_contours"]
        
        # AI Vision functions - Purple #8b5cf6
        ai_funcs = ["Load_YuNet_Model", "Run_YuNet_Model", "Load_ONNX_Model", "Run_ONNX_Model",
                   "Detect_Faces", "Draw_Detections", "Draw_Detections_MultiClass",
                   "Draw_Engine_Detections"]
        
        # Display & Dashboard functions - Indigo #6366f1
        display_funcs = ["Show_Image", "Show_Multiple_Images", "Close_All_Windows",
                        "Update_Dashboard", "Show_FPS", "Observe_Variable"]
        
        # Drawing functions - Pink #ec4899
        drawing_funcs = ["Draw_Rectangle", "Draw_Circle", "Draw_Line", "Draw_Polygon",
                        "Draw_Text_On_Image"]
        
        # Determine category and return colors (case-insensitive comparison)
        func_name_lower = func_name.lower()
        
        if any(f.lower() == func_name_lower for f in camera_funcs):
            # Camera - Orange
            return ("rgba(254, 243, 199, 1)", "#f97316")
        elif any(f.lower() == func_name_lower for f in image_funcs):
            # Image Processing - Green/Mint
            return ("rgba(209, 250, 229, 1)", "#10b981")
        elif any(f.lower() == func_name_lower for f in ai_funcs):
            # AI Vision - Purple/Violet
            return ("rgba(237, 233, 254, 1)", "#8b5cf6")
        elif any(f.lower() == func_name_lower for f in display_funcs):
            # Display & Dashboard - Indigo
            return ("rgba(224, 231, 255, 1)", "#6366f1")
        elif any(f.lower() == func_name_lower for f in drawing_funcs):
            # Drawing - Pink
            return ("rgba(252, 231, 243, 1)", "#ec4899")
        else:
            return (default_bg, default_text)
    
    def _toggle_instruction(self, line_num):
        """Toggle visibility of instruction for a specific blank."""
        if line_num in self._instruction_labels:
            info = self._instruction_labels[line_num]
            info['visible'] = not info['visible']
            info['label'].setVisible(info['visible'])
            # Update button icon
            info['button'].setText("▲" if info['visible'] else "▼")

    def get_blank_contents(self):
        contents = {}
        for line_num, textbox in self._blank_boxes.items():
            contents[line_num] = textbox.text().strip()
        return contents

    def set_blank_feedback(self, results):
        for result in results:
            line_num = result.line_number
            if line_num in self._blank_boxes:
                self._blank_boxes[line_num].set_feedback(result.is_correct)

    def clear_blank_feedback(self, line_num):
        if line_num in self._blank_boxes:
            self._blank_boxes[line_num].clear_feedback()

    def fill_blanks_with_answers(self, blank_map):
        for line_num, blank_info in blank_map.items():
            if line_num in self._blank_boxes and blank_info.expected_answers:
                self._blank_boxes[line_num].setText(blank_info.expected_answers[0])

    def toPlainText(self):
        if not self._parsed_step:
            return ""
            
        full_lines = []
        for line_num, line in enumerate(self._parsed_step.display_lines):
            if line_num in self._blank_boxes:
                text_input = self._blank_boxes[line_num].text().strip()
                full_lines.append(self._parsed_step.blank_map[line_num].indentation + text_input)
            else:
                full_lines.append(line)
                
        return "\n".join(full_lines)
