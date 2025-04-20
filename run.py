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
from model.database import init_db, auto_save_timer

class ApplicationManager(QObject):
    def __init__(self):
        super().__init__()
        self.logger = setup_logging()
        self.app = None
        self.theme_manager = None
        self.main_window = None
        self.login_window = None
        
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
            self.theme_manager.apply_theme('light')  # Default theme
            
            return True
            
        except Exception as e:
            self.logger.critical(f"Failed to initialize application: {str(e)}", exc_info=True)
            return False
    
    def show_login(self):
        """Show the login window and handle its result."""
        try:
            self.logger.info("Showing login window")
            self.login_window = LoginWindow(self.theme_manager)
            return self.login_window.exec()
        except Exception as e:
            self.logger.error(f"Error showing login window: {str(e)}", exc_info=True)
            return 0
    
    def show_main(self):
        """Show the main application window."""
        try:
            self.logger.info("Showing main window")
            if self.main_window:
                self.main_window.close()
                
            self.main_window = MainWindow(self.theme_manager)
            self.main_window.show()
            
            # Start auto-save timer
            self.logger.info("Starting auto-save timer")
            auto_save_timer.start(300000)  # 5 minutes in milliseconds
            
            return True
        except Exception as e:
            self.logger.error(f"Error showing main window: {str(e)}", exc_info=True)
            return False
    
    def cleanup(self):
        """Clean up application resources."""
        if self.main_window:
            self.main_window.close()
        if self.login_window:
            self.login_window.close()
            
    def run(self):
        """Run the application main loop."""
        if not self.initialize():
            return 1
            
        try:
            while True:
                # Show login window
                if self.show_login() != 1:
                    self.logger.info("Login cancelled")
                    break
                    
                # Show main window
                if not self.show_main():
                    break
                    
                try:
                    # Wait for main window to close
                    self.app.exec()
                except SystemExit:
                    # Handle system exit (from X button)
                    self.logger.info("Application exit requested")
                    return 0
                    
                self.logger.info("Main window closed, returning to login")
            
            # Clean exit
            self.cleanup()
            return 0
            
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