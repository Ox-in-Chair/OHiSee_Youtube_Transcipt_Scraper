# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

**Repository**: https://github.com/Ox-in-Chair/OHiSee_Youtube_Transcipt_Scraper.git

## Project Overview

**YouTube Transcript Scraper** - Lean, minimal desktop tool for searching YouTube videos and extracting transcripts with GPT-4 powered query optimization. Single working implementation focused on core functionality.

**Architecture**: Minimal 675-line single-file application with clean three-panel layout (search, results, actions). Built for simplicity, speed, and maintainability.

## Quick Start Commands

```bash
# Launch application
python src/app_minimal.py

# Or use batch launcher (Windows)
run.bat

# Build standalone .exe (requires PyInstaller)
python scripts/build_exe_minimal.py

# Output: dist/YouTubeTranscriptScraper.exe (~80MB)
```

## Architecture

### Minimal Application (1,127 Total Lines)

**Core Files**:
- `src/app.py` (27 lines) - Entry point
- `src/app_minimal.py` (675 lines) - Main application
- `src/core/scraper_engine.py` (~171 lines) - Scraping engine
- `src/core/search_optimizer.py` (~43 lines) - GPT-4 optimizer
- `src/utils/config.py` (~33 lines) - API key storage
- `src/utils/filters.py` (~69 lines) - Filter configurations
- `src/utils/prompts.py` (~89 lines) - GPT-4 prompts

**Design Principle**: Minimalism - only what works, nothing more.

### How It Works

1. **Query Optimization** (optional):
   - User enters natural language query
   - GPT-4 optimizes to YouTube-friendly search (6-10 words)
   - Supports advanced operators: `"exact phrases"`, `OR`, `-excluded`
   - Example: "workflow automation BRCGS manufacturing" → `workflow automation manufacturing BRCGS`

2. **Video Search**:
   - Uses `yt-dlp` via subprocess with 60-second timeout
   - Applies filters: upload date, sort by (relevance/views/rating)
   - Returns video metadata (title, channel, URL)

3. **Transcript Extraction**:
   - Selenium navigates to YouTube video page
   - Clicks "Show transcript" button
   - Extracts text from DOM elements
   - Formats into clean paragraphs without timestamps

4. **Output**:
   - Saves to `[OutputPath]/[Title]_[Channel]_[Date].md`
   - Markdown format with metadata header

### Application Features

**Three-Panel Layout**:
- **Top Panel**: Query input, filters (date, sort, max results), GPT-4 toggle, search button
- **Middle Panel**: Video results with checkboxes (select which to download)
- **Bottom Panel**: Progress display, download button, status updates

**Core Functionality**:
- YouTube search with advanced filters
- Video selection with checkboxes
- GPT-4 query optimization (optional)
- Transcript extraction from selected videos
- Markdown output with metadata
- Progress tracking and status updates
- API key persistence

**Performance**:
- Startup: 0.3s
- Memory: 40MB
- Search: 3-4s for 10 results

### Integration as Library

```python
from src.core.scraper_engine import TranscriptScraper
from src.core.search_optimizer import optimize_search_query

# Optimize query with GPT-4
optimized = optimize_search_query("complex user query", api_key="sk-...")

# Scrape transcripts
scraper = TranscriptScraper(output_dir="./transcripts", callback=print)
result = scraper.scrape(
    query=optimized,
    max_results=10,
    filters={'upload_date': 'month', 'sort_by': 'rating'}
)
# Returns: {"saved": 5, "skipped": 5, "files": [...]}
```

## Key Implementation Details

### Search Query Optimization (GPT-4)

**Model**: GPT-4 (required for accuracy)
**Cost**: ~$0.02-0.04 per query optimization
**Prompt**: Defined in `src/utils/prompts.py`

**Critical Rules**:
- Keep queries 6-10 words (YouTube works best with simple queries)
- Use operators sparingly (max 2-3 OR terms, 1-2 exclusions)
- Preserve critical context (standards like BRCGS, ISO, technical terms)
- Extract CORE concept from abstract queries

### API Key Persistence

- Saved to: `~/.youtube_scraper_config.json` (JSON format)
- Auto-loads on application startup
- Managed by `src/utils/config.py` Config class

### YouTube Search Filters

**Implemented via yt-dlp**:
- Upload date: Last 7/30/90/180/365 days
- Sort by: relevance, date, views, rating
- Filter options defined in `src/utils/filters.py`

### Transcript Extraction Method

**DOM-based approach**:
1. Navigate to `youtube.com/watch?v={video_id}`
2. Find and click transcript button
3. Wait for transcript panel to load
4. Extract text from DOM elements
5. Format into clean paragraphs

**Why DOM extraction**:
- More reliable than network interception
- Handles YouTube's dynamic loading
- Stable across YouTube UI changes

### Error Handling

