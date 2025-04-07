# Cleanup script for Aquaphotomics repository
Write-Host "Starting cleanup process..." -ForegroundColor Green

# 1. Remove Python bytecode files
Write-Host "Removing Python bytecode files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Include "*.pyc","*.pyo","*.pyd" | Where-Object { $_.FullName -notlike "*\venv\*" } | ForEach-Object { Remove-Item $_.FullName -Force; Write-Host "Removed: $($_.FullName)" -ForegroundColor Gray }

# 2. Remove log files (except the most recent)
Write-Host "Cleaning up log files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Include "*.log" -File | ForEach-Object { if ($_.Name -ne "aquaphotomics_error.log") { Remove-Item $_.FullName -Force; Write-Host "Removed: $($_.FullName)" -ForegroundColor Gray } }

# 3. Remove temporary files
Write-Host "Removing temporary files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Include "*.tmp","*.bak","*.temp" | ForEach-Object { Remove-Item $_.FullName -Force; Write-Host "Removed: $($_.FullName)" -ForegroundColor Gray }

# 4. Clean __pycache__ directories (except in venv)
Write-Host "Cleaning __pycache__ directories..." -ForegroundColor Yellow
Get-ChildItem -Path . -Directory -Recurse -Filter "__pycache__" | Where-Object { $_.FullName -notlike "*\venv\*" } | ForEach-Object { Remove-Item $_.FullName -Recurse -Force; Write-Host "Removed directory: $($_.FullName)" -ForegroundColor Gray }

# Check critical files
Write-Host "Cleanup completed!" -ForegroundColor Green
Write-Host "The following critical files were preserved:" -ForegroundColor Cyan

$criticalFiles = @("run_launcher.bat", "launcher.ps1", "setup.ps1", "aquaphotomics_refactored.py", "requirements.txt", "LAUNCHER_FLOW.md")

foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file" -ForegroundColor Green
    } else {
        Write-Host "✗ $file" -ForegroundColor Red
    }
}

Write-Host "Press Enter to exit..." -ForegroundColor Yellow
pause 