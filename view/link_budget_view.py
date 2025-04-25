from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter,
    QLabel, QComboBox, QPushButton, QDoubleSpinBox, QSizePolicy, QGroupBox, QFrame, QScrollArea,
    QTabWidget, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QPalette, QColor
import numpy as np
from scipy.special import erfc
import pyqtgraph as pg
import math
import sys

class ParameterCard(QGroupBox):
    def __init__(self, title: str, fields: list, parent=None):
        super().__init__(title, parent)
        self.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        self.setStyleSheet("""
            QGroupBox {
                background: palette(AlternateBase);
                border: 1px solid palette(Dark);
                border-radius: 6px;
                margin-top: 16px;
                padding: 24px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 12px;
                color: palette(WindowText);
            }
            QDoubleSpinBox, QComboBox {
                background: palette(Base);
                border: 1px solid palette(Mid);
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 36px;
            }
            QDoubleSpinBox {
                min-width: 120px;
            }
            QComboBox {
                min-width: 80px;
            }
            QDoubleSpinBox:focus, QComboBox:focus {
                border: 2px solid palette(Highlight);
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 16px;
                border: none;
                background: transparent;
            }
            QLabel {
                color: palette(WindowText);
                padding-left: 0;
            }
        """)
        
        grid = QGridLayout()
        grid.setContentsMargins(0, 8, 0, 0)
        grid.setColumnMinimumWidth(0, 140)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(12)
        
        for row, (label_text, widgets) in enumerate(fields):
            # Create and configure label
            label = QLabel(label_text)
            label.setFont(QFont("Inter", 11))
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            grid.addWidget(label, row, 0)
            
            if isinstance(widgets, list):
                # For value + unit pairs
                value_widget = widgets[0]
                unit_widget = widgets[1]
                
                # Configure value widget
                value_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                grid.addWidget(value_widget, row, 1)
                
                # Configure unit widget
                unit_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                unit_widget.setFixedWidth(80)
                grid.addWidget(unit_widget, row, 2)
            else:
                # For single value inputs
                widgets.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                grid.addWidget(widgets, row, 1, 1, 2)  # Span across unit column
        
        self.setLayout(grid)

