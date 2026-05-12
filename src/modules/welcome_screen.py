"""
Welcome Screen - Initial screen when app starts
Allows user to choose between Creative Mode and Unlock Mode
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class WelcomeScreen(QWidget):
    """
    Welcome screen displayed on app startup.
    User chooses between Creative Mode or Unlock Mode.
    """
    
    creative_mode_selected = pyqtSignal()
    unlock_mode_selected = pyqtSignal()
    
    def __init__(self, parent=None, lang="en"):
        super().__init__(parent)
        self.lang = lang
        
        # Main background
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f0c29, stop:0.5 #1a1a2e, stop:1 #24243e);
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Welcome title
        title = QLabel("Welcome to AI Education App" if lang == "en" else "Chào mừng đến với Ứng dụng Giáo dục AI")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #FFFFFF;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Choose your learning path" if lang == "en" else "Chọn lộ trình học tập của bạn")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #9CA3AF;
            margin-bottom: 20px;
        """)
        main_layout.addWidget(subtitle)
        
        # Buttons container - use horizontal layout with proper spacing
        buttons_container = QWidget()
        buttons_container.setStyleSheet("QWidget { background: transparent; }")
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(20)
        buttons_layout.setAlignment(Qt.AlignCenter)
        
        # Creative Mode Card
        creative_card = self._create_mode_card(
            title="Creative Mode" if lang == "en" else "Chế độ Sáng tạo",
            description="Work freely with unlocked functions" if lang == "en" else "Làm việc tự do với các chức năng đã mở khóa",
            icon="🎨",
            color="#8B5CF6",
            callback=self._on_creative_mode_clicked
        )
        buttons_layout.addWidget(creative_card)
        
        # Unlock Mode Card
        unlock_card = self._create_mode_card(
            title="Unlock Mode" if lang == "en" else "Chế độ Mở khóa",
            description="Complete lessons to unlock new functions" if lang == "en" else "Hoàn thành bài học để mở khóa chức năng mới",
            icon="🔓",
            color="#10B981",
            callback=self._on_unlock_mode_clicked
        )
        buttons_layout.addWidget(unlock_card)
        
        main_layout.addWidget(buttons_container)
        
        # Add spacer at bottom
        main_layout.addStretch()
    
    def _create_mode_card(self, title, description, icon, color, callback):
        """Create a mode selection card with fixed size."""
        card = QFrame()
        card.setObjectName("modeCard")
        card.setFixedSize(220, 280)  # Fixed size to prevent overlap
        card.setStyleSheet(f"""
            QFrame#modeCard {{
                background: rgba(43, 45, 66, 0.9);
                border: 2px solid {color};
                border-radius: 16px;
                padding: 20px;
            }}
            QFrame#modeCard:hover {{
                background: rgba(50, 52, 74, 0.95);
                border: 3px solid {color};
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setAlignment(Qt.AlignCenter)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            font-size: 48px;
            background: transparent;
        """)
        card_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #FFFFFF;
            background: transparent;
        """)
        card_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            font-size: 12px;
            color: #9CA3AF;
            background: transparent;
            min-height: 40px;
        """)
        card_layout.addWidget(desc_label)
        
        # Select button
        select_btn = QPushButton("Select" if self.lang == "en" else "Chọn")
        select_btn.setFixedHeight(40)
        select_btn.setCursor(Qt.PointingHandCursor)
        select_btn.clicked.connect(callback)
        select_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color}, stop:1 {self._darken_color(color)});
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background: {color};
            }}
        """)
        card_layout.addWidget(select_btn)
        
        return card
    
    def _darken_color(self, color):
        """Darken a hex color for gradient."""
        color_map = {
            "#8B5CF6": "#6D28D9",
            "#10B981": "#059669"
        }
        return color_map.get(color, color)
    
    def _on_creative_mode_clicked(self):
        """Handle Creative Mode selection."""
        self.creative_mode_selected.emit()
    
    def _on_unlock_mode_clicked(self):
        """Handle Unlock Mode selection."""
        self.unlock_mode_selected.emit()
