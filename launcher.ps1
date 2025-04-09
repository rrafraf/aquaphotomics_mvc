# Stop on any error
$ErrorActionPreference = "Stop"

# Function to write to both console and log file
function Write-Log {
    param (
        [string]$Message,
        [string]$Color = "White",
        [string]$Command = "",
        [string]$CommandOutput = ""
    )
    
    # Get script name dynamically
    $scriptName = $MyInvocation.ScriptName | Split-Path -Leaf
    
    # Format the log message
    $logMessage = "[$scriptName] $Message"
    
    # Add command context if provided
    if ($Command) {
        $logMessage += " (Command: $Command)"
    }
    
    # Output the message
    Write-Host $logMessage -ForegroundColor $Color
    Add-Content -Path "aquaphotomics_error.log" -Value "$(Get-Date) - $logMessage"
    
    # Add command output if provided
    if ($CommandOutput) {
        # Split properly by actual newlines
        $outputLines = $CommandOutput -split "`r`n|`r|`n"
        
        # Only add the header if there's actual output
        if ($outputLines.Count -gt 0 -and $outputLines[0].Trim() -ne "") {
            $headerMessage = "[$scriptName] Command output:"
            Write-Host $headerMessage -ForegroundColor DarkGray
            Add-Content -Path "aquaphotomics_error.log" -Value "$(Get-Date) - $headerMessage"
            
            foreach ($line in $outputLines) {
                if ($line.Trim() -ne "") {
                    $outputMessage = "[$scriptName]   $line"
                    Write-Host $outputMessage -ForegroundColor DarkGray
                    Add-Content -Path "aquaphotomics_error.log" -Value "$(Get-Date) - $outputMessage"
                }
            }
        }
    }
}

