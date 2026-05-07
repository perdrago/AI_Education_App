"""
Tutorials View - Displays Lessons and Examples in a unified interface
Replaces the Code Editor when user clicks "Tutorials" button in header
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class TutorialsView(QWidget):
    """
    Tutorials View widget that shows Lessons or Examples based on toggle.
    Emits signals when user clicks Start (lesson) or Load (example).
    """
    
    lesson_started = pyqtSignal(str, int)  # lesson_id, step_number
    example_loaded = pyqtSignal(str)  # example_file_path
    
    def __init__(self, parent=None, lang="en"):
        super().__init__(parent)
        self.lang = lang
        self.current_view = "lessons"  # "lessons" or "examples"
        self._is_small = False
        
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fafc, stop:1 #e0e7ff);
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Combined container for both toggle buttons and level badges
        combined_outer_container = QFrame()
        combined_outer_container.setObjectName("combinedOuterContainer")
        combined_outer_container.setStyleSheet("""
            QFrame#combinedOuterContainer {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e0e7ff, stop:0.5 #f3e8ff, stop:1 #fce7f3);
                border-radius: 20px;
                padding: 15px;
            }
        """)
        
        combined_layout = QVBoxLayout(combined_outer_container)
        combined_layout.setContentsMargins(0, 0, 0, 0)
        combined_layout.setSpacing(15)
        
        # Toggle buttons (Lessons | Examples)
        toggle_container = QWidget()
        toggle_container.setStyleSheet("QWidget { background: transparent; }")  # Make transparent
        toggle_layout = QHBoxLayout(toggle_container)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setSpacing(0)
        toggle_layout.setAlignment(Qt.AlignCenter)
        
        # Lessons button
        lessons_text = "📚 Lessons" if lang == "en" else "📚 Bài học"
        self.btn_lessons = QPushButton(lessons_text)
        self.btn_lessons.setFixedSize(200, 60)
        self.btn_lessons.setCursor(Qt.PointingHandCursor)
        self.btn_lessons.setCheckable(True)
        self.btn_lessons.setChecked(True)
        self.btn_lessons.clicked.connect(lambda: self.switch_view("lessons"))
        
        # Examples button
        examples_text = "🎯 Examples" if lang == "en" else "🎯 Ví dụ"
        self.btn_examples = QPushButton(examples_text)
        self.btn_examples.setFixedSize(200, 60)
        self.btn_examples.setCursor(Qt.PointingHandCursor)
        self.btn_examples.setCheckable(True)
        self.btn_examples.clicked.connect(lambda: self.switch_view("examples"))
        
        # Apply toggle styles
        self._apply_toggle_styles()
        
        toggle_layout.addWidget(self.btn_lessons)
        toggle_layout.addWidget(self.btn_examples)
        
        combined_layout.addWidget(toggle_container)
        
        # Level filter badges container with different gradient (more vibrant)
        level_outer_container = QFrame()
        level_outer_container.setObjectName("levelOuterContainer")
        level_outer_container.setStyleSheet("""
            QFrame#levelOuterContainer {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #c7d2fe, stop:0.5 #ddd6fe, stop:1 #f5d0fe);
                border-radius: 16px;
                padding: 10px 15px;
            }
        """)
        level_outer_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Fixed size to fit content
        
        level_outer_layout = QVBoxLayout(level_outer_container)
        level_outer_layout.setContentsMargins(0, 0, 0, 0)
        level_outer_layout.setSpacing(0)
        level_outer_layout.setSizeConstraint(QVBoxLayout.SetFixedSize)  # Shrink to content
        
        self.level_filter_container = QWidget()
        self.level_filter_container.setStyleSheet("QWidget { background: transparent; }")  # Make transparent
        level_filter_layout = QHBoxLayout(self.level_filter_container)
        level_filter_layout.setContentsMargins(0, 0, 0, 0)
        level_filter_layout.setSpacing(20)
        level_filter_layout.setAlignment(Qt.AlignCenter)
        
        self.current_level_filter = "Beginner"  # Default filter
        self.level_badges = {}
        
        # Create level badges with smaller size (60x60)
        levels = [
            ("Beginner", "⭐", "#22c55e"),
            ("Intermediate", "🚀", "#f59e0b"),
            ("Advanced", "🏆", "#ef4444")
        ]
        
        for level, icon, color in levels:
            badge = QPushButton(f"{icon}")
            badge.setFixedSize(60, 60)  # Smaller size
            badge.setCursor(Qt.PointingHandCursor)
            badge.setCheckable(True)
            badge.setChecked(level == "Beginner")  # Beginner active by default
            badge.clicked.connect(lambda checked, l=level: self.filter_by_level(l))
            
            # Store badge reference
            self.level_badges[level] = badge
            level_filter_layout.addWidget(badge)
        
        # Apply initial badge styles
        self._apply_level_badge_styles()
        
        level_outer_layout.addWidget(self.level_filter_container)
        
        # Wrapper to center the level container
        level_wrapper = QWidget()
        level_wrapper.setStyleSheet("QWidget { background: transparent; }")
        level_wrapper_layout = QHBoxLayout(level_wrapper)
        level_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        level_wrapper_layout.setAlignment(Qt.AlignCenter)
        level_wrapper_layout.addWidget(level_outer_container)
        
        combined_layout.addWidget(level_wrapper)
        
        main_layout.addWidget(combined_outer_container)
        
        # Content area (scrollable)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("QScrollArea { background: transparent; }")
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(15)
        self.content_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)
        
    def _apply_toggle_styles(self):
        """Apply gradient styles to toggle buttons."""
        active_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8b5cf6, stop:1 #6d28d9);
                color: white;
                border: 3px solid rgba(255, 255, 255, 0.6);
                border-radius: 16px;
                font-weight: bold;
                font-size: 18px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
        """
        
        inactive_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e0e7ff, stop:1 #c7d2fe);
                color: #4c1d95;
                border: 2px solid #a5b4fc;
                border-radius: 16px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c7d2fe, stop:1 #a5b4fc);
                border: 2px solid #8b5cf6;
            }
        """
        
        if self.btn_lessons.isChecked():
            self.btn_lessons.setStyleSheet(active_style)
            self.btn_examples.setStyleSheet(inactive_style)
        else:
            self.btn_lessons.setStyleSheet(inactive_style)
            self.btn_examples.setStyleSheet(active_style)
    
    def _apply_level_badge_styles(self):
        """Apply styles to level filter badges."""
        for level, badge in self.level_badges.items():
            if badge.isChecked():
                # Active badge style with rounded corners
                badge.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #8b5cf6, stop:1 #6d28d9);
                        color: white;
                        border: 3px solid rgba(255, 255, 255, 0.9);
                        border-radius: 16px;
                        font-size: 28px;
                    }
                    QPushButton:hover {
                        border: 3px solid white;
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #7c3aed, stop:1 #5b21b6);
                    }
                """)
            else:
                # Inactive badge style with rounded corners
                badge.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #f8fafc, stop:1 #e2e8f0);
                        color: #64748b;
                        border: 2px solid #cbd5e1;
                        border-radius: 16px;
                        font-size: 28px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #e2e8f0, stop:1 #cbd5e1);
                        border: 2px solid #8b5cf6;
                    }
                """)
    
    def filter_by_level(self, level):
        """Filter content by difficulty level."""
        # Prevent redundant filters
        if self.current_level_filter == level:
            return
        
        self.current_level_filter = level
        
        # Update badge states
        for lvl, badge in self.level_badges.items():
            badge.setChecked(lvl == level)
        
        self._apply_level_badge_styles()
        
        # Re-populate content with filter
        parent = self.parent()
        while parent and not hasattr(parent, '_populate_tutorials_view'):
            parent = parent.parent()
        
        if parent and hasattr(parent, '_populate_tutorials_view'):
            parent._populate_tutorials_view()
    
    def switch_view(self, view_type):
        """Switch between lessons and examples view."""
        # Prevent redundant switches
        if self.current_view == view_type:
            return
        
        self.current_view = view_type
        
        # Update toggle button states
        self.btn_lessons.setChecked(view_type == "lessons")
        self.btn_examples.setChecked(view_type == "examples")
        self._apply_toggle_styles()
        
        # Clear current content
        self.clear_content()
        
        # Trigger parent to reload content
        parent = self.parent()
        while parent and not hasattr(parent, '_populate_tutorials_view'):
            parent = parent.parent()
        
        if parent and hasattr(parent, '_populate_tutorials_view'):
            parent._populate_tutorials_view()
    
    def clear_content(self):
        """Clear all content from the content area."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def show_empty_state(self, message=None):
        """Show empty state message when no content matches filter."""
        if message is None:
            if self.current_view == "lessons":
                message = "No lessons available for this level" if self.lang == "en" else "Chưa có bài học cho cấp độ này"
            else:
                message = "No examples available for this level" if self.lang == "en" else "Chưa có ví dụ cho cấp độ này"
        
        empty_label = QLabel(message)
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet("""
            QLabel {
                color: #94a3b8;
                font-size: 16px;
                font-style: italic;
                padding: 60px 20px;
                background: transparent;
            }
        """)
        self.content_layout.addWidget(empty_label)
    
    def load_lessons(self):
        """Load and display lessons."""
        # This will be populated by MainWindow
        pass
    
    def load_examples(self):
        """Load and display examples."""
        # This will be populated by MainWindow
        pass
    
    def add_lesson_card(self, lesson_data):
        """Add a lesson card to the content area (respects level filter)."""
        # Check if lesson matches current level filter
        lesson_level = lesson_data.get("level", "Beginner")
        if lesson_level != self.current_level_filter:
            return  # Skip this lesson
        
        card = LessonCard(lesson_data, self.lang, self._is_small)
        
        # Connect signal - emit lesson_started when Start is clicked
        def on_start():
            lesson_id = str(lesson_data.get('id', ''))
            step_num = int(1)
            self.lesson_started.emit(lesson_id, step_num)
        
        card.start_clicked.connect(on_start)
        self.content_layout.addWidget(card)
    
    def add_example_card(self, example_data):
        """Add an example card to the content area (respects level filter)."""
        # Check if example matches current level filter
        example_level = example_data.get("level", "Beginner")
        if example_level != self.current_level_filter:
            return  # Skip this example
        
        card = ExampleCard(example_data, self.lang, self._is_small)
        card.load_clicked.connect(lambda: self.example_loaded.emit(
            example_data.get("file_path", "")
        ))
        self.content_layout.addWidget(card)
    
    def set_small_mode(self, is_small):
        """Update sizing for small screen mode."""
        self._is_small = is_small
        
        # Update toggle buttons
        btn_size = (160, 50) if is_small else (200, 60)
        self.btn_lessons.setFixedSize(*btn_size)
        self.btn_examples.setFixedSize(*btn_size)
        
        # Update toggle button font sizes
        font_size = 15 if is_small else 18
        for btn in [self.btn_lessons, self.btn_examples]:
            font = btn.font()
            font.setPointSize(font_size)
            btn.setFont(font)
        
        # Update level badges (smaller size)
        badge_size = 50 if is_small else 60
        for badge in self.level_badges.values():
            badge.setFixedSize(badge_size, badge_size)


