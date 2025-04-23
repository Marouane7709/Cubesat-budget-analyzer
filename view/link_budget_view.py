from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter,
    QLabel, QComboBox, QPushButton, QDoubleSpinBox, QSizePolicy, QGroupBox, QFrame, QScrollArea,
    QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import math
import sys
import numpy as np
from scipy.special import erfc

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
        
        # Create matplotlib figure with even larger size
        self.figure = Figure(figsize=(16, 10), dpi=100)  # Increased size
        self.canvas = FigureCanvas(self.figure)
        
        # Enable tight layout and better backend
        self.figure.set_tight_layout(True)
        
        # Store current data series and background
        self.data_series = []
        self.background = None
        
        # Create the navigation toolbar with custom style
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet("""
            QToolBar {
                background: transparent;
                spacing: 6px;
                border: none;
                min-height: 48px;
            }
            QToolButton {
                background: transparent;
                border: none;
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
            }
            QToolButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        
        # Add toolbar and canvas to layout
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # Setup controls with larger size
        controls = QHBoxLayout()
        controls.setContentsMargins(12, 12, 12, 12)
        controls.setSpacing(12)
        
        # Plot type selector with larger size
        self.plot_type = QComboBox()
        self.plot_type.addItems([
            "BER vs Eb/N0 [dB]",
            "Link Margin vs. Distance",
            "Link Margin vs. Frequency"
        ])
        self.plot_type.setMinimumHeight(36)
        
        # Modulation scheme selector with larger size
        self.modulation = QComboBox()
        self.modulation.addItems([
            "BPSK",
            "QPSK",
            "8PSK",
            "16PSK"  # Added 16PSK
        ])
        self.modulation.setMinimumHeight(36)
        
        # Style the comboboxes
        for combo in [self.plot_type, self.modulation]:
            combo.setStyleSheet("""
                QComboBox {
                    background: #2b2b2b;
                    border: 1px solid #3d3d3d;
                    border-radius: 4px;
                    padding: 8px 12px;
                    min-width: 180px;
                    color: white;
                    font-size: 14px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border: none;
                }
            """)
        
        # Add labels and widgets to controls
        for label_text, widget in [("Plot Type:", self.plot_type), ("Modulation:", self.modulation)]:
            label = QLabel(label_text)
            label.setStyleSheet("color: white; font-size: 14px;")
            controls.addWidget(label)
            controls.addWidget(widget)
        controls.addStretch()
        
        # Generate Plot button with larger size
        self.plot_button = QPushButton("Generate Plot")
        self.plot_button.setMinimumHeight(36)
        self.plot_button.setStyleSheet("""
            QPushButton {
                background: #0d47a1;
                border-radius: 4px;
                color: white;
                padding: 8px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 140px;
            }
            QPushButton:hover {
                background: #1565c0;
            }
        """)
        controls.addWidget(self.plot_button)
        
        layout.addLayout(controls)
        
        # Enable mouse events and better interaction
        self.canvas.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.canvas.setFocus()
        
        # Connect events for smooth interaction
        self.canvas.mpl_connect('draw_event', self._on_draw)
        self.canvas.mpl_connect('resize_event', self._on_resize)
        self.canvas.mpl_connect('motion_notify_event', self._on_motion)
        
        # Set up animation timer for smooth updates
        self._timer = QTimer()
        self._timer.setInterval(16)  # 60 FPS
        self._timer.timeout.connect(self._update_plot)
        self._timer.start()
        
        # Initialize plot state
        self._last_cursor_pos = None
        self._is_panning = False
        self._zoom_scale = 1.0

    def _on_draw(self, event):
        """Cache the background for blitting on draw events."""
        if self.figure.axes:
            self.background = self.canvas.copy_from_bbox(self.figure.axes[0].bbox)

    def _on_motion(self, event):
        """Handle smooth panning and cursor updates."""
        if not event.inaxes or not self.background:
            return
            
        if self._is_panning and event.button == 1:  # Left mouse button
            if self._last_cursor_pos:
                dx = event.xdata - self._last_cursor_pos[0]
                dy = event.ydata - self._last_cursor_pos[1]
                ax = event.inaxes
                
                # Update limits with smooth transition
                x1, x2 = ax.get_xlim()
                y1, y2 = ax.get_ylim()
                
                ax.set_xlim(x1 - dx, x2 - dx)
                ax.set_ylim(y1 - dy, y2 - dy)
                
                # Restore background and redraw
                self.canvas.restore_region(self.background)
                ax.draw_artist(ax.patch)
                for line in ax.lines:
                    ax.draw_artist(line)
                self.canvas.blit(ax.bbox)
                
        self._last_cursor_pos = (event.xdata, event.ydata)

    def _on_resize(self, event):
        """Handle window resize events."""
        # Update figure size while maintaining aspect ratio
        w, h = self.canvas.get_width_height()
        self.figure.set_size_inches(w/self.figure.get_dpi(), h/self.figure.get_dpi())
        
        # Force tight layout update
        self.figure.tight_layout()
        
        # Redraw with blitting
        if self.background:
            self.canvas.restore_region(self.background)
            if self.figure.axes:
                ax = self.figure.axes[0]
                ax.draw_artist(ax.patch)
                for line in ax.lines:
                    ax.draw_artist(line)
                self.canvas.blit(ax.bbox)
        else:
            self.canvas.draw_idle()

    def _update_plot(self):
        """Update the plot for smooth animations."""
        if self.figure.axes and self.background:
            ax = self.figure.axes[0]
            self.canvas.restore_region(self.background)
            ax.draw_artist(ax.patch)
            for line in ax.lines:
                ax.draw_artist(line)
            self.canvas.blit(ax.bbox)

    def setSizeHint(self):
        """Set the preferred size for the widget."""
        return QSize(1600, 1000)  # Even larger default size

    def minimumSizeHint(self):
        """Set the minimum size for the widget."""
        return QSize(1200, 800)  # Larger minimum size

    def get_ebno_value(self):
        """Get Eb/N0 value from parent view."""
        if self.parent and hasattr(self.parent, 'ebno'):
            return self.parent.ebno.value()
        return 10.0  # Default value if not available

    def _create_ber_plot(self):
        """Create a plot showing BER vs Eb/N0 with modern styling."""
        try:
            # Clear any existing plots
            self.clear_data_series()
            
            # Create subplot with specific size ratio
            ax = self.figure.add_subplot(111)
            
            # Generate Eb/N0 points
            eb_n0_db = np.linspace(0, 20, 500)  # Increased range and points
            eb_n0_linear = 10**(eb_n0_db/10)
            
            # Calculate BER for each modulation scheme
            ber_bpsk_qpsk = 0.5 * erfc(np.sqrt(eb_n0_linear))
            ber_8psk = (2/3) * erfc(np.sqrt(3 * eb_n0_linear * np.log2(8) / 8))
            
            # Plot styling
            ax.set_facecolor('white')
            self.figure.patch.set_facecolor('white')
            
            # Plot curves
            ax.semilogy(eb_n0_db, ber_bpsk_qpsk, '-', color='#2196F3', 
                       label='BPSK/QPSK', linewidth=1.5)
            ax.semilogy(eb_n0_db, ber_8psk, '-', color='#FF9800',
                       label='8-PSK', linewidth=1.5)
            
            # Add threshold lines
            ax.axhline(y=1e-3, color='#ffcdd2', linestyle='--', linewidth=1)
            ax.axhline(y=1e-5, color='#c8e6c9', linestyle='--', linewidth=1)
            
            # Grid styling
            ax.grid(True, which='both', color='#f5f5f5', linewidth=0.5)
            ax.grid(True, which='major', color='#eeeeee', linewidth=0.8)
            
            # Set axis limits and labels
            ax.set_xlim(0, 20)
            ax.set_ylim(1e-6, 1e0)
            ax.set_xlabel('Eb/N0 [dB]')
            ax.set_ylabel('Bit Error Rate (BER)')
            
            # Style spines
            for spine in ax.spines.values():
                spine.set_color('#dddddd')
                spine.set_linewidth(0.5)
            
            # Set tick parameters
            ax.tick_params(colors='#666666', grid_color='#eeeeee', grid_alpha=0.8)
            
            # Add legend with clean styling
            legend = ax.legend(loc='lower left', frameon=True, fontsize=9)
            legend.get_frame().set_facecolor('white')
            legend.get_frame().set_edgecolor('#dddddd')
            legend.get_frame().set_linewidth(0.5)
            
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
                
                ax.plot(current_ebno, current_ber, 'o', color='#E91E63',
                       markersize=6, label='Operating Point')
            
            # Adjust layout
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error in _create_ber_plot: {str(e)}")
            raise Exception(f"Error creating BER plot: {str(e)}")

    def clear_data_series(self):
        """Clear all data series from the plot."""
        self.data_series = []
        self.figure.clear()
        self.canvas.draw()

    def plot_link_margin(self, x_values, y_values, x_label, title, label=None):
        """Plot link margin analysis."""
        try:
            if not hasattr(self, 'current_ax'):
                self.figure.clear()
                self.current_ax = self.figure.add_subplot(111)
            
            line, = self.current_ax.plot(x_values, y_values, linewidth=2, label=label)
            if label:
                self.current_ax.legend()
            
            self.current_ax.set_xlabel(x_label)
            self.current_ax.set_ylabel('Link Margin (dB)')
            self.current_ax.set_title(title)
            self.current_ax.grid(True)
            
            self.canvas.draw()
            return line
            
        except Exception as e:
            print(f"Error in plot_link_margin: {str(e)}")
            raise Exception(f"Error plotting link margin: {str(e)}")

    def add_data_series(self, x_data, y_data, label=None):
        """Add a new data series to the plot."""
        try:
            line = self.plot_link_margin(x_data, y_data, '', '', label)
            self.data_series.append((line, {'x': x_data, 'y': y_data}))
        except Exception as e:
            print(f"Error in add_data_series: {str(e)}")
            raise Exception(f"Error adding data series: {str(e)}")

    def _generate_plot(self):
        """Generate the selected plot type."""
        try:
            self.clear_data_series()
            plot_type = self.plot_type.currentText()
            
            if plot_type == "BER vs Eb/N0 [dB]":
                self._create_ber_plot()
            elif plot_type == "Link Margin vs. Distance":
                self._create_distance_margin_plot()
            elif plot_type == "Link Margin vs. Frequency":
                self._create_frequency_margin_plot()
            
        except Exception as e:
            print(f"Error generating plot: {str(e)}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Plot Error",
                f"Error generating plot: {str(e)}"
            )

    def _setup_grid_and_style(self, ax):
        """Set up grid lines and plot style."""
        # Major grid
        ax.grid(True, which='major', color='#CCCCCC', linestyle='-', linewidth=0.8, alpha=0.5)
        # Minor grid
        ax.grid(True, which='minor', color='#DDDDDD', linestyle=':', linewidth=0.5, alpha=0.3)
        
        # Enable minor ticks
        ax.minorticks_on()
        
        # Style spines
        for spine in ax.spines.values():
            spine.set_color('#666666')
            spine.set_linewidth(0.8)
        
        # Set background color
        ax.set_facecolor('white')
        self.figure.patch.set_facecolor('white')
        
        # Style tick parameters
        ax.tick_params(which='major', length=6, width=0.8, colors='#333333')
        ax.tick_params(which='minor', length=3, width=0.6, colors='#666666')

    def _create_distance_margin_plot(self):
        """Create a plot showing link margin vs distance."""
        try:
            # Clear any existing plots
            self.clear_data_series()
            
            # Create subplot with specific size ratio
            ax = self.figure.add_subplot(111)
            
            # Set up grid and style
            self._setup_grid_and_style(ax)
            
            # Generate distance points (logarithmic scale)
            distances = np.logspace(0, 4, 200)  # 1 km to 10000 km
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
                        print(f"Error calculating margin for distance {d}: {str(e)}")
                        margins.append(np.nan)
                
                # Restore original distance
                params['distance_km'] = base_distance
            else:
                raise Exception("Cannot access link budget parameters")
            
            # Convert to numpy array for easier handling
            margins = np.array(margins)
            
            # Plot data with thicker line
            ax.semilogx(distances, margins, '-', color='#2196F3', 
                       label=f"Modulation: {self.modulation.currentText()}", 
                       linewidth=2.0)
            
            # Add threshold line at 0 dB
            ax.axhline(y=0, color='#ffcdd2', linestyle='--', linewidth=1.5,
                      label='Minimum Required Margin')
            
            # Set axis limits and labels with larger font
            ax.set_xlim(distances[0], distances[-1])
            margin_range = np.nanmax(margins) - np.nanmin(margins)
            ax.set_ylim(np.nanmin(margins) - 0.1 * margin_range,
                       np.nanmax(margins) + 0.1 * margin_range)
            
            # Larger font sizes
            ax.set_xlabel('Distance [km]', fontsize=12, labelpad=10)
            ax.set_ylabel('Link Margin [dB]', fontsize=12, labelpad=10)
            ax.tick_params(labelsize=10)
            
            # Add legend with clean styling and larger font
            legend = ax.legend(loc='upper right', frameon=True, fontsize=11)
            legend.get_frame().set_facecolor('white')
            legend.get_frame().set_edgecolor('#dddddd')
            legend.get_frame().set_linewidth(0.5)
            
            # Add current operating point with larger marker
            if base_distance >= distances[0] and base_distance <= distances[-1]:
                current_margin = margins[np.abs(distances - base_distance).argmin()]
                ax.plot(base_distance, current_margin, 'o', color='#E91E63',
                       markersize=8, label='Operating Point')
                
                # Add annotation for current point with larger font
                ax.annotate(f'Current: {current_margin:.1f} dB',
                           xy=(base_distance, current_margin),
                           xytext=(10, 10), textcoords='offset points',
                           bbox=dict(facecolor='white', edgecolor='#dddddd',
                                   alpha=0.8),
                           fontsize=11)
            
            # Adjust layout
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error in _create_distance_margin_plot: {str(e)}")
            raise Exception(f"Error creating distance margin plot: {str(e)}")

    def _calculate_link_budget(self, params):
        """Calculate link budget for a given set of parameters."""
        try:
            # Convert power to dBm if needed
            power = params['tx_power_dbm']
            freq = params['frequency_hz']
            
            # Calculate free space path loss
            c = 3e8  # speed of light in m/s
            d = params['distance_km'] * 1000  # convert km to m
            fspl = 20 * np.log10(4 * np.pi * d * freq / c)
            
            # Calculate received power
            rx_power = power + params['tx_gain_dbi'] + params['rx_gain_dbi'] - fspl - params['rx_implementation_loss_db']
            
            # Calculate noise power
            k = 1.38e-23  # Boltzmann constant
            noise_power = 10 * np.log10(k * params['temperature_k'] * params['bandwidth_hz']) + 30  # convert to dBm
            
            # Calculate C/N0
            cn0 = rx_power - noise_power
            
            # Calculate link margin
            link_margin = cn0 - params['required_ebno_db'] - 10 * np.log10(params['bandwidth_hz'])
            
            return {
                'eirp': f"{power + params['tx_gain_dbi']:.1f} dBW",
                'path_loss': f"{fspl:.1f} dB",
                'received_power': f"{rx_power:.1f} dBW",
                'cn0': f"{cn0:.1f} dB-Hz",
                'link_margin': f"{link_margin:.1f} dB"
            }
            
        except Exception as e:
            raise Exception(f"Error calculating link budget: {str(e)}")

    def _create_frequency_margin_plot(self):
        """Create a plot showing link margin vs frequency."""
        try:
            # Clear any existing plots
            self.clear_data_series()
            
            # Create subplot with specific size ratio
            ax = self.figure.add_subplot(111)
            
            # Set plot style
            ax.set_facecolor('white')
            self.figure.patch.set_facecolor('white')
            
            # Generate frequency points (logarithmic scale)
            frequencies = np.logspace(6, 11, 200)  # 1 MHz to 100 GHz
            margins = []
            
            # Get current parameters from parent view
            if self.parent and hasattr(self.parent, 'get_parameters'):
                params = self.parent.get_parameters()
                base_freq = params['frequency_hz']
                
                # Calculate margins for each frequency
                for f in frequencies:
                    params['frequency_hz'] = f
                    try:
                        # Calculate link budget for this frequency
                        result = self._calculate_link_budget(params)
                        margin = float(result['link_margin'].split()[0])
                        margins.append(margin)
                    except Exception as e:
                        print(f"Error calculating margin for frequency {f}: {str(e)}")
                        margins.append(np.nan)
                
                # Restore original frequency
                params['frequency_hz'] = base_freq
            else:
                raise Exception("Cannot access link budget parameters")
            
            # Convert to numpy array for easier handling
            margins = np.array(margins)
            
            # Plot data
            ax.semilogx(frequencies/1e9, margins, '-', color='#2196F3', 
                       label=f"Modulation: {self.modulation.currentText()}", 
                       linewidth=1.5)
            
            # Add threshold line at 0 dB
            ax.axhline(y=0, color='#ffcdd2', linestyle='--', linewidth=1,
                      label='Minimum Required Margin')
            
            # Grid styling
            ax.grid(True, which='both', color='#f5f5f5', linewidth=0.5)
            ax.grid(True, which='major', color='#eeeeee', linewidth=0.8)
            
            # Set axis limits and labels
            ax.set_xlim(frequencies[0]/1e9, frequencies[-1]/1e9)
            margin_range = np.nanmax(margins) - np.nanmin(margins)
            ax.set_ylim(np.nanmin(margins) - 0.1 * margin_range,
                       np.nanmax(margins) + 0.1 * margin_range)
            ax.set_xlabel('Frequency [GHz]')
            ax.set_ylabel('Link Margin [dB]')
            
            # Style spines
            for spine in ax.spines.values():
                spine.set_color('#dddddd')
                spine.set_linewidth(0.5)
            
            # Set tick parameters
            ax.tick_params(colors='#666666', grid_color='#eeeeee', grid_alpha=0.8)
            
            # Add legend with clean styling
            legend = ax.legend(loc='upper right', frameon=True, fontsize=9)
            legend.get_frame().set_facecolor('white')
            legend.get_frame().set_edgecolor('#dddddd')
            legend.get_frame().set_linewidth(0.5)
            
            # Add current operating point
            current_freq = base_freq/1e9  # Convert to GHz for plotting
            if frequencies[0]/1e9 <= current_freq <= frequencies[-1]/1e9:
                current_margin = margins[np.abs(frequencies/1e9 - current_freq).argmin()]
                ax.plot(current_freq, current_margin, 'o', color='#E91E63',
                       markersize=6, label='Operating Point')
                
                # Add annotation for current point
                ax.annotate(f'Current: {current_margin:.1f} dB',
                           xy=(current_freq, current_margin),
                           xytext=(10, 10), textcoords='offset points',
                           bbox=dict(facecolor='white', edgecolor='#dddddd',
                                   alpha=0.8))
            
            # Adjust layout
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error in _create_frequency_margin_plot: {str(e)}")
            raise Exception(f"Error creating frequency margin plot: {str(e)}")

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
        
        # Connect the plot button to the PlotWidget's generate method
        self.plot_widget.plot_button.clicked.connect(self.plot_widget._generate_plot)

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
        btns.addWidget(self.pdf_button)
        btns.addStretch()

        main.addLayout(btns)

    def _make_connections(self):
        """Set up signal/slot connections."""
        self.setup_connections()
        
        # Connect calculate button
        self.calculate_button.clicked.connect(self._on_calculate)
        
        # Connect PDF button
        self.pdf_button.clicked.connect(self._on_generate_pdf)
        
        # Connect plot button
        if hasattr(self, 'plot_widget'):
            self.plot_widget.plot_button.clicked.connect(self.plot_widget._generate_plot)

    def setup_connections(self):
        """Set up signal/slot connections for calculations and UI updates."""
        try:
            # Connect unit changes with value conversion
            self.tx_power_unit.currentTextChanged.connect(self._on_power_unit_changed)
            self.freq_unit.currentTextChanged.connect(self._on_freq_unit_changed)
            
        except Exception as e:
            print(f"Error in setup_connections: {str(e)}")

    def _on_calculate(self):
        """Handle calculate button click."""
        try:
            print("Calculate button clicked")
            params = self.get_parameters()
            print(f"Parameters collected in view: {params}")
            if params:
                print("Emitting calculate_clicked signal")
                self.calculate_clicked.emit(params)
                print("Signal emitted")
        except Exception as e:
            print(f"Error in _on_calculate: {str(e)}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Calculation Error",
                f"Error during calculation: {str(e)}"
            )
            
    def _on_generate_pdf(self):
        """Handle generate PDF button click."""
        try:
            print("Generate PDF button clicked")
            params = self.get_parameters()
            if params:
                self.generate_pdf_clicked.emit(params)
        except Exception as e:
            print(f"Error in _on_generate_pdf: {str(e)}")
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
            print(f"Error in _on_power_unit_changed: {str(e)}")
            
    def _on_freq_unit_changed(self, unit):
        """Convert frequency value between MHz and GHz."""
        try:
            current_value = self.freq.value()
            
            if unit == "GHz" and self.freq_unit.currentText() == "MHz":
                self.freq.setValue(current_value / 1000)
            elif unit == "MHz" and self.freq_unit.currentText() == "GHz":
                self.freq.setValue(current_value * 1000)
            
        except Exception as e:
            print(f"Error in _on_freq_unit_changed: {str(e)}")

    def get_parameters(self):
        """Get all parameter values as a dictionary."""
        try:
            print("Getting parameters in view...")
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
                
            params = {
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
            print(f"Parameters collected: {params}")
            return params
            
        except Exception as e:
            print(f"Error in get_parameters: {str(e)}")
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
            print(f"Updating results in view with: {result}")
            for key, value in result.items():
                if key in self.result_labels:
                    # Check for valid numeric values
                    try:
                        # Extract numeric value from the string (e.g., "39.0 dBW" -> 39.0)
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
            print(f"Error in update_results: {str(e)}")
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
            print(f"Error updating recommendations: {str(e)}")
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
            print(f"Error getting save filename: {str(e)}")
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
