from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QSplitter, QScrollArea, QSizePolicy
from PyQt6.QtCore import Qt

class Card(QFrame):
    """A styled card widget with consistent theming."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        
        # Set up layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)
        
        # Make scrollable
        self.scroll = QScrollArea()
        self.scroll.setWidget(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Style scroll bar
        self.scroll.setStyleSheet("""
            QScrollBar:vertical {
                width: 6px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: palette(Mid);
                border-radius: 3px;
            }
            QScrollBar:vertical:hover {
                width: 8px;
            }
        """)

class ResizableCardContainer(QWidget):
    """A container with two cards that can be resized using a splitter."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create cards
        self.left_card = Card()
        self.right_card = Card()
        
        # Add cards to splitter
        self.splitter.addWidget(self.left_card.scroll)
        self.splitter.addWidget(self.right_card.scroll)
        
        # Set stretch factors
        self.splitter.setStretchFactor(0, 3)  # Parameters card gets more space
        self.splitter.setStretchFactor(1, 1)  # Results card gets less space
        
        layout.addWidget(self.splitter)
        
    def resizeEvent(self, event):
        """Handle resize events to adjust splitter orientation."""
        super().resizeEvent(event)
        if self.width() < 1000:
            self.splitter.setOrientation(Qt.Orientation.Vertical)
        else:
            self.splitter.setOrientation(Qt.Orientation.Horizontal) 