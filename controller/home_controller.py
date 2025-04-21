from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QPushButton
from view.home_view import HomeWindow

class HomeController(QObject):
    navigate_to_login = pyqtSignal()
    navigate_to_module = pyqtSignal(str)
    quit_application = pyqtSignal()

    def __init__(self, view: HomeWindow):
        super().__init__()
        self.view = view
        self.setup_connections()

    def setup_connections(self):
        # Connect back button if it exists
        back_button = self.view.findChild(QPushButton, "back_button")
        if back_button:
            back_button.clicked.connect(self.navigate_to_login.emit)

        # Connect analysis buttons
        for btn in self.view.findChildren(QPushButton, "analysis_button"):
            module = btn.property("data-module")
            if module:  # Only connect if module property exists
                btn.clicked.connect(lambda checked, m=module: self.open_module(m))

        # Connect window closing signal
        self.view.window_closing.connect(self.quit_application.emit)

    def open_module(self, module_name: str):
        """Open the specified analysis module."""
        if module_name == "link_budget_analysis":
            self.navigate_to_module.emit("link_budget")
        elif module_name == "data_budget_analysis":
            self.navigate_to_module.emit("data_budget")
        # Add more module mappings as needed 