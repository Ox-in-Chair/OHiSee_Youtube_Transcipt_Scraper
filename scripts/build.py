#!/usr/bin/env python3
"""Build standalone .exe for YouTube Transcript Scraper"""
import PyInstaller.__main__
from pathlib import Path
import sys

# Project root
root = Path(__file__).parent.parent

print("=" * 70)
print(" YOUTUBE TRANSCRIPT SCRAPER")
print(" PyInstaller Build Script")
print("=" * 70)
print(f"\nProject root: {root}")
print(f"Entry point: {root / 'src' / 'main.py'}")
print(f"Output directory: {root / 'dist'}")

# Verify entry point exists
entry_point = root / 'src' / 'main.py'
if not entry_point.exists():
    print(f"\n[ERROR] Entry point not found: {entry_point}")
    sys.exit(1)

print(f"\n[OK] Entry point verified: {entry_point}")

# PyInstaller configuration
args = [
    str(entry_point),
    '--onefile',
    '--windowed',
    '--name=YouTubeTranscriptScraper',
    f'--distpath={root / "dist"}',
    f'--workpath={root / "build"}',
    f'--specpath={root}',
    f'--add-data={root / "src" / "utils" / "filters.py"};utils',
    '--hidden-import=seleniumwire',
    '--hidden-import=seleniumwire.undetected_chromedriver',
    '--hidden-import=yt_dlp',
    '--hidden-import=yt_dlp.utils',
    '--hidden-import=openai',
    '--collect-all=seleniumwire',
    '--collect-all=yt_dlp',
    '--clean',
    '--noconfirm',
]

print("\n" + "=" * 70)
print(" STARTING PYINSTALLER BUILD")
print("=" * 70)
print("\nThis may take 5-10 minutes...\n")

# Execute build
try:
    PyInstaller.__main__.run(args)

    exe_path = root / 'dist' / 'YouTubeTranscriptScraper.exe'
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print("\n" + "=" * 70)
        print(" [SUCCESS] BUILD COMPLETE!")
        print("=" * 70)
        print(f"\nExecutable: {exe_path}")
        print(f"Size: {size_mb:.1f} MB")
        print("=" * 70)
    else:
        print(f"\n[ERROR] Expected output not found: {exe_path}")
        sys.exit(1)

except Exception as e:
    print(f"\n[ERROR] BUILD FAILED: {e}")
    sys.exit(1)
