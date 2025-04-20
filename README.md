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
