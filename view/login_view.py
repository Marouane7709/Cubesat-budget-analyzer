from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QPushButton, QMessageBox, QWidget,
                            QMenuBar, QMainWindow, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont

class LoginWindow(QMainWindow):
    login_successful = pyqtSignal()
    
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self.setup_ui()
        self.update_theme(self.theme_manager.current_theme)
        self.theme_manager.theme_changed.connect(self.update_theme)

    def update_theme(self, theme):
        """Update the window theme."""
        if theme == 'dark':
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #121212;
                }
                QLabel {
                    color: #E0E0E0;
                }
                QWidget#logo_placeholder {
                    background-color: #1E1E1E;
                    border: 2px dashed #424242;
                }
                QLabel#title_label {
                    color: #2196F3;
                }
                QLabel#subtitle_label {
                    color: #9E9E9E;
                }
                QWidget#form_container {
                    background-color: #1E1E1E;
                    border: 1px solid #424242;
                    border-radius: 4px;
                    padding: 20px;
                }
                QLineEdit {
                    background-color: #2D2D2D;
                    color: #E0E0E0;
                    border: 1px solid #424242;
                    border-radius: 4px;
                    padding: 8px;
                    min-height: 20px;
                    selection-background-color: #2196F3;
                }
                QLineEdit:focus {
                    border: 1px solid #2196F3;
                    background-color: #1E1E1E;
                }
                QPushButton {
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    min-width: 80px;
                    font-size: 13px;
                }
                QPushButton#login_button {
                    background-color: #2196F3;
                    color: white;
                }
                QPushButton#login_button:hover {
                    background-color: #1976D2;
                }
                QPushButton#cancel_button {
                    background-color: #424242;
                    color: #E0E0E0;
                }
                QPushButton#cancel_button:hover {
                    background-color: #616161;
                }
                QMenuBar {
                    background-color: #1E1E1E;
                    color: #E0E0E0;
                }
                QMenuBar::item:selected {
                    background-color: #424242;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #FFFFFF;
                }
                QLabel {
                    color: #212121;
                }
                QWidget#logo_placeholder {
                    background-color: #F5F5F5;
                    border: 2px dashed #BDBDBD;
                }
                QLabel#title_label {
                    color: #2196F3;
                }
                QLabel#subtitle_label {
                    color: #757575;
                }
                QWidget#form_container {
                    background-color: #FFFFFF;
                    border: 1px solid #E0E0E0;
                    border-radius: 4px;
                    padding: 20px;
                }
                QLineEdit {
                    background-color: #FFFFFF;
                    color: #212121;
                    border: 1px solid #BDBDBD;
                    border-radius: 4px;
                    padding: 8px;
                    min-height: 20px;
                }
                QLineEdit:focus {
                    border: 1px solid #2196F3;
                }
                QPushButton {
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    min-width: 80px;
                    font-size: 13px;
                }
                QPushButton#login_button {
                    background-color: #2196F3;
                    color: white;
                }
                QPushButton#login_button:hover {
                    background-color: #1976D2;
                }
                QPushButton#cancel_button {
                    background-color: #F5F5F5;
                    color: #757575;
                    border: 1px solid #BDBDBD;
                }
                QPushButton#cancel_button:hover {
                    background-color: #E0E0E0;
                }
            """)
        
    def setup_ui(self):
        """Setup the login dialog UI."""
        self.setWindowTitle("Login")
        self.setFixedSize(400, 600)
        
        # Center the window on screen
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 10, 30, 30)

        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # View menu
        view_menu = menubar.addMenu("View")
        toggle_theme_action = view_menu.addAction("Toggle Theme")
        toggle_theme_action.triggered.connect(self.theme_manager.toggle_theme)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)
        
        # Logo placeholder
        logo_widget = QWidget()
        logo_widget.setObjectName("logo_placeholder")
        logo_widget.setFixedSize(150, 150)
        main_layout.addWidget(logo_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Title
        title_label = QLabel("CubeSat Budget Analyzer")
        title_label.setObjectName("title_label")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Subtitle
        subtitle_label = QLabel("Satellite Communication and Data\nBudget Analysis Tool")
        subtitle_label.setObjectName("subtitle_label")
        subtitle_font = QFont()
        subtitle_font.setPointSize(11)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Add some spacing
        main_layout.addSpacing(20)
        
        # Login form container
        form_container = QWidget()
        form_container.setObjectName("form_container")
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # Username input
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        
        # Add spacing between fields
        form_layout.addSpacing(5)
        
        # Password input
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        
        # Add spacing before buttons
        form_layout.addSpacing(15)
        
        # Buttons container with fixed width
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(8)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.login_button = QPushButton("Login")
        self.login_button.setObjectName("login_button")
        self.login_button.setFixedWidth(130)
        self.login_button.setFixedHeight(30)
        self.login_button.clicked.connect(self.authenticate)
        button_layout.addWidget(self.login_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setFixedWidth(130)
        self.cancel_button.setFixedHeight(30)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        form_layout.addWidget(button_container, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(form_container)

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About CubeSat Budget Analyzer",
            "CubeSat Budget Analyzer v1.0\n\n"
            "A tool for analyzing CubeSat link and data budgets.\n\n"
            "© 2024 Your Organization"
        )

    def reject(self):
        """Handle dialog rejection."""
        self.close()

    def authenticate(self):
        """Authenticate the user."""
        username = self.username_input.text()
        password = self.password_input.text()
        
        # TODO: Implement proper authentication
        # For now, accept any non-empty username/password
        if username and password:
            self.login_successful.emit()
            self.close()
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