from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QPushButton, QMessageBox, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont

class LoginWindow(QDialog):
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the login dialog UI."""
        self.setWindowTitle("Login")
        self.setFixedSize(400, 500)
        self.setModal(True)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Logo placeholder
        logo_widget = QWidget()
        logo_widget.setFixedSize(150, 150)
        logo_widget.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border: 2px dashed #cccccc;
                border-radius: 75px;
            }
        """)
        main_layout.addWidget(logo_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Title
        title_label = QLabel("CubeSat Budget Analyzer")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2196F3;")
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Subtitle
        subtitle_label = QLabel("Satellite Communication and Data Budget Analysis Tool")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #757575;
                padding: 10px 0;
                line-height: 1.5;
            }
        """)
        subtitle_label.setWordWrap(True)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setMinimumHeight(60)  # Ensure enough space for two lines
        main_layout.addWidget(subtitle_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Add some spacing
        main_layout.addSpacing(30)
        
        # Login form container
        form_container = QWidget()
        form_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)
        
        # Username input
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
            }
        """)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        form_layout.addLayout(username_layout)
        
        # Password input
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
            }
        """)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        form_layout.addLayout(password_layout)
        
        main_layout.addWidget(form_container)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.login_button.clicked.connect(self.authenticate)
        button_layout.addWidget(self.login_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                color: #757575;
                border: 1px solid #BDBDBD;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
    def authenticate(self):
        """Authenticate the user."""
        username = self.username_input.text()
        password = self.password_input.text()
        
        # TODO: Implement proper authentication
        # For now, accept any non-empty username/password
        if username and password:
            self.accept()
        else:
            # Clear the password field
            self.password_input.clear()
            # Show error message
            QMessageBox.warning(
                self,
                "Authentication Failed",
                "Please enter both username and password"
            )
            # Keep the window open and focus on the username field
            self.username_input.setFocus() 