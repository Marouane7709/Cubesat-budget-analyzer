from PyQt6.QtCore import QObject
from model.data_budget_model import DataBudgetModel
from view.data_budget_view import DataBudgetView

class DataBudgetController(QObject):
    """Controller class for data budget calculations."""
    
    def __init__(self):
        super().__init__()
        self.model = DataBudgetModel()
        self.view = DataBudgetView()
        
        # Connect signals
        self.view.calculate_clicked.connect(self._handle_calculate)
        self.view.parameter_changed.connect(self._handle_parameter_change)
    
    def _handle_calculate(self, params):
        """Handle calculation request from view."""
        try:
            self.model.set_parameters(params)
            result = self.model.calculate()
            self.view.update_results(result)
        except ValueError as e:
            self.view.show_error("Calculation Error", str(e))
    
    def _handle_parameter_change(self, param_name: str, value: float):
        """Handle parameter changes from view."""
        try:
            self.model.set_parameters({param_name: value})
        except ValueError as e:
            self.view.show_error("Input Error", str(e))
    
    def get_view(self) -> DataBudgetView:
        """Return the view instance."""
        return self.view 