class MetricTile(QFrame):
    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: palette(Base);
                border-radius: 6px;
                padding: 12px;
            }
            QLabel[class="metric_label"] {
                font: 11pt "Inter";
                color: palette(PlaceholderText);
            }
            QLabel[class="metric_value"] {
                font: 700 18pt "Inter";
                color: #4CAF50;
            }
        """)
        v = QVBoxLayout(self)
        v.setContentsMargins(12, 12, 12, 12)
        v.setSpacing(4)
        
        self.label = QLabel(label)
        self.label.setProperty("class", "metric_label")
        self.value = QLabel("--")
        self.value.setProperty("class", "metric_value")
        
        v.addWidget(self.label)
        v.addWidget(self.value)

class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create pyqtgraph plot with enhanced styling
        self.pg_plot = pg.PlotWidget()
        self.pg_plot.setBackground('w')
        self.pg_plot.showGrid(x=True, y=True, alpha=0.3)
        self.pg_plot.setLabel('left', 'Link Margin', units='dB', color='k')
        self.pg_plot.setLabel('bottom', 'Parameter Value', color='k')
        
        # Style the plot
        self.pg_plot.getAxis('left').setPen(pg.mkPen(color='k', width=1))
        self.pg_plot.getAxis('bottom').setPen(pg.mkPen(color='k', width=1))
        self.pg_plot.getAxis('left').setTextPen(pg.mkPen(color='k'))
        self.pg_plot.getAxis('bottom').setTextPen(pg.mkPen(color='k'))
        
        # Add plot to layout
        layout.addWidget(self.pg_plot)
        
        # Store current curves
        self.pg_curves = []
        
        # Setup controls
        controls = QHBoxLayout()
        controls.setContentsMargins(12, 12, 12, 12)
        controls.setSpacing(12)
        
        # Plot type selector
        self.plot_type = QComboBox()
        self.plot_type.addItems([
            "BER vs Eb/N0 [dB]",
            "Link Margin vs. Distance",
            "Link Margin vs. Frequency"
        ])
        self.plot_type.setMinimumHeight(36)
        
        # Modulation scheme selector
        self.modulation = QComboBox()
        self.modulation.addItems(["BPSK", "QPSK", "8-PSK"])
        self.modulation.setMinimumHeight(36)
        
        # Add controls to layout
        controls.addWidget(QLabel("Plot Type:"))
        controls.addWidget(self.plot_type)
        controls.addWidget(QLabel("Modulation:"))
        controls.addWidget(self.modulation)
        controls.addStretch()
        
        layout.addLayout(controls)
        
        # Connect signals
        self.plot_type.currentTextChanged.connect(self._generate_plot)
        self.modulation.currentTextChanged.connect(self._generate_plot)
        
        # Setup timer for real-time updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_real_time)
        self.update_timer.start(100)  # Update every 100ms

    def _calculate_link_budget(self, params):
        """Calculate link budget using parent's parameters."""
        if not self.parent or not hasattr(self.parent, 'calculate_clicked'):
            raise Exception("Cannot calculate link budget - parent view not accessible")
            
        try:
            # Emit the calculation signal and wait for results
            self.parent.calculate_clicked.emit(params)
            
            # Create a dictionary to store results
            results = {}
            
            # Calculate EIRP
            tx_power_dbm = params['tx_power_dbm']
            tx_gain_dbi = params['tx_gain_dbi']
            eirp = tx_power_dbm + tx_gain_dbi
            results['eirp'] = f"{eirp:.2f} dBm"
            
            # Calculate Path Loss
            freq_hz = params['frequency_hz']
            distance_km = params['distance_km']
            path_loss = 20 * np.log10(4 * np.pi * distance_km * 1000 * freq_hz / 3e8)
            results['path_loss'] = f"{path_loss:.2f} dB"
            
            # Calculate Received Power
            rx_gain_dbi = params['rx_gain_dbi']
            rx_power = eirp - path_loss + rx_gain_dbi
            results['received_power'] = f"{rx_power:.2f} dBm"
            
            # Calculate C/N0
            k = 1.38e-23  # Boltzmann constant
            temp_k = params['temperature_k']
            rx_nf_db = params['rx_noise_figure_db']
            impl_loss_db = params['rx_implementation_loss_db']
            
            n0_dbm = 10 * np.log10(k * temp_k * 1000)  # Convert to dBm/Hz
            cn0 = rx_power - n0_dbm - rx_nf_db - impl_loss_db
            results['cn0'] = f"{cn0:.2f} dB-Hz"
            
            # Calculate Link Margin
            bandwidth_hz = params['bandwidth_hz']
            required_ebno_db = params['required_ebno_db']
            
            # Calculate actual Eb/N0
            ebno = cn0 - 10 * np.log10(bandwidth_hz)
            
            # Calculate margin
            margin = ebno - required_ebno_db
            results['link_margin'] = f"{margin:.2f} dB"
            
            return results
            
        except Exception as e:
            raise Exception(f"Error in link budget calculation: {str(e)}")
            
    def _update_real_time(self):
        """Update real-time plot with current parameters."""
        try:
            # Get current parameters
            if not self.parent or not hasattr(self.parent, 'get_parameters'):
                self.update_timer.stop()
                raise Exception("Parent view not accessible")
                
            params = self.parent.get_parameters()
            if not params:
                return
                
            # Calculate current margin
            result = self._calculate_link_budget(params)
            current_margin = float(result['link_margin'].split()[0])
            
            # Initialize data arrays if no curves exist
            if not self.pg_curves:
                # Create new curve if none exists
                curve = self.pg_plot.plot(
                    x=[1],  # Start with first point
                    y=[current_margin],
                    pen=pg.mkPen(color='#2196F3', width=2)
                )
                self.pg_curves.append(curve)
            else:
                # Get existing data
                curve = self.pg_curves[0]
                x_data, y_data = curve.getData()
                
                if x_data is None or y_data is None:
                    # Reinitialize data if it's None
                    x_data = np.array([1])
                    y_data = np.array([current_margin])
                else:
                    # Add new point
                    x_data = np.append(x_data, len(x_data) + 1)
                    y_data = np.append(y_data, current_margin)
                    
                    # Keep only last 100 points
                    if len(x_data) > 100:
                        x_data = x_data[-100:]
                        y_data = y_data[-100:]
                
                # Update the curve with new data
                curve.setData(x_data, y_data)
            
        except Exception as e:
            # Stop the timer to prevent error spam
            self.update_timer.stop()
            QMessageBox.warning(
                self,
                "Real-time Update Error",
                f"Error updating real-time plot: {str(e)}\nReal-time updates have been stopped."
            )

    def _create_distance_margin_plot(self):
        """Create a plot showing link margin vs distance."""
        try:
            # Clear existing plots
            self.pg_plot.clear()
            self.pg_curves.clear()
            
            # Set labels
            self.pg_plot.setLabel('bottom', 'Distance', units='km')
            self.pg_plot.setLabel('left', 'Link Margin', units='dB')
            
            # Generate distance points (logarithmic scale)
            distances = np.logspace(0, 4, 500)  # 1 km to 10000 km
            margins = []
            
            # Get current parameters from parent view
            if self.parent and hasattr(self.parent, 'get_parameters'):
                params = self.parent.get_parameters()
                base_distance = params['distance_km']
                
                # Calculate margins for each distance
                for d in distances:
                    params['distance_km'] = d
                    try:
                        result = self._calculate_link_budget(params)
                        margin = float(result['link_margin'].split()[0])
                        margins.append(margin)
                    except Exception as e:
                        QMessageBox.warning(
                            self,
                            "Calculation Error",
                            f"Error calculating margin for distance {d} km: {str(e)}"
                        )
                        margins.append(np.nan)
                
                # Restore original distance
                params['distance_km'] = base_distance
            else:
                raise Exception("Cannot access link budget parameters")
            
            # Convert to numpy array for easier handling
            margins = np.array(margins)
            
            # Create main curve
            curve = self.pg_plot.plot(
                distances, margins,
                pen=pg.mkPen(color='#2196F3', width=2),
                name=f"Modulation: {self.modulation.currentText()}"
            )
            self.pg_curves.append(curve)
            
            # Add threshold line at 0 dB
            threshold = self.pg_plot.plot(
                distances, np.zeros_like(distances),
                pen=pg.mkPen(color='#ffcdd2', width=1.5, style=Qt.PenStyle.DashLine),
                name='Minimum Required Margin'
            )
            self.pg_curves.append(threshold)
            
            # Add current operating point
            if base_distance >= distances[0] and base_distance <= distances[-1]:
                current_margin = margins[np.abs(distances - base_distance).argmin()]
                point = self.pg_plot.plot(
                    [base_distance], [current_margin],
                    pen=None,
                    symbol='o',
                    symbolSize=10,
                    symbolBrush='#E91E63',
                    name='Operating Point'
                )
                self.pg_curves.append(point)
                
                # Add text label for current point
                text = pg.TextItem(
                    f'Current: {current_margin:.1f} dB',
                    color='k',
                    anchor=(0, 1)
                )
                text.setPos(base_distance, current_margin)
                self.pg_plot.addItem(text)
            
            # Set log mode for x-axis
            self.pg_plot.setLogMode(x=True, y=False)
            
            # Add legend
            self.pg_plot.addLegend()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Plot Error",
                f"Error creating distance margin plot: {str(e)}"
            )
            raise Exception(f"Error creating distance margin plot: {str(e)}")

    def _create_frequency_margin_plot(self):
        """Create a plot showing link margin vs frequency."""
        try:
            # Clear existing plots
            self.pg_plot.clear()
            self.pg_curves.clear()
            
            # Set labels
            self.pg_plot.setLabel('bottom', 'Frequency', units='GHz')
            self.pg_plot.setLabel('left', 'Link Margin', units='dB')
            
            # Generate frequency points (logarithmic scale)
            frequencies = np.logspace(6, 11, 500)  # 1 MHz to 100 GHz
            margins = []
            
            # Get current parameters from parent view
            if self.parent and hasattr(self.parent, 'get_parameters'):
                params = self.parent.get_parameters()
                base_freq = params['frequency_hz']
                
                # Calculate margins for each frequency
                for f in frequencies:
                    params['frequency_hz'] = f
                    try:
                        result = self._calculate_link_budget(params)
                        margin = float(result['link_margin'].split()[0])
                        margins.append(margin)
                    except Exception as e:
                        QMessageBox.warning(
                            self,
                            "Calculation Error",
                            f"Error calculating margin for frequency {f/1e9:.2f} GHz: {str(e)}"
                        )
                        margins.append(np.nan)
                
                # Restore original frequency
                params['frequency_hz'] = base_freq
            else:
                raise Exception("Cannot access link budget parameters")
            
            # Convert to numpy array for easier handling
            margins = np.array(margins)
            
            # Create main curve
            curve = self.pg_plot.plot(
                frequencies/1e9, margins,
                pen=pg.mkPen(color='#2196F3', width=2),
                name=f"Modulation: {self.modulation.currentText()}"
            )
            self.pg_curves.append(curve)
            
            # Add threshold line at 0 dB
            threshold = self.pg_plot.plot(
                frequencies/1e9, np.zeros_like(frequencies),
                pen=pg.mkPen(color='#ffcdd2', width=1.5, style=Qt.PenStyle.DashLine),
                name='Minimum Required Margin'
            )
            self.pg_curves.append(threshold)
            
            # Add current operating point
            current_freq = base_freq/1e9
            if frequencies[0]/1e9 <= current_freq <= frequencies[-1]/1e9:
                current_margin = margins[np.abs(frequencies/1e9 - current_freq).argmin()]
                point = self.pg_plot.plot(
                    [current_freq], [current_margin],
                    pen=None,
                    symbol='o',
                    symbolSize=10,
                    symbolBrush='#E91E63',
                    name='Operating Point'
                )
                self.pg_curves.append(point)
                
                # Add text label for current point
                text = pg.TextItem(
                    f'Current: {current_margin:.1f} dB',
                    color='k',
                    anchor=(0, 1)
                )
                text.setPos(current_freq, current_margin)
                self.pg_plot.addItem(text)
            
            # Set log mode for x-axis
            self.pg_plot.setLogMode(x=True, y=False)
            
            # Add legend
            self.pg_plot.addLegend()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Plot Error",
                f"Error creating frequency margin plot: {str(e)}"
            )
            raise Exception(f"Error creating frequency margin plot: {str(e)}")
            
    def _create_ber_plot(self):
        """Create a plot showing BER vs Eb/N0 with modern styling."""
        try:
            # Clear existing plots
            self.pg_plot.clear()
            self.pg_curves.clear()
            
            # Set labels
            self.pg_plot.setLabel('bottom', 'Eb/N0', units='dB')
            self.pg_plot.setLabel('left', 'Bit Error Rate (BER)')
            
            # Generate Eb/N0 points
            eb_n0_db = np.linspace(0, 20, 500)
            eb_n0_linear = 10**(eb_n0_db/10)
            
            # Calculate BER for each modulation scheme
            ber_bpsk_qpsk = 0.5 * erfc(np.sqrt(eb_n0_linear))
            ber_8psk = (2/3) * erfc(np.sqrt(3 * eb_n0_linear * np.log2(8) / 8))
            
            # Create curves
            curve1 = self.pg_plot.plot(
                eb_n0_db, ber_bpsk_qpsk,
                pen=pg.mkPen(color='#2196F3', width=2),
                name='BPSK/QPSK'
            )
            curve2 = self.pg_plot.plot(
                eb_n0_db, ber_8psk,
                pen=pg.mkPen(color='#FF9800', width=2),
                name='8-PSK'
            )
            self.pg_curves.extend([curve1, curve2])
            
            # Add threshold lines
            threshold1 = self.pg_plot.plot(
                eb_n0_db, np.full_like(eb_n0_db, 1e-3),
                pen=pg.mkPen(color='#ffcdd2', width=1.5, style=Qt.PenStyle.DashLine)
            )
            threshold2 = self.pg_plot.plot(
                eb_n0_db, np.full_like(eb_n0_db, 1e-5),
                pen=pg.mkPen(color='#c8e6c9', width=1.5, style=Qt.PenStyle.DashLine)
            )
            self.pg_curves.extend([threshold1, threshold2])
            
            # Add current operating point if within range
            current_ebno = self.get_ebno_value()
            if 0 <= current_ebno <= 20:
                current_mod = self.modulation.currentText()
                current_ebno_linear = 10**(current_ebno/10)
                
                if current_mod in ['BPSK', 'QPSK']:
                    current_ber = 0.5 * erfc(np.sqrt(current_ebno_linear))
                    color = '#2196F3'
                else:  # 8-PSK
                    current_ber = (2/3) * erfc(np.sqrt(3 * current_ebno_linear * np.log2(8) / 8))
                    color = '#FF9800'
                
                point = self.pg_plot.plot(
                    [current_ebno], [current_ber],
                    pen=None,
                    symbol='o',
                    symbolSize=10,
                    symbolBrush='#E91E63',
                    name='Operating Point'
                )
                self.pg_curves.append(point)
                
                # Add text label for current point
                text = pg.TextItem(
                    f'Current: {current_ber:.1e}',
                    color='k',
                    anchor=(0, 1)
                )
                text.setPos(current_ebno, current_ber)
                self.pg_plot.addItem(text)
            
            # Set log mode for y-axis
            self.pg_plot.setLogMode(x=False, y=True)
            
            # Set axis ranges
            self.pg_plot.setXRange(0, 20)
            self.pg_plot.setYRange(1e-6, 1)
            
            # Add legend
            self.pg_plot.addLegend()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Plot Error",
                f"Error creating BER plot: {str(e)}"
            )
            raise Exception(f"Error creating BER plot: {str(e)}")
            
    def clear_data_series(self):
        """Clear all data series from the plot."""
        self.pg_plot.clear()
        self.pg_curves.clear()

    def get_ebno_value(self):
        """Get Eb/N0 value from parent view."""
        if self.parent and hasattr(self.parent, 'ebno'):
            return self.parent.ebno.value()
        return 10.0  # Default value if not available

    def _generate_plot(self):
        """Generate the selected plot type."""
        try:
            # Stop the real-time update timer while generating plots
            self.update_timer.stop()
            
            plot_type = self.plot_type.currentText()
            
            if plot_type == "BER vs Eb/N0 [dB]":
                self._create_ber_plot()
            elif plot_type == "Link Margin vs. Distance":
                self._create_distance_margin_plot()
            elif plot_type == "Link Margin vs. Frequency":
                self._create_frequency_margin_plot()
                
            # Restart the timer after plot generation
            self.update_timer.start()
            
        except Exception as e:
            # Keep the timer stopped if there was an error
            self.update_timer.stop()
            QMessageBox.critical(
                self,
                "Plot Error",
                f"Error generating plot: {str(e)}\nReal-time updates have been stopped."
            )

