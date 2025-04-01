# Stop on any error
$ErrorActionPreference = "Stop"

Write-Host "Setting up Python virtual environment..." -ForegroundColor Green

# Check if Python is available via py launcher
$pythonPath = $null
$pythonVersion = $null

try {
    $pyLauncherExists = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncherExists) {
        $versionInfo = & py -V 2>&1
        if ($versionInfo -match "Python\s+(\d+\.\d+)") {
            $pythonPath = "py"
            $pythonVersion = $matches[1]
            Write-Host "Found Python $pythonVersion via py launcher: $versionInfo" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "Python launcher (py) not found or not working properly." -ForegroundColor Red
    Write-Host "Please ensure Python is installed and the py launcher is available." -ForegroundColor Yellow
    exit 1
}

if (-not $pythonPath) {
    Write-Host "Python not found!" -ForegroundColor Red
    Write-Host "Please install Python and ensure the py launcher is available." -ForegroundColor Yellow
    exit 1
}

Write-Host "Using Python at: $pythonPath" -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating new Python $pythonVersion virtual environment..." -ForegroundColor Green
    & $pythonPath -m venv venv
} else {
    Write-Host "Virtual environment already exists, checking version..." -ForegroundColor Yellow
    
    # Try to determine Python version in existing venv
    $venvPython = ".\venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        $venvVersion = & $venvPython -V 2>&1
        if ($venvVersion -match "Python\s+(\d+\.\d+)") {
            $pythonVersion = $matches[1]
            Write-Host "Existing virtual environment is using Python $pythonVersion. Continuing..." -ForegroundColor Green
        } else {
            Write-Host "Could not determine Python version in existing environment." -ForegroundColor Red
            Write-Host "Continuing with existing virtual environment. This may cause compatibility issues." -ForegroundColor Yellow
        }
    } else {
        Write-Host "Could not find Python in existing environment." -ForegroundColor Red
        Write-Host "Continuing with existing virtual environment. This may cause compatibility issues." -ForegroundColor Yellow
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
.\venv\Scripts\activate.ps1

# Upgrade pip within the virtualenv
Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip

# Install requirements
Write-Host "Installing dependencies..." -ForegroundColor Green
pip install -r requirements.txt

Write-Host "`nSetup completed successfully!" -ForegroundColor Green
Write-Host "Python $pythonVersion virtual environment is now active" -ForegroundColor Cyan
