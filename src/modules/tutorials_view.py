"""
Tutorials View - Clean Modern UI matching design specifications
Displays Lessons and Examples with precise styling
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QPointF
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QPolygonF


class TutorialsView(QWidget):
    """
    Tutorials View widget - Clean modern design
    """
    
    lesson_started = pyqtSignal(str, int)  # lesson_id, step_number
    example_loaded = pyqtSignal(str)  # example_file_path
    
    def __init__(self, parent=None, lang="en", view_type="examples"):
        super().__init__(parent)
        self.lang = lang
        self.view_type = view_type  # "lessons" or "examples"
        self.current_level_filter = "Beginner"
        self._is_small = False
        
        # Main background color
        self.setStyleSheet("""
            QWidget {
                background: #1E1E2E;
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            }
        """)
        
        # Main layout with generous margins
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Top container for title and timeline
        top_container = QFrame()
        top_container.setStyleSheet("QFrame { background: transparent; }")
        top_container_layout = QVBoxLayout(top_container)
        top_container_layout.setContentsMargins(0, 0, 0, 0)
        top_container_layout.setSpacing(20)
        
        # Single title button (centered) - no toggle needed
        title_container = QWidget()
        title_container.setStyleSheet("QWidget { background: transparent; }")
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setAlignment(Qt.AlignCenter)
        
        # Add stretch to push title to center and coins to right
        title_layout.addStretch()
        
        # Create single button based on view_type
        if view_type == "lessons":
            button_text = "Lessons" if lang == "en" else "Bài học"
        else:
            button_text = "Examples" if lang == "en" else "Ví dụ"
        
        self.title_button = QPushButton(button_text)
        self.title_button.setFixedHeight(40)
        self.title_button.setMinimumWidth(200)
        self.title_button.setEnabled(False)  # Not clickable, just a label
        self.title_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8B5CF6, stop:1 #6366F1);
                color: #FFFFFF;
                border: none;
                border-radius: 20px;
                font-size: 15px;
                font-weight: bold;
                padding: 8px 30px;
            }
        """)
        
        title_layout.addWidget(self.title_button)
        
        # Add stretch to center the title
        title_layout.addStretch()
        
        # Add Coins Display (only for examples view)
        if view_type == "examples":
            from src.modules.stars_coins_widget import CoinsDisplayWidget
            self.coins_widget = CoinsDisplayWidget(lang=lang)
            title_layout.addWidget(self.coins_widget)
            
            # Load initial coins from progress manager
            try:
                from src.modules.progress_manager import get_progress_manager
                pm = get_progress_manager()
                self.coins_widget.set_coins(pm.get_total_coins())
                print(f"💰 Coins display initialized: {pm.get_total_coins()} coins")
            except Exception as e:
                print(f"⚠️ Could not load coins: {e}")
                self.coins_widget.set_coins(0)
        else:
            self.coins_widget = None
        
        top_container_layout.addWidget(title_container)
        
        # Progress Timeline
        timeline_container = QWidget()
        timeline_container.setStyleSheet("QWidget { background: transparent; }")
        timeline_layout = QHBoxLayout(timeline_container)
        timeline_layout.setContentsMargins(0, 0, 0, 0)
        timeline_layout.setSpacing(0)
        timeline_layout.setAlignment(Qt.AlignCenter)
        
        self.timeline_nodes = {}
        levels = [
            ("Beginner", 1, "Basic"),
            ("Intermediate", 2, "Intermediate"),
            ("Advanced", 3, "Advanced")
        ]
        
        for idx, (level, level_number, label_text) in enumerate(levels):
            # Create timeline node with hexagon badge
            node = TimelineNode(level_number, label_text, level == "Beginner")
            node.clicked.connect(lambda l=level: self.filter_by_level(l))
            self.timeline_nodes[level] = node
            timeline_layout.addWidget(node)
            
            # Add connecting line
            if idx < len(levels) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setFixedHeight(2)
                line.setFixedWidth(100)
                line.setStyleSheet("""
                    background: #3F3F5A;
                    border: none;
                    margin-top: 30px;
                """)
                timeline_layout.addWidget(line)
        
        top_container_layout.addWidget(timeline_container)
        main_layout.addWidget(top_container)
        
        # Content area (scrollable)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("""
            QScrollArea { 
                background: transparent; 
                border: none;
            }
            QScrollBar:vertical {
                background: #2A2A3C;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #8B5CF6;
                border-radius: 5px;
            }
        """)
        
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("QWidget { background: transparent; }")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 10, 0, 10)
        self.content_layout.setSpacing(10)  # Reduced from 15
        self.content_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)
    
    def filter_by_level(self, level):
        """Filter content by difficulty level."""
        if self.current_level_filter == level:
            return
        
        self.current_level_filter = level
        
        # Update timeline nodes
        for lvl, node in self.timeline_nodes.items():
            node.set_active(lvl == level)
        
        # Re-populate content
        parent = self.parent()
        while parent and not hasattr(parent, '_populate_view_content'):
            parent = parent.parent()
        
        if parent and hasattr(parent, '_populate_view_content'):
            parent._populate_view_content(self)
    
    def clear_content(self):
        """Clear all content from the content area."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def show_empty_state(self, message=None):
        """Show empty state message."""
        if message is None:
            if self.view_type == "lessons":
                message = "No lessons available for this level" if self.lang == "en" else "Chưa có bài học cho cấp độ này"
            else:
                message = "No examples available for this level" if self.lang == "en" else "Chưa có ví dụ cho cấp độ này"
        
        empty_label = QLabel(message)
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet("""
            QLabel {
                color: #6B7280;
                font-size: 16px;
                font-style: italic;
                padding: 60px 20px;
                background: transparent;
            }
        """)
        self.content_layout.addWidget(empty_label)
    
    def add_lesson_card(self, lesson_data):
        """Add a lesson card to the content area."""
        # Check if lesson matches current level filter
        lesson_level = lesson_data.get("level", "Beginner")
        if lesson_level != self.current_level_filter:
            return
        
        card = LessonCard(lesson_data, self.lang, self._is_small)
        
        def on_start():
            lesson_id = str(lesson_data.get('id', ''))
            step_num = int(1)
            self.lesson_started.emit(lesson_id, step_num)
        
        card.start_clicked.connect(on_start)
        self.content_layout.addWidget(card)
    
    def add_example_card(self, example_data):
        """Add an example card to the content area."""
        # Check if example matches current level filter
        example_level = example_data.get("level", "Beginner")
        if example_level != self.current_level_filter:
            return
        
        card = ExampleCard(example_data, self.lang, self._is_small)
        card.load_clicked.connect(lambda: self.example_loaded.emit(
            example_data.get("file_path", "")
        ))
        card.unlock_requested.connect(self._on_unlock_requested)
        self.content_layout.addWidget(card)
    
    def _on_unlock_requested(self, example_id, cost):
        """Handle unlock request from example card."""
        print(f"🔓 Unlock requested: {example_id}, cost: {cost} coins")
        # Store for parent to handle
        self._pending_unlock = (example_id, cost)
    
    def set_small_mode(self, is_small):
        """Update sizing for small screen mode."""
        self._is_small = is_small
        # Update coins widget if exists
        if hasattr(self, 'coins_widget') and self.coins_widget:
            self.coins_widget.set_small_mode(is_small)
    
    def refresh_coins(self):
        """Refresh coins display from progress manager."""
        if hasattr(self, 'coins_widget') and self.coins_widget:
            try:
                from src.modules.progress_manager import get_progress_manager
                from src.modules.developer_mode import get_developer_mode
                
                pm = get_progress_manager()
                dev_mode = get_developer_mode()
                
                # Use developer coins if dev mode is enabled
                if dev_mode.is_enabled():
                    total_coins = dev_mode.get_coins()
                    print(f"💰 Coins refreshed (DEV MODE): {total_coins} coins")
                else:
                    total_coins = pm.get_total_coins()
                    print(f"💰 Coins refreshed: {total_coins} coins")
                
                self.coins_widget.set_coins(total_coins)
            except Exception as e:
                print(f"⚠️ Could not refresh coins: {e}")