class LessonCard(QFrame):
    """Individual lesson card widget."""
    
    start_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    
    def __init__(self, lesson_data, lang="en", is_small=False):
        super().__init__()
        self.lesson_data = lesson_data
        self.lang = lang
        self.is_active = lesson_data.get("is_active", False)
        
        self.setObjectName("lessonCard")
        
        # Card styling with gradient border
        border_color = self._get_level_color(lesson_data.get("level", "Beginner"))
        self.setStyleSheet(f"""
            QFrame#lessonCard {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 3px solid {border_color};
                border-radius: 16px;
                padding: 20px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(15)
        
        # Icon
        icon_label = QLabel(lesson_data.get("icon", "📚"))
        icon_label.setStyleSheet("font-size: 48px; background: transparent;")
        icon_label.setFixedSize(70, 70)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Content (title + description)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(5)
        
        title = QLabel(lesson_data.get("title", "Lesson"))
        title.setStyleSheet(f"""
            font-size: {'16px' if is_small else '20px'};
            font-weight: bold;
            color: {border_color};
            background: transparent;
        """)
        content_layout.addWidget(title)
        
        desc = QLabel(lesson_data.get("description", ""))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"""
            font-size: {'11px' if is_small else '14px'};
            color: #64748b;
            background: transparent;
        """)
        content_layout.addWidget(desc)
        
        layout.addLayout(content_layout, 1)
        
        # Buttons (Level badge + Start/Stop)
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.setAlignment(Qt.AlignCenter)
        
        # Level badge
        level_badge = QLabel(lesson_data.get("level", "Beginner"))
        level_badge.setAlignment(Qt.AlignCenter)
        level_badge.setStyleSheet(f"""
            background: {border_color};
            color: white;
            border-radius: 12px;
            padding: 6px 20px;
            font-weight: bold;
            font-size: {'11px' if is_small else '13px'};
        """)
        buttons_layout.addWidget(level_badge)
        
        # Start/Stop button
        if self.is_active:
            self.action_btn = QPushButton("⏹ Stop")
            self.action_btn.clicked.connect(lambda: self._on_stop_clicked())
            btn_gradient = "stop:0 #ef4444, stop:1 #dc2626"
        else:
            self.action_btn = QPushButton("▶ Start")
            self.action_btn.clicked.connect(lambda: self._on_start_clicked())
            btn_gradient = "stop:0 #8b5cf6, stop:1 #6d28d9"
        
        self.action_btn.setFixedSize(140 if is_small else 160, 40 if is_small else 45)
        self.action_btn.setCursor(Qt.PointingHandCursor)
        self.action_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, {btn_gradient});
                color: white;
                border-radius: {'10px' if is_small else '12px'};
                font-weight: bold;
                font-size: {'13px' if is_small else '15px'};
                border: 2px solid rgba(255, 255, 255, 0.3);
            }}
            QPushButton:hover {{
                border: 2px solid rgba(255, 255, 255, 0.6);
            }}
        """)
        buttons_layout.addWidget(self.action_btn)
        
        layout.addLayout(buttons_layout)
    
    def _on_start_clicked(self):
        """Handle start button click."""
        self.start_clicked.emit()
    
    def _on_stop_clicked(self):
        """Handle stop button click."""
        self.stop_clicked.emit()
    
    def _get_level_color(self, level):
        """Get color based on difficulty level."""
        colors = {
            "Beginner": "#22c55e",
            "Intermediate": "#f59e0b",
            "Advanced": "#ef4444"
        }
        return colors.get(level, "#8b5cf6")


