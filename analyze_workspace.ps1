# Workspace Analysis Script
Write-Host "Analyzing workspace..." -ForegroundColor Green

# 1. Get all top-level files and folders
$allItems = Get-ChildItem -Path . -Force | Select-Object -ExpandProperty Name
Write-Host "`nAll top-level items in workspace:" -ForegroundColor Cyan
$allItems | ForEach-Object { Write-Host "  $_" }

# 2. Define essential files and folders based on LAUNCHER_FLOW.md
$essentialItems = @(
    # Critical Files
    "run_launcher.bat",
    "launcher.ps1", 
    "setup.ps1",
    "aquaphotomics_refactored.py",
    "requirements.txt",
    "LAUNCHER_FLOW.md",
    
    # Supporting Directories
    "venv",
    "images",
    
    # Git-related items (keep these to maintain version control)
    ".git",
    ".gitignore",
    
    # Tool configurations
    ".cursor",
    
    # Currently used scripts
    "run_cleanup.bat",
    "cleanup.bat",
    "cleanup.ps1",
    "analyze_workspace.ps1"
)

Write-Host "`nEssential items (should be kept):" -ForegroundColor Green
$essentialItems | ForEach-Object { Write-Host "  $_" }

# 3. Find items that can be safely removed
$itemsToRemove = $allItems | Where-Object { $_ -notin $essentialItems }
Write-Host "`nItems that can be safely removed:" -ForegroundColor Yellow
if ($itemsToRemove.Count -eq 0) {
    Write-Host "  No unnecessary items found!"
} else {
    $itemsToRemove | ForEach-Object { Write-Host "  $_" }
}

# 4. Provide a command to remove these items
if ($itemsToRemove.Count -gt 0) {
    Write-Host "`nTo remove these items, use the following commands:" -ForegroundColor Magenta
    $itemsToRemove | ForEach-Object {
        $item = $_
        if (Test-Path -Path ".\$item" -PathType Container) {
            Write-Host "  Remove-Item -Path '.\$item' -Recurse -Force # (Directory)" -ForegroundColor Yellow
        } else {
            Write-Host "  Remove-Item -Path '.\$item' -Force # (File)" -ForegroundColor Yellow
        }
    }
    
    # Generate a batch script that can remove these items
    $batchContent = @"
@echo off
echo Starting workspace cleanup...

"@

    foreach ($item in $itemsToRemove) {
        if (Test-Path -Path ".\$item" -PathType Container) {
            $batchContent += "echo Removing directory: $item`r`n"
            $batchContent += "rd /s /q `"$item`" 2>nul`r`n"
        } else {
            $batchContent += "echo Removing file: $item`r`n"
            $batchContent += "del /f /q `"$item`" 2>nul`r`n"
        }
    }

    $batchContent += @"

echo.
echo Cleanup complete!
echo.
pause
"@

    $batchContent | Out-File -FilePath "remove_unnecessary.bat" -Encoding ASCII
    Write-Host "`nA batch file 'remove_unnecessary.bat' has been created to remove these items." -ForegroundColor Magenta
}

Write-Host "`nAnalysis complete!" -ForegroundColor Green 