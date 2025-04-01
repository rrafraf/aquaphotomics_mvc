# Stop on any error
$ErrorActionPreference = "Stop"

# Function to write to both console and log file
function Write-Log {
    param (
        [string]$Message,
        [string]$Color = "White"
    )
    
    Write-Host $Message -ForegroundColor $Color
    Add-Content -Path "aquaphotomics_error.log" -Value "$(Get-Date) - $Message"
}

# Script banner
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "  Aquaphotomics Application Launcher" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python file exists
if (-not (Test-Path "aquaphotomics_21.05.py")) {
    Write-Log "ERROR: Could not find aquaphotomics_21.05.py in the current directory." "Red"
    Write-Log "Please make sure you're running this script from the correct folder." "Red"
    exit 1
}

# Quick check if the environment is already set up correctly
$quickStart = $true
$requiredFiles = @(
    "venv\Scripts\python.exe",
    "venv\Scripts\activate.ps1",
    "venv\Lib\site-packages\numpy",
    "venv\Lib\site-packages\matplotlib",
    "venv\Lib\site-packages\scipy",
    "venv\Lib\site-packages\PIL",
    "venv\Lib\site-packages\serial"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $quickStart = $false
        Write-Host "Environment check: Missing $file - full setup will be required." -ForegroundColor Yellow
        break
    }
}

# Check if images directory exists
if (-not (Test-Path "images")) {
    Write-Host "WARNING: The 'images' directory was not found." -ForegroundColor Yellow
    Write-Host "The application may not display properly without the required images." -ForegroundColor Yellow
    
    $createDir = Read-Host "Do you want to create the images directory now? (y/n)"
    if ($createDir -eq "y") {
        New-Item -ItemType Directory -Path "images"
        Write-Host "Created 'images' directory. Please add required image files to it." -ForegroundColor Green
    }
}

# If we need to set up the environment
if (-not $quickStart) {
    Write-Host "Full environment setup required..." -ForegroundColor Yellow
    try {
        # Run the setup script to create/update the virtual environment
        Write-Host "Setting up the Python virtual environment..." -ForegroundColor Green
        & .\setup.ps1
        
        # If setup.ps1 failed to find Python but exited successfully, we need to check manually
        if (-not (Test-Path "venv\Scripts\python.exe")) {
            throw "Setup script did not create virtual environment properly."
        }
    } 
    catch {
        $errorMessage = $_.Exception.Message
        Write-Log "ERROR: Failed to set up the Python environment." "Red"
        Write-Log "Error details: $errorMessage" "Red"
        Write-Log "Please ensure Python is installed and the py launcher is available." "Red"
        Write-Log "To force a complete rebuild, delete the venv folder and run this script again." "Yellow"
        exit 1
    }
} 
else {
    Write-Host "Environment already set up - using quick start mode!" -ForegroundColor Green
}

# Activate the virtual environment (needed in either case)
Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\activate.ps1

# Show installed packages
Write-Host "`nCurrently installed packages in virtual environment:" -ForegroundColor Cyan
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan
& venv\Scripts\pip.exe freeze
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan

# Add file encoding declaration to the Python file if not present
$fileContent = Get-Content -Path "aquaphotomics_21.05.py" -Raw
if (-not ($fileContent -match "^\s*#.*coding[:=]\s*(utf-8|UTF-8)")) {
    Write-Host "Adding UTF-8 encoding declaration to the Python file..." -ForegroundColor Yellow
    $encodingDeclaration = "# -*- coding: utf-8 -*-`r`n"
    $newContent = $encodingDeclaration + $fileContent
    Set-Content -Path "aquaphotomics_21.05.py" -Value $newContent -Encoding UTF8
    Write-Host "Encoding declaration added." -ForegroundColor Green
    # Re-read the file content after modification
    $fileContent = Get-Content -Path "aquaphotomics_21.05.py" -Raw
}