class LinkBudgetView(QWidget):
    # Signals
    calculate_clicked = pyqtSignal(dict)
    generate_pdf_clicked = pyqtSignal(dict)
    parameter_changed = pyqtSignal(str, float)

    def __init__(self):
        super().__init__()
        # Set light theme palette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#F4F4F4"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#FAFAFA"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#202020"))
        self.setPalette(palette)
        
        self._build_ui()
        self._make_connections()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(24)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid palette(mid);
                border-radius: 6px;
                background: palette(base);
            }
            QTabBar::tab {
                background: palette(alternate-base);
                border: 1px solid palette(mid);
                padding: 8px 16px;
                margin-right: 4px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: palette(base);
                border-bottom-color: palette(base);
            }
        """)

        # Create "Parameter Results" tab
        params_tab = QWidget()
        params_layout = QVBoxLayout(params_tab)
        
        # Create input fields and unit selectors with no limitations
        def create_value_unit_pair(units):
            """Helper function to create value-unit pairs without range limitations"""
            value = QDoubleSpinBox()
            value.setRange(float('-inf'), float('inf'))
            value.setDecimals(2)
            value.setMinimumHeight(36)
            value.setAlignment(Qt.AlignmentFlag.AlignRight)
            value.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
            
            unit = QComboBox()
            unit.addItems(units)
            unit.setMinimumHeight(36)
            unit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            unit.setFixedWidth(80)
            
            return value, unit

        # Single value inputs without limitations
        def create_single_value_input(suffix):
            """Helper function to create single value inputs without range limitations"""
            value = QDoubleSpinBox()
            value.setRange(float('-inf'), float('inf'))
            value.setDecimals(2)
            value.setMinimumHeight(36)
            value.setAlignment(Qt.AlignmentFlag.AlignRight)
            value.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
            if suffix:
                value.setSuffix(suffix)
            return value

        # Create all input fields
        self.tx_power, self.tx_power_unit = create_value_unit_pair(["dBm", "W"])
        self.freq, self.freq_unit = create_value_unit_pair(["GHz", "MHz"])
        self.tx_gain = create_single_value_input(" dBi")
        self.rx_gain = create_single_value_input(" dBi")
        self.rx_noise_figure = create_single_value_input(" dB")
        self.rx_implementation_loss = create_single_value_input(" dB")
        self.dist = create_single_value_input(" km")
        self.temp = create_single_value_input(" K")
        self.bw = create_single_value_input(" Hz")
        self.ebno = create_single_value_input(" dB")

        # Move existing parameter and results content to params_tab
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # Left panel with parameter cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setSpacing(16)

        # Create parameter cards
        tx_card = ParameterCard("Transmitter Parameters", [
            ("Transmit Power:", [self.tx_power, self.tx_power_unit]),
            ("Antenna Gain:", self.tx_gain),
        ])

        rx_card = ParameterCard("Receiver Parameters", [
            ("Antenna Gain:", self.rx_gain),
            ("Noise Figure:", self.rx_noise_figure),
            ("Implementation Loss:", self.rx_implementation_loss),
        ])

        ch_card = ParameterCard("Channel Parameters", [
            ("Frequency:", [self.freq, self.freq_unit]),
            ("Distance:", self.dist),
            ("System Temp:", self.temp),
            ("Bandwidth:", self.bw),
            ("Required Eb/No:", self.ebno),
        ])

        lv.addWidget(tx_card)
        lv.addWidget(rx_card)
        lv.addWidget(ch_card)
        lv.addStretch()
        
        scroll.setWidget(left)
        splitter.addWidget(scroll)

        # Right panel with results
        rt = QWidget()
        rv = QVBoxLayout(rt)
        rv.setSpacing(16)

        # Results section
        results_section = QWidget()
        results_layout = QVBoxLayout(results_section)
        results_layout.setSpacing(16)
        results_layout.setContentsMargins(16, 16, 16, 16)
        results_section.setStyleSheet("""
            QWidget {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 8px;
            }
            QLabel {
                color: palette(text);
                border: none;
            }
        """)

        # Results header
        results_label = QLabel("Link Budget Results")
        results_label.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        results_label.setStyleSheet("""
            color: palette(text);
            padding: 4px;
            background: none;
        """)
        results_layout.addWidget(results_label)
        results_layout.addSpacing(8)

        # Results grid
        results_grid = QGridLayout()
        results_grid.setSpacing(16)
        results_grid.setColumnMinimumWidth(0, 150)
        
        # Create result value labels
        self.result_labels = {}
        result_items = [
            ('eirp', 'EIRP:'),
            ('path_loss', 'Path Loss:'),
            ('received_power', 'Received Power:'),
            ('cn0', 'C/N<sub>0</sub>:'),
            ('link_margin', 'Link Margin:')
        ]

        for row, (key, label_text) in enumerate(result_items):
            label = QLabel(label_text)
            label.setFont(QFont("Inter", 11))
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setTextFormat(Qt.TextFormat.RichText)
            label.setStyleSheet("""
                color: palette(text);
                background: none;
                opacity: 0.8;
            """)
            results_grid.addWidget(label, row, 0)

            value = QLabel("--")
            value.setFont(QFont("Inter", 11))
            value.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            value.setStyleSheet("""
                color: #4CAF50;
                font-weight: bold;
                background: none;
            """)
            self.result_labels[key] = value
            results_grid.addWidget(value, row, 1)

        results_layout.addLayout(results_grid)
        results_layout.addStretch()
        rv.addWidget(results_section)
        rv.addStretch()

        splitter.addWidget(rt)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        params_layout.addWidget(splitter)

        # Create "Link Margin Analysis" tab
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        analysis_layout.setContentsMargins(0, 0, 0, 0)
        self.plot_widget = PlotWidget(self)  # Pass self as parent
        analysis_layout.addWidget(self.plot_widget)
        
        # Add tabs
        self.tab_widget.addTab(params_tab, "Parameter Results")
        self.tab_widget.addTab(analysis_tab, "Link Margin Analysis")

        main.addWidget(self.tab_widget)

        # Create action buttons
        btns = QHBoxLayout()
        btns.setSpacing(16)

        self.calculate_button = QPushButton("Calculate Link Budget")
        self.calculate_button.setFixedHeight(40)
        self.calculate_button.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                border-radius: 6px;
                color: white;
                font: 700 14pt 'Inter';
                padding: 0 24px;
            }
            QPushButton:hover {
                background: #66BB6A;
            }
        """)

        self.plot_button = QPushButton("Plot Graph")
        self.plot_button.setFixedHeight(40)
        self.plot_button.setStyleSheet("""
            QPushButton {
                background: #FF9800;
                border-radius: 6px;
                color: white;
                font: 700 14pt 'Inter';
                padding: 0 24px;
            }
            QPushButton:hover {
                background: #FFA726;
            }
        """)

        self.pdf_button = QPushButton("Generate PDF Report")
        self.pdf_button.setFixedHeight(40)
        self.pdf_button.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                border-radius: 6px;
                color: white;
                font: 700 14pt 'Inter';
                padding: 0 24px;
            }
            QPushButton:hover {
                background: #42A5F5;
            }
        """)

        btns.addStretch()
        btns.addWidget(self.calculate_button)
        btns.addWidget(self.plot_button)
        btns.addWidget(self.pdf_button)
        btns.addStretch()

        main.addLayout(btns)

    def _make_connections(self):
        """Set up signal/slot connections."""
        self.setup_connections()
        
        # Connect calculate button
        self.calculate_button.clicked.connect(self._on_calculate)
        
        # Connect plot button
        self.plot_button.clicked.connect(self._on_plot)
        
        # Connect PDF button
        self.pdf_button.clicked.connect(self._on_generate_pdf)

    def setup_connections(self):
        """Set up signal/slot connections for calculations and UI updates."""
        try:
            # Connect unit changes with value conversion
            self.tx_power_unit.currentTextChanged.connect(self._on_power_unit_changed)
            self.freq_unit.currentTextChanged.connect(self._on_freq_unit_changed)
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Setup Error",
                f"Error setting up connections: {str(e)}"
            )

    def _on_calculate(self):
        """Handle calculate button click."""
        try:
            params = self.get_parameters()
            if params:
                self.calculate_clicked.emit(params)
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Calculation Error",
                f"Error during calculation: {str(e)}"
            )
            
    def _on_generate_pdf(self):
        """Handle generate PDF button click."""
        try:
            params = self.get_parameters()
            if params:
                self.generate_pdf_clicked.emit(params)
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "PDF Generation Error",
                f"Error generating PDF: {str(e)}"
            )
            
    def _on_power_unit_changed(self, unit):
        """Convert power value between W and dBm."""
        try:
            current_value = self.tx_power.value()
            
            if unit == "dBm" and self.tx_power_unit.currentText() == "W":
                # Convert W to dBm
                new_value = 10 * math.log10(current_value * 1000)
                self.tx_power.setValue(new_value)
                
            elif unit == "W" and self.tx_power_unit.currentText() == "dBm":
                # Convert dBm to W
                new_value = math.pow(10, current_value/10) / 1000
                self.tx_power.setValue(new_value)
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Conversion Error",
                f"Error converting power units: {str(e)}"
            )
            
    def _on_freq_unit_changed(self, unit):
        """Convert frequency value between MHz and GHz."""
        try:
            current_value = self.freq.value()
            
            if unit == "GHz" and self.freq_unit.currentText() == "MHz":
                self.freq.setValue(current_value / 1000)
            elif unit == "MHz" and self.freq_unit.currentText() == "GHz":
                self.freq.setValue(current_value * 1000)
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Conversion Error",
                f"Error converting frequency units: {str(e)}"
            )

    def _on_plot(self):
        """Handle plot button click."""
        try:
            # Switch to the Link Margin Analysis tab
            self.tab_widget.setCurrentIndex(1)
            # Generate the plot
            self.plot_widget._generate_plot()
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Plot Error",
                f"Error generating plot: {str(e)}"
            )

    def get_parameters(self):
        """Get all parameter values as a dictionary."""
        try:
            # Convert power to dBm if needed
            power = self.tx_power.value()
            if self.tx_power_unit.currentText() == "W":
                power = 10 * math.log10(power * 1000)  # Convert W to dBm
                
            # Convert frequency to Hz
            freq = self.freq.value()
            if self.freq_unit.currentText() == "GHz":
                freq *= 1e9
            else:  # MHz
                freq *= 1e6
                
            return {
                'tx_power_dbm': power,
                'tx_gain_dbi': self.tx_gain.value(),
                'rx_gain_dbi': self.rx_gain.value(),
                'rx_noise_figure_db': self.rx_noise_figure.value(),
                'rx_implementation_loss_db': self.rx_implementation_loss.value(),
                'frequency_hz': freq,
                'distance_km': self.dist.value(),
                'temperature_k': self.temp.value(),
                'bandwidth_hz': self.bw.value(),
                'required_ebno_db': self.ebno.value()
            }
            
        except Exception as e:
            return None

    def resizeEvent(self, e):
        super().resizeEvent(e)
        spl = self.findChild(QSplitter)
        if spl:
            if self.width() < 1000 and spl.orientation() == Qt.Orientation.Horizontal:
                spl.setOrientation(Qt.Orientation.Vertical)
            elif self.width() >= 1000 and spl.orientation() == Qt.Orientation.Vertical:
                spl.setOrientation(Qt.Orientation.Horizontal)

    def set_parameters(self, params: dict) -> None:
        """Set link budget parameters from a dictionary.
        
        Args:
            params: Dictionary containing parameter values
        """
        try:
            # Set frequency
            if 'frequency' in params:
                freq_value = params['frequency'].get('value', 0)
                freq_unit = params['frequency'].get('unit', 'MHz')
                self.freq.setValue(freq_value)
                self.freq_unit.setCurrentText(freq_unit)
            
            # Set transmit power
            if 'transmit_power' in params:
                power_value = params['transmit_power'].get('value', 0)
                power_unit = params['transmit_power'].get('unit', 'W')
                self.tx_power.setValue(power_value)
                self.tx_power_unit.setCurrentText(power_unit)
            
            # Set transmitter gain
            if 'tx_gain' in params:
                self.tx_gain.setValue(params['tx_gain'])
                
            # Set receiver parameters
            if 'rx_gain' in params:
                self.rx_gain.setValue(params['rx_gain'])
            if 'rx_noise_figure' in params:
                self.rx_noise_figure.setValue(params['rx_noise_figure'])
            if 'rx_implementation_loss' in params:
                self.rx_implementation_loss.setValue(params['rx_implementation_loss'])
            
            # Set distance
            if 'distance' in params:
                self.dist.setValue(params['distance'])
            
            # Trigger calculation with new parameters
            self._on_calculate()
            
        except Exception as e:
            raise ValueError(f"Failed to set parameters: {str(e)}")

    def update_results(self, result):
        """Update the view with calculation results."""
        try:
            for key, value in result.items():
                if key in self.result_labels:
                    try:
                        numeric_value = float(value.split()[0])
                        if math.isnan(numeric_value) or math.isinf(numeric_value):
                            self.result_labels[key].setText("Invalid")
                            self.result_labels[key].setStyleSheet("""
                                color: #FF0000;
                                font-weight: bold;
                                background: none;
                            """)
                        else:
                            self.result_labels[key].setText(str(value))
                            self.result_labels[key].setStyleSheet("""
                                color: #4CAF50;
                                font-weight: bold;
                                background: none;
                            """)
                    except (ValueError, IndexError):
                        self.result_labels[key].setText("Invalid")
                        self.result_labels[key].setStyleSheet("""
                            color: #FF0000;
                            font-weight: bold;
                            background: none;
                        """)
            
            # Add recommendations based on results
            self._update_recommendations(result)
            
            # Force update of the UI
            QApplication.processEvents()
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Update Error",
                f"Error updating results: {str(e)}"
            )

    def _update_recommendations(self, result):
        """Update recommendations based on link budget results."""
        try:
            # Extract numeric values from result strings
            link_margin = float(result['link_margin'].split()[0])
            path_loss = float(result['path_loss'].split()[0])

            recommendations = []

            # Link Margin Analysis - Primary recommendation
            if link_margin < 0:
                recommendations.append("""
                    <p><b>Critical: Negative Link Margin</b><br>
                    The communication link may fail. Consider:
                    • Increasing transmit power
                    • Using higher gain antennas
                    • Reducing the distance</p>
                """)
            elif link_margin < 3:
                recommendations.append("""
                    <p><b>Warning: Low Link Margin</b><br>
                    Add safety margin for:
                    • Weather conditions
                    • Antenna pointing losses</p>
                """)

            # Path Loss Analysis - Only show for significant issues
            if path_loss > 180:
                recommendations.append("""
                    <p><b>High Path Loss</b><br>
                    Consider:
                    • Operating at a lower frequency
                    • Using higher gain antennas</p>
                """)

            # Create recommendations section if it doesn't exist
            if not hasattr(self, 'recommendations_label'):
                self.recommendations_label = QLabel()
                self.recommendations_label.setWordWrap(True)
                self.recommendations_label.setStyleSheet("""
                    QLabel {
                        background-color: palette(base);
                        border: 1px solid palette(mid);
                        border-radius: 8px;
                        padding: 16px;
                        margin-top: 8px;
                        color: palette(text);
                        font: 11pt 'Inter';
                    }
                """)
                # Add to the right panel's layout
                for i in range(self.layout().count()):
                    widget = self.layout().itemAt(i).widget()
                    if isinstance(widget, QSplitter):
                        right_widget = widget.widget(1)
                        if isinstance(right_widget, QWidget):
                            right_widget.layout().insertWidget(
                                right_widget.layout().count() - 1,  # Insert before the last stretch
                                self.recommendations_label
                            )

            # Update recommendations text
            if recommendations:
                self.recommendations_label.setText("""
                    <h3 style='color: palette(text); margin-bottom: 12px;'>Recommendations</h3>
                    {}
                """.format("".join(recommendations)))
            else:
                self.recommendations_label.setText("")  # Hide recommendations if none are needed

        except Exception as e:
            self.recommendations_label.setText("""
                <p style='color: palette(text);'>
                    Unable to generate recommendations. Please ensure all values are properly calculated.
                </p>
            """)

    def show_error(self, title: str, message: str):
        """Show error message to user."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, title, message)

    def get_save_filename(self):
        """Get the save location for the PDF report."""
        try:
            from PyQt6.QtWidgets import QFileDialog
            import os
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save PDF Report",
                os.path.expanduser("~/link_budget_report.pdf"),
                "PDF Files (*.pdf)"
            )
            return file_path
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "File Dialog Error",
                f"Error opening file dialog: {str(e)}"
            )
            return None

    def show_report_success(self, filepath):
        """Show success message after report generation."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Report Generated",
            f"PDF report has been saved to:\n{filepath}"
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = LinkBudgetView()
    w.show()
    sys.exit(app.exec())