class HexagonBadge(QWidget):
    """Custom hexagon badge with number inside."""
    
    def __init__(self, number, is_active=False):
        super().__init__()
        self.number = number
        self.is_active = is_active
        self.setFixedSize(50, 50)
        
        # Color scheme matching the badge colors in lesson/example cards
        self.colors = {
            1: ("#10B981", "#059669"),  # Emerald Green (Beginner)
            2: ("#EAB308", "#CA8A04"),  # Yellow (Intermediate)
            3: ("#EF4444", "#DC2626"),  # Red (Advanced)
        }
    
    def set_active(self, active):
        """Update active state."""
        self.is_active = active
        self.update()
    
    def paintEvent(self, event):
        """Draw hexagon with number."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get colors based on level
        fill_color, border_color = self.colors.get(self.number, ("#10B981", "#059669"))
        
        # Create hexagon points
        center_x, center_y = 25, 25
        
        # Simplified hexagon
        hexagon = QPolygonF([
            QPointF(center_x, center_y - 18),
            QPointF(center_x + 16, center_y - 9),
            QPointF(center_x + 16, center_y + 9),
            QPointF(center_x, center_y + 18),
            QPointF(center_x - 16, center_y + 9),
            QPointF(center_x - 16, center_y - 9),
        ])
        
        # Draw hexagon with appropriate colors
        if self.is_active:
            # Active state: bright vibrant colors
            painter.setBrush(QColor(fill_color))
            painter.setPen(QPen(QColor(fill_color), 3))
        else:
            # Inactive state: muted/darker colors
            painter.setBrush(QColor(fill_color).darker(200))
            painter.setPen(QPen(QColor(border_color).darker(150), 2))
        
        painter.drawPolygon(hexagon)
        
        # Draw number (always white for good contrast)
        painter.setPen(QColor("#FFFFFF"))
        font = painter.font()
        font.setPointSize(16)
        font.setBold(True)
        painter.setFont(font)
        # Offset rect slightly up and right to compensate for font rendering offset on Windows
        from PyQt5.QtCore import QRect
        text_rect = QRect(self.rect().x() + 1, self.rect().y() - 1,
                          self.rect().width(), self.rect().height())
        painter.drawText(text_rect, Qt.AlignCenter, str(self.number))


class TimelineNode(QWidget):
    """Timeline node widget for level filter."""
    
    clicked = pyqtSignal()
    
    def __init__(self, level_number, label, is_active=False):
        super().__init__()
        self.is_active = is_active
        self.level_number = level_number
        
        self.setStyleSheet("QWidget { background: transparent; }")
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)
        
        # Hexagon badge
        self.badge = HexagonBadge(level_number, is_active)
        layout.addWidget(self.badge, alignment=Qt.AlignCenter)
        
        # Label
        self.text_label = QLabel(label)
        self.text_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.text_label)
        
        self._update_style()
    
    def set_active(self, active):
        """Set active state."""
        self.is_active = active
        self.badge.set_active(active)
        self._update_style()
    
    def _update_style(self):
        """Update visual style based on active state."""
        if self.is_active:
            self.text_label.setStyleSheet("""
                QLabel {
                    color: #FFFFFF;
                    font-size: 13px;
                    font-weight: bold;
                    background: transparent;
                }
            """)
        else:
            self.text_label.setStyleSheet("""
                QLabel {
                    color: #6B7280;
                    font-size: 13px;
                    font-weight: normal;
                    background: transparent;
                }
            """)
    
    def mousePressEvent(self, event):
        """Handle mouse click."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


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
        self.setStyleSheet("""
            QFrame#lessonCard {
                background: #2A2A3C;
                border: 1px solid #3F3F5A;
                border-radius: 12px;
                padding: 12px;
            }
            QFrame#lessonCard:hover {
                border: 1px solid #8B5CF6;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(12)
        
        # Icon - smaller
        icon_label = QLabel(lesson_data.get("icon", "📚"))
        icon_label.setStyleSheet("font-size: 48px; background: transparent;")
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Content (title + description)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        title = QLabel(lesson_data.get("title", "Lesson"))
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #FFFFFF;
            background: transparent;
        """)
        content_layout.addWidget(title)
        
        desc = QLabel(lesson_data.get("description", ""))
        desc.setWordWrap(True)
        desc.setStyleSheet("""
            font-size: 12px;
            color: #A1A1AA;
            background: transparent;
        """)
        content_layout.addWidget(desc)
        
        layout.addLayout(content_layout, 1)
        
        # Right side buttons
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(6)
        buttons_layout.setAlignment(Qt.AlignCenter)
        
        # Level badge with dynamic colors
        level_text = lesson_data.get("level", "Beginner")
        if lang == "vi":
            level_map = {"Beginner": "Cơ bản", "Intermediate": "Trung cấp", "Advanced": "Nâng cao"}
            display_text = level_map.get(level_text, level_text)
        else:
            display_text = level_text
        
        # Dynamic badge color based on level
        badge_colors = {
            "Beginner": "#10B981",      # Emerald Green
            "Intermediate": "#EAB308",  # Yellow
            "Advanced": "#EF4444"       # Red
        }
        badge_color = badge_colors.get(level_text, "#10B981")
        
        level_badge = QLabel(display_text)
        level_badge.setAlignment(Qt.AlignCenter)
        level_badge.setStyleSheet(f"""
            background: {badge_color};
            color: #FFFFFF;
            border-radius: 8px;
            padding: 3px 10px;
            font-weight: bold;
            font-size: 11px;
        """)
        buttons_layout.addWidget(level_badge)
        
        # Start/Stop button - smaller
        if self.is_active:
            self.action_btn = QPushButton("⏹ Stop")
            self.action_btn.clicked.connect(lambda: self._on_stop_clicked())
        else:
            start_text = "▶ Start" if lang == "en" else "▶ Bắt đầu"
            self.action_btn = QPushButton(start_text)
            self.action_btn.clicked.connect(lambda: self._on_start_clicked())
        
        self.action_btn.setFixedSize(100, 32)
        self.action_btn.setCursor(Qt.PointingHandCursor)
        self.action_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8B5CF6, stop:1 #6366F1);
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 13px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9F7AEA, stop:1 #7C3AED);
            }
        """)
        buttons_layout.addWidget(self.action_btn)
        
        layout.addLayout(buttons_layout)
    
    def _on_start_clicked(self):
        """Handle start button click."""
        self.start_clicked.emit()
    
    def _on_stop_clicked(self):
        """Handle stop button click."""
        self.stop_clicked.emit()


class ExampleCard(QFrame):
    """Individual example card widget."""
    
    load_clicked = pyqtSignal()
    unlock_requested = pyqtSignal(str, int)  # example_id, cost
    
    def __init__(self, example_data, lang="en", is_small=False):
        super().__init__()
        self.example_data = example_data
        self.lang = lang
        self.is_locked = not example_data.get("is_unlocked", False)
        self.example_id = example_data.get("id", "")
        self.cost = example_data.get("cost", 5)
        
        self.setObjectName("exampleCard")
        
        # Different styling for locked vs unlocked
        if self.is_locked:
            self.setStyleSheet("""
                QFrame#exampleCard {
                    background: #1F1F2E;
                    border: 2px dashed #3F3F5A;
                    border-radius: 12px;
                    padding: 12px;
                }
                QFrame#exampleCard:hover {
                    border: 2px dashed #6366F1;
                    background: #252535;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame#exampleCard {
                    background: #2A2A3C;
                    border: 1px solid #3F3F5A;
                    border-radius: 12px;
                    padding: 12px;
                }
                QFrame#exampleCard:hover {
                    border: 1px solid #8B5CF6;
                }
            """)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(12)
        
        # Icon - with lock overlay if locked
        icon_container = QWidget()
        icon_container.setFixedSize(48, 48)
        icon_container.setStyleSheet("background: transparent;")
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        if self.is_locked:
            icon_label = QLabel("🔒")
            icon_label.setStyleSheet("font-size: 36px; background: transparent; color: #6B7280;")
        else:
            icon_label = QLabel(example_data.get("icon", "🎯"))
            icon_label.setStyleSheet("font-size: 48px; background: transparent;")
        
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)
        layout.addWidget(icon_container)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        title = QLabel(example_data.get("title", "Example"))
        if self.is_locked:
            title.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #6B7280;
                background: transparent;
            """)
        else:
            title.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #FFFFFF;
                background: transparent;
            """)
        content_layout.addWidget(title)
        
        desc = QLabel(example_data.get("description", ""))
        desc.setWordWrap(True)
        if self.is_locked:
            desc.setStyleSheet("""
                font-size: 12px;
                color: #4B5563;
                background: transparent;
            """)
        else:
            desc.setStyleSheet("""
                font-size: 12px;
                color: #A1A1AA;
                background: transparent;
            """)
        content_layout.addWidget(desc)
        
        layout.addLayout(content_layout, 1)
        
        # Right side buttons
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(6)
        buttons_layout.setAlignment(Qt.AlignCenter)
        
        # Level badge with dynamic colors
        level_text = example_data.get("level", "Beginner")
        if lang == "vi":
            level_map = {"Beginner": "Cơ bản", "Intermediate": "Trung cấp", "Advanced": "Nâng cao"}
            display_text = level_map.get(level_text, level_text)
        else:
            display_text = level_text
        
        # Dynamic badge color based on level
        badge_colors = {
            "Beginner": "#10B981",      # Emerald Green
            "Intermediate": "#EAB308",  # Yellow
            "Advanced": "#EF4444"       # Red
        }
        badge_color = badge_colors.get(level_text, "#10B981")
        
        level_badge = QLabel(display_text)
        level_badge.setAlignment(Qt.AlignCenter)
        if self.is_locked:
            level_badge.setStyleSheet(f"""
                background: #374151;
                color: #9CA3AF;
                border-radius: 8px;
                padding: 3px 10px;
                font-weight: bold;
                font-size: 11px;
            """)
        else:
            level_badge.setStyleSheet(f"""
                background: {badge_color};
                color: #FFFFFF;
                border-radius: 8px;
                padding: 3px 10px;
                font-weight: bold;
                font-size: 11px;
            """)
        buttons_layout.addWidget(level_badge)
        
        # Load/Unlock button
        if self.is_locked:
            # Show unlock button with cost
            unlock_text = f"🔓 {self.cost} 🪙" if lang == "en" else f"🔓 {self.cost} 🪙"
            self.action_btn = QPushButton(unlock_text)
            self.action_btn.clicked.connect(self._on_unlock_clicked)
            self.action_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #F59E0B, stop:1 #D97706);
                    color: #FFFFFF;
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 13px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FBBF24, stop:1 #F59E0B);
                }
            """)
        else:
            # Show load button
            load_text = "📂 Load" if lang == "en" else "📂 Tải"
            self.action_btn = QPushButton(load_text)
            self.action_btn.clicked.connect(self.load_clicked.emit)
            self.action_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #8B5CF6, stop:1 #6366F1);
                    color: #FFFFFF;
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 13px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #9F7AEA, stop:1 #7C3AED);
                }
            """)
        
        self.action_btn.setFixedSize(100, 32)
        self.action_btn.setCursor(Qt.PointingHandCursor)
        buttons_layout.addWidget(self.action_btn)
        
        layout.addLayout(buttons_layout)
    
    def _on_unlock_clicked(self):
        """Handle unlock button click."""
        self.unlock_requested.emit(self.example_id, self.cost)
