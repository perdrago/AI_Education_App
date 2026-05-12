"""
Stars and Coins Widget - Display stars earned and coins available
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class StarsCoinsWidget(QWidget):
    """Widget to display stars (for steps) or HP (for challenge) and coins."""
    
    def __init__(self, parent=None, mode="stars", lang="en"):
        """
        Initialize widget.
        
        Args:
            mode: "stars" for step mode, "hp" for challenge mode
            lang: Language code
        """
        super().__init__(parent)
        self.mode = mode  # "stars" or "hp"
        self.lang = lang
        self.stars = 0
        self.hp = 5
        self.max_hp = 5
        
        self.setStyleSheet("background: transparent;")
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Stars/HP label
        self.indicator_label = QLabel()
        self.indicator_label.setFixedHeight(36)
        self.indicator_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.indicator_label)
        
        self.update_display()
    
    def set_mode(self, mode: str):
        """
        Change display mode.
        
        Args:
            mode: "stars" or "hp"
        """
        self.mode = mode
        self.update_display()
    
    def set_stars(self, stars: int):
        """Set number of stars earned."""
        self.stars = stars
        self.update_display()
    
    def add_stars(self, amount: int):
        """Add stars."""
        self.stars += amount
        self.update_display()
    
    def set_hp(self, hp: int, max_hp: int = 5):
        """Set HP for challenge mode."""
        self.hp = hp
        self.max_hp = max_hp
        self.update_display()
    
    def decrease_hp(self) -> int:
        """Decrease HP by 1. Returns remaining HP."""
        self.hp = max(0, self.hp - 1)
        self.update_display()
        return self.hp
    
    def update_display(self):
        """Update the visual display based on current mode."""
        if self.mode == "stars":
            # Stars mode - Yellow star icon
            self.indicator_label.setText(f"⭐ {self.stars}")
            self.indicator_label.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                color: #f59e0b;
                padding: 0px 16px;
                background: rgba(245, 158, 11, 0.1);
                border-radius: 8px;
                border: 2px solid rgba(245, 158, 11, 0.3);
            """)
        else:  # hp mode
            # HP mode - Red heart icon
            self.indicator_label.setText(f"❤️ {self.hp}/{self.max_hp}")
            
            # Change color based on HP level
            if self.hp >= 4:
                color = "#10b981"  # Green - healthy
                bg_color = "rgba(16, 185, 129, 0.1)"
                border_color = "rgba(16, 185, 129, 0.3)"
            elif self.hp >= 2:
                color = "#f59e0b"  # Orange - warning
                bg_color = "rgba(245, 158, 11, 0.1)"
                border_color = "rgba(245, 158, 11, 0.3)"
            else:
                color = "#dc2626"  # Red - danger
                bg_color = "rgba(220, 38, 38, 0.1)"
                border_color = "rgba(220, 38, 38, 0.3)"
            
            self.indicator_label.setStyleSheet(f"""
                font-size: 18px;
                font-weight: bold;
                color: {color};
                padding: 0px 16px;
                background: {bg_color};
                border-radius: 8px;
                border: 2px solid {border_color};
            """)
    
    def set_small_mode(self, is_small: bool):
        """Adjust sizing for small screens."""
        font_size = 13 if is_small else 18
        padding = 8 if is_small else 16
        height = 24 if is_small else 36
        
        self.indicator_label.setFixedHeight(height)
        
        # Re-apply stylesheet with new sizes
        if self.mode == "stars":
            self.indicator_label.setStyleSheet(f"""
                font-size: {font_size}px;
                font-weight: bold;
                color: #f59e0b;
                padding: 0px {padding}px;
                background: rgba(245, 158, 11, 0.1);
                border-radius: 6px;
                border: 1.5px solid rgba(245, 158, 11, 0.3);
            """)
        else:
            # Recalculate color based on HP
            if self.hp >= 4:
                color = "#10b981"
                bg_color = "rgba(16, 185, 129, 0.1)"
                border_color = "rgba(16, 185, 129, 0.3)"
            elif self.hp >= 2:
                color = "#f59e0b"
                bg_color = "rgba(245, 158, 11, 0.1)"
                border_color = "rgba(245, 158, 11, 0.3)"
            else:
                color = "#dc2626"
                bg_color = "rgba(220, 38, 38, 0.1)"
                border_color = "rgba(220, 38, 38, 0.3)"
            
            self.indicator_label.setStyleSheet(f"""
                font-size: {font_size}px;
                font-weight: bold;
                color: {color};
                padding: 0px {padding}px;
                background: {bg_color};
                border-radius: 6px;
                border: 1.5px solid {border_color};
            """)


class CoinsDisplayWidget(QWidget):
    """Widget to display total coins available (for unlocking examples)."""
    
    def __init__(self, parent=None, lang="en"):
        super().__init__(parent)
        self.lang = lang
        self.coins = 0
        
        self.setStyleSheet("background: transparent;")
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Coins label
        self.coins_label = QLabel()
        self.coins_label.setAlignment(Qt.AlignCenter)
        self.coins_label.setFixedHeight(40)
        layout.addWidget(self.coins_label)
        
        self.update_display()
    
    def set_coins(self, coins: int):
        """Set number of coins."""
        self.coins = coins
        self.update_display()
    
    def add_coins(self, amount: int):
        """Add coins."""
        self.coins += amount
        self.update_display()
    
    def spend_coins(self, amount: int) -> bool:
        """
        Spend coins.
        
        Returns:
            bool: True if successful, False if not enough coins
        """
        if self.coins >= amount:
            self.coins -= amount
            self.update_display()
            return True
        return False
    
    def update_display(self):
        """Update the visual display."""
        self.coins_label.setText(f"🪙 {self.coins}")
        self.coins_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #f59e0b;
            padding: 0px 20px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(245, 158, 11, 0.15),
                stop:1 rgba(217, 119, 6, 0.15));
            border-radius: 10px;
            border: 2px solid rgba(245, 158, 11, 0.4);
        """)
    
    def set_small_mode(self, is_small: bool):
        """Adjust sizing for small screens."""
        font_size = 14 if is_small else 20
        padding = 12 if is_small else 20
        height = 28 if is_small else 40
        
        self.coins_label.setFixedHeight(height)
        self.coins_label.setStyleSheet(f"""
            font-size: {font_size}px;
            font-weight: bold;
            color: #f59e0b;
            padding: 0px {padding}px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(245, 158, 11, 0.15),
                stop:1 rgba(217, 119, 6, 0.15));
            border-radius: {6 if is_small else 10}px;
            border: {1.5 if is_small else 2}px solid rgba(245, 158, 11, 0.4);
        """)
