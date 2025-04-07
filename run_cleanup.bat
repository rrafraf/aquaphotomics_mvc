@echo off
REM This batch file launches PowerShell with execution policy bypass
REM and runs the cleanup.ps1 script

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& '%~dp0cleanup.ps1'"
pause 