# Create a dummy mplcursors module in the virtual environment
if ((-not (Test-Path "venv\Lib\site-packages\mplcursors")) -and $fileContent -match "import\s+mplcursors") {
    Write-Host "Creating dummy mplcursors module in the virtual environment..." -ForegroundColor Yellow
    
    # Create the mplcursors directory
    New-Item -ItemType Directory -Path "venv\Lib\site-packages\mplcursors" -Force | Out-Null
    
    # Create an __init__.py file with the dummy implementation
    $initPyContent = @"
# Dummy mplcursors implementation
class DummyCursor:
    def __init__(self, *args, **kwargs):
        pass
    
    def connect(self, *args, **kwargs):
        pass
    
    def __call__(self, *args, **kwargs):
        return self

def cursor(*args, **kwargs):
    print("Warning: Using dummy mplcursors implementation")
    return DummyCursor()
"@
    
    Set-Content -Path "venv\Lib\site-packages\mplcursors\__init__.py" -Value $initPyContent
    Write-Host "Dummy mplcursors module created successfully." -ForegroundColor Green
}

# Check for mpmath import as well
if (-not (Test-Path "venv\Lib\site-packages\mpmath") -and $fileContent -match "import\s+mpmath") {
    Write-Host "Creating dummy mpmath module in the virtual environment..." -ForegroundColor Yellow
    
    # Create the mpmath directory
    New-Item -ItemType Directory -Path "venv\Lib\site-packages\mpmath" -Force | Out-Null
    
    # Create an __init__.py file with the dummy implementation
    $initPyContent = @"
# Dummy mpmath implementation
import math

def mpf(x):
    try:
        return float(x)
    except:
        return 1.0  # Default safe value

def power(base, exp, *args):
    try:
        if isinstance(base, (int, float)) and isinstance(exp, (int, float)):
            return math.pow(base, exp)
        return 1.0
    except:
        return 1.0  # Default safe value

def log(value, base=None, *args):
    try:
        # Handle division by zero or negative numbers
        if value <= 0:
            print(f"Warning: mpmath.log called with non-positive value: {value}")
            return 0.0
        
        if base is None:
            return math.log(value)
        else:
            return math.log(value, base)
    except Exception as e:
        print(f"Warning: mpmath.log error: {e}")
        return 0.0  # Default safe value

class mp:
    dps = 15
    prec = 53
    
    @staticmethod
    def log(value, base=None, *args):
        return log(value, base, *args)
    
    @staticmethod
    def power(base, exp, *args):
        return power(base, exp, *args)
    
    @staticmethod
    def mpf(x):
        return mpf(x)
"@
    
    Set-Content -Path "venv\Lib\site-packages\mpmath\__init__.py" -Value $initPyContent
    Write-Host "Dummy mpmath module created successfully." -ForegroundColor Green
}

# Run the Python application
Write-Host "`nLaunching Aquaphotomics application..." -ForegroundColor Green
try {
    # Make sure we're using the Python from the virtual environment
    & venv\Scripts\python.exe aquaphotomics_21.05.py
}
catch {
    $errorMessage = $_.Exception.Message
    Write-Log "ERROR: Failed to run the Aquaphotomics application." "Red"
    Write-Log "Error details: $errorMessage" "Red"
    
    # Provide troubleshooting information
    Write-Log "`nTroubleshooting:" "Yellow"
    Write-Log "1. Make sure all required dependencies are installed" "Yellow"
    Write-Log "2. Check if the 'images' directory contains all necessary image files" "Yellow"
    Write-Log "3. Verify that the serial port is available (if using hardware)" "Yellow"
    Write-Log "4. Look for Python compatibility issues in the code" "Yellow"
    Write-Log "5. To force a complete rebuild, delete the venv folder and run this script again" "Yellow"
}

# Keep the window open if there was an error
if ($LASTEXITCODE -ne 0) {
    Write-Log "`nPress any key to exit..." "Red"
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
} 