@echo off

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b
) else (
    echo Python is already installed.
)

REM Upgrade pip (user level)
echo Upgrading pip...
python -m pip install --upgrade pip --user

REM Install required libraries at user level
echo Installing pandas...
python -m pip install pandas --user

echo Installing numpy...
python -m pip install numpy --user

echo Installing streamlit...
python -m pip install streamlit --user

echo Installation completed.
pause
