# One-Click YouTube Upload Shortcut
# Right-click this file and select "Run with PowerShell"
# Or just type: .\upload_shortcut.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI YOUTUBE UPLOADER - ONE CLICK" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check configuration
if (-not (Test-Path ".env")) {
    Write-Host "ERROR: Configuration missing!" -ForegroundColor Red
    Write-Host "Run: python setup.py" -ForegroundColor Yellow
    pause
    exit
}

if (-not (Test-Path "credentials.json")) {
    Write-Host "ERROR: YouTube credentials missing!" -ForegroundColor Red
    Write-Host "Add credentials.json file" -ForegroundColor Yellow
    pause
    exit
}

# Find latest video
$videos = Get-ChildItem -Filter "*.mp4" | Sort-Object LastWriteTime -Descending
if ($videos.Count -eq 0) {
    Write-Host "No MP4 videos found in this folder!" -ForegroundColor Red
    pause
    exit
}

$video = $videos[0]
Write-Host "Found video: $($video.Name)" -ForegroundColor Green
Write-Host "Size: $([Math]::Round($video.Length / 1MB, 2)) MB" -ForegroundColor Green
Write-Host ""

Write-Host "Starting upload..." -ForegroundColor Cyan
Write-Host ""

# Run upload
python upload_now.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Upload process completed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Upload encountered an error!" -ForegroundColor Red
}

pause
