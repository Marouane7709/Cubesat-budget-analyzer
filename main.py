import sys
from PyQt6.QtWidgets import QApplication
from model.link_budget_model import LinkBudgetModel
from view.link_budget_view import LinkBudgetView
from controller.link_budget_controller import LinkBudgetController

def main():
    """Initialize and run the link budget calculator application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Create MVC components
    model = LinkBudgetModel()
    view = LinkBudgetView()
    controller = LinkBudgetController(model, view)
    
    # Show the main window
    view.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 