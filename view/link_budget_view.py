from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QComboBox, QPushButton, QTabWidget, QDoubleSpinBox, QMessageBox,
    QFileDialog, QScrollArea, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, pyqtSlot, QSettings
from PyQt6.QtGui import QFont
import numpy as np
from pathlib import Path
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


# ──────────────────────────────────────────────────────────────────────────────
# Helper widgets
# ──────────────────────────────────────────────────────────────────────────────
class CollapsibleSection(QWidget):
    """A dark‑theme accordion section that remembers its open/closed state."""
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self._title = title
        self.setObjectName("collapsible_section")

        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # Header
        header = QFrame()
        header.setObjectName("section_header")
        header.setCursor(Qt.CursorShape.PointingHandCursor)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(16, 12, 16, 12)

        lbl = QLabel(title)
        lbl.setObjectName("section_title")
        try:
            lbl.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        except Exception:
            lbl.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        h_lay.addWidget(lbl)
        h_lay.addStretch()

        # Accent line
        accent = QFrame()
        accent.setObjectName("accent_line")
        accent.setFrameShape(QFrame.Shape.HLine)

        main.addWidget(header)
        main.addWidget(accent)

        # Body
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        main.addWidget(self.content)

        # Toggle on click
        header.mouseReleaseEvent = lambda e: self.setCollapsed(self.content.isVisible())

        # Restore previous state
        self.setCollapsed(not QSettings().value(f"sxn_open_{title}", True, bool))

    def setCollapsed(self, collapsed: bool):
        self.content.setVisible(not collapsed)
        QSettings().setValue(f"sxn_open_{self._title}", not collapsed)


