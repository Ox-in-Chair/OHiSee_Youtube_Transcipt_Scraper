# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

**Repository**: https://github.com/Ox-in-Chair/OHiSee_Youtube_Transcipt_Scraper.git

## Project Overview

**YouTube Transcript Scraper** - Production-ready desktop tool for searching YouTube videos and extracting transcripts with intelligent GPT-4 powered search optimization and multi-tier fallback strategy.

**Architecture**: Clean 700-line single-file GUI application with modular core engine (scraper + optimizer). Built for reliability, simplicity, and zero-result prevention.

## Quick Start Commands

```bash
# Launch application
python src/main.py

# Or use batch launcher (Windows)
run.bat

# Build standalone .exe
python scripts/build.py

# Output: dist/YouTubeTranscriptScraper.exe (~80MB)
```

## Core Features

### Multi-Tier Search Fallback

Prevents zero-result failures from over-optimized queries:

**Tier 1**: Optimized query with all filters (GPT-4 enhanced)
**Tier 2**: Fallback to original unoptimized query
**Tier 3**: Relax upload_date filter (expand time window)
**Tier 4**: GPT-4 synonym expansion (if API key configured)

Transparent logging shows which tier succeeded. Fully backward compatible.

### Enhanced Video Metadata (NEW)

**Displayed inline in results**:
- ⏱ Duration (HH:MM:SS format)
- 📅 Upload Date (YYYY-MM-DD)
- 👁 View Count (formatted, e.g., "1.2M")

**Included in MD files**:
```markdown
## Video Information
- **Channel**: [Channel Name]
- **Uploader**: [Uploader Name]
- **Upload Date**: YYYY-MM-DD
- **Duration**: HH:MM:SS
- **Views**: 123,456
- **URL**: https://youtube.com/watch?v=[ID]
- **Scraped**: YYYY-MM-DD HH:MM:SS
```

### Search Optimization Log (NEW)

**Visible in GUI** - Shows AI optimization comparison:
```
Original Query: "workflow automation BRCGS manufacturing"
Optimized Query: "workflow automation manufacturing BRCGS compliance"
Search completed with multi-tier fallback strategy
Results Found: 12 videos
```

Helps users understand what changes AI made and assess search effectiveness.

### Three-Panel GUI

- **Search Panel**: Query input, filters (date, sort, max results), GPT-4 toggle, optimization log
- **Results Panel**: Video checkboxes with inline metadata (duration, date, views)
- **Status Panel**: Progress tracking, download controls

## Architecture

### Code Structure (1,343 Total Lines)

```
src/app.py:                   27 lines  # Entry point
src/main.py:                 723 lines  # GUI application (enhanced metadata display)
src/core/scraper_engine.py:  332 lines  # Multi-tier search + enhanced metadata
src/core/search_optimizer.py: 101 lines  # GPT-4 query optimization
src/utils/config.py:           33 lines  # API key persistence
src/utils/filters.py:          69 lines  # Filter configurations
src/utils/prompts.py:          89 lines  # GPT-4 system prompts
tests/test_token_efficiency.py: 278 lines # Token efficiency validation
────────────────────────────────────────
TOTAL:                      1,652 lines (core: 1,374 lines)
```

**Design Principle**: Minimalism with reliability - only what works, enhanced for production.

### How It Works

1. **Query Optimization** (optional):
   - User enters natural language query
   - GPT-4 optimizes to YouTube-friendly keywords (6-10 words)
   - Example: "workflow automation BRCGS manufacturing" → `workflow automation manufacturing BRCGS`

2. **Multi-Tier Video Search**:
   - Uses `yt-dlp` for YouTube search (no API quotas)
   - Applies filters: upload date, sort by (relevance/views/rating)
   - Fallback strategy if optimized query returns insufficient results
   - Transparent tier logging for debugging

3. **Transcript Extraction**:
   - Selenium navigates to YouTube video page
   - Finds and clicks "Show transcript" button
   - Scrolls transcript panel to load ALL segments (handles long videos)
   - Extracts text from DOM, removes timestamps

