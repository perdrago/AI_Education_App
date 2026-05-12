"""
Developer Mode - Testing utilities for developers
Password: kdi@2026
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class DeveloperModeDialog(QDialog):
    """Dialog for entering developer mode password."""
    
    authenticated = pyqtSignal()  # Emitted when password is correct
    
    def __init__(self, parent=None, lang="en"):
        super().__init__(parent)
        self.lang = lang
        self.password = "kdi@2026"  # Default password
        
        self.setWindowTitle("Developer Mode" if lang == "en" else "Chế Độ Người Phát Triển")
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        # Center on parent
        if parent:
            parent_geo = parent.geometry()
            x = parent_geo.x() + (parent_geo.width() - 400) // 2
            y = parent_geo.y() + (parent_geo.height() - 200) // 2
            self.move(x, y)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Icon
        icon_label = QLabel("🔐")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; background: transparent;")
        layout.addWidget(icon_label)
        
        # Title
        title = QLabel("Developer Mode" if self.lang == "en" else "Chế Độ Người Phát Triển")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Enter password to access developer features" if self.lang == "en" 
                     else "Nhập mật khẩu để truy cập chức năng người phát triển")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 12px; color: #cbd5e1;")
        layout.addWidget(desc)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Password" if self.lang == "en" else "Mật khẩu")
        self.password_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
                background: rgba(255, 255, 255, 0.15);
            }
        """)
        self.password_input.returnPressed.connect(self._check_password)
        layout.addWidget(self.password_input)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        # Cancel button
        btn_cancel = QPushButton("Cancel" if self.lang == "en" else "Hủy")
        btn_cancel.setFixedSize(120, 40)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.05);
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        # Login button
        btn_login = QPushButton("Login" if self.lang == "en" else "Đăng Nhập")
        btn_login.setFixedSize(120, 40)
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_login.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background: #2563eb;
            }
            QPushButton:pressed {
                background: #1d4ed8;
            }
        """)
        btn_login.clicked.connect(self._check_password)
        btn_layout.addWidget(btn_login)
        
        layout.addLayout(btn_layout)
        
        # Style the dialog
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 12px;
            }
            QLabel {
                background: transparent;
            }
        """)
        
        # Focus on password input
        self.password_input.setFocus()
    
    def _check_password(self):
        """Check if password is correct."""
        entered = self.password_input.text()
        
        if entered == self.password:
            self.authenticated.emit()
            self.accept()
        else:
            # Show error
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Error" if self.lang == "en" else "Lỗi")
            msg.setText("Incorrect password!" if self.lang == "en" else "Mật khẩu không đúng!")
            msg.setStyleSheet("""
                QMessageBox {
                    background: #1e293b;
                }
                QMessageBox QLabel {
                    color: white;
                    font-size: 14px;
                }
                QPushButton {
                    background: #3b82f6;
                    color: white;
                    border-radius: 6px;
                    padding: 8px 20px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background: #2563eb;
                }
            """)
            msg.exec_()
            
            # Clear and refocus
            self.password_input.clear()
            self.password_input.setFocus()


class DeveloperMode:
    """Manager for developer mode state and features."""
    
    def __init__(self):
        self.enabled = False
        self.infinite_coins = 9999
        self.auto_pass = True
    
    def enable(self):
        """Enable developer mode."""
        self.enabled = True
        print("🔓 Developer Mode ENABLED")
        print(f"   - Infinite coins: {self.infinite_coins}")
        print(f"   - Auto-pass: {self.auto_pass}")
    
    def disable(self):
        """Disable developer mode."""
        self.enabled = False
        print("🔒 Developer Mode DISABLED")
    
    def is_enabled(self) -> bool:
        """Check if developer mode is enabled."""
        return self.enabled
    
    def get_coins(self) -> int:
        """Get coins amount (9999 if dev mode, otherwise None)."""
        if self.enabled:
            return self.infinite_coins
        return None
    
    def should_auto_pass(self) -> bool:
        """Check if auto-pass is enabled."""
        return self.enabled and self.auto_pass


# Global instance
_developer_mode = None

def get_developer_mode() -> DeveloperMode:
    """Get global developer mode instance."""
    global _developer_mode
    if _developer_mode is None:
        _developer_mode = DeveloperMode()
    return _developer_mode
