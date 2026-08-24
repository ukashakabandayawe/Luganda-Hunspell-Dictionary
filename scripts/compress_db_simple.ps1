param([switch]$ShowBackups, [switch]$ScheduleDaily, [switch]$BackupOnly)

$djangoDir = "$PSScriptRoot\lgflagsite"
$venvPython = "$PSScriptRoot\.venv\Scripts\python.exe"
$backupsDir = "$djangoDir\backups"

if (-not (Test-Path $djangoDir)) { Write-Host "ERROR: Django directory not found" -ForegroundColor Red; exit 1 }
if (-not (Test-Path $venvPython)) { Write-Host "ERROR: Python venv not found" -ForegroundColor Red; exit 1 }

if ($ShowBackups) {
    if (Test-Path $backupsDir) {
        Write-Host "Recent backups:" -ForegroundColor Cyan
        Get-ChildItem $backupsDir -Filter "*.sqlite3.gz" | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | `
            ForEach-Object { Write-Host "  $($_.Name) - $(  [math]::Round($_.Length/1MB,2)) MB" }
    } else {
        Write-Host "No backups yet" -ForegroundColor Yellow
    }
    exit 0
}

$args = @("lgflagsite\manage.py", "compress_database")
if ($BackupOnly) { $args += "--backup-only" } else { $args += "--backup" }

Write-Host "Compressing database..." -ForegroundColor Cyan
& $venvPython $args

Write-Host "`nStats:" -ForegroundColor Cyan
Write-Host "  Live DB: $(  [math]::Round((Get-Item "$djangoDir\db.sqlite3").Length/1MB,2)) MB"
if (Test-Path $backupsDir) {
    $latest = Get-ChildItem $backupsDir -Filter "*.sqlite3.gz" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latest) { Write-Host "  Latest backup: $($latest.Name)" }
}

if ($ScheduleDaily) {
    Write-Host "Scheduling daily task..." -ForegroundColor Cyan
    $task = Get-ScheduledTask -TaskName "LugandaDictionary-CompressDB" -ErrorAction SilentlyContinue
    if ($task) { Unregister-ScheduledTask -TaskName "LugandaDictionary-CompressDB" -Confirm:$false }
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$($MyInvocation.MyCommand.Path)`""
    Register-ScheduledTask -TaskName "LugandaDictionary-CompressDB" -Action $action -Trigger (New-ScheduledTaskTrigger -Daily -At "02:00") | Out-Null
    Write-Host "[OK] Scheduled for 2:00 AM daily" -ForegroundColor Green
}
