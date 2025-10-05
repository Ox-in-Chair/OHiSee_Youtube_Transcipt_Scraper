@echo off
REM Quick launcher for minimal YouTube Transcript Scraper

echo.
echo ========================================
echo YouTube Transcript Scraper
echo Modular Architecture (Phase 2)
echo ========================================
echo.
echo Launching application...
echo.

cd /d "%~dp0"
python src\app.py

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to launch
    echo.
    echo Possible issues:
    echo - Python not installed or not in PATH
    echo - Missing dependencies (run: pip install -r requirements.txt)
    echo.
    pause
)
