# YouTube Transcript Scraper - Minimal Edition

**Single-file application delivering 80/20 value**: Search YouTube videos and download transcripts with a clean, simple interface.

## Features

- **YouTube Search**: Query videos with filters (max results, upload date)
- **AI Query Optimization** (optional): GPT-4-powered search enhancement
- **Bulk Download**: Select multiple videos and download transcripts as markdown files
- **Progress Tracking**: Real-time progress bar during downloads
- **Persistent Settings**: API key and output directory saved locally

## Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Chrome browser** installed (for transcript extraction)
3. **Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Launch Application

**Windows**:
```bash
launch_minimal.bat
```

**Command Line**:
```bash
python src/app_minimal.py
```

## Usage Guide

### Basic Search

1. Enter search query (e.g., "Python tutorial")
2. Select max results (5, 10, 15, 25, or 50)
3. Choose upload date filter (Last 7 days, 30 days, etc.)
4. Click **Search**

### AI-Powered Search (Optional)

1. Click **⚙ Settings**
2. Enter your OpenAI API key
3. Save settings
4. Enable **"Use AI Optimization (GPT-4)"** checkbox
5. Search with complex queries:
   - Input: "How to automate workflows in manufacturing with BRCGS standards"
   - Optimized: "workflow automation manufacturing BRCGS food safety..."

### Download Transcripts

1. After search completes, results appear with checkboxes
2. Select videos to download (default: all selected)
3. Click **"Download Selected"**
4. Progress bar shows download status
5. Transcripts saved to configured output directory (default: `transcripts/`)

### Export All

Click **"Export All (.md)"** to download all search results at once.

## File Structure

```
src/
  app_minimal.py          # Main application (675 lines)
  core/
    scraper_engine.py     # Core scraping engine (reused)
    search_optimizer.py   # GPT-4 query optimization (reused)
  utils/
    config.py             # Configuration manager (reused)
    filters.py            # YouTube filter options (reused)
    prompts.py            # AI optimization prompt (reused)

tests/
  test_minimal_app.py     # Automated test suite

launch_minimal.bat        # Windows launcher
TEST_REPORT.md            # Test results documentation
README_MINIMAL.md         # This file
```

## Configuration

Settings stored in: `~/.youtube_scraper_config.json`

Example:
```json
{
  "openai_api_key": "sk-...",
  "output_dir": "C:\\Transcripts"
}
```

## Output Format

Transcripts saved as markdown files:

**Filename**: `{Title}_{Channel}_{Date}.md`

**Content**:
```markdown
# Video Title

## Video Information
- **Channel**: Channel Name
- **URL**: https://www.youtube.com/watch?v=...
- **Scraped**: 2025-10-05 14:30

## Transcript

Paragraph 1 of transcript text...

Paragraph 2 of transcript text...
```

## Performance

- **Startup time**: <0.5 seconds
- **Search time**: 3-5 seconds (15 results)
- **Memory usage**: ~40MB
- **Download speed**: ~10-15 seconds per video (network dependent)

## Troubleshooting

### "Search failed" error

**Cause**: Network timeout or yt-dlp issue
**Fix**: Check internet connection, try again

### "No videos found"

**Cause**: Query too specific or no matching content
**Fix**: Simplify search query, remove filters

### "Browser Error: Failed to setup browser"

**Cause**: Chrome not installed or ChromeDriver issue
**Fix**:
1. Install Chrome browser
2. ChromeDriver auto-installs via `webdriver_manager`
3. If still fails, check antivirus blocking Selenium

### "AI optimization failed"

**Cause**: Invalid or missing OpenAI API key
**Fix**:
1. Get API key from https://platform.openai.com/api-keys
2. Enter in Settings dialog
3. Test with simple query first

### "Video has no transcript"

**Cause**: Video genuinely lacks auto-generated or manual captions
**Fix**: This is normal - YouTube doesn't provide transcripts for all videos

## Comparison: Minimal vs. Full

| Feature                  | Minimal (app_minimal.py) | Full (scraper_gui.py) |
|--------------------------|--------------------------|------------------------|
| Lines of code            | 675                      | 794                    |
| UI design                | Single window            | 5-step wizard          |
| Research templates       | No                       | Yes (6 presets)        |
| Quality gates            | No                       | Yes (scoring system)   |
| Live preview             | No                       | Yes (JSON export)      |
| AI transparency panel    | No                       | Yes (model details)    |
| Complexity               | Simple                   | Advanced               |
| **Best for**             | Quick transcripts        | Research workflows     |

## Technical Details

### Architecture

**Single-file design**:
- `MinimalScraperApp`: Main Tkinter window
- `VideoResultItem`: Individual result component
- **Threading**: Background threads for search/download (non-blocking UI)

### Key Libraries

- **yt-dlp**: YouTube search API
- **selenium-wire**: Browser automation for transcript extraction
- **openai**: GPT-4 query optimization
- **tkinter**: GUI framework

### Code Quality

- **Line count**: 675 (target: 600-800) ✓
- **Imports**: Reuses 100% of core modules (no duplication)
- **Error handling**: Try/except blocks on all critical operations
- **Thread safety**: `self.after()` for UI updates from background threads

## Testing

Run automated test suite:
```bash
python tests/test_minimal_app.py
```

**Results**: 5/5 tests passed (see TEST_REPORT.md)

## Known Limitations

1. **Chrome dependency**: Requires Chrome browser (not bundled in .exe)
2. **No offline mode**: Internet required for search and download
3. **No transcript preview**: Cannot view before download
4. **No search history**: Previous searches not saved
5. **No batch export configuration**: "Export All" downloads immediately

## Future Enhancements (Out of Scope for Minimal)

- [ ] Transcript preview before download
- [ ] Search history and favorites
- [ ] Export to PDF/DOCX formats
- [ ] Batch download queue with pause/resume
- [ ] Built-in Chrome bundling for .exe

## Contributing

This is a minimal implementation focused on core functionality. For advanced features, see `scraper_gui.py` (full research platform).

## License

Same as parent project.

## Support

- **Issues**: Check TEST_REPORT.md for known issues
- **Documentation**: See CLAUDE.md for technical details
- **Original PRD**: youtube_transcript_scraper_prd.md

---

**Version**: 1.0
**Build**: 2025-10-05
**Status**: READY FOR USER TESTING
