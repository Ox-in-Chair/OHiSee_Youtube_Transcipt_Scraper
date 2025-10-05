# YouTube Transcript Scraper - Build Guide

**Repository**: https://github.com/Ox-in-Chair/OHiSee_Youtube_Transcipt_Scraper.git

## Building the Standalone .exe

### Prerequisites
- Python 3.8+ installed
- All dependencies installed (`pip install -r requirements.txt`)
- PyInstaller installed (included in requirements.txt)

### Build Steps

```bash
# Navigate to project folder
cd "path/to/OHiSee_Youtube_Transcipt_Scraper"

# Run build script
python scripts/build.py

# Wait ~2-3 minutes for build to complete

# Executable created at:
# dist/YouTubeTranscriptScraper.exe (~150-200MB)
```

## Installing on Your PC

### Automated Installation (Recommended)

After building the .exe, run the installer:

```bash
# Install to system with shortcuts
scripts/install.bat
```

This will:
- ✅ Copy .exe to `C:\Users\[YourName]\AppData\Local\Programs\YouTubeTranscriptScraper\`
- ✅ Create Desktop shortcut
- ✅ Create Start Menu entry (Windows Search → "YouTube Transcript Scraper")
- ✅ Include uninstaller script

**File Locations After Installation:**
```
C:\Users\[YourName]\
├── Desktop\
│   └── YouTube Transcript Scraper.lnk       ← Desktop shortcut
│
├── AppData\Roaming\Microsoft\Windows\Start Menu\Programs\
│   └── YouTube Transcript Scraper.lnk       ← Start Menu
│
└── AppData\Local\Programs\YouTubeTranscriptScraper\
    ├── YouTubeTranscriptScraper.exe         ← Installed program
    └── uninstall.bat                        ← Uninstaller
```

### Manual Installation

1. Copy `dist/YouTubeTranscriptScraper.exe` to desired location
2. Right-click Desktop → New → Shortcut
3. Point to .exe location
4. Name: "YouTube Transcript Scraper"

### Uninstalling

Run: `C:\Users\[YourName]\AppData\Local\Programs\YouTubeTranscriptScraper\uninstall.bat`

Or manually delete:
- Desktop shortcut
- Start Menu shortcut (`%APPDATA%\Microsoft\Windows\Start Menu\Programs\YouTube Transcript Scraper.lnk`)
- Program folder (`%LOCALAPPDATA%\Programs\YouTubeTranscriptScraper\`)

### Distribution

The built .exe is **portable** and can be distributed to any Windows PC:

1. Copy `dist/YouTubeTranscriptScraper.exe` to USB drive or network share
2. Copy to target Windows PC
3. Double-click to run (or run `install.bat` for shortcuts)
4. **Requirements for target PC**:
   - Chrome browser installed
   - Internet connection
   - No Python installation needed ✅

## Development Workflow

**IMPORTANT**: Keep the project directory separate from the installed program.

**Project Directory** (wherever you cloned the repository):
- ✅ Keep for development and future code changes
- Contains: source code, git repository, build scripts
- Do NOT run the program from here daily

**Installed Program** (`%LOCALAPPDATA%\Programs\YouTubeTranscriptScraper\`):
- ✅ Where you launch the program from (via shortcuts)
- Separate from development files
- Standard Windows user program location

### Making Changes to the Code

After modifying any source code, follow this workflow:

```bash
# 1. Navigate to project directory
cd "path/to/OHiSee_Youtube_Transcipt_Scraper"

# 2. Test changes locally
python src/main.py

# 3. Run tests
python -m pytest tests/ -v

# 4. Stage and commit changes
git add .
git commit -m "Description of changes"

# 5. Push to GitHub
git push origin main
```

### Rebuilding After Code Changes

```bash
# Clean previous build artifacts (optional but recommended)
rm -rf build dist

# Rebuild executable
python scripts/build.py

# Test the new .exe
./dist/YouTubeTranscriptScraper.exe
```

## Project Structure

### Core Implementation (394 lines total)
```
src/
├── scraper_core.py      (170 lines) - Core scraping engine
├── scraper_gui.py       (159 lines) - Desktop GUI
├── filters.py           (22 lines)  - YouTube filter configurations
└── search_optimizer.py  (43 lines)  - GPT-4 query optimization
```

### Utility Files (Don't count toward 400-line limit)
```
src/
├── config.py            (29 lines)  - API key persistence
└── prompts.py           (45 lines)  - GPT-4 prompts
```

### Build & Scripts
```
scripts/
├── build.py                         - PyInstaller build script
└── Launch_Scraper.bat              - GUI launcher
```

### Documentation
```
docs/
├── USAGE.md                        - User guide
├── BUILDING.md                     - This file
└── PRD.md                          - Product requirements
```

## Git Workflow Reference

### Pushing Changes to GitHub

```bash
# Check status
git status