4. **Markdown Output**:
   - Saves to `[OutputPath]/[Title]_[Channel]_[Date].md`
   - Includes enhanced metadata header (channel, uploader, upload date, duration, views, URL, scrape timestamp)
   - Clean paragraph formatting (groups of 5 sentences)

## Key Implementation Details

### Multi-Tier Search Strategy

**File**: `src/core/scraper_engine.py` - `search_videos()` method

```python
def search_videos(self, query, max_results=10, filters=None, original_query=None):
    """
    Tier 1: Optimized query with all filters
    Tier 2: Original unoptimized query (if Tier 1 < target)
    Tier 3: Relax upload_date filter
    Tier 4: GPT-4 synonym expansion (optional)

    Returns best tier that meets/exceeds max_results.
    """
```

**Benefits**:
- Prevents zero-result failures from over-guardrailing
- Transparent logging (user sees which tier worked)
- Graceful degradation (returns best attempt even if all fail)
- No breaking changes (backward compatible)

### Search Query Optimization

**Model**: GPT-4 (required for accuracy)
**Cost**: ~$0.02-0.04 per query
**Prompt**: `src/utils/prompts.py` - `GODLY_SEARCH_PROMPT`

**Rules**:
- Keep queries 6-10 words (YouTube algorithm optimized)
- Preserve critical terms (standards, technical jargon)
- Remove filler words, extract core concepts
- Use operators sparingly (max 2-3 OR terms)

### API Key Persistence

- Location: `~/.youtube_scraper_config.json`
- Format: JSON `{"openai_api_key": "sk-..."}`
- Auto-loaded on startup
- Managed by `src/utils/config.py`

### Transcript Extraction

**Method**: DOM-based (reliable, handles lazy loading)

1. Navigate to `youtube.com/watch?v={video_id}`
2. Scroll page, expand description
3. Find transcript button via CSS selectors
4. Click button, wait for panel load
5. **Scroll transcript panel** to force-load all segments (prevents cutoff)
6. Extract text from `.segment-text` elements
7. Format into paragraphs

**Why DOM vs Network Interception**:
- More stable across YouTube UI changes
- Handles dynamic/lazy-loaded content reliably
- No fragile network request dependencies

## Building the .exe

```bash
python scripts/build.py
```

**PyInstaller Configuration**:
- `--onefile` - Single executable (~80MB)
- `--windowed` - No console window
- Bundles: Python runtime + all dependencies
- **NOT bundled**: Chrome browser (must be installed separately)

**Distribution**:
- Portable executable (no Python required)
- Requires: Chrome browser + Internet connection
- Target PC: Windows 7/10/11 (64-bit)

## Testing

### Automated Tests

```bash
# Run test suite
python -m pytest tests/ -v

# Quality gates
python -m pytest tests/            # 11/11 tests
python -m flake8 src/              # 0 errors
python -m pylint src/core/ --disable=C0301,E0401  # 10.00/10
python -m black src/ --check       # Formatted
```

**Test Coverage** (11 tests):
- Module imports validation
- Config manager (save/load API key)
- Scraper search functionality
- AI optimization infrastructure
- GUI initialization (headless)
- Scrolling functionality

### Manual Integration Test

```python
from src.core.scraper_engine import TranscriptScraper
from src.core.search_optimizer import optimize_search_query

# Test multi-tier search with over-optimized query
scraper = TranscriptScraper(callback=print)

# Intentionally narrow query (trigger Tier 2 fallback)
optimized = "BRCGS"  # Too specific, will fall back
original = "BRCGS manufacturing quality standards"

results = scraper.search_videos(
    query=optimized,
    max_results=10,
    filters={'upload_date': 7, 'sort_by': 'relevance'},
    original_query=original  # Fallback enabled
)

# Expected output:
# [Tier 1] Searching with optimized query: 'BRCGS'
# ⊘ Tier 1 returned 2 results (below target of 10)
# [Tier 2] Trying original query: 'BRCGS manufacturing quality standards'
# ✓ Tier 2 successful: 12 results (better than Tier 1)
```

