# YouTube Transcript Scraper

**Production-ready research tool for extracting YouTube transcripts with intelligent GPT-4 powered search and multi-tier fallback.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-11%2F11%20passing-brightgreen.svg)](tests/)
[![Code Quality](https://img.shields.io/badge/pylint-10.00%2F10-brightgreen.svg)](CLAUDE.md)

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch application
python src/main.py

# Or use Windows launcher
run.bat
```

## ✨ Features

- ✅ **Multi-Tier Search** - Intelligent fallback prevents zero-result failures
- ✅ **GPT-4 Optimization** - Natural language → YouTube-optimized queries
- ✅ **Smart Transcript Extraction** - Handles long videos (scrolling auto-loads all segments)
- ✅ **Advanced Filters** - Upload date, sort by relevance/views/rating
- ✅ **Video Selection** - Choose which videos to download
- ✅ **Clean Markdown Output** - Formatted transcripts without timestamps
- ✅ **Standalone .exe** - Build portable Windows executable

## 🎯 What Makes This Different

### Multi-Tier Search Fallback

Prevents frustrating zero-result searches with intelligent fallback strategy:

1. **Tier 1**: Optimized query with all filters (GPT-4 enhanced)
2. **Tier 2**: Falls back to original query if Tier 1 returns too few results
3. **Tier 3**: Relaxes date filters to expand search window
4. **Tier 4**: Uses GPT-4 synonym expansion as last resort

**Result**: You always get the best possible matches, even if GPT-4 over-optimizes your query.

### Complete Transcript Extraction

Unlike basic scrapers, this tool:
- ✅ Scrolls transcript panels to load ALL segments (no cutoffs)
- ✅ Handles videos of any length (tested up to 3+ hours)
- ✅ Formats cleanly into paragraphs (removes timestamps automatically)

## 📖 How It Works

```
User Query → GPT-4 Optimization → Multi-Tier Search → Extract Transcripts → Save as Markdown
```

**Example**:
```
Input:  "videos about workflow automation in manufacturing"
Output: 10 transcripts saved to ./transcripts/
```

**Each transcript includes**:
- Video title and channel
- Video URL for reference
- Scrape date/time
- Clean formatted paragraphs (no timestamps)

## ⚙️ Installation

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

# Launch
python src/main.py
```

## 🖥️ Usage

### GUI Application

1. Enter search query (e.g., "Python tutorials for beginners")
2. Select filters (upload date, sort by, max results)
3. *(Optional)* Enable GPT-4 optimization for better results
4. Click **Search**
5. Select videos from results
6. Click **Download Selected**
7. Transcripts saved to your chosen folder

### As a Python Library

```python
from src.core.scraper_engine import TranscriptScraper

# Create scraper instance
scraper = TranscriptScraper(
    output_dir="./transcripts",
    callback=print  # Optional progress logging
)

# Scrape transcripts
result = scraper.scrape(
    query="Python tutorial",
    max_results=10,
    filters={'upload_date': 30, 'sort_by': 'rating'}  # Last 30 days, sorted by rating
)

print(f"Saved {result['saved']} transcripts")
```

## 🏗️ Building Standalone .exe

```bash
# Build Windows executable
python scripts/build.py

# Output: dist/YouTubeTranscriptScraper.exe (~80MB)
```

**Distribution Requirements**:
- Target PC needs Google Chrome installed
- No Python installation required
- Fully portable (~80MB single file)

See [docs/BUILDING.md](docs/BUILDING.md) for detailed build instructions.

## 🧪 Testing

```bash
# Run automated tests
python -m pytest tests/ -v

# Quality gates
python -m flake8 src/              # Linting
python -m pylint src/core/         # Code quality (10.00/10)
python -m black src/ --check       # Formatting
```

**Test Results**: 11/11 passing ✅

## 📁 Project Structure

```
├── src/
│   ├── main.py                   # GUI application
│   ├── core/
│   │   ├── scraper_engine.py     # Multi-tier search + extraction
│   │   └── search_optimizer.py   # GPT-4 query optimization
│   └── utils/                    # Config, filters, prompts
├── scripts/
│   └── build.py                  # Build automation
├── tests/                        # Automated tests (11/11 passing)
├── docs/                         # Documentation
└── README.md                     # This file
```

## 🛠️ Configuration

### API Key Setup

1. Launch application
2. Click **Settings** (gear icon)
3. Enter your OpenAI API key
4. Click **Save**

API key saved to `~/.youtube_scraper_config.json` (auto-loaded next time).

### YouTube Search Filters

- **Upload Date**: Last 7/30/90/180/365 days or any time
- **Sort By**: Relevance, date uploaded, view count, rating
- **Max Results**: 1-50 videos per search

## 💡 Tips & Best Practices

**For Best Search Results**:
- Use specific keywords (e.g., "Python list comprehension" vs "Python tricks")
- Enable GPT-4 optimization for natural language queries
- Start with shorter timeframes (last 30 days) for recent content
- Use "Sort by rating" for highest quality videos

**For Large Batches**:
- Search returns up to 50 results per query
- Select 10-15 videos at a time for faster downloads
- Enable progress logging to monitor extraction status

**GPT-4 Costs**:
- Query optimization: ~$0.02-0.04 per search
- Synonym expansion (Tier 4): ~$0.02 per fallback
- Optional feature - works fine without API key

## 🐛 Troubleshooting

**Search returns 0 results**:
- Check tier logs in output panel (which tier was attempted?)
- Try disabling AI optimization (use your original query directly)
- Expand date range (try "Any time")
- Simplify query (fewer keywords often works better)

**Transcript shows as "Not available"**:
- Video doesn't have captions (check for CC icon on YouTube)
- Video may be age-restricted or region-locked
- Private/unlisted videos not accessible

**Chrome driver errors**:
- Ensure Google Chrome (not Chromium) is installed
- Driver auto-downloads on first run
- Check Chrome is up to date

**Build fails**:
- Verify PyInstaller installed: `pip install pyinstaller`
- Run from project root directory
- Python 3.8+ required

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Development guide for AI assistants
- **[docs/BUILDING.md](docs/BUILDING.md)** - Build & distribution guide
- **[docs/USAGE.md](docs/USAGE.md)** - Detailed user manual
- **[docs/How to search YouTube.md](docs/How%20to%20search%20YouTube.md)** - Search optimization tips
- **[docs/current_workflow_human_readable.md](docs/current_workflow_human_readable.md)** - How the scraper works internally

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Run quality gates (`pytest`, `flake8`, `pylint`, `black`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open Pull Request

**Code Quality Requirements**:
- All tests must pass (pytest)
- Linting score ≥9.0/10 (pylint)
- Code formatted with black (120 char line length)
- No breaking changes to public API

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

- **yt-dlp** - YouTube search without API quotas
- **Selenium Wire** - Reliable browser automation
- **OpenAI GPT-4** - Intelligent query optimization
- **PyInstaller** - Standalone executable builds

---

**Production-ready** • **Multi-tier search fallback** • **11/11 tests passing** • **Zero-result prevention**

Built with ❤️ for researchers who need reliable YouTube transcript extraction.
