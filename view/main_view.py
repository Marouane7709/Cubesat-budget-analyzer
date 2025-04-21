from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QTabWidget, QMenuBar, QMenu, QStatusBar,
                            QMessageBox, QFileDialog, QPushButton, QStackedWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from view.link_budget_view import LinkBudgetView
from view.data_budget_view import DataBudgetView
from model.database import session, Project
import json
from pathlib import Path

class MainWindow(QMainWindow):
    navigate_to_login = pyqtSignal()  # Add signal for navigation
    navigate_to_home = pyqtSignal()  # Signal for navigating to home
    
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self.current_project = None
        self.setup_ui()
        
    def closeEvent(self, event):
        """Handle window close event (X button)."""
        reply = QMessageBox.question(
            self,
            "Exit Application",
            "Are you sure you want to exit the application? Any unsaved changes will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Exit the entire application
            import sys
            sys.exit(0)
        else:
            event.ignore()  # Don't close the window
            
    def setup_ui(self):
        """Setup the main window UI components."""
        self.setWindowTitle("CubeSat Budget Analyzer")
        self.setMinimumSize(800, 600)
        # Maximize the window
        self.showMaximized()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)  # Remove spacing between widgets
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create stacked widget instead of tab widget
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Add pages
        self.link_budget_view = LinkBudgetView()
        self.data_budget_view = DataBudgetView()
        
        self.stacked_widget.addWidget(self.link_budget_view)
        self.stacked_widget.addWidget(self.data_budget_view)
        
        # Add spacer to push content up
        layout.addStretch()
        
        # Create bottom navigation bar
        self.bottom_nav = QWidget()
        self.bottom_nav.setObjectName("bottom_nav")
        bottom_layout = QHBoxLayout(self.bottom_nav)
        bottom_layout.setContentsMargins(10, 10, 10, 10)
        
        self.back_button = QPushButton("Back to Home")
        self.back_button.clicked.connect(self.go_back_to_home)
        bottom_layout.addWidget(self.back_button)
        bottom_layout.addStretch()
        
        layout.addWidget(self.bottom_nav)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Update theme initially
        self.update_theme(self.theme_manager.current_theme)
        # Connect to theme manager's theme changed signal
        self.theme_manager.theme_changed.connect(self.update_theme)
        
    def update_theme(self, theme):
        """Update the theme of the bottom navigation and back button."""
        if theme == 'dark':
            # Dark theme
            bottom_nav_style = """
                QWidget {
                    background-color: #121212;
                    border-top: 1px solid #424242;
                }
            """
            button_style = """
                QPushButton {
                    background-color: #424242;
                    color: #E0E0E0;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #616161;
                }
            """
        else:
            # Light theme
            bottom_nav_style = """
                QWidget {
                    background-color: #FFFFFF;
                    border-top: 1px solid #BDBDBD;
                }
            """
            button_style = """
                QPushButton {
                    background-color: #F5F5F5;
                    color: #757575;
                    border: 1px solid #BDBDBD;
                    padding: 8px 16px;
                    border-radius: 4px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #E0E0E0;
                }
            """
        
        # Apply styles directly to the widgets
        self.bottom_nav.setStyleSheet(bottom_nav_style)
        self.back_button.setStyleSheet(button_style)
        
    def go_back_to_home(self):
        """Return to the home screen."""
        reply = QMessageBox.question(
            self, "Return to Home",
            "Are you sure you want to return to the home screen? Any unsaved changes will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.hide()
            self.navigate_to_home.emit()
            
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = file_menu.addAction("New Project")
        new_action.triggered.connect(self.new_project)
        
        open_action = file_menu.addAction("Open Project")
        open_action.triggered.connect(self.open_project)
        
        save_action = file_menu.addAction("Save Project")
        save_action.triggered.connect(self.save_project)
        
        file_menu.addSeparator()
        
        export_config_action = file_menu.addAction("Export Config")
        export_config_action.triggered.connect(self.export_config)
        
        import_config_action = file_menu.addAction("Import Config")
        import_config_action.triggered.connect(self.import_config)
        
        file_menu.addSeparator()
        
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
        
    def new_project(self):
        """Create a new project."""
        if self.current_project:
            reply = QMessageBox.question(
                self, "New Project",
                "Current project will be closed. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        self.current_project = Project(name="New Project")
        session.add(self.current_project)
        session.commit()
        self.status_bar.showMessage("New project created")
        
    def open_project(self):
        """Open an existing project."""
        projects = session.query(Project).all()
        if not projects:
            QMessageBox.information(self, "Open Project", "No projects found")
            return
            
        # TODO: Implement project selection dialog
        self.status_bar.showMessage("Project opened")
        
    def save_project(self):
        """Save the current project."""
        if not self.current_project:
            QMessageBox.warning(self, "Save Project", "No project to save")
            return
            
        try:
            session.commit()
            self.status_bar.showMessage("Project saved")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save project: {str(e)}")
            
    def export_config(self):
        """Export current configuration to JSON file."""
        if not self.current_project:
            QMessageBox.warning(self, "Export Config", "No project to export")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Configuration",
            str(Path.home()),
            "JSON Files (*.json)"
        )
        
        if file_path:
            config = {
                'project_name': self.current_project.name,
                'link_budget': self.link_budget_view.get_config(),
                'data_budget': self.data_budget_view.get_config()
            }
            
            try:
                with open(file_path, 'w') as f:
                    json.dump(config, f, indent=4)
                self.status_bar.showMessage("Configuration exported")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export config: {str(e)}")
                
    def import_config(self):
        """Import configuration from JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Configuration",
            str(Path.home()),
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    config = json.load(f)
                    
                # Create new project
                self.new_project()
                self.current_project.name = config['project_name']
                
                # Apply configurations
                self.link_budget_view.set_config(config['link_budget'])
                self.data_budget_view.set_config(config['data_budget'])
                
                self.status_bar.showMessage("Configuration imported")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import config: {str(e)}")
                
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About CubeSat Budget Analyzer",
            "CubeSat Budget Analyzer v1.0\n\n"
            "A tool for analyzing CubeSat link and data budgets.\n\n"
            "© 2024 Your Organization"
        )

    def switch_to_module(self, module_name: str):
        """Switch to the specified module."""
        if module_name == "link_budget":
            self.stacked_widget.setCurrentWidget(self.link_budget_view)
            self.setWindowTitle("CubeSat Budget Analyzer - Link Budget")
        elif module_name == "data_budget":
            self.stacked_widget.setCurrentWidget(self.data_budget_view)
            self.setWindowTitle("CubeSat Budget Analyzer - Data Budget") 