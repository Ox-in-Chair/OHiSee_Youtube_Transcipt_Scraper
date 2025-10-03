# YouTube Transcript Scraper - User Guide

## Quick Start

### Desktop GUI (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Launch GUI
python src/scraper_gui.py

# Or use the launcher
scripts/Launch_Scraper.bat
```

### As a Python Library

```python
from src.scraper_core import TranscriptScraper

scraper = TranscriptScraper()
result = scraper.scrape(
    query="Python tutorial",
    max_results=10,
    output_dir="./MyFolder"
)
```

## Features

✅ **Desktop Interface** - Easy-to-use GUI (no command-line needed)
✅ **AI Query Optimization** - GPT-4 integration to improve search results
✅ **YouTube Filters** - Filter by upload date, sort by relevance/views/rating
✅ **Custom Output Folders** - Organize transcripts by topic
✅ **Progress Tracking** - Real-time status updates
✅ **Persistent API Key** - Saves to `~/.youtube_scraper_config.json`
✅ **Under 400 Lines** - Simple, maintainable codebase

## Using the GUI

### 1. Describe Your Videos
Enter natural language description like:
- "I want instructional videos on golf to help with my putting stroke"
- "Python tutorials for beginners"
- "Surfing technique videos"

### 2. Set Filters (Optional)
- **Upload date**: Any time, Last hour, Today, This week, This month, This year
- **Sort by**: Relevance, Upload date, View count, Rating
- **Max results**: 1-50 videos

### 3. Choose Output Folder
- Enter a **Folder name** (e.g., "Golf", "Python", "Surfing")
- **Browse** to select save location
- Transcripts will be saved to: `[Path]/[FolderName]/`

### 4. Enable AI Optimization (Recommended)
- Enter your **OpenAI API key** and click "Set & Save"
- Check "Optimize (AI)" to convert your description into better search terms
- Example: "golf putting help" → `golf putting stroke improvement tutorial`
- **Cost**: ~$0.03 per query (GPT-4)

### 5. Start Scraping
- Click **Start** button
- Watch progress in real-time
- Transcripts save automatically

## Example Workflows

**Collect Surfing Videos:**
```
Query: "surfing tutorials for beginners"
Filters: Upload=This month, Sort=Rating
Folder: Surfing
Path: C:\Users\mike\Videos\
→ Saves to: C:\Users\mike\Videos\Surfing\
```

**Collect Golf Videos:**
```
Query: "golf putting stroke improvement"
Filters: Upload=This week, Sort=View count
Folder: Golf
Path: C:\Users\mike\Videos\
→ Saves to: C:\Users\mike\Videos\Golf\
```

## Output Format

Each transcript is saved as:
```
[VideoTitle]_[Channel]_[Date].md
```

Example file contents:
```markdown
# How to Improve Your Golf Putting Stroke

## Video Information
- **Channel**: Golf Tips Pro
- **URL**: https://youtube.com/watch?v=abc123
- **Scraped**: 2025-10-03 14:30

## Transcript

Today we're going to talk about improving your putting stroke. The key is to maintain a steady pendulum motion with your arms...
```

## Library Integration

Use as a Python library in your own programs:

```python
from src.scraper_core import TranscriptScraper
from src.search_optimizer import optimize_search_query

# Optional: Optimize query with GPT-4
optimized = optimize_search_query(
    "complex user query",
    api_key="sk-..."
)

# Scrape transcripts
scraper = TranscriptScraper(output_dir="./MyFolder")
result = scraper.scrape(
    query=optimized,
    max_results=10,
    filters={'upload_date': 'week', 'sort_by': 'rating'}
)

print(f"Saved {result['saved']} transcripts")
print(f"Skipped {result['skipped']} videos")
print(f"Files: {result['files']}")
```

## How It Works

1. **Query Optimization** (optional): GPT-4 converts natural language into optimal YouTube search terms
2. **Search**: Uses `yt-dlp` to search YouTube for videos
3. **Navigate**: Opens each video in headless Chrome browser (Selenium)
4. **Extract**: Clicks "Show transcript" button and extracts text from DOM
5. **Format**: Converts to clean paragraphs (no timestamps)
6. **Save**: Individual markdown files with metadata

## Requirements

- Python 3.8+
- Chrome browser (must be installed)
- Internet connection
- (Optional) OpenAI API key for query optimization

## Troubleshooting

**"yt-dlp not found"**
→ Run: `pip install -r requirements.txt`

**"No transcript available"**
→ Video doesn't have transcripts enabled (check for "CC" icon on YouTube)

**GUI won't start**
→ Make sure tkinter is installed (comes with Python on Windows)

**Search times out after 60 seconds**
→ Complex queries can timeout. Try simplifying your query or enable AI optimization.

**Slow performance**
→ Reduce max results or use filters to narrow search

**Chrome driver errors**
→ Chrome browser must be installed. Driver downloads automatically via webdriver-manager.

## Advanced: Search Operators

When "Optimize (AI)" is disabled, you can use YouTube search operators:

```
"exact phrase"              - Videos must contain exact phrase
term1 OR term2              - Videos with either term
-excluded                   - Exclude term from results
term1 term2 term3           - All terms must appear
```

Examples:
```
"Python tutorial" -music           # Python tutorials, no music
Python OR JavaScript tutorial      # Tutorials for either language
"data science" Python -R           # Data science with Python, not R
```

## Project Structure

```
scraper_core.py      (170 lines) - Core scraping engine
filters.py           (22 lines)  - Filter configurations
search_optimizer.py  (43 lines)  - GPT-4 query optimization
scraper_gui.py       (159 lines) - Desktop GUI
─────────────────────────────────
Total: 394 lines
```

Utility files:
```
config.py            (29 lines)  - API key persistence
prompts.py           (45 lines)  - GPT-4 prompts
build_exe.py         (28 lines)  - PyInstaller build
```

## Notes

- Modular design for easy integration
- Under 400 lines for core implementation
- Not enterprise-grade (by design)
- Simple, maintainable, functional
- Respects YouTube's terms of service
- Random delays between requests to avoid detection
