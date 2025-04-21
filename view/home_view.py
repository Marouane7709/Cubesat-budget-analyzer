from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFrame, QLabel,
                            QPushButton, QGridLayout, QHBoxLayout,
                            QMessageBox, QMenuBar)
from PyQt6.QtCore import Qt, pyqtSignal

class HomeWindow(QMainWindow):
    navigate_to_login = pyqtSignal()
    navigate_to_module = pyqtSignal(str)
    window_closing = pyqtSignal()

    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self.setObjectName("home_window")
        self.setup_ui()

    def setup_ui(self):
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Maximize the window
        self.showMaximized()
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

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

        # Welcome banner
        welcome_banner = QFrame()
        welcome_banner.setObjectName("welcome_banner")
        welcome_layout = QVBoxLayout(welcome_banner)
        
        welcome_header = QLabel("Welcome, Engineer!")
        welcome_header.setObjectName("welcome_header")
        welcome_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome_header)
        
        layout.addWidget(welcome_banner)

        # Description panel
        description_panel = QFrame()
        description_panel.setObjectName("description_panel")
        description_layout = QVBoxLayout(description_panel)
        
        description_text = QLabel(
            "This application provides comprehensive analysis tools for CubeSat design and budgeting.\n\n"
            "Select an analysis module below to begin your CubeSat design process."
        )
        description_text.setObjectName("description_text")
        description_text.setWordWrap(True)
        description_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_layout.addWidget(description_text)
        
        layout.addWidget(description_panel)

        # Analysis grid
        analysis_grid = QFrame()
        analysis_grid.setObjectName("analysis_grid")
        grid_layout = QGridLayout(analysis_grid)
        grid_layout.setSpacing(10)

        # Create analysis buttons
        buttons = [
            ("Link Budget Analysis", "link_budget_analysis", True),
            ("Data Budget Analysis", "data_budget_analysis", True),
            ("Mass Budget Analysis", "mass_budget_analysis", False),
            ("Power Budget Analysis", "power_budget_analysis", False),
            ("Thermal Analysis Budget", "thermal_analysis_budget", False)
        ]

        for i, (text, module, enabled) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setObjectName("analysis_button")
            btn.setProperty("data-module", module)
            btn.setEnabled(enabled)
            
            if i == 4:  # Thermal Analysis spans two columns
                grid_layout.addWidget(btn, 2, 0, 1, 2)
            else:
                grid_layout.addWidget(btn, i // 2, i % 2)

        layout.addWidget(analysis_grid)
        layout.addStretch()

        # Bottom bar with back button
        bottom_bar = QFrame()
        bottom_bar.setObjectName("bottom_bar")
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        back_button = QPushButton("← Back to Login")
        back_button.setObjectName("back_button")
        back_button.clicked.connect(self.confirm_return_to_login)
        bottom_layout.addWidget(back_button)
        bottom_layout.addStretch()
        
        layout.addWidget(bottom_bar)

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About CubeSat Budget Analyzer",
            "CubeSat Budget Analyzer v1.0\n\n"
            "A tool for analyzing CubeSat link and data budgets.\n\n"
            "© 2024 Your Organization"
        )

    def confirm_return_to_login(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Return to Login")
        msg_box.setText("Are you sure you want to return to the login screen? Any unsaved changes will be lost.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            self.navigate_to_login.emit()

    def closeEvent(self, event):
        """Handle window close event"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Exit Application")
        msg_box.setText("Are you sure you want to exit the application? Any unsaved changes will be lost.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            self.window_closing.emit()
            event.accept()
        else:
            event.ignore() 