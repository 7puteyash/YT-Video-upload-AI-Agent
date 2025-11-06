@echo off
REM One-Click YouTube Upload with AI Agent
REM This script automatically uploads the latest video in the folder

title AI YouTube Uploader - One Click Upload
color 0A

echo.
echo ============================================================
echo    AI-POWERED YOUTUBE UPLOADER - ONE CLICK UPLOAD
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if configuration exists
if not exist ".env" (
    echo ERROR: Configuration missing!
    echo Please run: python setup.py
    pause
    exit /b 1
)

if not exist "credentials.json" (
    echo ERROR: YouTube credentials missing!
    echo Please add credentials.json
    pause
    exit /b 1
)

REM Check if required modules are installed
python -c "import google_auth_oauthlib" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install groq google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv opencv-python Pillow moviepy requests
)

REM Run the quick upload script
echo.
echo Starting upload process...
echo.
python quick_upload.py

if errorlevel 1 (
    echo.
    echo ERROR: Upload failed!
    pause
) else (
    echo.
    echo Upload completed!
    pause
)
