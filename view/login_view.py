from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QPushButton, QMessageBox, QWidget,
                            QMenuBar, QMainWindow, QApplication, QFrame, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QPalette, QColor, QPainter, QPainterPath, QIcon
from PyQt6.QtSvg import QSvgRenderer

class LoginCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("login_card")
        self.setStyleSheet("""
            QFrame#login_card {
                background: #2A2A2A;
                border: 1px solid #505050;
                border-radius: 8px;
            }
            QFrame#login_card[light="true"] {
                background: #FFFFFF;
                border: 1px solid #E0E0E0;
            }
        """)
        self.setFixedWidth(360)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 32, 24, 32)
        layout.setSpacing(20)
        
        # Rocket SVG Icon
        icon = QLabel()
        icon.setFixedSize(150, 150)
        icon.setStyleSheet("background: transparent;")
        
        # Embed SVG directly with duotone colors
        svg_data = '''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="150" height="150" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path fill="#FFFFFF" d="M13.13 22.19l-1.63-3.83c1.57-.58 3.04-1.36 4.4-2.27l-2.77 6.1M5.64 12.5l-3.83-1.63 6.1-2.77c-.91 1.36-1.69 2.83-2.27 4.4M21.61 2.39S16.66.269 11 5.93c-2.19 2.19-3.5 4.6-4.32 6.91-.23.65-.04 1.35.46 1.85l1.83 1.83c.5.5 1.2.69 1.85.46 2.31-.82 4.72-2.13 6.91-4.32 5.66-5.66 3.54-10.61 3.54-10.61m-5.43 7.33c-.78.78-2.05.78-2.83 0-.78-.78-.78-2.05 0-2.83.78-.78 2.05-.78 2.83 0 .78.78.78 2.05 0 2.83m-7.5 12.99l-3.24-3.24c-.51-.51-1.34-.51-1.85 0-.51.51-.51 1.34 0 1.85l3.24 3.24c.51.51 1.34.51 1.85 0 .51-.51.51-1.34 0-1.85"/>
            <path fill="#4CAF50" d="M13.13 22.19l-1.63-3.83c1.57-.58 3.04-1.36 4.4-2.27l-2.77 6.1M5.64 12.5l-3.83-1.63 6.1-2.77c-.91 1.36-1.69 2.83-2.27 4.4M21.61 2.39S16.66.269 11 5.93c-2.19 2.19-3.5 4.6-4.32 6.91-.23.65-.04 1.35.46 1.85l1.83 1.83c.5.5 1.2.69 1.85.46 2.31-.82 4.72-2.13 6.91-4.32 5.66-5.66 3.54-10.61 3.54-10.61m-5.43 7.33c-.78.78-2.05.78-2.83 0-.78-.78-.78-2.05 0-2.83.78-.78 2.05-.78 2.83 0 .78.78.78 2.05 0 2.83m-7.5 12.99l-3.24-3.24c-.51-.51-1.34-.51-1.85 0-.51.51-.51 1.34 0 1.85l3.24 3.24c.51.51 1.34.51 1.85 0 .51-.51.51-1.34 0-1.85"/>
        </svg>'''
        
        renderer = QSvgRenderer()
        renderer.load(bytes(svg_data, 'utf-8'))
        icon.setProperty("renderer", renderer)
        icon.paintEvent = lambda e: renderer.render(QPainter(icon))
        
        # Title and subtitle
        self.title = QLabel("CubeSat Budget Analyzer")
        self.title.setObjectName("title_label")
        self.title.setFont(QFont("Inter", 24, QFont.Weight.Bold))
        self.title.setStyleSheet("""
            QLabel#title_label {
                color: #4CAF50;
            }
            QLabel#title_label[light="true"] {
                color: #2E7D32;
            }
        """)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.subtitle = QLabel("Satellite Communication and\nData Budget Analysis Tool")
        self.subtitle.setObjectName("subtitle_label")
        self.subtitle.setFont(QFont("Inter", 12))
        self.subtitle.setStyleSheet("""
            QLabel#subtitle_label {
                color: #B0B0B0;
            }
            QLabel#subtitle_label[light="true"] {
                color: #616161;
            }
        """)
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Username field
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter username")
        self.username.setFixedHeight(40)
        
        # Password field
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setFixedHeight(40)
        
        # Remember me and Forgot password row
        remember_row = QHBoxLayout()
        remember_row.setContentsMargins(0, 0, 0, 0)
        
        self.remember = QCheckBox("Remember me")
        self.remember.setFont(QFont("Inter", 11))
        self.remember.setStyleSheet("""
            QCheckBox {
                color: #E0E0E0;
            }
            QCheckBox[light="true"] {
                color: #424242;
            }
        """)
        
        self.forgot = QPushButton("Forgot Password?")
        self.forgot.setFont(QFont("Inter", 11))
        self.forgot.setCursor(Qt.CursorShape.PointingHandCursor)
        self.forgot.setFlat(True)
        self.forgot.setStyleSheet("""
            QPushButton {
                color: #4CAF50;
                border: none;
                text-decoration: underline;
                text-align: right;
            }
            QPushButton:hover {
                color: #66BB6A;
            }
        """)
        
        remember_row.addWidget(self.remember)
        remember_row.addWidget(self.forgot)
        
        # Login button
        self.login_btn = QPushButton("Login")
        self.login_btn.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        self.login_btn.setFixedHeight(44)
        self.login_btn.setEnabled(False)
        
        # Add all widgets to layout
        layout.addWidget(icon, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addLayout(remember_row)
        layout.addWidget(self.login_btn)
        
        # Setup field styling
        self.setup_field_styling()
        
        # Connect signals
        self.username.textChanged.connect(self.check_fields)
        self.password.textChanged.connect(self.check_fields)
        
    def setup_field_styling(self):
        """Setup styling for input fields"""
        field_style = """
            QLineEdit {
                background: #1E1E1E;
                border: 1px solid #505050;
                border-radius: 6px;
                padding: 0 12px;
                font: 12pt 'Inter';
                color: #E0E0E0;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QLineEdit::placeholder {
                color: #808080;
            }
            QLineEdit[light="true"] {
                background: #FAFAFA;
                border: 1px solid #E0E0E0;
                color: #202020;
            }
            QLineEdit[light="true"]:focus {
                border: 2px solid #4CAF50;
            }
            QLineEdit[light="true"]::placeholder {
                color: #808080;
            }
        """
        self.username.setStyleSheet(field_style)
        self.password.setStyleSheet(field_style)
        
        button_style = """
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                font: bold 16pt 'Inter';
            }
            QPushButton:hover {
                background: #66BB6A;
            }
            QPushButton:disabled {
                background: #BDBDBD;
            }
        """
        self.login_btn.setStyleSheet(button_style)
        
    def check_fields(self):
        """Enable login button only if both fields have content"""
        self.login_btn.setEnabled(
            bool(self.username.text()) and bool(self.password.text())
        )

class LoginWindow(QWidget):
    login_successful = pyqtSignal(str, str, bool)
    back_requested = pyqtSignal()
    forgot_requested = pyqtSignal()
    
    def __init__(self, theme_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the login view UI"""
        # Set window properties
        self.setWindowTitle("Login - CubeSat Budget Analyzer")
        self.resize(800, 600)
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create centered container
        container = QWidget()
        container.setObjectName("login_container")
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create and add login card
        self.card = LoginCard()
        container_layout.addWidget(self.card, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Add container to main layout
        layout.addWidget(container)
        
        # Connect signals
        self.card.login_btn.clicked.connect(self.on_login)
        self.card.forgot.clicked.connect(self.forgot_requested)
        
        # Apply theme
        self.update_theme(self.theme_manager.current_theme if self.theme_manager else 'light')
        if self.theme_manager:
            self.theme_manager.theme_changed.connect(self.update_theme)
            
    def update_theme(self, theme):
        """Update the view's theme"""
        if theme == 'dark':
            self.setStyleSheet("""
                QWidget#login_container {
                    background: #1E1E1E;
                }
            """)
            self.card.setProperty("light", "false")
            self.card.username.setProperty("light", "false")
            self.card.password.setProperty("light", "false")
            self.card.title.setProperty("light", "false")
            self.card.subtitle.setProperty("light", "false")
            self.card.remember.setProperty("light", "false")
        else:
            self.setStyleSheet("""
                QWidget#login_container {
                    background: #F4F4F4;
                }
            """)
            self.card.setProperty("light", "true")
            self.card.username.setProperty("light", "true")
            self.card.password.setProperty("light", "true")
            self.card.title.setProperty("light", "true")
            self.card.subtitle.setProperty("light", "true")
            self.card.remember.setProperty("light", "true")
            
    def on_login(self):
        """Handle login button click"""
        self.login_successful.emit(
            self.card.username.text(),
            self.card.password.text(),
            self.card.remember.isChecked()
        )
        
    def show_error(self, message):
        """Show error message"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Login Error", message)
        
    def clear_fields(self):
        """Clear input fields"""
        self.card.username.clear()
        self.card.password.clear()
        self.card.remember.setChecked(False) 