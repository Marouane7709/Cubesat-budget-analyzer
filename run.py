#!/usr/bin/env python3
"""
CubeSat Budget Analyzer - Main Entry Point
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QObject
from controller.theme_manager import ThemeManager
from view.login_view import LoginWindow
from view.main_view import MainWindow
from view.home_view import HomeWindow
from controller.home_controller import HomeController
from model.database import init_db, auto_save_timer

class ApplicationManager(QObject):
    def __init__(self):
        super().__init__()
        self.logger = setup_logging()
        self.app = None
        self.theme_manager = None
        self.main_window = None
        self.login_window = None
        self.home_window = None
        self.home_controller = None
        
    def initialize(self):
        """Initialize the application components."""
        try:
            # Create application instance
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("CubeSat Budget Analyzer")
            self.app.setApplicationVersion("1.0.0")
            self.app.setOrganizationName("Your Organization")
            
            # Initialize database
            self.logger.info("Initializing database")
            init_db()
            
            # Setup theme manager
            self.logger.info("Setting up theme manager")
            self.theme_manager = ThemeManager()
            self.theme_manager.apply_theme('dark')  # Default theme
            
            # Start auto-save timer
            self.logger.info("Starting auto-save timer")
            auto_save_timer.start(300000)  # 5 minutes in milliseconds
            
            return True
            
        except Exception as e:
            self.logger.critical(f"Failed to initialize application: {str(e)}", exc_info=True)
            return False
    
    def show_login(self):
        """Show the login window and handle its result."""
        try:
            self.logger.info("Showing login window")
            
            # Hide other windows
            if self.main_window:
                self.main_window.hide()
            if self.home_window:
                self.home_window.hide()
            
            # Create login window if it doesn't exist
            if not self.login_window:
                self.login_window = LoginWindow(self.theme_manager)
                self.login_window.login_successful.connect(self.show_home)  # Connect to show_home instead of show_main
            
            self.login_window.show()
            return True
            
        except Exception as e:
            self.logger.error(f"Error showing login window: {str(e)}", exc_info=True)
            return False

    def show_home(self):
        """Show the home window."""
        try:
            self.logger.info("Showing home window")
            
            # Hide other windows
            if self.login_window:
                self.login_window.hide()
            if self.main_window:
                self.main_window.hide()
            
            # Create home window if it doesn't exist
            if not self.home_window:
                self.home_window = HomeWindow(self.theme_manager)
                self.home_controller = HomeController(self.home_window)
                # Connect signals
                self.theme_manager.theme_changed.connect(self.home_window.update)
                self.home_controller.navigate_to_login.connect(self.show_login)
                self.home_controller.navigate_to_module.connect(self.load_module)
            
            self.home_window.show()
            return True
            
        except Exception as e:
            self.logger.error(f"Error showing home window: {str(e)}", exc_info=True)
            return False
    
    def show_main(self):
        """Show the main application window."""
        try:
            self.logger.info("Showing main window")
            
            # Hide other windows
            if self.login_window:
                self.login_window.hide()
            if self.home_window:
                self.home_window.hide()
            
            # Create main window if it doesn't exist
            if not self.main_window:
                self.main_window = MainWindow(self.theme_manager)
                self.main_window.navigate_to_home.connect(self.show_home)  # Connect the new home navigation signal
            
            self.main_window.show()
            return True
            
        except Exception as e:
            self.logger.error(f"Error showing main window: {str(e)}", exc_info=True)
            return False

    def load_module(self, module_name: str):
        """Load a specific module."""
        try:
            self.logger.info(f"Loading module: {module_name}")
            self.show_main()  # Show main window when loading a module
            
            # Switch to the appropriate module tab
            if self.main_window:
                self.main_window.switch_to_module(module_name)
            
        except Exception as e:
            self.logger.error(f"Error loading module {module_name}: {str(e)}", exc_info=True)
    
    def cleanup(self):
        """Clean up application resources."""
        try:
            if self.main_window:
                self.main_window.close()
                self.main_window.deleteLater()
                self.main_window = None
                
            if self.login_window:
                self.login_window.close()
                self.login_window.deleteLater()
                self.login_window = None
                
            if self.home_window:
                self.home_window.close()
                self.home_window.deleteLater()
                self.home_window = None
                self.home_controller = None
                
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}", exc_info=True)
    
    def run(self):
        """Run the application main loop."""
        if not self.initialize():
            return 1
            
        try:
            # Show initial login window
            if not self.show_login():
                return 1
                
            # Start application event loop
            return self.app.exec()
            
        except Exception as e:
            self.logger.critical(f"Application error: {str(e)}", exc_info=True)
            self.cleanup()
            return 1

def setup_logging():
    """Setup application logging."""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions."""
    logger = logging.getLogger(__name__)
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

def main():
    """Main application entry point."""
    sys.excepthook = handle_exception
    app_manager = ApplicationManager()
    return app_manager.run()

if __name__ == '__main__':
    sys.exit(main()) 