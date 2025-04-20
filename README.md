# CubeSat Budget Analyzer

A Python desktop application for analyzing CubeSat link and data budgets using PyQt6, SQLAlchemy, and other open-source libraries.

## Features

- **Link Budget Analysis**
  - Calculate received power, C/N ratio, BER, and link margin
  - Support for multiple propagation models (AWGN implemented)
  - Visualize results with interactive charts
  - Export analysis to PDF

- **Data Budget Analysis**
  - Calculate data generation, downlink capacity, and storage requirements
  - Generate recommendations for storage optimization
  - Visualize storage usage and data backlog
  - Export analysis to CSV and Excel

- **Project Management**
  - Save and load projects
  - Auto-save functionality
  - Import/export configurations
  - Light/dark theme support

## Requirements

- Python 3.8 or higher
- PyQt6
- SQLAlchemy
- pyqtgraph
- reportlab
- pandas
- openpyxl

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cube_sat_budget.git
cd cube_sat_budget
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Log in with any username/password (authentication is currently a stub)

3. Use the tabs to switch between Link Budget and Data Budget analysis

4. Enter parameters and click "Calculate" to see results

5. Export results using the appropriate buttons

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

## License

This project is licensed under the MIT License - see the LICENSE file for details.

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