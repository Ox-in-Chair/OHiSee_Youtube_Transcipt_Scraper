"""Build standalone .exe with PyInstaller"""
import PyInstaller.__main__
import os

# Get project root directory (parent of scripts/)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

PyInstaller.__main__.run([
    os.path.join(project_root, 'src', 'scraper_gui.py'),
    '--name=YouTubeTranscriptScraper',
    '--onefile',  # Single .exe file
    '--windowed',  # No console window
    '--add-data=requirements.txt;.',
    '--paths=' + os.path.join(project_root, 'src'),
    '--hidden-import=seleniumwire',
    '--hidden-import=webdriver_manager',
    '--hidden-import=openai',
    '--hidden-import=config',
    '--hidden-import=prompts',
    '--hidden-import=filters',
    '--hidden-import=search_optimizer',
    '--hidden-import=scraper_core',
    '--collect-all=selenium',
    '--collect-all=seleniumwire',
    '--collect-all=webdriver_manager',
    '--noconfirm',
    '--clean'
])

print("\n" + "="*60)
print("Build complete!")
print(f"Executable: {project_root}\\dist\\YouTubeTranscriptScraper.exe")
print("="*60)