class ExampleCard(QFrame):
    """Individual example card widget."""
    
    load_clicked = pyqtSignal()
    
    def __init__(self, example_data, lang="en", is_small=False):
        super().__init__()
        self.example_data = example_data
        self.lang = lang
        
        self.setObjectName("exampleCard")
        
        # Card styling with green gradient border
        self.setStyleSheet("""
            QFrame#exampleCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f0fdf4);
                border: 3px solid #22c55e;
                border-radius: 16px;
                padding: 20px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(15)
        
        # Icon
        icon_label = QLabel(example_data.get("icon", "🎯"))
        icon_label.setStyleSheet("font-size: 48px; background: transparent;")
        icon_label.setFixedSize(70, 70)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(5)
        
        title = QLabel(example_data.get("title", "Example"))
        title.setStyleSheet(f"""
            font-size: {'16px' if is_small else '20px'};
            font-weight: bold;
            color: #16a34a;
            background: transparent;
        """)
        content_layout.addWidget(title)
        
        desc = QLabel(example_data.get("description", ""))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"""
            font-size: {'11px' if is_small else '14px'};
            color: #64748b;
            background: transparent;
        """)
        content_layout.addWidget(desc)
        
        layout.addLayout(content_layout, 1)
        
        # Buttons
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.setAlignment(Qt.AlignCenter)
        
        # Level badge
        level_badge = QLabel(example_data.get("level", "Beginner"))
        level_badge.setAlignment(Qt.AlignCenter)
        level_badge.setStyleSheet(f"""
            background: #22c55e;
            color: white;
            border-radius: 12px;
            padding: 6px 20px;
            font-weight: bold;
            font-size: {'11px' if is_small else '13px'};
        """)
        buttons_layout.addWidget(level_badge)
        
        # Load button
        load_btn = QPushButton("📂 Load")
        load_btn.setFixedSize(140 if is_small else 160, 40 if is_small else 45)
        load_btn.setCursor(Qt.PointingHandCursor)
        load_btn.clicked.connect(self.load_clicked.emit)
        load_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8b5cf6, stop:1 #6d28d9);
                color: white;
                border-radius: {'10px' if is_small else '12px'};
                font-weight: bold;
                font-size: {'13px' if is_small else '15px'};
                border: 2px solid rgba(255, 255, 255, 0.3);
            }}
            QPushButton:hover {{
                border: 2px solid rgba(255, 255, 255, 0.6);
            }}
        """)
        buttons_layout.addWidget(load_btn)
        
        layout.addLayout(buttons_layout)
