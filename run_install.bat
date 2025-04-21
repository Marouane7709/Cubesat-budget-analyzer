@echo off
echo Starting CubeSat Budget Analyzer...

REM Set the project root directory
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

REM Check if venv exists, if not create it
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Ensure we're using the virtual environment's Python
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Failed to upgrade pip
    pause
    exit /b 1
)

REM Install wheel
echo Installing wheel...
pip install wheel
if errorlevel 1 (
    echo Failed to install wheel
    pause
    exit /b 1
)

REM Install core dependencies one by one to ensure they're properly installed
echo Installing dependencies...

echo Installing PyQt6...
pip install --no-cache-dir PyQt6
if errorlevel 1 goto :error

echo Installing pyqtgraph...
pip install --no-cache-dir pyqtgraph
if errorlevel 1 goto :error

echo Installing reportlab...
pip install --no-cache-dir reportlab
if errorlevel 1 goto :error

echo Installing other dependencies...
pip install --no-cache-dir matplotlib SQLAlchemy pandas openpyxl
if errorlevel 1 goto :error

REM Run the application
echo Running application...
python run.py

REM Keep the window open if there's an error
if errorlevel 1 (
    echo.
    echo Error running the application. Press any key to exit...
    pause >nul
)
goto :end

:error
echo.
echo Failed to install dependencies
echo Please try running as administrator if you haven't already
pause
exit /b 1

:end
exit /b 0 