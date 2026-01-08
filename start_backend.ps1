# Backend Startup Script for Windows PowerShell
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RED AI Backend Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to the script's directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if we're in the backend directory
if (-not (Test-Path "requirements.txt")) {
    Write-Host "ERROR: requirements.txt not found!" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "Please make sure this script is in the backend folder." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found. Creating one..." -ForegroundColor Yellow
    Write-Host "Using Python 3.12 or 3.13..." -ForegroundColor Cyan
    Write-Host ""
    
    # Try Python 3.12 first, then 3.13, then default
    py -3.12 -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Trying Python 3.13..." -ForegroundColor Yellow
        py -3.13 -m venv venv
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Trying default Python..." -ForegroundColor Yellow
            python -m venv venv
            if ($LASTEXITCODE -ne 0) {
                Write-Host "ERROR: Failed to create virtual environment!" -ForegroundColor Red
                Write-Host "Please make sure Python 3.12 or 3.13 is installed." -ForegroundColor Yellow
                Read-Host "Press Enter to exit"
                exit 1
            }
        }
    }
    Write-Host "Virtual environment created successfully!" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& "venv\Scripts\Activate.ps1"

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Cyan
try {
    # Use Python from venv if available
    if (Test-Path "venv\Scripts\python.exe") {
        & "venv\Scripts\python.exe" -c "import fastapi" 2>$null
    } else {
        python -c "import fastapi" 2>$null
    }
    if ($LASTEXITCODE -ne 0) {
        throw "FastAPI not found"
    }
    Write-Host "Dependencies are installed." -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "Dependencies not found. Installing..." -ForegroundColor Yellow
    Write-Host ""
    
    # Use Python from venv if available, otherwise use py launcher
    if (Test-Path "venv\Scripts\python.exe") {
        & "venv\Scripts\python.exe" -m pip install --upgrade pip
        & "venv\Scripts\python.exe" -m pip install -r requirements.txt
    } else {
        py -3.12 -m pip install --upgrade pip
        if ($LASTEXITCODE -ne 0) {
            py -3.13 -m pip install --upgrade pip
        }
        py -3.12 -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            py -3.13 -m pip install -r requirements.txt
        }
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "Dependencies installed successfully!" -ForegroundColor Green
    Write-Host ""
}

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found!" -ForegroundColor Yellow
    Write-Host "Please create a .env file with your OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host "Example: 'OPENAI_API_KEY=your_key_here' | Out-File -FilePath .env -Encoding utf8" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to continue (or Ctrl+C to cancel)"
}

# Run the server
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Backend Server..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Use Python from venv if available, otherwise try py launcher
if (Test-Path "venv\Scripts\python.exe") {
    & "venv\Scripts\python.exe" run.py
} else {
    python run.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Trying with Python 3.12..." -ForegroundColor Yellow
        py -3.12 run.py
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Trying with Python 3.13..." -ForegroundColor Yellow
            py -3.13 run.py
            if ($LASTEXITCODE -ne 0) {
                Write-Host ""
                Write-Host "ERROR: Failed to start server!" -ForegroundColor Red
                Write-Host "Make sure Python 3.12 or 3.13 is installed and virtual environment is activated." -ForegroundColor Yellow
                Read-Host "Press Enter to exit"
                exit 1
            }
        }
    }
}

