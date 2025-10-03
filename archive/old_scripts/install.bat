@echo off
echo ========================================
echo YouTube Transcript Scraper Installer
echo ========================================
echo.

REM Create installation directory
echo Creating installation directory...
if not exist "%LOCALAPPDATA%\Programs\YouTubeTranscriptScraper" (
    mkdir "%LOCALAPPDATA%\Programs\YouTubeTranscriptScraper"
)

REM Copy executable
echo Copying program files...
copy /Y "%~dp0..\dist\YouTubeTranscriptScraper.exe" "%LOCALAPPDATA%\Programs\YouTubeTranscriptScraper\"

REM Copy uninstaller
copy /Y "%~dp0uninstall.bat" "%LOCALAPPDATA%\Programs\YouTubeTranscriptScraper\"

REM Create shortcuts using PowerShell script
echo Creating shortcuts...
powershell -ExecutionPolicy Bypass -File "%~dp0create_shortcuts.ps1"

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Program installed to:
echo %LOCALAPPDATA%\Programs\YouTubeTranscriptScraper
echo.
echo Shortcuts created:
echo - Desktop
echo - Start Menu (search for "YouTube Transcript Scraper")
echo.
echo To uninstall, run:
echo %LOCALAPPDATA%\Programs\YouTubeTranscriptScraper\uninstall.bat
echo.
pause
