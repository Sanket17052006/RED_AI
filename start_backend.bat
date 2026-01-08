@echo off
REM Backend Startup Script for Windows
echo ========================================
echo   RED AI Backend Startup Script
echo ========================================
echo.

REM Change to the script's directory
cd /d "%~dp0"

REM Check if we're in the backend directory
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found!
    echo Current directory: %CD%
    echo Please make sure this script is in the backend folder.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating one...
    echo Using Python 3.12 or 3.13...
    echo.
    py -3.12 -m venv venv
    if errorlevel 1 (
        echo Trying Python 3.13...
        py -3.13 -m venv venv
        if errorlevel 1 (
            echo Trying default Python...
            python -m venv venv
            if errorlevel 1 (
                echo ERROR: Failed to create virtual environment!
                echo Please make sure Python 3.12 or 3.13 is installed.
                pause
                exit /b 1
            )
        )
    )
    echo Virtual environment created successfully!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Dependencies not found. Installing...
    echo.
    REM Try to use the Python from venv, or fallback to py launcher
    if exist "venv\Scripts\python.exe" (
        venv\Scripts\python.exe -m pip install --upgrade pip
        venv\Scripts\python.exe -m pip install -r requirements.txt
    ) else (
        py -3.12 -m pip install --upgrade pip
        if errorlevel 1 (
            py -3.13 -m pip install --upgrade pip
        )
        py -3.12 -m pip install -r requirements.txt
        if errorlevel 1 (
            py -3.13 -m pip install -r requirements.txt
            if errorlevel 1 (
                echo ERROR: Failed to install dependencies!
                pause
                exit /b 1
            )
        )
    )
    echo Dependencies installed successfully!
    echo.
) else (
    echo Dependencies are installed.
    echo.
)

REM Check for .env file
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please create a .env file with your OPENAI_API_KEY
    echo Example: echo OPENAI_API_KEY=your_key_here ^> .env
    echo.
    pause
)

REM Run the server
echo ========================================
echo   Starting Backend Server...
echo ========================================
echo Server will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Press Ctrl+C to stop the server
echo.
REM Use Python from venv if available, otherwise use py launcher
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe run.py
) else (
    python run.py
    if errorlevel 1 (
        echo.
        echo Trying with Python 3.12...
        py -3.12 run.py
        if errorlevel 1 (
            echo Trying with Python 3.13...
            py -3.13 run.py
            if errorlevel 1 (
                echo ERROR: Failed to start server!
                echo Make sure Python 3.12 or 3.13 is installed and virtual environment is activated.
                pause
                exit /b 1
            )
        )
    )
)

pause