- 60-second timeout on yt-dlp subprocess
- Full error tracebacks shown in GUI
- "No videos found" message when search returns 0 results
- Handles videos without transcripts gracefully
- Background threading prevents UI freeze

## Building the .exe

```bash
python scripts/build_exe_minimal.py
```

**PyInstaller Configuration**:
- `--onefile` - Single executable
- `--windowed` - No console window
- Bundles: Python, all dependencies
- **NOT bundled**: Chrome browser (must be installed separately)

**Distribution Requirements**:
- Target PC needs: Chrome browser + Internet
- No Python installation required
- Portable executable (~80MB)

## Architecture Statistics

**Current Implementation**:
```
src/app.py:                  27 lines (entry point)
src/app_minimal.py:         675 lines (main application)
src/core/scraper_engine.py: 171 lines (scraping logic)
src/core/search_optimizer.py: 43 lines (GPT-4 integration)
src/utils/config.py:          33 lines (config management)
src/utils/filters.py:         69 lines (filter definitions)
src/utils/prompts.py:         89 lines (GPT-4 prompts)
────────────────────────────────
TOTAL:                     1,127 lines
```

**Code Reduction**: 84% (from 7,090 lines to 1,127 lines)

## Testing

### Automated Tests

```bash
# Run unit tests
python tests/test_minimal_app.py
```

**Test Results**: 5/5 passing ✅

**Test Coverage**:
- Imports validation
- Config manager (save/load)
- Scraper search functionality
- AI optimization infrastructure
- App initialization

### Manual Testing

**Test query optimization**:
```python
from src.core.search_optimizer import optimize_search_query
result = optimize_search_query(
    "Videos on workflow automation for manufacturing with BRCGS standards",
    api_key="sk-..."
)
# Returns: "workflow automation manufacturing BRCGS standards"
```

**Test scraper without GUI**:
```python
from src.core.scraper_engine import TranscriptScraper
scraper = TranscriptScraper(output_dir="./test", callback=print)
scraper.scrape("Python tutorial", max_results=2)
```

### Common Issues

- **Search times out**: Query too complex. Enable AI optimization or simplify.
- **"No transcript available"**: Video doesn't have captions (check for CC icon).
- **Chrome driver errors**: Chrome browser must be installed.
- **Build fails**: Ensure PyInstaller is installed: `pip install pyinstaller`

## Project Structure

```
youtube-transcript-scraper/
├── src/
│   ├── app.py              # Entry point (27 lines)
│   ├── app_minimal.py      # Main application (675 lines)
│   ├── core/               # Core engine
│   │   ├── scraper_engine.py    # Scraping logic (171 lines)
│   │   └── search_optimizer.py  # GPT-4 optimizer (43 lines)
│   └── utils/              # Helper functions
│       ├── config.py       # API key storage (33 lines)
│       ├── filters.py      # Filter options (69 lines)
│       └── prompts.py      # GPT-4 prompts (89 lines)
├── scripts/
│   └── build_exe_minimal.py     # Build automation
├── tests/                  # Automated tests
│   ├── test_minimal_app.py      # Unit tests (5/5 passing)
│   ├── gui_automation_test.py   # GUI automation
│   └── test_scrolling.py        # Scrolling tests
├── docs/                   # Documentation
│   ├── architecture/       # Architecture Decision Records
│   ├── project_history/    # Refactor history
│   ├── README_MINIMAL.md   # Minimal app guide
│   └── How to search YouTube.md # Search tips
├── archive/                # Old versions (reference only)
├── dist/                   # Build output (.exe)
├── README.md               # Project README
├── CLAUDE.md               # This file
├── requirements.txt        # Python dependencies
└── launch_minimal.bat      # Windows launcher
```

## Configuration Files

- `requirements.txt` - Python dependencies (yt-dlp, selenium-wire, openai, tkinter)
- `~/.youtube_scraper_config.json` - Persistent API key storage
- `.gitignore` - Excludes API keys, tokens, build artifacts

## Important Constraints

1. **Minimal architecture**: Single working implementation, no alternatives
2. **Simplicity first**: YouTube search works best with 6-10 word queries
3. **Chrome required**: Selenium needs Chrome browser installed
4. **GPT-4 cost**: ~$0.02-0.04 per optimization (optional feature)
5. **No bloat**: Only essential features, nothing extra

## Development Guidelines

**When making changes**:
- Preserve the minimal architecture (don't add complexity)
- Keep `app_minimal.py` as single working implementation
- Test changes with `python tests/test_minimal_app.py`
- Update this file if core functionality changes
- Maintain the 80/20 principle (20% of code provides 80% of value)

**Code Quality**:
- Fast startup (target: <0.5s)
- Low memory (target: <50MB)
- Clear error messages
- Background threading for long operations
- Graceful error handling

## License

MIT License - See [LICENSE](LICENSE) file

---

**Lean minimal architecture** • **84% code reduction** • **Production ready** • **1,127 total lines**
