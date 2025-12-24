@echo off
title AI Track Masterer - Setup
color 0A

echo.
echo ============================================================
echo             AI Track Masterer - Setup Script
echo ============================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

:: Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not available!
    echo Please reinstall Python with pip included.
    pause
    exit /b 1
)

echo [OK] pip found:
pip --version
echo.

:: Create virtual environment (optional but recommended)
echo.
echo Do you want to create a virtual environment? (Recommended)
set /p venv_choice="Enter Y for Yes, N for No: "

if /i "%venv_choice%"=="Y" (
    echo.
    echo Creating virtual environment...
    python -m venv venv

    if exist "venv\Scripts\activate.bat" (
        echo [OK] Virtual environment created!
        echo.
        echo Activating virtual environment...
        call venv\Scripts\activate.bat
    ) else (
        echo [WARNING] Failed to create virtual environment. Continuing without it...
    )
)

:: Install dependencies
echo.
echo ============================================================
echo Installing Python dependencies...
echo ============================================================
echo.

:: Install setuptools first (required for Python 3.12+)
echo Installing setuptools...
pip install --upgrade setuptools wheel

echo.
echo Installing other dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to install some dependencies!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo [OK] Python dependencies installed successfully!
echo.

:: Check for FFmpeg
echo ============================================================
echo Checking for FFmpeg (needed for MP3 export)...
echo ============================================================
echo.

ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] FFmpeg is not installed!
    echo.
    echo MP3 export will not work without FFmpeg.
    echo.
    echo To install FFmpeg on Windows:
    echo   1. Download from: https://ffmpeg.org/download.html
    echo   2. Or use winget: winget install FFmpeg
    echo   3. Or use chocolatey: choco install ffmpeg
    echo.
    echo You can still use WAV and FLAC formats without FFmpeg.
    echo.
) else (
    echo [OK] FFmpeg found!
)

:: Create uploads and output directories
echo.
echo Creating required directories...
if not exist "uploads" mkdir uploads
if not exist "output" mkdir output
echo [OK] Directories created!

echo.
echo ============================================================
echo              Setup Complete!
echo ============================================================
echo.
echo To run the application:
echo   1. Double-click "run.bat"
echo   2. Or run: python run.py
echo.
echo The web interface will be available at:
echo   http://localhost:5000
echo.
pause
