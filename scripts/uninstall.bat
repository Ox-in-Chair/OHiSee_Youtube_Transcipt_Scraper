@echo off
echo ========================================
echo YouTube Transcript Scraper Uninstaller
echo ========================================
echo.
echo This will remove:
echo - Desktop shortcut
echo - Start Menu shortcut
echo - Program files
echo.
pause

REM Remove shortcuts
echo Removing shortcuts...
del "%USERPROFILE%\Desktop\YouTube Transcript Scraper.lnk" 2>nul
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\YouTube Transcript Scraper.lnk" 2>nul

REM Remove program directory (self-delete)
echo Removing program files...
cd /d "%TEMP%"
rmdir /s /q "%LOCALAPPDATA%\Programs\YouTubeTranscriptScraper"

echo.
echo ========================================
echo Uninstallation complete!
echo ========================================
echo.
pause
