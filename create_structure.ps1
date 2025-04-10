# PowerShell Script to Create Aquaphotomics Project Structure Scaffold

# Stop on errors
$ErrorActionPreference = "Stop"

function Write-HostColored {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

Write-HostColored "Creating project structure for Aquaphotomics..." "Cyan"

# --- Create Root Level Files/Dirs ---
Write-HostColored "Creating root directories and files..." "Green"

# Docs (Assuming it exists from previous steps, ensure flowcharts exists)
New-Item -ItemType Directory -Path "docs/flowcharts" -ErrorAction SilentlyContinue | Out-Null

# Source Directory
New-Item -ItemType Directory -Path "src" -ErrorAction SilentlyContinue | Out-Null
Write-Host "  - Created src/"

# Assets Directory
New-Item -ItemType Directory -Path "assets" -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType Directory -Path "assets/images" -ErrorAction SilentlyContinue | Out-Null
Write-Host "  - Created assets/images/"

# Tests Directory
New-Item -ItemType Directory -Path "tests" -ErrorAction SilentlyContinue | Out-Null
Write-Host "  - Created tests/"

# Root run script placeholder
@"
# Simple entry point to run the application from the project root
import sys
import os

# Add src directory to path to allow importing aquaphotomics package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

if __name__ == '__main__':
    # TODO: Import and run the main application function/class from src.aquaphotomics.main
    # from aquaphotomics.main import run_app
    # run_app()
    print("Placeholder run.py - Please implement application launch.")
"@ | Out-File -FilePath "run.py" -Encoding utf8
Write-Host "  - Created run.py"

# Empty requirements file
New-Item -ItemType File -Path "requirements.txt" -ErrorAction SilentlyContinue | Out-Null
Write-Host "  - Created requirements.txt"

# Basic .gitignore
@"
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environment
venv/
.venv/
env/
ENV/
*.env
*.venv

# Distribution / packaging
.eggs/
*.egg-info/
dist/
build/
wheels/
*.egg

# Logs and Databases
*.log
*.db
*.sqlite3

# OS generated files
.DS_Store
Thumbs.db

# Config (if sensitive, otherwise remove)
# config.yaml

# Temp files
*.tmp
*~
"@ | Out-File -FilePath ".gitignore" -Encoding utf8
Write-Host "  - Created .gitignore"

# --- Create Source Package Structure ---
Write-HostColored "Creating src/aquaphotomics package structure..." "Green"
$srcBase = "src/aquaphotomics"

# Main Package Directory + __init__
New-Item -ItemType Directory -Path $srcBase -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType File -Path "$srcBase/__init__.py" -ErrorAction SilentlyContinue | Out-Null
@"
# Makes 'aquaphotomics' a package
# Define package-level attributes like __version__ here later
# __version__ = "..."
"@ | Out-File -FilePath "$srcBase/__init__.py" -Encoding utf8
Write-Host "  - Created $srcBase/__init__.py"

# Core Logic Sub-package
$coreDir = "$srcBase/core"
New-Item -ItemType Directory -Path $coreDir -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType File -Path "$coreDir/__init__.py" -ErrorAction SilentlyContinue | Out-Null
Write-Host "  - Created $coreDir/__init__.py"
@"
# Core application logic (non-GUI)
"@ | Out-File -FilePath "$coreDir/__init__.py" -Encoding utf8

New-Item -ItemType File -Path "$coreDir/constants.py" -ErrorAction SilentlyContinue | Out-Null
@"
# Define hardware constants (e.g., WAVELENGTHS) and derived values (e.g., THETA) here.
import numpy as np

# Example:
# WAVELENGTHS = [660, 680, ...]
# NUM_CHANNELS = len(WAVELENGTHS)
# THETA = [(np.pi / 2) - ((2 * np.pi / NUM_CHANNELS) * j) for j in range(NUM_CHANNELS)]
"@ | Out-File -FilePath "$coreDir/constants.py" -Encoding utf8
Write-Host "  - Created $coreDir/constants.py"

New-Item -ItemType File -Path "$coreDir/exceptions.py" -ErrorAction SilentlyContinue | Out-Null
@"
# Define custom application-specific exceptions here.

class DataProcessingError(Exception):
    '''Exception raised for errors in data processing.'''
    pass

# Add other custom exceptions as needed
"@ | Out-File -FilePath "$coreDir/exceptions.py" -Encoding utf8
Write-Host "  - Created $coreDir/exceptions.py"

New-Item -ItemType File -Path "$coreDir/serial_device.py" -ErrorAction SilentlyContinue | Out-Null
@"
# Contains SerialDevice and MockSerialDevice classes for hardware communication.
# TODO: Move relevant classes from aquaphotomics_refactored.py here.
pass
"@ | Out-File -FilePath "$coreDir/serial_device.py" -Encoding utf8
Write-Host "  - Created $coreDir/serial_device.py"

New-Item -ItemType File -Path "$coreDir/measurement.py" -ErrorAction SilentlyContinue | Out-Null
@"
# Contains MeasurementData class and related data processing/calculation logic.
# TODO: Move relevant classes/functions from aquaphotomics_refactored.py here.
pass
"@ | Out-File -FilePath "$coreDir/measurement.py" -Encoding utf8
Write-Host "  - Created $coreDir/measurement.py"


# GUI Sub-package
$guiDir = "$srcBase/gui"
New-Item -ItemType Directory -Path $guiDir -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType File -Path "$guiDir/__init__.py" -ErrorAction SilentlyContinue | Out-Null
@"
# GUI related components (Tkinter specific code)
"@ | Out-File -FilePath "$guiDir/__init__.py" -Encoding utf8
Write-Host "  - Created $guiDir/__init__.py"

New-Item -ItemType File -Path "$guiDir/app.py" -ErrorAction SilentlyContinue | Out-Null
@"
# Contains the main AquaphotomicsApp Tkinter class.
# TODO: Move AquaphotomicsApp class definition here.
pass
"@ | Out-File -FilePath "$guiDir/app.py" -Encoding utf8
Write-Host "  - Created $guiDir/app.py"

New-Item -ItemType File -Path "$guiDir/dialogs.py" -ErrorAction SilentlyContinue | Out-Null
@"
# Contains Tkinter dialog classes (UserDialog, ConnectionDialog, SampleListDialog).
# TODO: Move dialog class definitions here.
pass
"@ | Out-File -FilePath "$guiDir/dialogs.py" -Encoding utf8
Write-Host "  - Created $guiDir/dialogs.py"

# Optional GUI Views Sub-package (Scaffold only)
$viewsDir = "$guiDir/views"
New-Item -ItemType Directory -Path $viewsDir -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType File -Path "$viewsDir/__init__.py" -ErrorAction SilentlyContinue | Out-Null
@"
# Optional: For separating distinct parts of the GUI view if needed later.
"@ | Out-File -FilePath "$viewsDir/__init__.py" -Encoding utf8
Write-Host "  - Created $viewsDir/__init__.py"


# Visualization Sub-package
$visDir = "$srcBase/visualization"
New-Item -ItemType Directory -Path $visDir -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType File -Path "$visDir/__init__.py" -ErrorAction SilentlyContinue | Out-Null
@"
# Plotting and visualization logic (Matplotlib specific code)
"@ | Out-File -FilePath "$visDir/__init__.py" -Encoding utf8
Write-Host "  - Created $visDir/__init__.py"

New-Item -ItemType File -Path "$visDir/figures.py" -ErrorAction SilentlyContinue | Out-Null
@"
# Contains FigureCollection and AquaphotomicsFigures classes.
# TODO: Move relevant classes from aquaphotomics_refactored.py here.
pass
"@ | Out-File -FilePath "$visDir/figures.py" -Encoding utf8
Write-Host "  - Created $visDir/figures.py"


# Configuration Sub-package
$configDir = "$srcBase/config"
New-Item -ItemType Directory -Path $configDir -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType File -Path "$configDir/__init__.py" -ErrorAction SilentlyContinue | Out-Null
@"
# Configuration management code
"@ | Out-File -FilePath "$configDir/__init__.py" -Encoding utf8
Write-Host "  - Created $configDir/__init__.py"

New-Item -ItemType File -Path "$configDir/manager.py" -ErrorAction SilentlyContinue | Out-Null
@"
# Contains the Config class for loading/managing config.yaml.
# TODO: Move Config class from config_manager.py here.
# Remember to update imports if the original config_manager.py used relative paths.
pass
"@ | Out-File -FilePath "$configDir/manager.py" -Encoding utf8
Write-Host "  - Created $configDir/manager.py"


# Main Entry Point Logic File
New-Item -ItemType File -Path "$srcBase/main.py" -ErrorAction SilentlyContinue | Out-Null
@"
# Main application entry point logic.
# This script initializes and runs the application.

# Example:
# from .gui.app import AquaphotomicsApp
#
# def run_app():
#     print("Starting Aquaphotomics App from main.py...") # Replace with version string later
#     app = AquaphotomicsApp()
#     app.mainloop()
#
# if __name__ == '__main__':
#     run_app()

print("Placeholder main.py - Please implement app initialization and launch.")
"@ | Out-File -FilePath "$srcBase/main.py" -Encoding utf8
Write-Host "  - Created $srcBase/main.py"


# --- Create Test Structure ---
Write-HostColored "Creating tests/ structure..." "Green"

# Test __init__
New-Item -ItemType File -Path "tests/__init__.py" -ErrorAction SilentlyContinue | Out-Null
Write-Host "  - Created tests/__init__.py"

# Core Tests
$testCoreDir = "tests/core"
New-Item -ItemType Directory -Path $testCoreDir -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType File -Path "$testCoreDir/__init__.py" -ErrorAction SilentlyContinue | Out-Null
Write-Host "  - Created $testCoreDir/__init__.py"

New-Item -ItemType File -Path "$testCoreDir/test_measurement.py" -ErrorAction SilentlyContinue | Out-Null
@"
# Placeholder for tests related to core/measurement.py
import unittest

class TestMeasurement(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
"@ | Out-File -FilePath "$testCoreDir/test_measurement.py" -Encoding utf8
Write-Host "  - Created $testCoreDir/test_measurement.py"

New-Item -ItemType File -Path "$testCoreDir/test_serial_device.py" -ErrorAction SilentlyContinue | Out-Null
@"
# Placeholder for tests related to core/serial_device.py
import unittest

class TestSerialDevice(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
"@ | Out-File -FilePath "$testCoreDir/test_serial_device.py" -Encoding utf8
Write-Host "  - Created $testCoreDir/test_serial_device.py"

# GUI Tests (Placeholder)
$testGuiDir = "tests/gui"
New-Item -ItemType Directory -Path $testGuiDir -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType File -Path "$testGuiDir/__init__.py" -ErrorAction SilentlyContinue | Out-Null
Write-Host "  - Created $testGuiDir/__init__.py"

# --- Done ---
Write-HostColored "`nProject structure scaffold created successfully." "Cyan"
Write-Host "Next steps:"
Write-Host "1. Review the generated structure."
Write-Host "2. Run 'python -m venv venv' and '.\venv\Scripts\Activate.ps1' (or use setup.ps1)."
Write-Host "3. Populate requirements.txt and run 'pip install -r requirements.txt'."
Write-Host "4. Gradually move code from 'aquaphotomics_refactored.py' into the 'src/aquaphotomics/' modules."
Write-Host "5. Update 'run.py' and 'src/aquaphotomics/main.py' to launch the app."
Write-Host "6. Consider modifying launcher scripts to choose between old/new app." 