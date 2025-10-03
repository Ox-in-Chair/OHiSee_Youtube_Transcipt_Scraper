# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**YouTube Transcript Scraper** - Desktop GUI application that searches YouTube videos and extracts transcripts automatically. Features AI-powered search optimization with GPT-4, persistent API key storage, and can be built as a standalone Windows .exe.

**Critical Constraint**: Main application code MUST stay **under 400 lines total** (scraper_core.py + filters.py + search_optimizer.py + scraper_gui.py). Utility files (config.py, prompts.py, build_exe.py) don't count toward this limit.

## Quick Start Commands

```bash
# Launch GUI application
python scraper_gui.py

# Or use batch launcher
Launch_Scraper.bat

# Build standalone .exe (requires PyInstaller)
python build_exe.py

# Output: dist/YouTubeTranscriptScraper.exe (~150-200MB)
```

## Architecture

### Modular Design (400-Line Core)

**4 Main Files** (count toward 400-line limit):
- `scraper_core.py` (176 lines) - Core scraping engine, reusable library
- `filters.py` (22 lines) - YouTube filter configurations
- `search_optimizer.py` (43 lines) - GPT-4 query optimization
- `scraper_gui.py` (159 lines) - tkinter desktop GUI

**Utility Files** (don't count):
- `config.py` (29 lines) - API key persistence to `~/.youtube_scraper_config.json`
- `prompts.py` (45 lines) - GPT-4 "godly" search optimization prompt
- `build_exe.py` (28 lines) - PyInstaller build configuration

**Legacy File**:
- `auto_scraper.py` - Original CLI version, kept for reference

### How It Works

1. **Search Optimization** (optional):
   - User enters natural language query
   - GPT-4 optimizes to YouTube-friendly search (6-10 words)
   - Supports advanced operators: `"exact phrases"`, `OR`, `-excluded`
   - Example: "workflow automation BRCGS manufacturing" → `workflow automation manufacturing BRCGS standards`

2. **Video Search**:
   - Uses `yt-dlp` via subprocess with 60-second timeout
   - Applies filters: upload date, sort by (relevance/views/rating)
   - Returns video metadata (title, channel, URL)

3. **Transcript Extraction**:
   - Selenium Wire intercepts browser network requests
   - Navigates to YouTube video, clicks "Show transcript" button
   - Extracts text from DOM (not network interception anymore)
   - Formats into clean paragraphs without timestamps

4. **Output**:
   - Saves to `[OutputPath]/[TopicFolder]/[Title]_[Channel]_[Date].md`
   - Markdown format with metadata header

### Integration as Library

```python
from scraper_core import TranscriptScraper
from search_optimizer import optimize_search_query

# Optimize query with GPT-4
optimized = optimize_search_query("complex user query", api_key="sk-...")

# Scrape transcripts
scraper = TranscriptScraper(output_dir="./MyFolder", callback=my_log_function)
result = scraper.scrape(
    query=optimized,
    max_results=10,
    filters={'upload_date': 'week', 'sort_by': 'rating'}
)
# Returns: {"saved": 5, "skipped": 5, "files": [...]}
```

## Key Implementation Details

### Search Query Optimization (GPT-4)

**Model**: GPT-4 (not GPT-3.5) for 100% accuracy
**Cost**: ~$0.03 per query optimization
**Prompt**: Defined in `prompts.py` - extracts core concepts, simplifies complex queries

**Critical Rules**:
- Keep queries 6-10 words (YouTube works best with simple queries)
- Use operators sparingly (max 2-3 OR terms, 1-2 exclusions)
- Preserve critical context (standards like BRCGS, ISO, technical terms)
- Extract CORE concept from abstract queries

### API Key Persistence

- Saved to: `~/.youtube_scraper_config.json` (JSON format)
- Auto-loads on GUI startup
- Managed by `config.py` Config class

### YouTube Search Filters

**Supported via yt-dlp**:
- Upload date: `date:hour|today|week|month|year`
- Sort by: `sortby:date|views|rating`
- Build filter string in `filters.py`

**NOT supported**:
- Duration filters (YouTube/yt-dlp limitation)

### Transcript Extraction Method

**Current approach** (DOM-based):
1. Navigate to `youtube.com/watch?v={video_id}`
2. Scroll to description, expand if needed
3. Find transcript button by CSS selectors
4. Click button, wait for panel to load
5. Extract text from `.segment-text` elements

**Why not network interception**:
- Previous approach intercepted `/timedtext` requests
- Unreliable due to YouTube's dynamic loading
- DOM extraction is more stable

### Error Handling

- 60-second timeout on yt-dlp subprocess
- Full error tracebacks shown in GUI
- "No videos found" message when search returns 0 results
- Handles videos without transcripts gracefully

## Building the .exe

```bash
python build_exe.py
```

**PyInstaller Configuration**:
- `--onefile` - Single executable
- `--windowed` - No console window
- Bundles: Python, all dependencies, ChromeDriver
- **NOT bundled**: Chrome browser (must be installed separately)

**Distribution Requirements**:
- Target PC needs: Chrome browser + Internet
- No Python installation required
- .exe is portable (~150-200MB)

## Line Count Management

**Critical**: Total must stay ≤ 400 lines

**Current allocation**:
```
scraper_core.py:     176 lines (core engine)
filters.py:           22 lines (filter configs)
search_optimizer.py:  43 lines (GPT-4 integration)
scraper_gui.py:      159 lines (GUI)
─────────────────────────────
TOTAL:               400 lines ✅
```

**If adding features**:
1. First try to compress existing code (combine lines, remove comments)
2. Move complex logic to utility files (config.py, prompts.py)
3. Externalize long strings/prompts to prompts.py

**Verification**:
```bash
wc -l scraper_core.py filters.py search_optimizer.py scraper_gui.py
```

## Testing & Debugging

**Test query optimization**:
```python
from search_optimizer import optimize_search_query
result = optimize_search_query(
    "Videos on workflow automation for manufacturing with BRCGS standards",
    api_key="sk-..."
)
# Should return simplified query like: "workflow automation manufacturing BRCGS standards"
```

**Test scraper without GUI**:
```python
from scraper_core import TranscriptScraper
scraper = TranscriptScraper(output_dir="./test", callback=print)
scraper.scrape("Python tutorial", max_results=2)
```

**Common issues**:
- **"yt-dlp not found"**: Uses `python -m yt_dlp` (already fixed)
- **Hanging on search**: 60-second timeout added (already fixed)
- **Over-complex queries**: GPT-4 prompt updated to simplify (already fixed)
- **No transcript button**: Some videos genuinely lack transcripts

## PRD Reference

See `youtube_transcript_scraper_prd.md` for:
- Original product requirements
- Feature specifications
- Design constraints (<400 lines, standalone .exe)
- Distribution requirements

## Configuration Files

- `requirements.txt` - Python dependencies (yt-dlp, selenium-wire, openai, etc.)
- `config.json` - App settings (legacy, not actively used)
- `~/.youtube_scraper_config.json` - Persistent API key storage
- `.gitignore` - Excludes API keys, tokens, build artifacts

## Important Constraints

1. **Line limit**: Main 4 files must stay ≤ 400 lines total
2. **No enterprise features**: Simple, personal use focus
3. **Simpler is better**: YouTube search works best with 6-10 word queries
4. **Chrome required**: Selenium needs Chrome browser installed
5. **GPT-4 cost**: ~$0.03 per optimization (20x more than GPT-3.5, but required for accuracy)
