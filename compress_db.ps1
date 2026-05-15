# ============================================================================
# Database Compression Script for Luganda Hunspell Dictionary
# ============================================================================
# Compresses the Django SQLite database and creates backups
#
# Usage:
#   .\compress_db.ps1                    # Compress + backup
#   .\compress_db.ps1 -BackupOnly        # Only backup without compressing
#   .\compress_db.ps1 -ShowBackups       # Show recent backups
#   .\compress_db.ps1 -ScheduleDaily     # Schedule automatic daily compression
# ============================================================================

param(
    [switch]$BackupOnly,
    [switch]$ScheduleDaily,
    [switch]$ShowBackups
)

$djangoDir = "$PSScriptRoot\lgflagsite"
$venvPython = "$PSScriptRoot\.venv\Scripts\python.exe"

# Check prerequisites
if (-not (Test-Path $djangoDir)) {
    Write-Host "ERROR: Django directory not found: $djangoDir" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $venvPython)) {
    Write-Host "ERROR: Python venv not found: $venvPython" -ForegroundColor Red
    exit 1
}

# Show backups if requested
if ($ShowBackups) {
    $backupsDir = "$djangoDir\backups"
    if (Test-Path $backupsDir) {
        Write-Host "Recent database backups:" -ForegroundColor Cyan
        Get-ChildItem $backupsDir -Filter "*.sqlite3.gz" | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | ForEach-Object {
            $size = [math]::Round($_.Length / 1MB, 2)
            Write-Host "  $($_.Name) - $size MB - $($_.LastWriteTime)"
        }
    } else {
        Write-Host "No backups directory yet" -ForegroundColor Yellow
    }
    exit 0
}

# Build command arguments
$args = @("lgflagsite\manage.py", "compress_database")
if ($BackupOnly) { $args += "--backup-only" } else { $args += "--backup" }

# Run compression
Write-Host "Starting database compression..." -ForegroundColor Cyan
try {
    & $venvPython $args
    Write-Host "✓ Database compression completed!" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to compress database: $_" -ForegroundColor Red
    exit 1
}

# Schedule daily task if requested
if ($ScheduleDaily) {
    Write-Host "Setting up Windows Task Scheduler..." -ForegroundColor Cyan
    try {
        $taskName = "LugandaDictionary-CompressDB"
        $scriptPath = $MyInvocation.MyCommand.Path
        
        # Remove existing task if present
        $existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if ($existing) {
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
            Write-Host "Removed existing scheduled task" -ForegroundColor Yellow
        }
        
        $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
        $trigger = New-ScheduledTaskTrigger -Daily -At "02:00"
        $settings = New-ScheduledTaskSettingsSet -RunOnlyIfNetworkAvailable -StartWhenAvailable
        
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings | Out-Null
        Write-Host "✓ Scheduled daily compression at 2:00 AM" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to schedule task: $_" -ForegroundColor Red
        exit 1
    }
}

# Show summary
Write-Host ""
Write-Host "Quick stats:" -ForegroundColor Cyan
$dbSize = [math]::Round((Get-Item "$djangoDir\db.sqlite3").Length / 1MB, 2)
Write-Host "  Live database: $dbSize MB"

$backupsDir = "$djangoDir\backups"
if (Test-Path $backupsDir) {
    $backups = @(Get-ChildItem $backupsDir -Filter "*.sqlite3.gz")
    if ($backups.Count -gt 0) {
        $latestBackup = $backups | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        $backupSize = [math]::Round($latestBackup.Length / 1MB, 2)
        Write-Host "  Latest backup: $($latestBackup.Name) ($backupSize MB compressed)"
        Write-Host "  Total backups: $($backups.Count) files"
    }
}
