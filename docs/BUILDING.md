# YouTube Transcript Scraper v2.0 - Build Guide

**Repository**: https://github.com/Ox-in-Chair/OHiSee_Youtube_Transcipt_Scraper.git
**Version**: 2.0.0 (AI Research Intelligence System)

## Quick Start

```bash
# Clone repository
git clone https://github.com/Ox-in-Chair/OHiSee_Youtube_Transcipt_Scraper.git
cd OHiSee_Youtube_Transcipt_Scraper

# Install dependencies
pip install -r requirements.txt

# Run application
python src/main.py

# Or use Windows batch launcher
run.bat
```

## Building Standalone .exe

### Prerequisites
- Python 3.8+ installed
- All dependencies from `requirements.txt`
- PyInstaller (included in requirements)
- Chrome browser installed

### Build Steps

```bash
# Navigate to project root
cd OHiSee_Youtube_Transcipt_Scraper

# Run build script
python scripts/build.py

# Wait 2-3 minutes for compilation

# Output: dist/YouTubeTranscriptScraper.exe (~80-100MB)
```

### Build Configuration

The build uses PyInstaller with optimized settings:

**Key Settings** (`scripts/build.py`):
- `--onefile`: Single executable (~80-100MB)
- `--windowed`: No console window (GUI mode)
- `--paths src/`: Include source modules
- `--hidden-import`: Bundle all v2.0 modules
- `--collect-all selenium`: Include browser automation

**Bundled Components**:
- ✅ Python 3.8+ runtime
- ✅ All v1.0 core dependencies
- ✅ All v2.0 intelligence modules
- ✅ tkinter GUI framework
- ✅ Selenium + webdriver-manager
- ✅ OpenAI API client

**NOT Bundled** (must be installed separately on target PC):
- ❌ Chrome browser (required for transcript extraction)
- ❌ OpenAI API key (user provides)

## Distribution

### For End Users

The .exe is **portable** and can be distributed to any Windows PC:

**Requirements for Target PC**:
- Windows 7/10/11 (64-bit)
- Chrome browser installed
- Internet connection
- **No Python installation needed** ✅

**Setup**:
1. Copy `dist/YouTubeTranscriptScraper.exe` to target PC
2. Double-click to launch
3. Configure OpenAI API key on first run
4. Start using immediately

### Installation Options

**Option 1: Portable Mode** (Recommended for testing)
- Copy .exe anywhere
- Run directly
- Config saved to `~/.youtube_scraper_config.json`

**Option 2: System Installation** (Recommended for production)
- Copy to `C:\Program Files\YouTubeTranscriptScraper\`
- Create desktop shortcut
- Add to Start Menu

**Option 3: USB Distribution**
- Copy .exe to USB drive
- Portable across multiple PCs
- Config is PC-specific

## Project Structure

### v1.0 Core (1,652 lines - Production Ready)
```
src/
├── app.py                      # Entry point (27 lines)
├── main.py                     # GUI application (723 lines)
├── core/                       # Core engine
│   ├── scraper_engine.py       # Multi-tier search + extraction (332 lines)
│   └── search_optimizer.py     # GPT-4 query optimization (101 lines)
└── utils/                      # Utilities (191 lines)
    ├── config.py               # API key persistence
    ├── filters.py              # Search filters
    └── prompts.py              # GPT-4 prompts
