from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLabel, QLineEdit, QComboBox, QPushButton,
                            QGroupBox, QTableWidget, QTableWidgetItem,
                            QMessageBox, QFileDialog, QTextEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
import pyqtgraph as pg
import pandas as pd
from model.data_budget import DataBudgetCalculator
import os
from pathlib import Path

class DataBudgetView(QWidget):
    def __init__(self):
        super().__init__()
        self.calculator = DataBudgetCalculator()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the data budget UI components."""
        layout = QVBoxLayout(self)
        
        # Input form
        input_group = QGroupBox("Data Budget Parameters")
        form_layout = QFormLayout()
        
        # Data rate input
        self.data_rate_input = QLineEdit()
        self.data_rate_input.setValidator(QDoubleValidator(0.0, 1000.0, 1))
        self.data_rate_input.setText("1.0")  # Default 1 Mbps
        form_layout.addRow("Data Rate (Mbps):", self.data_rate_input)
        
        # Duty cycle input
        self.duty_cycle_input = QLineEdit()
        self.duty_cycle_input.setValidator(QDoubleValidator(0.0, 100.0, 1))
        self.duty_cycle_input.setText("100.0")  # Default 100%
        form_layout.addRow("Duty Cycle (%):", self.duty_cycle_input)
        
        # Downlink parameters
        self.downlink_rate_input = QLineEdit()
        self.downlink_rate_input.setValidator(QDoubleValidator(0.0, 1000.0, 1))
        self.downlink_rate_input.setText("10.0")  # Default 10 Mbps
        form_layout.addRow("Downlink Rate (Mbps):", self.downlink_rate_input)
        
        self.downlink_duration_input = QLineEdit()
        self.downlink_duration_input.setValidator(QDoubleValidator(0.0, 24.0, 1))
        self.downlink_duration_input.setText("4.0")  # Default 4 hours
        form_layout.addRow("Downlink Duration (hours/day):", self.downlink_duration_input)
        
        # Storage parameters
        self.storage_capacity_input = QLineEdit()
        self.storage_capacity_input.setValidator(QDoubleValidator(0.0, 10000.0, 1))
        self.storage_capacity_input.setText("1000.0")  # Default 1000 MB
        form_layout.addRow("Storage Capacity (MB):", self.storage_capacity_input)
        
        self.current_storage_input = QLineEdit()
        self.current_storage_input.setValidator(QDoubleValidator(0.0, 10000.0, 1))
        self.current_storage_input.setText("0.0")  # Default 0 MB
        form_layout.addRow("Current Storage (MB):", self.current_storage_input)
        
        input_group.setLayout(form_layout)
        layout.addWidget(input_group)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.results_table)
        
        # Recommendations
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        layout.addWidget(self.recommendations_text)
        
        # Charts
        chart_layout = QHBoxLayout()
        
        self.storage_chart = pg.PlotWidget()
        self.storage_chart.setTitle("Storage Usage")
        self.storage_chart.setLabel('left', 'Storage (MB)')
        self.storage_chart.setLabel('bottom', 'Time (days)')
        chart_layout.addWidget(self.storage_chart)
        
        self.backlog_chart = pg.PlotWidget()
        self.backlog_chart.setTitle("Data Backlog")
        self.backlog_chart.setLabel('left', 'Backlog (MB)')
        self.backlog_chart.setLabel('bottom', 'Time (days)')
        chart_layout.addWidget(self.backlog_chart)
        
        layout.addLayout(chart_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate)
        button_layout.addWidget(self.calculate_button)
        
        self.export_csv_button = QPushButton("Export CSV")
        self.export_csv_button.clicked.connect(self.export_csv)
        button_layout.addWidget(self.export_csv_button)
        
        self.export_excel_button = QPushButton("Export Excel")
        self.export_excel_button.clicked.connect(self.export_excel)
        button_layout.addWidget(self.export_excel_button)
        
        layout.addLayout(button_layout)
        
    def calculate(self):
        """Calculate data budget and update UI."""
        try:
            # Get input values
            data_rate = float(self.data_rate_input.text()) * 1e6  # Convert to bps
            duty_cycle = float(self.duty_cycle_input.text())
            downlink_rate = float(self.downlink_rate_input.text()) * 1e6  # Convert to bps
            downlink_duration = float(self.downlink_duration_input.text())
            storage_capacity = float(self.storage_capacity_input.text())
            current_storage = float(self.current_storage_input.text())
            
            # Calculate results
            result = self.calculator.calculate(
                data_rate=data_rate,
                duty_cycle=duty_cycle,
                downlink_rate=downlink_rate,
                downlink_duration=downlink_duration,
                storage_capacity=storage_capacity,
                current_storage=current_storage
            )
            
            # Update results table
            self.results_table.setRowCount(5)
            self.results_table.setItem(0, 0, QTableWidgetItem("Data Generated"))
            self.results_table.setItem(0, 1, QTableWidgetItem(f"{result.data_generated:.1f} MB/day"))
            self.results_table.setItem(1, 0, QTableWidgetItem("Downlink Capacity"))
            self.results_table.setItem(1, 1, QTableWidgetItem(f"{result.downlink_capacity:.1f} MB/day"))
            self.results_table.setItem(2, 0, QTableWidgetItem("Storage Required"))
            self.results_table.setItem(2, 1, QTableWidgetItem(f"{result.storage_required:.1f} MB"))
            self.results_table.setItem(3, 0, QTableWidgetItem("Storage Available"))
            self.results_table.setItem(3, 1, QTableWidgetItem(f"{result.storage_available:.1f} MB"))
            self.results_table.setItem(4, 0, QTableWidgetItem("Backlog"))
            self.results_table.setItem(4, 1, QTableWidgetItem(f"{result.backlog:.1f} MB"))
            
            # Update recommendations
            self.recommendations_text.clear()
            if result.recommendations:
                self.recommendations_text.append("Recommendations:")
                for rec in result.recommendations:
                    self.recommendations_text.append(f"• {rec}")
            
            # Update charts
            self.update_charts(result)
            
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Invalid input: {str(e)}")
            
    def update_charts(self, result):
        """Update the storage and backlog charts."""
        # Clear existing plots
        self.storage_chart.clear()
        self.backlog_chart.clear()
        
        # Generate 30-day projection
        days = list(range(31))
        storage = []
        backlog = []
        
        current_storage = float(self.current_storage_input.text())
        daily_accumulation = result.data_generated - result.downlink_capacity
        
        for day in days:
            storage.append(min(current_storage + day * daily_accumulation, 
                             float(self.storage_capacity_input.text())))
            backlog.append(max(0, day * daily_accumulation))
        
        # Add storage plot
        self.storage_chart.plot(days, storage, pen='b')
        
        # Add backlog plot
        self.backlog_chart.plot(days, backlog, pen='r')
        
    def export_csv(self):
        """Export the data budget analysis to CSV."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export CSV",
            str(Path.home()),
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                data = []
                for row in range(self.results_table.rowCount()):
                    param = self.results_table.item(row, 0).text()
                    value = self.results_table.item(row, 1).text()
                    data.append([param, value])
                
                df = pd.DataFrame(data, columns=["Parameter", "Value"])
                df.to_csv(file_path, index=False)
                QMessageBox.information(self, "Success", "CSV exported successfully")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export CSV: {str(e)}")
                
    def export_excel(self):
        """Export the data budget analysis to Excel."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Excel",
            str(Path.home()),
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                data = []
                for row in range(self.results_table.rowCount()):
                    param = self.results_table.item(row, 0).text()
                    value = self.results_table.item(row, 1).text()
                    data.append([param, value])
                
                df = pd.DataFrame(data, columns=["Parameter", "Value"])
                df.to_excel(file_path, index=False)
                QMessageBox.information(self, "Success", "Excel exported successfully")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export Excel: {str(e)}")
                
    def get_config(self):
        """Get current configuration as a dictionary."""
        return {
            'data_rate': self.data_rate_input.text(),
            'duty_cycle': self.duty_cycle_input.text(),
            'downlink_rate': self.downlink_rate_input.text(),
            'downlink_duration': self.downlink_duration_input.text(),
            'storage_capacity': self.storage_capacity_input.text(),
            'current_storage': self.current_storage_input.text()
        }
        
    def set_config(self, config):
        """Set configuration from a dictionary."""
        self.data_rate_input.setText(config['data_rate'])
        self.duty_cycle_input.setText(config['duty_cycle'])
        self.downlink_rate_input.setText(config['downlink_rate'])
        self.downlink_duration_input.setText(config['downlink_duration'])
        self.storage_capacity_input.setText(config['storage_capacity'])
        self.current_storage_input.setText(config['current_storage']) 