@echo off
REM This batch file launches PowerShell with execution policy bypass
REM and runs the launcher.ps1 script

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& '%~dp0launcher.ps1'"
pause 