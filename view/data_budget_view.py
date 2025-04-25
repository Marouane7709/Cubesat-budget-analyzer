from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QDoubleSpinBox, QMessageBox,
    QGroupBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

class MetricCard(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: palette(Base);
                border-radius: 6px;
                padding: 12px;
            }
            QLabel[class="metric_title"] {
                font: 11pt "Inter";
                color: palette(PlaceholderText);
            }
            QLabel[class="metric_value"] {
                font: 700 18pt "Inter";
                color: palette(Link);
            }
            QLabel[class="metric_unit"] {
                font: 10pt "Inter";
                color: palette(PlaceholderText);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)
        
        self.title = QLabel(title)
        self.title.setProperty("class", "metric_title")
        self.value = QLabel("--")
        self.value.setProperty("class", "metric_value")
        self.unit = QLabel("GB/day")
        self.unit.setProperty("class", "metric_unit")
        
        layout.addWidget(self.title)
        layout.addWidget(self.value)
        layout.addWidget(self.unit)

class DataBudgetView(QWidget):
    # Signals
    calculate_clicked = pyqtSignal(dict)
    parameter_changed = pyqtSignal(str, float)
    
    def __init__(self):
        super().__init__()
        self._build_ui()
        self._make_connections()
    
    def _build_ui(self):
        """Build the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)
        
        # Input Parameters Section
        params_group = QGroupBox("Data Budget Parameters")
        params_group.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        params_layout = QGridLayout()
        params_layout.setColumnMinimumWidth(1, 150)
        params_layout.setHorizontalSpacing(16)
        params_layout.setVerticalSpacing(16)
        
        # Create input fields
        self.payload_rate = self._create_input_field("Payload Data Rate (Mbps):", 0, 1000)
        self.storage_capacity = self._create_input_field("Storage Capacity (GB):", 0, 10000)
        self.downlink_rate = self._create_input_field("Downlink Rate (Mbps):", 0, 1000)
        self.pass_duration = self._create_input_field("Pass Duration (minutes):", 0, 60)
        self.passes_per_day = self._create_input_field("Passes per Day:", 0, 24)
        
        # Add fields to layout
        fields = [
            (0, "Payload Data Rate (Mbps):", self.payload_rate),
            (1, "Storage Capacity (GB):", self.storage_capacity),
            (2, "Downlink Rate (Mbps):", self.downlink_rate),
            (3, "Pass Duration (minutes):", self.pass_duration),
            (4, "Passes per Day:", self.passes_per_day)
        ]
        
        for row, label_text, widget in fields:
            label = QLabel(label_text)
            label.setFont(QFont("Inter", 11))
            params_layout.addWidget(label, row, 0)
            params_layout.addWidget(widget, row, 1)
        
        params_group.setLayout(params_layout)
        main_layout.addWidget(params_group)
        
        # Results Section
        results_layout = QHBoxLayout()
        
        # Create metric cards
        self.data_generated = MetricCard("Data Generated")
        self.downlink_capacity = MetricCard("Downlink Capacity")
        self.storage_backlog = MetricCard("Storage Backlog")
        
        results_layout.addWidget(self.data_generated)
        results_layout.addWidget(self.downlink_capacity)
        results_layout.addWidget(self.storage_backlog)
        
        main_layout.addLayout(results_layout)
        
        # Status and Recommendations
        self.status_label = QLabel()
        self.status_label.setStyleSheet("font: 12pt 'Inter'; color: palette(Text);")
        self.recommendations_label = QLabel()
        self.recommendations_label.setStyleSheet("font: 11pt 'Inter'; color: palette(Text);")
        self.recommendations_label.setWordWrap(True)
        
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.recommendations_label)
        
        # Calculate Button
        self.calculate_button = QPushButton("Calculate Data Budget")
        self.calculate_button.setFont(QFont("Inter", 12))
        self.calculate_button.setMinimumHeight(40)
        self.calculate_button.setStyleSheet("""
            QPushButton {
                background: palette(Button);
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: palette(Highlight);
                color: palette(BrightText);
            }
        """)
        
        main_layout.addWidget(self.calculate_button)
        main_layout.addStretch()
    
    def _create_input_field(self, label: str, min_val: float, max_val: float) -> QDoubleSpinBox:
        """Create a styled input field."""
        field = QDoubleSpinBox()
        field.setRange(min_val, max_val)
        field.setDecimals(2)
        field.setFont(QFont("Inter", 11))
        field.setMinimumHeight(36)
        field.setStyleSheet("""
            QDoubleSpinBox {
                background: palette(Base);
                border: 1px solid palette(Mid);
                border-radius: 4px;
                padding: 4px 8px;
            }
            QDoubleSpinBox:focus {
                border: 2px solid palette(Highlight);
            }
        """)
        return field
    
    def _make_connections(self):
        """Connect signals and slots."""
        self.calculate_button.clicked.connect(self._on_calculate)
        
        # Connect parameter changes
        for field, param in [
            (self.payload_rate, 'payload_data_rate'),
            (self.storage_capacity, 'storage_capacity'),
            (self.downlink_rate, 'downlink_rate'),
            (self.pass_duration, 'pass_duration'),
            (self.passes_per_day, 'passes_per_day')
        ]:
            field.valueChanged.connect(lambda v, p=param: self.parameter_changed.emit(p, v))
    
    def _on_calculate(self):
        """Handle calculate button click."""
        params = {
            'payload_data_rate': self.payload_rate.value(),
            'storage_capacity': self.storage_capacity.value(),
            'downlink_rate': self.downlink_rate.value(),
            'pass_duration': self.pass_duration.value(),
            'passes_per_day': self.passes_per_day.value()
        }
        self.calculate_clicked.emit(params)
    
    def update_results(self, result):
        """Update the display with calculation results."""
        # Update metric cards
        self.data_generated.value.setText(f"{result.total_data_per_day:.2f}")
        self.downlink_capacity.value.setText(f"{result.available_downlink_per_day:.2f}")
        self.storage_backlog.value.setText(f"{result.storage_backlog:.2f}")
        
        # Update status
        self.status_label.setText(result.storage_status)
        
        # Update recommendations
        if result.recommendations:
            self.recommendations_label.setText("\n".join(result.recommendations))
        else:
            self.recommendations_label.setText("No recommendations needed - data budget is balanced.")
        
        # Color code the backlog based on status
        if result.storage_backlog > 0:
            self.storage_backlog.value.setStyleSheet("QLabel { color: #FF4444; }")
        else:
            self.storage_backlog.value.setStyleSheet("QLabel { color: #44FF44; }")
    
    def show_error(self, title: str, message: str):
        """Show error message dialog."""
        QMessageBox.critical(self, title, message) 