# Function to execute a command and capture output
function Invoke-CommandWithLogging {
    param (
        [string]$Command,
        [string]$Message,
        [string]$Color = "White"
    )
    
    Write-Log $Message $Color $Command
    
    try {
        # Determine if this is a script file to execute or a regular command
        if ($Command.StartsWith(".\") -and $Command.EndsWith(".ps1")) {
            # This is a PowerShell script - execute it directly
            $output = & $Command 2>&1
            $exitCode = $LASTEXITCODE
        }
        # Handle PowerShell commands vs external commands differently
        elseif ($Command -match "^(Get-|Set-|Test-|New-|Remove-|Import-|Export-|ConvertTo-|ConvertFrom-)") {
            # This is a PowerShell cmdlet - use Invoke-Expression
            $output = Invoke-Expression "$Command 2>&1" -ErrorVariable errorVar
            $exitCode = if ($?) { 0 } else { 1 }
        }
        elseif ($Command -match "^(pip|python)(\s|$)") {
            # Use cmd.exe for Python and pip commands to preserve output formatting
            $tempFile = [System.IO.Path]::GetTempFileName()
            cmd /c "$Command > `"$tempFile`" 2>&1"
            $exitCode = $LASTEXITCODE
            $output = Get-Content -Path $tempFile -Raw
            Remove-Item -Path $tempFile -Force
        } 
        else {
            # Regular PowerShell command
            $output = Invoke-Expression "$Command 2>&1" -ErrorVariable errorVar
            $exitCode = if ($?) { 0 } else { 1 }
        }
        
        # Log command output without the empty "Command output:" line
        if ($output) {
            # Use a default color instead of empty string
            Write-Log " " "DarkGray" "" $output
        }
        
        return @{
            Success = ($exitCode -eq 0)
            Output = $output
            ExitCode = $exitCode
        }
    }
    catch {
        $errorMessage = $_.Exception.Message
        Write-Log "Command execution failed" "Red" $Command -CommandOutput $errorMessage
        return @{
            Success = $false
            Output = $errorMessage
            ExitCode = 1
        }
    }
}

# Script banner
Write-Log "=========================================================" "Cyan"
Write-Log "  Aquaphotomics Application Launcher (Modular Edition)" "Cyan"
Write-Log "=========================================================" "Cyan"
Write-Log "" "White"

# Target Python file
$PYTHON_SCRIPT = "aquaphotomics_refactored.py"

# Only check if venv folder exists
$venvExists = Test-Path "venv"

# If venv doesn't exist, create it using setup.ps1
if (-not $venvExists) {
    Write-Log "Python virtual environment not found - setting up environment..." "Yellow"
    try {
        # Run setup.ps1 directly in the current process
        Write-Log "Running setup script" "Green" ".\setup.ps1"
        # Dot-source to run in current process
        . .\setup.ps1
        
        # Verify venv was created
        if (-not (Test-Path "venv")) {
            throw "Setup script completed but virtual environment was not created properly"
        }
    }
    catch {
        $errorMessage = $_.Exception.Message
        Write-Log "ERROR: Failed to set up the Python environment" "Red"
        Write-Log "Error details: $errorMessage" "Red"
        Write-Log "Please ensure Python is installed and available in your PATH" "Red"
        exit 1
    }
}

# Activate the virtual environment 
Write-Log "Activating virtual environment" "Green" ".\venv\Scripts\activate.ps1"
try {
    # Dot-source the activation script to ensure it runs in the current scope
    . .\venv\Scripts\activate.ps1
    Write-Log "Virtual environment activated successfully" "Green"
} catch {
    $errorMessage = $_.Exception.Message
    Write-Log "WARNING: Failed to activate virtual environment" "Yellow" -CommandOutput $errorMessage
    Write-Log "Will attempt to continue with absolute path to Python executable" "Yellow"
}

# Show installed packages for debugging purposes only (if verbose mode is enabled)
if ($env:AQUA_DEBUG -eq "1") {
    Write-Log "Checking installed packages in virtual environment:" "Cyan"
    Write-Log "--------------------------------------------------------" "Cyan"
    $result = Invoke-CommandWithLogging "pip list" "Retrieving installed packages" "White"
    Write-Log "--------------------------------------------------------" "Cyan"
}

# Check if we already have an encoding declaration (without logging the entire file content)
# First just check the first line to avoid reading and logging the entire file
$firstLine = Get-Content -Path $PYTHON_SCRIPT -TotalCount 1
$needsEncoding = -not ($firstLine -match "coding[:=]\s*(utf-8|UTF-8)")

if ($needsEncoding) {
    Write-Log "Adding UTF-8 encoding declaration to the Python file..." "Yellow"
    $fileContent = Get-Content -Path $PYTHON_SCRIPT -Raw
    $encodingDeclaration = "# -*- coding: utf-8 -*-`r`n"
    $newContent = $encodingDeclaration + $fileContent
    Set-Content -Path $PYTHON_SCRIPT -Value $newContent -Encoding UTF8
    Write-Log "Encoding declaration added." "Green"
}

# Run the Python application
Write-Log "`nLaunching Aquaphotomics application..." "Green"

# Run Python with improved error handling
try {
    Write-Log "Running Python application: $PYTHON_SCRIPT" "Green"
    
    # Create a more detailed log file for better error capture
    $errorLogFile = "python_error.log"
    
    # Check if we have an activated Python environment
    $pythonCommand = if (Test-Path Env:\VIRTUAL_ENV) { 
        "python" # Use activated environment's python
    } else {
        "venv\Scripts\python.exe" # Fallback to direct path
    }
    
    Write-Log "Using Python: $pythonCommand" "Green"
    
    # Use Start-Process to get better error handling
    $processInfo = Start-Process -FilePath $pythonCommand -ArgumentList $PYTHON_SCRIPT -NoNewWindow -Wait -PassThru -RedirectStandardError $errorLogFile
    $exitCode = $processInfo.ExitCode
    
    if ($exitCode -ne 0) {
        Write-Log "ERROR: Application exited with code $exitCode" "Red"
        
        # Check if we have error logs to display
        if (Test-Path $errorLogFile) {
            $errorOutput = Get-Content -Path $errorLogFile -Raw
            if ($errorOutput) {
                Write-Log "Python Error Output:" "Red" -CommandOutput $errorOutput
            }
        }
        
        # Keep the window open if there was an error
        Write-Log "`nPress any key to exit..." "Red"
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    else {
        Write-Log "Application exited successfully." "Green"
    }
    
    # Clean up error log
    if (Test-Path $errorLogFile) {
        Remove-Item $errorLogFile -Force
    }
}
catch {
    $errorMessage = $_.Exception.Message
    Write-Log "ERROR: Failed to run the Python application." "Red"
    Write-Log "Error details: $errorMessage" "Red"
} 