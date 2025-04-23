from PyQt6.QtCore import QFile, QObject, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication
from pathlib import Path

class ThemeView(QObject):
    """View class for managing application themes."""
    
    # Signal emitted when theme changes
    theme_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_theme = 'light'
        self.theme_path = Path(__file__).parent.parent / 'qss'
        
    def apply_theme(self, theme: str):
        """Apply the specified theme to the application."""
        self.current_theme = theme
        
        # Apply palette
        palette = QPalette()
        if theme == 'dark':
            # Dark theme colors
            window = QColor("#262626")
            base = QColor("#1E1E1E")
            alt_base = QColor("#2D2D2D")
            text = QColor("#FFFFFF")
            disabled_text = QColor("#9E9E9E")
            highlight = QColor("#4CAF50")
            highlight_text = QColor("#FFFFFF")
            button = QColor("#424242")
            button_text = QColor("#FFFFFF")
            link = QColor("#2196F3")
        else:
            # Light theme colors
            window = QColor("#F4F4F4")
            base = QColor("#FFFFFF")
            alt_base = QColor("#F8F8F8")
            text = QColor("#212121")
            disabled_text = QColor("#9E9E9E")
            highlight = QColor("#4CAF50")
            highlight_text = QColor("#FFFFFF")
            button = QColor("#E0E0E0")
            button_text = QColor("#212121")
            link = QColor("#1976D2")
        
        # Set palette colors
        palette.setColor(QPalette.ColorRole.Window, window)
        palette.setColor(QPalette.ColorRole.Base, base)
        palette.setColor(QPalette.ColorRole.AlternateBase, alt_base)
        palette.setColor(QPalette.ColorRole.WindowText, text)
        palette.setColor(QPalette.ColorRole.Text, text)
        palette.setColor(QPalette.ColorRole.PlaceholderText, disabled_text)
        palette.setColor(QPalette.ColorRole.Button, button)
        palette.setColor(QPalette.ColorRole.ButtonText, button_text)
        palette.setColor(QPalette.ColorRole.Highlight, highlight)
        palette.setColor(QPalette.ColorRole.HighlightedText, highlight_text)
        palette.setColor(QPalette.ColorRole.Link, link)
        
        # Apply palette
        QApplication.instance().setPalette(palette)
        
        # Load and apply theme stylesheet
        style_file_path = self.theme_path / f'{theme}.qss'
        try:
            with open(style_file_path, 'r', encoding='utf-8') as f:
                style_sheet = f.read()
                
            # Add modern styling
            style_sheet += """
                /* Typography */
                QLabel[title="true"] {
                    font: 600 16pt "Inter";
                    margin-bottom: 8px;
                }
                QLabel {
                    font: 13pt "Inter Medium";
                }
                QLabel[helper="true"] {
                    font: 11pt "Inter";
                    color: #9E9E9E;
                }
                
                /* Input Controls */
                QSpinBox, QDoubleSpinBox, QComboBox {
                    min-height: 36px;
                    border-radius: 6px;
                    padding: 4px 6px;
                }
                
                QSpinBox[state="ok"], QDoubleSpinBox[state="ok"] {
                    border: 2px solid #4CAF50;
                }
                QSpinBox[state="bad"], QDoubleSpinBox[state="bad"] {
                    border: 2px solid #FF5252;
                }
                
                /* Action Buttons */
                QPushButton {
                    min-height: 44px;
                    border-radius: 6px;
                    font: bold 14pt "Inter";
                    padding: 0 16px;
                }
                QPushButton:hover {
                    transform: translateY(-1px);
                }
                QPushButton#calculateButton {
                    background: #4CAF50;
                    color: white;
                }
                QPushButton#pdfButton {
                    background: #2196F3;
                    color: white;
                }
                QPushButton#backButton {
                    background: #7E7E7E;
                    color: white;
                }
                
                /* Cards */
                #card {
                    background: palette(AlternateBase);
                    border-radius: 8px;
                    border: 1px solid palette(Mid);
                }
            """
            
            QApplication.instance().setStyleSheet(style_sheet)
            
            # Emit theme changed signal
            self.theme_changed.emit(theme)
            
        except Exception as e:
            print(f"Error loading theme {theme}: {str(e)}")
            
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.apply_theme('dark' if self.current_theme == 'light' else 'light') 