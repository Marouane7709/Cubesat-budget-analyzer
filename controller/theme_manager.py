from PyQt6.QtCore import QFile, QObject, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
from pathlib import Path

class ThemeManager(QObject):
    # Signal emitted when theme changes
    theme_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_theme = 'light'
        self.theme_path = Path(__file__).parent.parent / 'qss'
        
    def apply_theme(self, theme: str):
        """Apply the specified theme to the application."""
        self.current_theme = theme
        style_file_path = self.theme_path / f'{theme}.qss'
        
        try:
            with open(style_file_path, 'r', encoding='utf-8') as f:
                style_sheet = f.read()
                
            # Apply the stylesheet
            from PyQt6.QtWidgets import QApplication
            QApplication.instance().setStyleSheet(style_sheet)
            
            # Apply palette for system colors
            palette = QPalette()
            if theme == 'dark':
                palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
                palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
                palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
                palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
                palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
                palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
                palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
                palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
                palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
                palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
                palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
                palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
                palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
            else:  # light theme
                palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
                palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
                palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
                palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
                palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
                palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
                palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
                palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
                palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
                palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
                palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
                palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
                palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
            
            QApplication.instance().setPalette(palette)
            
            # Emit theme changed signal
            self.theme_changed.emit(theme)
            
        except Exception as e:
            print(f"Error loading theme {theme}: {str(e)}")
            
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.apply_theme('dark' if self.current_theme == 'light' else 'light') 