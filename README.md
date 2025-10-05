# YouTube Transcript Scraper

**Clean, modular research platform for extracting YouTube video transcripts with GPT-4 powered search optimization.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Lines of Code](https://img.shields.io/badge/code-1%2C223%20lines-blue.svg)](CLAUDE.md)

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch minimal app (675 lines, fast startup)
python src/app_minimal.py

# Or launch full-featured app (25 components)
python src/main_app.py

# Or use batch launcher
launch_minimal.bat
```

## Features

### Core Functionality
- ✅ **YouTube Search** - Fast video search with yt-dlp (no API quotas)
- ✅ **Transcript Extraction** - Selenium-based DOM extraction
- ✅ **GPT-4 Optimization** - Natural language → optimal search queries
- ✅ **Advanced Filters** - Upload date, sort by, duration, features
- ✅ **Markdown Output** - Clean formatted transcripts

### Two Application Modes

**Minimal App** (`src/app_minimal.py` - 675 lines)
- Single-window, three-panel layout
- 0.3s startup, 40MB memory
- All core features included
- Perfect for daily use

**Full-Featured App** (`src/main_app.py` - 25 components)
- 5-step wizard workflow
- Research templates
- Smart prompt composer
- Live preview panel
- Quality gates
- AI transparency panel

## How It Works

1. **Query Optimization** (optional) - GPT-4 converts natural language → YouTube query
2. **Search** - yt-dlp searches YouTube with filters
3. **Extract** - Selenium extracts transcript from video page
4. **Format** - Converts to clean markdown (no timestamps)
5. **Save** - Individual files: `[Title]_[Channel]_[Date].md`

## Technology Stack

- **GUI**: tkinter (Python stdlib)
- **Search**: yt-dlp (YouTube search)
- **Extraction**: Selenium Wire + Chrome
- **Optimization**: OpenAI GPT-4
- **Build**: PyInstaller (standalone .exe)

## Installation

### Requirements
- Python 3.8+
- Google Chrome browser
- OpenAI API key (optional, for query optimization)

### Setup

```bash
# Clone repository
git clone https://github.com/Ox-in-Chair/OHiSee_Youtube_Transcipt_Scraper.git
cd OHiSee_Youtube_Transcipt_Scraper

# Install dependencies
pip install -r requirements.txt

# Launch app
python src/app_minimal.py
```

## Usage

### GUI Application

**Minimal App** (Recommended for daily use):
1. Enter search query
2. Select filters (date, sort, results)
3. Choose output folder
4. Click Search
5. Select videos to download
6. Click Download Selected

**Full-Featured App** (Advanced research workflows):
1. Define research (templates, smart composer)
2. Refine filters (advanced options)
3. Review configuration (live preview)
4. Run scraping (progress tracking)
5. Export results (browse, open folder)

### Library Integration

```python
from src.core.scraper_engine import TranscriptScraper
from src.core.search_optimizer import optimize_search_query

# Optional: Optimize query with GPT-4
optimized = optimize_search_query(
    "videos about workflow automation in manufacturing",
    api_key="sk-..."
)

# Scrape transcripts
scraper = TranscriptScraper(
    output_dir="./transcripts",
    callback=print  # Progress logging
)

result = scraper.scrape(
    query=optimized,
    max_results=10,
    filters={'upload_date': 'month', 'sort_by': 'rating'}
)

print(f"Saved {result['saved']} transcripts")
```

## Building Standalone .exe

```bash
# Build Windows executable
python scripts/build_exe_minimal.py

# Output: dist/YouTubeTranscriptScraper.exe (~80MB)
```

**Distribution Requirements**:
- Target PC needs Chrome browser
- No Python installation required
- Portable executable

## Project Structure

```
youtube-transcript-scraper/
├── src/
│   ├── app.py                    # Modular app entry point (26 lines)
│   ├── app_minimal.py            # Minimal app (675 lines)
│   ├── main_app.py               # Full-featured app (25 components)
│   ├── scraper.py                # Core adapter (183 lines)
│   ├── shared.py                 # Shared constants (160 lines)
│   ├── config.py                 # Settings (106 lines)
│   ├── ui/                       # Modular UI components
│   │   ├── main_window.py        # Main orchestrator (421 lines)
│   │   ├── search_panel.py       # Search controls (175 lines)
│   │   └── results_panel.py      # Results display (152 lines)
│   ├── core/                     # Core engine
│   │   ├── scraper_engine.py    # Scraping logic
│   │   └── search_optimizer.py  # GPT-4 optimizer
│   ├── components/               # Full-featured components
│   └── utils/                    # Helper functions
├── scripts/
│   └── build_exe_minimal.py     # Build automation
├── tests/                       # Automated tests
│   ├── test_minimal_app.py      # Unit tests (5/5 passing)
│   ├── gui_automation_test.py   # GUI automation
│   └── test_scrolling.py        # Scrolling tests
├── docs/
│   ├── architecture/            # Architecture docs (ADRs, design)
│   ├── project_history/         # Phase completion summaries
│   ├── README_MINIMAL.md        # Minimal app guide
│   └── How to search YouTube.md # Search tips
├── archive/                     # Old versions (reference only)
├── dist/                        # Build output (.exe)
├── README.md                    # This file
├── CLAUDE.md                    # Development guide
└── requirements.txt
```

## Architecture

### Modular Design (1,223 lines)

**Core Principle**: 80/20 rule - 20% of code provides 80% of value

**Component Breakdown**:
- `app.py` (26 lines) - Entry point
- `scraper.py` (183 lines) - Core adapter
- `shared.py` (160 lines) - Constants + widgets
- `config.py` (106 lines) - Settings dialog
- `ui/main_window.py` (421 lines) - Main orchestrator
- `ui/search_panel.py` (175 lines) - Search controls
- `ui/results_panel.py` (152 lines) - Results display

**Benefits**:
- Bug fixes touch <3 files
- No circular dependencies
- Unit testable components
- Clear separation of concerns

### Performance

- **Startup**: 0.3s (minimal app)
- **Memory**: 40MB (minimal app)
- **Search**: 3-4s for 10 results

## Configuration

### API Key Storage
Saved to `~/.youtube_scraper_config.json`:
```json
{
  "openai_api_key": "sk-..."
}
```

### YouTube Filters
- **Upload date**: Last 7/30/90/180/365 days
- **Sort by**: Relevance, date, views, rating
- **Features**: Subtitles/CC, HD, 4K, Live

## Advanced Features

### Search Operators

```
"exact phrase"              - Videos must contain exact phrase
term1 OR term2              - Videos with either term
-excluded                   - Exclude term from results
```

### GPT-4 Query Optimization

**Cost**: ~$0.02-0.04 per query
**Model**: GPT-4

Example transformations:
```
Input:  "Videos on workflow automation for manufacturing with BRCGS standards"
Output: workflow automation manufacturing BRCGS standards

Input:  "I want instructional videos on golf to help with my putting stroke"
Output: golf putting stroke improvement tutorial
```

## Troubleshooting

**Search times out after 60 seconds**
→ Query too complex. Enable AI optimization or simplify manually.

**"No transcript available"**
→ Video doesn't have captions. Check for "CC" icon on YouTube.

**Chrome driver errors**
→ Chrome browser must be installed. Driver downloads automatically.

**Build fails on Windows**
→ Ensure PyInstaller is installed: `pip install pyinstaller`

## Testing

```bash
# Run automated tests
python tests/test_minimal_app.py

# GUI automation tests
python tests/gui_automation_test.py

# Scrolling tests
python tests/test_scrolling.py
```

**Test Results**: 5/5 passing ✅

## Development

### Code Statistics

**Before Refactor**: 7,090 lines across 30+ files
**After Refactor**: 1,223 lines across 7 modular files
**Reduction**: 83%

**Quality Metrics**:
- All original features preserved
- 40% faster startup
- 80% less memory usage
- Bug fixes touch <3 files

### Contributing

See [CLAUDE.md](CLAUDE.md) for:
- Development setup
- Architecture patterns
- Modular design principles
- Implementation guidelines

## Documentation

- **[CLAUDE.md](CLAUDE.md)** - Development guide
- **[docs/README_MINIMAL.md](docs/README_MINIMAL.md)** - Minimal app guide
- **[docs/How to search YouTube.md](docs/How%20to%20search%20YouTube.md)** - Search tips
- **[docs/architecture/](docs/architecture/)** - Architecture Decision Records (ADRs)
- **[docs/project_history/](docs/project_history/)** - Refactor completion summaries

## License

MIT License - See [LICENSE](LICENSE)

## Acknowledgments

- **yt-dlp** - YouTube search without API quotas
- **Selenium Wire** - Browser automation
- **OpenAI GPT-4** - Query optimization
- **PyInstaller** - Standalone executable builds

---

**Clean modular architecture** • **83% code reduction** • **100% feature preservation** • **Production ready**
