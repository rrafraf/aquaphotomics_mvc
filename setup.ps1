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

Write-Log "Setting up Python virtual environment..." "Green"

# Check if Python is available via py launcher
$pythonPath = $null
$pythonVersion = $null

try {
    Write-Log "Checking for Python launcher (py)" "Green"
    
    # Check if py launcher exists
    $result = Invoke-CommandWithLogging "Get-Command py -ErrorAction SilentlyContinue" "Checking if py command exists" "Green"
    
    if ($result.Output) {
        $result = Invoke-CommandWithLogging "py -V" "Checking Python version" "Green"
        
        if ($result.Output -match "Python\s+(\d+\.\d+)") {
            $pythonPath = "py"
            $pythonVersion = $matches[1]
            Write-Log "Found Python $pythonVersion via py launcher" "Green"
        } else {
            Write-Log "Unexpected output from Python version check" "Yellow"
        }
    } else {
        Write-Log "Python launcher (py) was not found" "Yellow"
        Write-Log "Checking for python in PATH..." "Yellow"
        
        # Try direct python command as fallback
        $result = Invoke-CommandWithLogging "Get-Command python -ErrorAction SilentlyContinue" "Checking if python command exists" "Yellow"
        
        if ($result.Output) {
            $result = Invoke-CommandWithLogging "python -V" "Checking Python version" "Yellow"
            
            if ($result.Output -match "Python\s+(\d+\.\d+)") {
                $pythonPath = "python"
                $pythonVersion = $matches[1]
                Write-Log "Found Python $pythonVersion via direct command" "Green"
            }
        } else {
            Write-Log "Python command was not found in PATH" "Red"
        }
    }
} catch {
    $errorMessage = $_.Exception.Message
    Write-Log "Error checking for Python" "Red" -CommandOutput $errorMessage
}

if (-not $pythonPath) {
    Write-Log "No Python installation detected" "Red"
    Write-Log "Please install Python and ensure it's available in your PATH" "Yellow"
    exit 1
}

Write-Log "Using Python at: $pythonPath" "Green"

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    $result = Invoke-CommandWithLogging "$pythonPath -m venv venv" "Creating new Python $pythonVersion virtual environment" "Green"
    
    if (-not $result.Success) {
        Write-Log "Failed to create virtual environment" "Red"
        exit 1
    }
} else {
    Write-Log "Virtual environment already exists, checking version..." "Yellow"
    
    # Try to determine Python version in existing venv
    $venvPython = ".\venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        $result = Invoke-CommandWithLogging "$venvPython -V" "Checking virtual environment Python version" "Green"
        
        if ($result.Output -match "Python\s+(\d+\.\d+)") {
            $pythonVersion = $matches[1]
            Write-Log "Existing virtual environment is using Python $pythonVersion" "Green"
        } else {
            Write-Log "Could not determine Python version in existing environment" "Yellow" 
            Write-Log "Continuing with existing virtual environment" "Yellow"
        }
    } else {
        Write-Log "Virtual environment exists but python.exe not found" "Red" 
        Write-Log "Virtual environment may be corrupted, consider deleting venv folder and rerunning setup" "Yellow"
    }
}

# Activate virtual environment
$result = Invoke-CommandWithLogging ".\venv\Scripts\activate.ps1" "Activating virtual environment" "Green"

# Upgrade pip within the virtualenv
$result = Invoke-CommandWithLogging "python -m pip install --upgrade pip" "Upgrading pip" "Green"

# Install requirements
$result = Invoke-CommandWithLogging "pip install -r requirements.txt" "Installing dependencies" "Green"

if (-not $result.Success) {
    Write-Log "Some dependencies failed to install" "Yellow"
    Write-Log "Setup completed with warnings" "Yellow"
} else {
    Write-Log "Setup completed successfully!" "Green"
}

Write-Log "Python $pythonVersion virtual environment is now active" "Cyan"
