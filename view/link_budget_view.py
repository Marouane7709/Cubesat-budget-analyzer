from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLabel, QLineEdit, QComboBox, QPushButton,
                            QGroupBox, QTableWidget, QTableWidgetItem,
                            QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
import pyqtgraph as pg
from model.link_budget import LinkBudgetCalculator
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import os
from pathlib import Path

class LinkBudgetView(QWidget):
    def __init__(self):
        super().__init__()
        self.calculator = LinkBudgetCalculator()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the link budget UI components."""
        layout = QVBoxLayout(self)
        
        # Input form
        input_group = QGroupBox("Link Budget Parameters")
        form_layout = QFormLayout()
        
        # Frequency input
        self.frequency_input = QLineEdit()
        self.frequency_input.setValidator(QDoubleValidator(0.0, 100.0, 3))
        self.frequency_input.setText("2.4")  # Default 2.4 GHz
        form_layout.addRow("Frequency (GHz):", self.frequency_input)
        
        # Transmit power input
        self.tx_power_input = QLineEdit()
        self.tx_power_input.setValidator(QDoubleValidator(0.0, 100.0, 1))
        self.tx_power_input.setText("30.0")  # Default 30 dBm
        form_layout.addRow("Transmit Power (dBm):", self.tx_power_input)
        
        # Antenna gains
        self.tx_gain_input = QLineEdit()
        self.tx_gain_input.setValidator(QDoubleValidator(0.0, 50.0, 1))
        self.tx_gain_input.setText("3.0")  # Default 3 dBi
        form_layout.addRow("Transmit Antenna Gain (dBi):", self.tx_gain_input)
        
        self.rx_gain_input = QLineEdit()
        self.rx_gain_input.setValidator(QDoubleValidator(0.0, 50.0, 1))
        self.rx_gain_input.setText("3.0")  # Default 3 dBi
        form_layout.addRow("Receive Antenna Gain (dBi):", self.rx_gain_input)
        
        # Path loss
        self.path_loss_input = QLineEdit()
        self.path_loss_input.setValidator(QDoubleValidator(0.0, 200.0, 1))
        self.path_loss_input.setText("140.0")  # Default 140 dB
        form_layout.addRow("Path Loss (dB):", self.path_loss_input)
        
        # Propagation model
        self.prop_model_combo = QComboBox()
        self.prop_model_combo.addItems(self.calculator.propagation_models)
        form_layout.addRow("Propagation Model:", self.prop_model_combo)
        
        input_group.setLayout(form_layout)
        layout.addWidget(input_group)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.results_table)
        
        # Charts
        chart_layout = QHBoxLayout()
        
        self.margin_chart = pg.PlotWidget()
        self.margin_chart.setTitle("Link Margin")
        self.margin_chart.setLabel('left', 'Margin (dB)')
        self.margin_chart.setLabel('bottom', 'Time')
        chart_layout.addWidget(self.margin_chart)
        
        self.ber_chart = pg.PlotWidget()
        self.ber_chart.setTitle("Bit Error Rate")
        self.ber_chart.setLabel('left', 'BER')
        self.ber_chart.setLabel('bottom', 'Time')
        self.ber_chart.setLogMode(False, True)  # Log scale for y-axis
        chart_layout.addWidget(self.ber_chart)
        
        layout.addLayout(chart_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate)
        button_layout.addWidget(self.calculate_button)
        
        self.export_pdf_button = QPushButton("Export PDF")
        self.export_pdf_button.clicked.connect(self.export_pdf)
        button_layout.addWidget(self.export_pdf_button)
        
        layout.addLayout(button_layout)
        
    def calculate(self):
        """Calculate link budget and update UI."""
        try:
            # Get input values
            frequency = float(self.frequency_input.text()) * 1e9  # Convert to Hz
            tx_power = float(self.tx_power_input.text())
            tx_gain = float(self.tx_gain_input.text())
            rx_gain = float(self.rx_gain_input.text())
            path_loss = float(self.path_loss_input.text())
            prop_model = self.prop_model_combo.currentText()
            
            # Calculate results
            result = self.calculator.calculate(
                frequency=frequency,
                tx_power=tx_power,
                tx_antenna_gain=tx_gain,
                rx_antenna_gain=rx_gain,
                path_loss=path_loss,
                propagation_model=prop_model
            )
            
            # Update results table
            self.results_table.setRowCount(4)
            self.results_table.setItem(0, 0, QTableWidgetItem("Received Power"))
            self.results_table.setItem(0, 1, QTableWidgetItem(f"{result.received_power:.1f} dBm"))
            self.results_table.setItem(1, 0, QTableWidgetItem("Carrier-to-Noise Ratio"))
            self.results_table.setItem(1, 1, QTableWidgetItem(f"{result.carrier_to_noise:.1f} dB"))
            self.results_table.setItem(2, 0, QTableWidgetItem("Bit Error Rate"))
            self.results_table.setItem(2, 1, QTableWidgetItem(f"{result.bit_error_rate:.2e}"))
            self.results_table.setItem(3, 0, QTableWidgetItem("Link Margin"))
            self.results_table.setItem(3, 1, QTableWidgetItem(f"{result.margin:.1f} dB"))
            
            # Update charts
            self.update_charts(result)
            
            # Show warnings if any
            if result.margin < 0:
                QMessageBox.warning(
                    self,
                    "Warning",
                    f"Negative link margin: {result.margin:.1f} dB"
                )
                
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Invalid input: {str(e)}")
        except NotImplementedError as e:
            QMessageBox.information(self, "Not Implemented", str(e))
            
    def update_charts(self, result):
        """Update the margin and BER charts."""
        # Clear existing plots
        self.margin_chart.clear()
        self.ber_chart.clear()
        
        # Add margin plot
        self.margin_chart.plot([0, 1], [result.margin, result.margin], pen='g')
        
        # Add BER plot
        self.ber_chart.plot([0, 1], [result.bit_error_rate, result.bit_error_rate], pen='r')
        
    def export_pdf(self):
        """Export the link budget analysis to PDF."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export PDF",
            str(Path.home()),
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            try:
                c = canvas.Canvas(file_path, pagesize=letter)
                width, height = letter
                
                # Title
                c.setFont("Helvetica-Bold", 16)
                c.drawString(50, height - 50, "Link Budget Analysis")
                
                # Input parameters
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, height - 100, "Input Parameters:")
                c.setFont("Helvetica", 10)
                
                y = height - 120
                params = [
                    ("Frequency", f"{self.frequency_input.text()} GHz"),
                    ("Transmit Power", f"{self.tx_power_input.text()} dBm"),
                    ("Transmit Antenna Gain", f"{self.tx_gain_input.text()} dBi"),
                    ("Receive Antenna Gain", f"{self.rx_gain_input.text()} dBi"),
                    ("Path Loss", f"{self.path_loss_input.text()} dB"),
                    ("Propagation Model", self.prop_model_combo.currentText())
                ]
                
                for param, value in params:
                    c.drawString(70, y, f"{param}: {value}")
                    y -= 20
                
                # Results table
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y - 20, "Results:")
                
                data = []
                for row in range(self.results_table.rowCount()):
                    param = self.results_table.item(row, 0).text()
                    value = self.results_table.item(row, 1).text()
                    data.append([param, value])
                
                t = Table(data)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                t.wrapOn(c, width - 100, height)
                t.drawOn(c, 50, y - 120)
                
                c.save()
                QMessageBox.information(self, "Success", "PDF exported successfully")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export PDF: {str(e)}")
                
    def get_config(self):
        """Get current configuration as a dictionary."""
        return {
            'frequency': self.frequency_input.text(),
            'tx_power': self.tx_power_input.text(),
            'tx_gain': self.tx_gain_input.text(),
            'rx_gain': self.rx_gain_input.text(),
            'path_loss': self.path_loss_input.text(),
            'propagation_model': self.prop_model_combo.currentText()
        }
        
    def set_config(self, config):
        """Set configuration from a dictionary."""
        self.frequency_input.setText(config['frequency'])
        self.tx_power_input.setText(config['tx_power'])
        self.tx_gain_input.setText(config['tx_gain'])
        self.rx_gain_input.setText(config['rx_gain'])
        self.path_loss_input.setText(config['path_loss'])
        self.prop_model_combo.setCurrentText(config['propagation_model']) 