# Add all changes
git add .

# Commit with descriptive message
git commit -m "Fix: Resolved search timeout issue"

# Push to GitHub
git push origin main
```

### Pulling Latest Changes

```bash
# Pull latest from GitHub
git pull origin main

# Rebuild if source code changed
python scripts/build.py
```

### Creating a New Feature Branch

```bash
# Create and switch to new branch
git checkout -b feature/new-feature-name

# Make changes, commit
git add .
git commit -m "Add new feature"

# Push branch to GitHub
git push origin feature/new-feature-name

# Create pull request on GitHub
# Merge on GitHub
# Switch back to main and pull
git checkout main
git pull origin main
```

## Build Configuration

The build script (`scripts/build.py`) uses PyInstaller with these settings:

- **--onefile**: Single executable file
- **--windowed**: No console window (GUI only)
- **--paths**: Includes `src/` directory for imports
- **--hidden-import**: Ensures all dependencies are bundled
- **--collect-all**: Bundles Selenium and webdriver-manager data files

### Customizing the Build

Edit `scripts/build.py` to modify:

```python
# Add custom icon
'--icon=path/to/icon.ico',

# Change executable name
'--name=CustomName',

# Include additional data files
'--add-data=path/to/file;.',
```

## Testing the Build

### Test Checklist

Before distributing the .exe, verify:

1. ✅ **GUI launches**: Double-click .exe opens the interface
2. ✅ **API key persistence**: Set API key, close, reopen → key is saved
3. ✅ **Search works**: Run a test search with filters
4. ✅ **Optimization works**: Enable AI optimization, verify GPT-4 call
5. ✅ **Transcript extraction**: Complete end-to-end scrape
6. ✅ **Output files**: Verify markdown files are created correctly

### Test on Clean PC

For thorough testing:

1. Copy .exe to PC **without Python installed**
2. Ensure Chrome browser is installed
3. Run .exe and test all features
4. Verify no errors related to missing Python/dependencies

## Troubleshooting

### Build Fails

```bash
# Clean all build artifacts
rm -rf build dist __pycache__ src/__pycache__
rm -f *.spec

# Reinstall PyInstaller
pip uninstall pyinstaller -y
pip install pyinstaller

# Rebuild
python scripts/build.py
```

### .exe Won't Run on Target PC

**Error**: "Chrome driver not found"
→ Ensure Chrome browser is installed on target PC

**Error**: "Module not found"
→ Rebuild with `--collect-all` for missing module (edit build.py)

**Error**: "API key not persisting"
→ Check write permissions to `~/.youtube_scraper_config.json`

### Line Count Exceeded

If you exceed the 400-line constraint:

```bash
# Check current line count
wc -l src/scraper_core.py src/scraper_gui.py src/filters.py src/search_optimizer.py

# If over 400, options:
# 1. Compress code (combine lines where possible)
# 2. Move utility functions to config.py or prompts.py (don't count)
# 3. Refactor to reduce complexity
```

## Cost Considerations

### GPT-4 vs GPT-3.5-turbo

| Model | Cost per Query | Accuracy | Use Case |
|-------|---------------|----------|----------|
| GPT-4 | ~$0.03 | 100% | Production (current) |
| GPT-3.5-turbo | ~$0.0015 | ~85% | Cost-effective testing |

**To switch models** (edit `src/search_optimizer.py` line 24):
```python
model="gpt-3.5-turbo",  # Change from "gpt-4"
```

Test if GPT-3.5-turbo achieves acceptable accuracy → save 20x on costs.

## Quick Reference

### Launch GUI (Development)
```bash
python src/scraper_gui.py
# OR
scripts/Launch_Scraper.bat
```

### Build .exe
```bash
python scripts/build.py
```

### Verify Line Count
```bash
wc -l src/{scraper_core,scraper_gui,filters,search_optimizer}.py
```

### Push to GitHub
```bash
git add . && git commit -m "Update" && git push origin main
```

### Pull from GitHub
```bash
git pull origin main
```

---

**Repository**: https://github.com/Ox-in-Chair/OHiSee_Youtube_Transcipt_Scraper.git

**For code adjustments**: Always test locally → verify line count → commit → push to GitHub
