# Create Desktop Shortcut
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\YouTube Transcript Scraper.lnk")
$Shortcut.TargetPath = "$env:LOCALAPPDATA\Programs\YouTubeTranscriptScraper\YouTubeTranscriptScraper.exe"
$Shortcut.WorkingDirectory = "$env:LOCALAPPDATA\Programs\YouTubeTranscriptScraper"
$Shortcut.Description = "Extract YouTube transcripts with GPT-4 search optimization"
$Shortcut.Save()

Write-Host "Desktop shortcut created" -ForegroundColor Green

# Create Start Menu Shortcut
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\YouTube Transcript Scraper.lnk")
$Shortcut.TargetPath = "$env:LOCALAPPDATA\Programs\YouTubeTranscriptScraper\YouTubeTranscriptScraper.exe"
$Shortcut.WorkingDirectory = "$env:LOCALAPPDATA\Programs\YouTubeTranscriptScraper"
$Shortcut.Description = "Extract YouTube transcripts with GPT-4 search optimization"
$Shortcut.Save()

Write-Host "Start Menu shortcut created" -ForegroundColor Green
