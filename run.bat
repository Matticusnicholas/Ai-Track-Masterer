@echo off
title AI Track Masterer
color 0B

echo.
echo ============================================================
echo          AI Track Masterer - Starting Server
echo ============================================================
echo.

:: Change to script directory
cd /d "%~dp0"

:: Check if virtual environment exists and activate it
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
)

:: Check if dependencies are installed
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Dependencies not installed!
    echo.
    echo Please run setup.bat first to install dependencies.
    echo.
    set /p install_choice="Do you want to install now? (Y/N): "
    if /i "%install_choice%"=="Y" (
        echo.
        echo Installing dependencies...
        pip install -r requirements.txt
        echo.
    ) else (
        echo.
        echo Please run setup.bat and try again.
        pause
        exit /b 1
    )
)

echo.
echo ============================================================
echo   Server starting at: http://localhost:5000
echo ============================================================
echo.
echo   - Open your web browser to http://localhost:5000
echo   - Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.

:: Run the application
python run.py

:: If python exits with error
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Server stopped unexpectedly!
    echo.
    pause
)