class FloatingSpinBox(QWidget):
    """Input field with floating label + helper text (material‑ish)."""
    def __init__(self, label: str, suffix: str = "", helper_text: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("floating_input")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        lbl = QLabel(label, objectName="input_label")
        try:
            lbl.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        except Exception:
            lbl.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        lay.addWidget(lbl)

        self.spin_box = QDoubleSpinBox(objectName="dark_input")
        self.spin_box.setSuffix(suffix)
        self.spin_box.setMinimumWidth(140)
        self.spin_box.setFixedHeight(32)
        self.spin_box.setAlignment(Qt.AlignmentFlag.AlignLeft)
        lay.addWidget(self.spin_box)

        if helper_text:
            helper = QLabel(helper_text, objectName="helper_text")
            try:
                helper.setFont(QFont("Inter", 10))
            except Exception:
                helper.setFont(QFont("Arial", 10))
            lay.addWidget(helper)


# ──────────────────────────────────────────────────────────────────────────────
# Main window
# ──────────────────────────────────────────────────────────────────────────────
class LinkBudgetView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CubeSat Budget Analyzer - Link Budget")
        # Set minimum size but let the window be maximized
        self.setMinimumSize(800, 600)
        # Remove the fixed resize call since we'll maximize
        self.setup_ui()
        self.apply_dark_theme()
        self.setup_connections()
        # Maximize the window
        if self.parent() is None:  # Only if not embedded
            self.showMaximized()
        
    # ------------------------------------------------------------------ UI
    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        self.tabs = QTabWidget(objectName="link_budget_tabs")
        root.addWidget(self.tabs)

        self.parameters_tab = QWidget()
        self.results_tab = QWidget()
        self.analysis_tab = QWidget()
        self.tabs.addTab(self.parameters_tab, "Parameters")
        self.tabs.addTab(self.results_tab, "Results")
        self.tabs.addTab(self.analysis_tab, "Link Margin Analysis")

        self.setup_parameters_tab()
        self.setup_results_tab()
        self.setup_analysis_tab()

    # ------------------------------------------------------------------ Parameters tab
    def setup_parameters_tab(self):
        # **Layout hierarchy**
        # parameters_tab
        # ├─ scroll (index 0)   ← form inside here scrolls
        # └─ button_wrap (index 1)  ← pinned row, always visible
        outer = QVBoxLayout(self.parameters_tab)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(16)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll, 1)          # stretch factor 1 → takes remaining height

        container = QWidget()
        scroll.setWidget(container)
        form_lay = QVBoxLayout(container)
        form_lay.setContentsMargins(24, 24, 24, 24)
        form_lay.setSpacing(24)

        # 1) Transmitter section
        tx_sec = CollapsibleSection("Transmitter Parameters")
        form_lay.addWidget(tx_sec)
        tx_grid = QGridLayout()
        tx_grid.setHorizontalSpacing(24)
        tx_grid.setVerticalSpacing(12)
        tx_sec.content_layout.addLayout(tx_grid)

        power_wrap = QWidget()
        pw_lay = QHBoxLayout(power_wrap)
        pw_lay.setContentsMargins(0, 0, 0, 0)
        pw_lay.setSpacing(8)
        self.tx_power_spin = FloatingSpinBox("Transmit Power")
        self.tx_power_unit = QComboBox(objectName="dark_input")
        self.tx_power_unit.addItems(["W", "dBm"])
        self.tx_power_unit.setFixedWidth(80)
        self.tx_power_unit.setFixedHeight(32)
        pw_lay.addWidget(self.tx_power_spin, 1)
        pw_lay.addWidget(self.tx_power_unit)

        self.tx_gain_spin = FloatingSpinBox("Transmitter Gain", " dBi")
        tx_grid.addWidget(power_wrap, 0, 0)
        tx_grid.addWidget(self.tx_gain_spin, 0, 1)
        tx_grid.setColumnStretch(0, 1)
        tx_grid.setColumnStretch(1, 1)

        # 2) Channel section
        ch_sec = CollapsibleSection("Channel Parameters")
        form_lay.addWidget(ch_sec)
        ch_grid = QGridLayout()
        ch_grid.setHorizontalSpacing(24)
        ch_grid.setVerticalSpacing(12)
        ch_sec.content_layout.addLayout(ch_grid)

        self.freq_spin      = FloatingSpinBox("Carrier Frequency", " GHz")
        self.fspl_spin      = FloatingSpinBox("Free Space Path Loss", " dB")
        self.atm_loss_spin  = FloatingSpinBox("Atmospheric Loss", " dB")

        model_wrap = QWidget()
        mw_lay = QVBoxLayout(model_wrap)
        mw_lay.setContentsMargins(0, 0, 0, 0)
        mw_lay.setSpacing(6)
        model_lbl = QLabel("Propagation Model", objectName="input_label")
        self.prop_model_combo = QComboBox(objectName="dark_input")
        self.prop_model_combo.addItems([
            "AWGN (Additive White Gaussian Noise)",
            "Rayleigh Fading", "Rician Fading", "Log‑normal Shadowing"
        ])
        self.prop_model_combo.setFixedHeight(32)
        self.model_info_label = QLabel("", objectName="helper_text")
        mw_lay.addWidget(model_lbl)
        mw_lay.addWidget(self.prop_model_combo)
        mw_lay.addWidget(self.model_info_label)

        ch_grid.addWidget(self.freq_spin,     0, 0)
        ch_grid.addWidget(self.fspl_spin,     0, 1)
        ch_grid.addWidget(self.atm_loss_spin, 1, 0)
        ch_grid.addWidget(model_wrap,         1, 1)
        ch_grid.setColumnStretch(0, 1)
        ch_grid.setColumnStretch(1, 1)

        # 3) Receiver section
        rx_sec = CollapsibleSection("Receiver Parameters")
        form_lay.addWidget(rx_sec)
        rx_grid = QGridLayout()
        rx_grid.setHorizontalSpacing(24)
        rx_grid.setVerticalSpacing(12)
        rx_sec.content_layout.addLayout(rx_grid)

        self.rx_gain_spin = FloatingSpinBox("Receiver Gain", " dBi")
        self.temp_spin    = FloatingSpinBox("System Temperature", " K")
        self.bw_spin      = FloatingSpinBox("Bandwidth", " Hz")
        self.ebno_spin    = FloatingSpinBox("Required Eb/No", " dB")

        rx_grid.addWidget(self.rx_gain_spin, 0, 0)
        rx_grid.addWidget(self.temp_spin,    0, 1)
        rx_grid.addWidget(self.bw_spin,      1, 0)
        rx_grid.addWidget(self.ebno_spin,    1, 1)
        rx_grid.setColumnStretch(0, 1)
        rx_grid.setColumnStretch(1, 1)

        form_lay.addStretch()     # keeps bottom padding inside scroll

        # 4) Action buttons  (pinned row)
        button_wrap = QWidget(objectName="button_container")
        outer.addWidget(button_wrap)       # **outside** the scroll area
        btn_lay = QHBoxLayout(button_wrap)
        btn_lay.setContentsMargins(0, 0, 0, 0)
        btn_lay.setSpacing(16)

        self.calculate_button = QPushButton("Calculate Link Budget", objectName="calculate_button")
        self.generate_report_button = QPushButton("Generate PDF Report", objectName="generate_report_button")
        for b in (self.calculate_button, self.generate_report_button):
            b.setFixedHeight(40)
            b.setFont(QFont("Inter", 11))
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_lay.addStretch()
        btn_lay.addWidget(self.calculate_button, 1)
        btn_lay.addWidget(self.generate_report_button, 1)
        btn_lay.addStretch()

    # ------------------------------------------------------------------ Results tab
    def setup_results_tab(self):
        lay = QVBoxLayout(self.results_tab)
        lay.setContentsMargins(24, 24, 24, 24)

        res_sec = CollapsibleSection("Link Budget Results")
        lay.addWidget(res_sec)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setHorizontalSpacing(24)
        res_sec.content_layout.addLayout(form)

        self.received_power_label = QLabel("-- dBm")
        self.cn_ratio_label       = QLabel("-- dB")
        self.ber_label            = QLabel("--")
        self.link_margin_label    = QLabel("-- dB")
        form.addRow("Received Power:",                 self.received_power_label)
        form.addRow("Carrier‑to‑Noise Ratio (C/N):",   self.cn_ratio_label)
        form.addRow("Bit Error Rate (BER):",           self.ber_label)
        form.addRow("Link Margin:",                    self.link_margin_label)

        self.link_status = QLabel("", objectName="link_status",
                                   alignment=Qt.AlignmentFlag.AlignCenter)
        res_sec.content_layout.addWidget(self.link_status)
        lay.addStretch()

    # ------------------------------------------------------------------ Analysis tab
    def setup_analysis_tab(self):
        lay = QVBoxLayout(self.analysis_tab)
        lay.setContentsMargins(24, 24, 24, 24)
        msg = QLabel("Link Margin Analysis chart will be implemented in future updates.",
                     objectName="analysis_label",
                     alignment=Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(msg)

    # ------------------------------------------------------------------ Connections
    def setup_connections(self):
        self.calculate_button.clicked.connect(self.calculate_link_budget)
        self.generate_report_button.clicked.connect(self.generate_pdf_report)
        self.prop_model_combo.currentTextChanged.connect(self.on_model_changed)
        self.tx_power_unit.currentTextChanged.connect(self.on_power_unit_changed)

    # ───────────────────────────────────────────────────────────────── calculation
    @pyqtSlot()
    def calculate_link_budget(self):
        if self.prop_model_combo.currentText() != "AWGN (Additive White Gaussian Noise)":
            QMessageBox.information(self, "Model not implemented",
                                    "Only AWGN is implemented right now. Other models are coming soon!")
            return
        try:
            tx_pwr = self.tx_power_spin.spin_box.value()
            if self.tx_power_unit.currentText() == "W":
                tx_pwr = 10 * np.log10(tx_pwr * 1000)  # W → dBm

            tx_gain = self.tx_gain_spin.spin_box.value()
            rx_gain = self.rx_gain_spin.spin_box.value()
            fspl    = self.fspl_spin.spin_box.value()
            atm     = self.atm_loss_spin.spin_box.value()
            temp    = self.temp_spin.spin_box.value()
            bw      = self.bw_spin.spin_box.value()
            req_ebn = self.ebno_spin.spin_box.value()

            rx_power = tx_pwr + tx_gain + rx_gain - fspl - atm
            k = 1.38e-23  # Boltzmann constant
            noise_power = 10 * np.log10(k * temp * bw) + 30  # Convert to dBm
            cn = rx_power - noise_power
            margin = cn - req_ebn
            ber = 0.5 * np.exp(-10 ** (margin / 10) / 2)

            self.received_power_label.setText(f"{rx_power:.2f} dBm")
            self.cn_ratio_label.setText(f"{cn:.2f} dB")
            self.ber_label.setText(f"{ber:.2e}")
            self.link_margin_label.setText(f"{margin:.2f} dB")

            if margin < 0:
                self.link_status.setText("⚠️ Negative link margin — connection unstable")
                self.link_status.setStyleSheet("color:#FF5252; font-weight:bold;")
            elif margin < 3:
                self.link_status.setText("⚠️ Low link margin — may be unstable")
                self.link_status.setStyleSheet("color:#FFA726; font-weight:bold;")
            else:
                self.link_status.setText("✅ Link margin sufficient — stable connection expected")
                self.link_status.setStyleSheet("color:#66BB6A; font-weight:bold;")

            self.tabs.setCurrentWidget(self.results_tab)

        except Exception as e:
            QMessageBox.warning(self, "Calculation error", str(e))

    # ───────────────────────────────────────────────────────────────── PDF report
    def generate_pdf_report(self):
        fname, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", str(Path.home() / "link_budget_report.pdf"), "PDF (*.pdf)"
        )
        if not fname:
            return
        try:
            c = canvas.Canvas(fname, pagesize=letter)
            w, h = letter
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, h - 50, "Link Budget Analysis Report")
            c.setFont("Helvetica", 10)
            c.drawString(50, h - 70, f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}")
                
            # Input params
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, h - 100, "Input Parameters")
            params = [
                ("Transmit Power", f"{self.tx_power_spin.spin_box.value()} {self.tx_power_unit.currentText()}"),
                ("Transmitter Gain", f"{self.tx_gain_spin.spin_box.value()} dBi"),
                ("Carrier Frequency", f"{self.freq_spin.spin_box.value()} GHz"),
                ("Free Space Path Loss", f"{self.fspl_spin.spin_box.value()} dB"),
                ("Atmospheric Loss", f"{self.atm_loss_spin.spin_box.value()} dB"),
                ("Receiver Gain", f"{self.rx_gain_spin.spin_box.value()} dBi"),
                ("System Temperature", f"{self.temp_spin.spin_box.value()} K"),
                ("Bandwidth", f"{self.bw_spin.spin_box.value()} Hz"),
                ("Required Eb/No", f"{self.ebno_spin.spin_box.value()} dB")
            ]
            y = h - 120
            for p, v in params:
                y -= 18
                c.setFont("Helvetica", 10)
                c.drawString(70, y, f"{p}:")
                c.drawString(230, y, str(v))

            # Results
            c.setFont("Helvetica-Bold", 12)
            y -= 36
            c.drawString(50, y, "Link Budget Results")
            results = [
                ("Received Power", self.received_power_label.text()),
                ("Carrier-to-Noise Ratio", self.cn_ratio_label.text()),
                ("Bit Error Rate", self.ber_label.text()),
                ("Link Margin", self.link_margin_label.text())
            ]
            for r, v in results:
                y -= 18
                c.setFont("Helvetica", 10)
                c.drawString(70, y, f"{r}:")
                c.drawString(230, y, v)

            y -= 36
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Link Status")
            y -= 18
            c.setFont("Helvetica", 10)
            c.drawString(70, y, self.link_status.text())
            c.save()

            QMessageBox.information(self, "PDF created", f"Report saved to\n{fname}")
        except Exception as e:
            QMessageBox.warning(self, "PDF error", str(e))

    # ───────────────────────────────────────────────────────────────── slots
    @pyqtSlot(str)
    def on_model_changed(self, model: str):
        self.model_info_label.setText(
            "" if model == "AWGN (Additive White Gaussian Noise)"
            else "Only AWGN supported for now."
        )

    @pyqtSlot(str)
    def on_power_unit_changed(self, unit: str):
        if unit == "W":
            self.tx_power_spin.spin_box.setRange(0.001, 100.0)
            self.tx_power_spin.spin_box.setDecimals(3)
        else:
            self.tx_power_spin.spin_box.setRange(-50.0, 50.0)
            self.tx_power_spin.spin_box.setDecimals(2)

    # ------------------------------------------------------------------ style
    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget { background:#1E1E1E; color:#E0E0E0; font-family:'Inter',sans-serif; }

            /* Collapsible section header */
            #section_header { background:#252525; }
            #section_title  { color:#E0E0E0; }
            #accent_line    { background:#2196F3; min-height:2px; }

            /* Inputs */
            #input_label { color:#E0E0E0; }
            #helper_text { color:#9E9E9E; font-size:10px; }
            #dark_input, QDoubleSpinBox, QComboBox {
                background:#1A1A1A; border:1px solid #333; border-radius:4px;
                padding-left:6px; padding-right:6px; min-height:32px; color:#E0E0E0;
            }
            #dark_input:hover { border-color:#404040; }
            #dark_input:focus { border-color:#2196F3; background:#1C1C1C; }

            /* Buttons */
            QPushButton { border:none; border-radius:4px; padding:8px 16px; }
            #calculate_button { background:#2196F3; }
            #calculate_button:hover { background:#1976D2; }
            #generate_report_button { background:#66BB6A; }
            #generate_report_button:hover { background:#4CAF50; }

            /* Tabs */
            QTabWidget::pane { border:1px solid #424242; border-radius:6px; background:#252525; }
            QTabBar::tab { background:#2D2D2D; color:#9E9E9E; border-top-left-radius:4px;
                           border-top-right-radius:4px; padding:8px 16px; min-width:100px; }
            QTabBar::tab:selected { background:#252525; color:#E0E0E0; border-bottom:2px solid #2196F3; }
            QTabBar::tab:hover:!selected { color:#E0E0E0; }
        """)


# ──────────────────────────────────────────────────────────────────────────────
# Run
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = LinkBudgetView()
    w.resize(1100, 850)
    w.show()
    sys.exit(app.exec())
