from model.link_budget_model import LinkBudgetModel, LinkBudgetResult
from view.link_budget_view import LinkBudgetView
from PyQt6.QtCore import QObject, pyqtSignal
from pathlib import Path
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import numpy as np
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import math

class LinkBudgetController(QObject):
    """Controller class for link budget calculations."""
    
    # Signals for view updates
    calculation_complete = pyqtSignal(dict)
    visualization_updated = pyqtSignal()
    report_generated = pyqtSignal(str)
    
    def __init__(self, model: LinkBudgetModel, view: LinkBudgetView):
        """Initialize the controller with model and view instances."""
        super().__init__()
        self._model = model
        self._view = view
        
        # Connect signals
        self._view.calculate_clicked.connect(self.calculate_link_budget)
        self._view.generate_pdf_clicked.connect(self.generate_pdf_report)
        self._view.parameter_changed.connect(self.update_parameter)
        
        # Connect controller signals to view slots
        self.calculation_complete.connect(lambda result: self._view.update_results(result))
        self.report_generated.connect(self._view.show_report_success)
    
    def calculate_link_budget(self) -> None:
                
        #Core function for link budget calculations including free space loss,
        # received power, noise power, SNR, and link margin

        """Calculate link budget and update view."""
        try:
            print("Starting link budget calculation...")
            view_params = self._get_parameters_from_view()
            
            # Map view parameters to model parameters
            model_params = {
                'transmit_power': view_params['tx_power_dbm'],
                'transmit_antenna_gain': view_params['tx_gain_dbi'],
                'receive_antenna_gain': view_params['rx_gain_dbi'],
                'frequency': view_params['frequency_hz'],
                'distance': view_params['distance_km'],
                'system_temperature': view_params['temperature_k'],
                'receiver_bandwidth': view_params['bandwidth_hz'],
                'required_snr': view_params['required_ebno_db'],
                'atmospheric_loss': view_params['rx_implementation_loss_db']
            }
            
            self._model.set_parameters(model_params)
            result = self._model.calculate()
            
            # Convert result to dictionary format expected by view
            eirp = model_params['transmit_power'] + model_params['transmit_antenna_gain']
            view_result = {
                'eirp': f"{eirp:.1f} dBW",
                'path_loss': f"{result.noise_power:.1f} dB",
                'received_power': f"{result.received_power:.1f} dBW",
                'cn0': f"{result.carrier_to_noise:.1f} dB-Hz",
                'link_margin': f"{result.link_margin:.1f} dB"
            }
            print(f"View result prepared: {view_result}")
            
            # Update view directly
            self._view.update_results(view_result)
            
        except ValueError as e:
            print(f"ValueError occurred: {str(e)}")
            self._view.show_error("Invalid Input", str(e))
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            self._view.show_error("Calculation Error", f"An error occurred: {str(e)}")
    
    def _get_parameters_from_view(self) -> dict:
        """Get parameters directly from view's get_parameters method."""
        return self._view.get_parameters()
    
    def update_visualization(self) -> None:
        """Update visualization based on current parameters."""
        try:
            param_type = self._view.viz_controls.param_combo.currentText()
            start = self._view.viz_controls.start_value.value()
            end = self._view.viz_controls.end_value.value()
            step = self._view.viz_controls.step_value.value()
            modulation = self._view.viz_controls.mod_combo.currentText()
            
            # Generate x values and calculate margins
            x_values = np.arange(start, end + step, step)
            margins = [
                self._model.calculate_margin_vs_parameter(
                    param_type, x, modulation if param_type == "Modulation" else None
                )
                for x in x_values
            ]
            
            # Update visualization
            self.visualization_updated.emit()
            
        except Exception as e:
            self._view.show_error("Visualization Error", str(e))
    
    def on_parameter_changed(self, parameter: str) -> None:
        """Handle parameter selection change."""
        self._view.viz_controls.update_ranges(parameter)
        self._view.viz_controls.mod_combo.setEnabled(parameter == "Modulation")
    
    def generate_pdf_report(self):
        """Generate PDF report with link budget results."""
        try:
            # Get the current parameters and the results from the last calculations
            view_params = self._get_parameters_from_view()
            
            # Map view parameters to model parameters (same as in calculate_link_budget)
            params = {
                'transmit_power': view_params['tx_power_dbm'],
                'transmit_antenna_gain': view_params['tx_gain_dbi'],
                'receive_antenna_gain': view_params['rx_gain_dbi'],
                'frequency': view_params['frequency_hz'],
                'distance': view_params['distance_km'],
                'system_temperature': view_params['temperature_k'],
                'receiver_bandwidth': view_params['bandwidth_hz'],
                'required_snr': view_params['required_ebno_db'],
                'atmospheric_loss': view_params['rx_implementation_loss_db']
            }
            
            self._model.set_parameters(params)
            result = self._model.calculate()

            
            file_path = self._view.get_save_filename()
            if not file_path:
                return

            # we ensure the file has a .pdf extension
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'

            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.units import inch
            from datetime import datetime

            # Create the PDF document
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30
            )
            elements.append(Paragraph("Link Budget Analysis Report", title_style))
            elements.append(Spacer(1, 0.2 * inch))

            # Date and Time
            elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            elements.append(Spacer(1, 0.2 * inch))

            # Input Parameters Table
            input_data = [
                ["Parameter", "Value"],
                ["Transmit Power", f"{view_params['tx_power_dbm']:.1f} dBm"],
                ["Transmitter Gain", f"{view_params['tx_gain_dbi']:.1f} dBi"],
                ["Receiver Gain", f"{view_params['rx_gain_dbi']:.1f} dBi"],
                ["Frequency", f"{view_params['frequency_hz']/1e6:.1f} MHz"],
                ["Distance", f"{view_params['distance_km']:.1f} km"],
                ["System Temperature", f"{view_params['temperature_k']:.1f} K"],
                ["Bandwidth", f"{view_params['bandwidth_hz']/1e3:.1f} kHz"],
                ["Required Eb/No", f"{view_params['required_ebno_db']:.1f} dB"],
                ["Implementation Loss", f"{view_params['rx_implementation_loss_db']:.1f} dB"]
            ]

            # Results Table
            results_data = [
                ["Metric", "Value"],
                ["EIRP", f"{view_params['tx_power_dbm'] + view_params['tx_gain_dbi']:.1f} dBW"],
                ["Path Loss", f"{result.noise_power:.1f} dB"],
                ["Received Power", f"{result.received_power:.1f} dBW"],
                ["C/N₀", f"{result.carrier_to_noise:.1f} dB-Hz"],
                ["Link Margin", f"{result.link_margin:.1f} dB"]
            ]

            # Create and style tables
            def create_styled_table(data, title):
                elements.append(Paragraph(title, styles['Heading2']))
                elements.append(Spacer(1, 0.1 * inch))
                
                t = Table(data, colWidths=[2.5*inch, 2.5*inch])
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
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.2 * inch))

            create_styled_table(input_data, "Input Parameters")
            create_styled_table(results_data, "Link Budget Results")

            # Build PDF
            doc.build(elements)
            
            # Emit success signal with file path
            self.report_generated.emit(file_path)

        except Exception as e:
            print(f"PDF Generation Error: {str(e)}")  # Add debug print
            self._view.show_error("PDF Generation Error", str(e)) 
    
    def update_parameter(self, name: str, value: float):
        """Update a model parameter when changed in the view."""
        try:
            if hasattr(self._model, name):
                setattr(self._model, name, value)
                print(f"Updated {name} to {value}")
        except Exception as e:
            print(f"Error updating parameter {name}: {str(e)}") 