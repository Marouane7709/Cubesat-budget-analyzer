# CubeSat Budget Analyzer

A Python-based tool for analyzing and managing CubeSat project budgets.

## Features

- Budget tracking and analysis for Cubesatellite missions
- Interactive visualization of budget allocation
- Report generation
- Excel import/export support
- Modern PyQt6-based GUI

## Installation

```bash
pip install cubesat-budget-analyzer
```

## Development Setup

To set up the project for development:

```bash
git clone https://github.com/Marouane7709/cubesat-budget-analyzer.git
cd cubesat-budget-analyzer
pip install -e .
```

## Packaging and Distribution

The application is packaged for Windows and macOS using PyInstaller, a cross-platform tool that converts Python applications into standalone executables.

### Windows Packaging
- Executable created using: `pyinstaller --onefile --windowed --icon=assets/icon.ico main.py`
- Installer created using: Inno Setup
- Dependencies bundled automatically by PyInstaller
- Installer size: ~50MB
- Tested on Windows 10 & 11

### macOS Packaging
- Application bundle created using: `pyinstaller --onefile --windowed --icon=assets/icon.icns main.py`
- DMG installer created using: create-dmg
- Dependencies bundled automatically by PyInstaller
- Installer size: ~55MB
- Tested on macOS 10.15+ (Catalina and newer)

### Installation Verification
- Windows: Verified installation on clean Windows 10/11 VMs
- macOS: Verified installation on clean macOS 10.15+ VMs
- Both platforms: Confirmed proper functionality of all features
- Both platforms: Verified proper handling of user permissions and data storage

### OS-Specific Considerations
- Windows:
  - Requires .NET Framework 4.5 or newer
  - Uses Windows Registry for application settings
  - Supports both 32-bit and 64-bit systems

- macOS:
  - Requires macOS 10.15 or newer
  - Uses ~/Library/Application Support for application data
  - Supports both Intel and Apple Silicon (M1/M2) processors

### Versioning
- Follows semantic versioning (MAJOR.MINOR.PATCH)
- Installer includes automatic update checking
- Previous versions can be cleanly uninstalled

## Dependencies

- PyQt6
- SQLAlchemy
- matplotlib
- pyqtgraph
- reportlab
- pandas
- openpyxl

## License

MIT License

## Project Structure

```
cube_sat_budget/
├── model/                 # Data models and calculations
│   ├── database.py       # SQLAlchemy setup
│   ├── link_budget.py    # Link budget calculations
│   └── data_budget.py    # Data budget calculations
├── view/                 # UI components
│   ├── main_view.py      # Main window
│   ├── link_budget_view.py
│   └── data_budget_view.py
├── controller/           # Application logic
│   └── theme_manager.py  # Theme management
├── qss/                  # Qt stylesheets
│   ├── dark.qss
│   └── light.qss
└── main.py              # Application entry point
```

## Dependencies and Licenses

- PyQt6: GPL v3
- SQLAlchemy: MIT
- pyqtgraph: MIT
- reportlab: BSD
- pandas: BSD
- openpyxl: MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Acknowledgments

- PyQt6 team for the excellent GUI framework
- SQLAlchemy team for the ORM
- All other open-source projects used in this application 
