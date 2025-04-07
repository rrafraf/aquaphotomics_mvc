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

# Check if Python entry point exists
$result = Invoke-CommandWithLogging "Test-Path $PYTHON_SCRIPT" "Checking for main application script" "Green"
if (-not $result.Success -or $result.Output -ne "True") {
    Write-Log "ERROR: Main application script not found" "Red"
    Write-Log "Please make sure you're running this script from the correct folder." "Red"
    exit 1
}

# Quick check if the environment is already set up correctly
$quickStart = $true
$requiredFiles = @(
    "venv\Scripts\python.exe",
    "venv\Scripts\activate.ps1"
)

foreach ($file in $requiredFiles) {
    $result = Invoke-CommandWithLogging "Test-Path $file" "Checking for $file" "Green"
    if (-not $result.Success -or $result.Output -ne "True") {
        $quickStart = $false
        Write-Log "Environment check: Missing $file - full setup will be required." "Yellow"
        break
    }
}

# Check if images directory exists
$result = Invoke-CommandWithLogging "Test-Path images" "Checking for images directory" "Green"
if (-not $result.Success -or $result.Output -ne "True") {
    Write-Log "WARNING: The 'images' directory was not found." "Yellow"
    Write-Log "The application may not display properly without the required images." "Yellow"
    
    $createDir = Read-Host "Do you want to create the images directory now? (y/n)"
    if ($createDir -eq "y") {
        $result = Invoke-CommandWithLogging "New-Item -ItemType Directory -Path images" "Creating images directory" "Green"
        if ($result.Success) {
            Write-Log "Created 'images' directory. Please add required image files to it." "Green"
        } else {
            Write-Log "Failed to create images directory" "Red" -CommandOutput $result.Output
        }
    }
}

# If we need to set up the environment
if (-not $quickStart) {
    Write-Log "Full environment setup required..." "Yellow"
    try {
        # Run the setup script to create/update the virtual environment
        $result = Invoke-CommandWithLogging ".\setup.ps1" "Running setup script" "Green"
        
        # If setup.ps1 failed or virtual environment doesn't exist after running it
        if (-not $result.Success) {
            throw "Setup script failed with exit code $($result.ExitCode)"
        }
        
        $result = Invoke-CommandWithLogging "Test-Path venv\Scripts\python.exe" "Checking if virtual environment was created" "Green"
        if (-not $result.Success -or $result.Output -ne "True") {
            throw "Setup script completed but virtual environment was not created properly"
        }
    } 
    catch {
        $errorMessage = $_.Exception.Message
        Write-Log "ERROR: Failed to set up the Python environment" "Red"
        Write-Log "Error details: $errorMessage" "Red"
        Write-Log "Please ensure Python is installed and available in your PATH" "Red"
        Write-Log "To force a complete rebuild, delete the venv folder and run this script again" "Yellow"
        exit 1
    }
} 
else {
    Write-Log "Environment already set up - using quick start mode!" "Green"
}

# Activate the virtual environment (needed in either case)
$result = Invoke-CommandWithLogging ".\venv\Scripts\activate.ps1" "Activating virtual environment" "Green"
if (-not $result.Success) {
    Write-Log "WARNING: Failed to activate virtual environment. Continuing anyway..." "Yellow"
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
    
    # Use Start-Process to get better error handling
    $processInfo = Start-Process -FilePath "venv\Scripts\python.exe" -ArgumentList $PYTHON_SCRIPT -NoNewWindow -Wait -PassThru -RedirectStandardError $errorLogFile
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
        
        # Provide troubleshooting information
        Write-Log "`nTroubleshooting:" "Yellow"
        Write-Log "1. Make sure all required dependencies are installed" "Yellow"
        Write-Log "2. Check if the 'images' directory contains all necessary image files" "Yellow"
        Write-Log "3. Verify that the serial port is available (if using hardware)" "Yellow"
        Write-Log "4. Look for Python compatibility issues in the code" "Yellow"
        Write-Log "5. To force a complete rebuild, delete the venv folder and run this script again" "Yellow"
        
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