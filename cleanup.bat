@echo off
echo Starting cleanup process...

REM Remove Python bytecode files (except in venv)
echo Removing Python bytecode files...
for /r %%F in (*.pyc *.pyo *.pyd) do (
    echo %%F | findstr /i /c:"venv" >nul || (
        del "%%F"
        echo Removed: %%F
    )
)

REM Remove __pycache__ directories (except in venv)
echo Cleaning __pycache__ directories...
for /d /r %%D in (__pycache__) do (
    echo %%D | findstr /i /c:"venv" >nul || (
        rd /s /q "%%D"
        echo Removed directory: %%D
    )
)

REM Remove temporary files
echo Removing temporary files...
for /r %%F in (*.tmp *.bak *.temp) do (
    del "%%F" 2>nul
)

REM Remove old log files (keep aquaphotomics_error.log)
echo Cleaning up log files...
for %%F in (*.log) do (
    if not "%%~nxF"=="aquaphotomics_error.log" (
        del "%%F"
        echo Removed: %%F
    )
)

echo.
echo Cleanup completed!
echo.
echo Checking critical files:
for %%F in (
    run_launcher.bat
    launcher.ps1
    setup.ps1
    aquaphotomics_refactored.py
    requirements.txt
    LAUNCHER_FLOW.md
) do (
    if exist "%%F" (
        echo [✓] %%F
    ) else (
        echo [✗] %%F
    )
)

echo.
pause 