```

### v2.0 Intelligence Modules (12,187 lines - Production Ready)
```
src/modules/
├── core_001/                   # Enhanced summary engine (2,100 lines)
│   ├── engine.py               # GPT-4 insight extraction
│   ├── prompts.py              # Enhanced prompt templates
│   └── __init__.py             # Module exports
│
├── visual_001/                 # Diagram generation (1,652 lines)
│   ├── timeline_generator.py  # Technology evolution timelines
│   ├── architecture_generator.py # System architecture diagrams
│   ├── comparison_generator.py   # Tool comparison matrices
│   ├── flowchart_generator.py    # Decision flowcharts
│   ├── validator.py              # Mermaid syntax validation
│   └── __init__.py
│
├── exec_001/                   # Playbook & execution (2,635 lines)
│   ├── execution_engine.py     # Unified orchestration
│   ├── playbook_generator.py   # Step-by-step guides
│   ├── prompt_extractor.py     # Template extraction
│   ├── cli_parser.py           # Command documentation
│   ├── checklist_creator.py    # Progress tracking
│   └── __init__.py
│
├── intel_001/                  # ROI & intelligence (1,865 lines)
│   ├── intelligence_engine.py  # Unified API
│   ├── roi_scorer.py           # Value assessment
│   ├── readiness_analyzer.py   # Prerequisites & complexity
│   ├── learning_path_generator.py # Dependency-ordered paths
│   └── __init__.py
│
├── knowledge_001/              # Knowledge base (2,670 lines)
│   ├── knowledge_engine.py     # Unified API
│   ├── knowledge_store.py      # SQLite persistence
│   ├── search_engine.py        # FTS5 full-text search
│   ├── cross_reference.py      # Relationship discovery
│   └── __init__.py
│
├── ui_001/                     # Enhanced dashboard (2,172 lines)
│   ├── intelligence_dashboard.py # ROI/learning/knowledge panels
│   ├── visualization_panel.py    # Diagram viewer
│   ├── playbook_viewer.py        # Interactive navigation
│   ├── settings_panel.py         # Module configuration
│   └── __init__.py
│
└── integrate_001/              # System orchestration (893 lines)
    ├── workflow_orchestrator.py # Module coordination
    ├── output_assembler.py      # Report generation
    ├── export_manager.py        # Multi-format exports
    └── __init__.py
```

### Tests (4,230 lines - 213 tests passing)
```
tests/
├── test_app.py                 # v1.0 core (11 tests)
├── test_basic.py               # Basic functionality (10 tests)
├── test_exec_001.py            # EXEC-001 (39 tests)
├── test_intel_001.py           # INTEL-001 (40 tests)
├── test_knowledge_001.py       # KNOWLEDGE-001 (29 tests)
├── test_ui_001.py              # UI-001 (23 tests, require display)
├── test_visual_001/            # VISUAL-001 (87 tests)
│   ├── test_timeline.py
│   ├── test_architecture.py
│   ├── test_comparison.py
│   ├── test_flowchart.py
│   ├── test_validator.py
│   └── test_visual_engine.py
└── fixtures/                   # Test data
    ├── exec_001/
    ├── intel_001/
    └── visual_001/
```

## Development Workflow

### Making Code Changes

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes to source code

# 3. Run tests
python -m pytest tests/ -v

# 4. Run quality checks
python -m flake8 src/
python -m pylint src/modules/ --disable=C0301
python -m black src/ --check

# 5. Commit changes
git add .
git commit -m "feat: description of changes"

# 6. Push to GitHub
git push origin feature/your-feature-name

# 7. Create Pull Request on GitHub
```

### Quality Gates (Required Before Commit)

All tests and quality checks must pass:

```bash
# Run all tests (213 tests should pass)
python -m pytest tests/ --ignore=tests/test_ui_001.py -v

# Code quality
python -m flake8 src/              # Zero errors
python -m pylint src/modules/      # Score ≥9.0/10
python -m black src/ --check       # All files formatted
```

**Current Quality Metrics**:
- Tests: 213/213 passing (100%)
- Pylint: 9.60/10 average
- Flake8: Zero errors
- Black: 100% formatted

### Rebuilding After Changes

```bash
# Clean previous build
rm -rf build dist *.spec

# Rebuild
python scripts/build.py

# Test new .exe
dist/YouTubeTranscriptScraper.exe
```

## Testing

### Automated Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific module
python -m pytest tests/test_core_001.py -v
python -m pytest tests/test_visual_001/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Manual Testing Checklist

Before distributing .exe, verify:

