# YouTube Transcript Scraper

**Desktop GUI application for extracting YouTube video transcripts with GPT-4 powered search optimization.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style](https://img.shields.io/badge/code%20style-400%20lines-orange.svg)](CLAUDE.md)

## Features

✅ **Desktop GUI** - Easy-to-use tkinter interface (no command-line needed)
✅ **GPT-4 Search Optimization** - Converts natural language into optimal YouTube queries
✅ **Advanced Filters** - Upload date, sort by relevance/views/rating
✅ **Persistent API Key** - Saves to `~/.youtube_scraper_config.json`
✅ **Custom Output Folders** - Organize transcripts by topic
✅ **Standalone .exe** - Build Windows executable with PyInstaller
✅ **<400 Lines** - Core implementation maintained under 400 lines

## Quick Start

### Option 1: GUI Application (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Launch GUI
python src/scraper_gui.py

# Or use the batch launcher
scripts/Launch_Scraper.bat
```

### Option 2: Python Library

```python
from src.scraper_core import TranscriptScraper

scraper = TranscriptScraper(output_dir="./MyFolder")
result = scraper.scrape(
    query="Python tutorials",
    max_results=10,
    filters={'upload_date': 'week', 'sort_by': 'rating'}
)

print(f"Saved {result['saved']} transcripts")
```

## How It Works

1. **Query Optimization** (optional) - GPT-4 converts "I want golf putting videos" → `golf putting stroke improvement tutorial`
2. **Search** - yt-dlp searches YouTube with filters (date, sort)
3. **Extract** - Selenium navigates to each video and extracts transcript from DOM
4. **Format** - Converts to clean markdown paragraphs (no timestamps)
5. **Save** - Individual files: `[Title]_[Channel]_[Date].md`

## Technology Stack

- **GUI**: tkinter (Python standard library)
- **Search**: yt-dlp (YouTube video search with filters)
- **Extraction**: Selenium Wire + Chrome (browser automation)
- **Optimization**: OpenAI GPT-4 (query enhancement)
- **Build**: PyInstaller (standalone .exe)

## Installation

### Requirements
- Python 3.8+
- Google Chrome browser (must be installed)
- OpenAI API key (optional, for query optimization)

### Setup

```bash
# Clone repository
git clone https://github.com/Ox-in-Chair/OHiSee_Youtube_Transcipt_Scraper.git
cd OHiSee_Youtube_Transcipt_Scraper

# Install dependencies
pip install -r requirements.txt

# Launch GUI
python src/scraper_gui.py
```

## Usage Examples

### Desktop GUI

1. **Enter description**: "golf putting technique videos"
2. **Set filters**: Upload=This week, Sort=Rating, Max=10
3. **Choose folder**: Output folder name (e.g., "Golf")
4. **Enable AI** (optional): Add OpenAI API key, check "Optimize (AI)"
5. **Click Start**: Watch real-time progress

### Library Integration

```python
from src.scraper_core import TranscriptScraper
from src.search_optimizer import optimize_search_query

# Optional: Optimize query with GPT-4
optimized = optimize_search_query(
    "videos about workflow automation in manufacturing with BRCGS standards",
    api_key="sk-..."
)
# Returns: "workflow automation manufacturing BRCGS standards"

# Scrape transcripts
scraper = TranscriptScraper(
    output_dir="./Manufacturing",
    callback=lambda msg: print(msg)  # Progress logging
)

result = scraper.scrape(
    query=optimized,
    max_results=10,
    filters={'upload_date': 'month', 'sort_by': 'rating'}
)

# Result: {'saved': 8, 'skipped': 2, 'files': ['path1.md', 'path2.md', ...]}
```

## Output Format

Transcripts saved as markdown:

```markdown
# How to Improve Your Golf Putting Stroke

## Video Information
- **Channel**: Golf Tips Pro
- **URL**: https://youtube.com/watch?v=abc123
- **Scraped**: 2025-10-03 14:30

## Transcript

Today we're going to talk about improving your putting stroke. The key is to maintain a steady pendulum motion...
```

## Building Standalone .exe

```bash
# Build Windows executable (150-200MB)
python scripts/build_exe.py

# Output: dist/YouTubeTranscriptScraper.exe
```

**Distribution Requirements:**
- Target PC needs Chrome browser installed
- No Python installation required
- Portable executable

## Project Structure

```
youtube-transcript-scraper/
├── src/                      # Source code (394 lines total)
│   ├── scraper_core.py      # Core engine (170 lines)
│   ├── scraper_gui.py       # Desktop GUI (159 lines)
│   ├── filters.py           # YouTube filters (22 lines)
│   ├── search_optimizer.py  # GPT-4 optimizer (43 lines)
│   ├── config.py            # API key storage (29 lines)
│   └── prompts.py           # GPT-4 prompts (45 lines)
├── scripts/                  # Build & launcher
│   ├── build_exe.py         # PyInstaller build
│   └── Launch_Scraper.bat   # GUI launcher
├── docs/                     # Documentation
│   ├── USAGE.md             # User guide
│   ├── BUILDING.md          # Build instructions
│   └── PRD.md               # Product requirements
├── transcripts/              # Output folder (gitignored)
├── README.md                # This file
├── CLAUDE.md                # Development guide
└── requirements.txt
```

## Configuration

### API Key Persistence
Saved to `~/.youtube_scraper_config.json`:
```json
{
  "openai_api_key": "sk-..."
}
```

### YouTube Filters
Available via GUI or library:
- **Upload date**: `hour`, `today`, `week`, `month`, `year`
- **Sort by**: `relevance`, `date`, `views`, `rating`

## Advanced Features

### Search Operators

When AI optimization is disabled, use YouTube operators:

```
"exact phrase"              - Videos must contain exact phrase
term1 OR term2              - Videos with either term
-excluded                   - Exclude term from results
```

Examples:
```
"Python tutorial" -music           # Python tutorials, no music
data science Python OR R           # Data science with Python or R
"golf putting" -advertising        # Golf putting, no ads
```

### GPT-4 Query Optimization

**Cost**: ~$0.03 per query
**Model**: GPT-4 (required for 100% accuracy)

Example transformations:
```
Input:  "Videos on how to make peanut butter and jelly from scratch by growing peanuts and strawberries"
Output: homemade peanut butter jelly sandwich tutorial

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

See [docs/USAGE.md](docs/USAGE.md) for complete troubleshooting guide.

## Development

### Design Constraints

- **Line Limit**: Core implementation (4 files) must stay ≤400 lines total
- **Modularity**: Utilities (config, prompts, build) don't count toward limit
- **Simplicity**: "Not enterprise-grade, by design"

```bash
# Verify line count
wc -l src/scraper_core.py src/scraper_gui.py src/filters.py src/search_optimizer.py
# 170 + 159 + 22 + 43 = 394 lines ✅
```

### Contributing

See [CLAUDE.md](CLAUDE.md) for:
- Development setup
- Architecture overview
- 400-line constraint rules
- Implementation guidelines

## License

MIT License - See [LICENSE](LICENSE) file

## Acknowledgments

- **yt-dlp** - YouTube search without API quotas
- **Selenium Wire** - Browser automation
- **OpenAI GPT-4** - Query optimization
- **PyInstaller** - Standalone executable builds

---

**Built for simplicity** • **Maintained under 400 lines** • **No YouTube API quotas**
