import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from controller.theme_manager import ThemeManager
from view.login_view import LoginWindow
from view.main_view import MainWindow
from model.database import init_db, auto_save_timer

def main():
    app = QApplication(sys.argv)
    
    # Initialize database
    init_db()
    
    # Setup theme manager
    theme_manager = ThemeManager()
    theme_manager.apply_theme('light')  # Default theme
    
    # Show login window
    login_window = LoginWindow(theme_manager)
    if login_window.exec() == 1:  # Login successful
        main_window = MainWindow(theme_manager)
        main_window.show()
        
        # Start auto-save timer
        auto_save_timer.start(300000)  # 5 minutes in milliseconds
        
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == '__main__':
    main() 