## Project Structure

```
youtube-transcript-scraper/
├── src/
│   ├── app.py                    # Entry point (27 lines)
│   ├── main.py                   # GUI application (675 lines)
│   ├── core/
│   │   ├── scraper_engine.py     # Multi-tier search + extraction (303 lines)
│   │   └── search_optimizer.py   # GPT-4 query optimization (101 lines)
│   └── utils/
│       ├── config.py             # API key persistence (33 lines)
│       ├── filters.py            # YouTube filter options (69 lines)
│       └── prompts.py            # GPT-4 system prompts (89 lines)
├── scripts/
│   └── build.py                  # PyInstaller build automation
├── tests/
│   ├── test_app.py               # Unit tests (11/11 passing)
│   ├── test_basic.py             # Core functionality tests
│   └── test_scrolling.py         # Scrolling validation
├── docs/
│   ├── current_workflow_human_readable.md  # Workflow explanation
│   ├── How to search YouTube.md            # Search best practices
│   ├── BUILDING.md                         # Build guide
│   └── USAGE.md                            # User manual
├── README.md                     # Public-facing documentation
├── CLAUDE.md                     # This file (AI development guide)
├── requirements.txt              # Python dependencies
└── run.bat                       # Windows quick launcher
```

## Configuration Files

- `requirements.txt` - Python dependencies (yt-dlp, selenium-wire, openai, tkinter)
- `~/.youtube_scraper_config.json` - Persistent API key storage
- `.gitignore` - Excludes secrets, build artifacts, cache files

## Development Guidelines

### Code Quality Standards

**Quality Gates (Required Before Commit)**:
- ✅ pytest: All tests passing
- ✅ flake8: 0 linting errors
- ✅ pylint: Score ≥9.0/10
- ✅ black: Code formatted (120 char line length)
- ✅ No breaking changes to public API

**Performance Targets**:
- Startup: <0.5s
- Memory: <50MB idle
- Search: 3-5s for 10 results
- Transcript: ~10-15s per video

### When Making Changes

1. **Preserve minimalism** - Don't add complexity without clear value
2. **Test multi-tier search** - Verify fallback tiers work correctly
3. **Update line counts** - Keep CLAUDE.md statistics current
4. **Maintain backward compatibility** - Optional parameters only
5. **Run quality gates** - All must pass before commit

### Common Modifications

**Adding new search filter**:
1. Update `src/utils/filters.py` - Add option to dictionaries
2. Update `src/core/scraper_engine.py` - Handle new filter in `_attempt_search()`
3. Update `src/main.py` - Add GUI control (dropdown/checkbox)
4. Test with multi-tier search (ensure fallback still works)

**Modifying GPT-4 prompt**:
1. Update `src/utils/prompts.py` - Edit `GODLY_SEARCH_PROMPT` or add new function
2. Update `src/core/search_optimizer.py` - Use new prompt
3. Test query optimization quality (compare before/after)
4. Update cost estimates if token usage changes

## Troubleshooting

**Search returns 0 results**:
- Check tier logs (which tier was last attempted?)
- Verify GPT-4 optimization didn't over-narrow query
- Try disabling AI optimization (use original query directly)
- Check upload_date filter (try "Any time")

**Transcript cutoff (incomplete)**:
- Fixed in v1.2.0 (scroll loading implemented)
- Verify `scraper_engine.py` has scrolling logic (lines 215-233)

**Chrome driver errors**:
- Ensure Chrome browser installed (not just Chromium)
- Check Chrome version compatibility
- Webdriver auto-downloads correct version via `webdriver_manager`

**Build fails**:
- Verify PyInstaller installed: `pip install pyinstaller`
- Check Python version (3.8+ required)
- Run from project root directory

## License

MIT License - See [LICENSE](LICENSE) file

---

**Production-ready** • **Multi-tier search fallback** • **11/11 tests passing** • **1,254 total lines**