**v1.0 Core Features**:
- ✅ GUI launches successfully
- ✅ Search with multi-tier fallback works
- ✅ GPT-4 query optimization functions
- ✅ Transcript extraction completes
- ✅ Markdown output generated correctly
- ✅ API key persistence works

**v2.0 Intelligence Features**:
- ✅ Enhanced summary generates 50+ insights
- ✅ Diagrams render in Mermaid format
- ✅ Playbooks include step-by-step guides
- ✅ ROI scores calculate correctly
- ✅ Learning paths show dependencies
- ✅ Knowledge base stores/searches insights

### Test on Clean PC

For production validation:

1. Copy .exe to PC **without Python installed**
2. Ensure only Chrome browser is present
3. Run .exe and test all features end-to-end
4. Verify no Python-related errors

## Troubleshooting

### Build Issues

**Error: "ModuleNotFoundError"**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Clean and rebuild
rm -rf build dist __pycache__
python scripts/build.py
```

**Error: "PyInstaller not found"**
```bash
pip install pyinstaller
```

**Build succeeds but .exe is huge (>200MB)**
- Normal for v2.0 with all modules
- Expected size: 80-100MB
- If >200MB, check for duplicate dependencies

### Runtime Issues

**Error: "Chrome driver not found"**
- Install Chrome browser on target PC
- Webdriver auto-downloads on first run

**Error: "OpenAI API key invalid"**
- Check key starts with `sk-`
- Verify key has GPT-4 access
- Test with: https://platform.openai.com/playground

**Error: "Module 'tkinter' not found"**
- Rebuild with `--collect-all tkinter`
- Ensure Python includes tk/tcl libraries

### Performance Issues

**Slow startup (>10 seconds)**
- Normal on first run (webdriver download)
- Subsequent runs should be <2 seconds

**High memory usage (>500MB)**
- Close Chrome instances
- Restart application
- Check for memory leaks in long sessions

## Advanced Configuration

### Custom Icon

```python
# Edit scripts/build.py, add:
'--icon=path/to/icon.ico',
```

### Additional Data Files

```python
# Edit scripts/build.py, add:
'--add-data=data/file.txt;data/',
```

### Console Debugging

```python
# Edit scripts/build.py, remove:
'--windowed',
# This shows console for debugging
```

## Deployment

### GitHub Release

```bash
# 1. Tag version
git tag -a v2.0.0 -m "YouTube Scraper v2.0 - AI Intelligence System"
git push origin v2.0.0

# 2. Build .exe
python scripts/build.py

# 3. Create GitHub Release
# - Go to: https://github.com/Ox-in-Chair/OHiSee_Youtube_Transcipt_Scraper/releases
# - Click "Create new release"
# - Select tag: v2.0.0
# - Upload: dist/YouTubeTranscriptScraper.exe
# - Publish release
```

### Distribution Checklist

Before public release:

- ✅ All 213 tests passing
- ✅ Quality gates passed (Pylint, Flake8, Black)
- ✅ .exe tested on clean Windows PC
- ✅ README.md updated with v2.0 features
- ✅ CHANGELOG.md created with version history
- ✅ LICENSE file present (MIT)
- ✅ .gitignore excludes secrets/build artifacts
- ✅ GitHub repository set to public

## Quick Reference

### Build & Run
```bash
python scripts/build.py                    # Build .exe
python src/main.py                         # Run from source
run.bat                                    # Windows quick launcher
```

### Testing
```bash
python -m pytest tests/ -v                 # All tests
python -m pytest tests/test_visual_001/ -v # Specific module
python -m flake8 src/                      # Linting
python -m black src/ --check               # Formatting
```

### Git Workflow
```bash
git status                                 # Check changes
git add .                                  # Stage all
git commit -m "message"                    # Commit
git push origin main                       # Push
```

---

**Repository**: https://github.com/Ox-in-Chair/OHiSee_Youtube_Transcipt_Scraper.git
**Version**: 2.0.0
**Status**: Production Ready
**Tests**: 213/213 passing (100%)
**Total Lines**: 16,417 (12,187 prod + 4,230 tests)
