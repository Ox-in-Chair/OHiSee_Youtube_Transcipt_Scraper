# YouTube Transcript Scraper

**World-Class Research Platform for extracting YouTube video transcripts with GPT-4 powered search optimization.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Lines of Code](https://img.shields.io/badge/GUI-794%20lines-blue.svg)](CLAUDE.md)

## Features

### 🎯 Research Platform
✅ **5-Step Wizard Workflow** - Visual journey map (Define → Refine → Review → Run → Export)
✅ **Research Templates** - Opinionated presets (Topic Overview, Fact Check, Competitor Scan, Citation Harvest, Course Outline)
✅ **Smart Prompt Composer** - Structured chips for topic, audience, time window, quality bar, sources, output goals
✅ **Live Preview Panel** - Real-time plain language summary + exportable JSON config
✅ **Quality Gates** - Intelligent scoring prevents bad queries (minimum 60/100 to proceed)
✅ **AI Transparency Panel** - Shows model, cost estimates, optimization examples, advanced parameters
✅ **Connection Manager** - Secure API key management with test connection, model picker, privacy promise

### 🔧 Technical Features
✅ **GPT-4 Search Optimization** - Converts natural language into optimal YouTube queries
✅ **Advanced Filters** - Upload date, sort by relevance/views/rating, duration, features (CC/HD/4K/Live)
✅ **Results Slider with Presets** - Quick scan (5), Balanced (15), Deep dive (50) with runtime estimates
✅ **Professional Typography** - Segoe UI hierarchy with generous whitespace and clear visual scale
✅ **Keyboard Navigation** - Full accessibility with Tab/Enter/Escape shortcuts
✅ **Configuration Export/Import** - Reproducible research with JSON config files
✅ **Standalone .exe** - Build Windows executable with PyInstaller

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

### Desktop GUI - 5-Step Workflow

#### Step 1: Define Research (🎯)
1. **Choose Template**: Select from Topic Overview, Fact Check, Competitor Scan, Citation Harvest, Course Outline, or Custom
2. **Smart Prompt Composer**: Build structured query using chips
   - **Topic**: What are you researching? (e.g., "BRCGS automation")
   - **Audience**: Who is this for? (e.g., "food manufacturers")
   - **Time Window**: When was it published? (Last week, Last month, Last year, etc.)
   - **Quality Bar**: How deep should we search? (Quick scan, Balanced, Deep dive)
   - **Sources**: What kind of sources? (Tutorials, Reviews, Case studies, etc.)
   - **Output Goals**: What do you want to extract? (Key concepts, Implementation steps, etc.)
3. **Quality Gate**: Achieve minimum 60/100 score to proceed (shows real-time feedback)
4. **AI Transparency** (optional): View GPT-4 model details, cost estimates, optimization examples

#### Step 2: Refine Filters (⚙️)
1. **Upload Date**: Last 7 days, Last 30 days, Last 90 days, Last 6 months, Last year
2. **Sort By**: Relevance, Upload date, View count, Rating
3. **Results Slider**: Use presets (Quick scan: 5, Balanced: 15, Deep dive: 50) with runtime estimates
4. **Duration**: Any, Short (<4min), Long (>20min)
5. **Features**: Subtitles/CC, HD, 4K, Live
6. **Output Config**: Choose folder, enable GPT-4 optimization

#### Step 3: Review Configuration (👁️)
- View complete plain language summary of your research configuration
- Export config as JSON for reproducibility
- Copy config to clipboard
- Verify all settings before execution

#### Step 4: Run Scraping (▶️)
- Real-time progress bar
- Activity log showing each video being processed
- Live status updates

#### Step 5: Export Results (📦)
- Browse saved transcripts
- Open output folder
- Start new research
- View results summary (saved vs. skipped)

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

## Installing on Your PC

### Automated Installation (Recommended)

```bash
# After building the .exe, run:
scripts/install.bat
```

This will:
- ✅ Copy .exe to `%LOCALAPPDATA%\Programs\YouTubeTranscriptScraper\`
- ✅ Create Desktop shortcut
- ✅ Create Start Menu entry (search "YouTube Transcript Scraper")
- ✅ Include uninstaller

**Installed location**: `C:\Users\[YourName]\AppData\Local\Programs\YouTubeTranscriptScraper\`

### Manual Installation

1. Copy `dist/YouTubeTranscriptScraper.exe` to desired location
2. Right-click Desktop → New → Shortcut
3. Point to .exe location
4. Name: "YouTube Transcript Scraper"

### Uninstalling

Run: `%LOCALAPPDATA%\Programs\YouTubeTranscriptScraper\uninstall.bat`

Or manually delete:
- Desktop shortcut
- Start Menu shortcut
- `C:\Users\[YourName]\AppData\Local\Programs\YouTubeTranscriptScraper\`

**Distribution Requirements:**
- Target PC needs Chrome browser installed
- No Python installation required
- Portable executable

## Project Structure

```
youtube-transcript-scraper/
├── src/                      # Source code
│   ├── scraper_gui.py       # World-class research platform (794 lines)
│   │                        # └─ Components: WizardNav, LivePreview, PromptComposer,
│   │                        #               AITransparencyPanel, ConnectionManager,
│   │                        #               QueryQualityGate, ResearchTemplates
│   ├── scraper_core.py      # Core engine (171 lines)
│   ├── search_optimizer.py  # GPT-4 optimizer (43 lines)
│   ├── filters.py           # YouTube filters (22 lines)
│   ├── config.py            # API key storage (29 lines)
│   └── prompts.py           # GPT-4 prompts (45 lines)
├── scripts/                  # Build & launcher
│   ├── build_exe.py         # PyInstaller build
│   ├── install.bat          # Windows installation
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

### Architecture Overview

- **Research Platform**: 794-line world-class GUI with 9 integrated phases
- **Modular Components**: WizardNav, LivePreview, PromptComposer, AITransparencyPanel, ConnectionManager
- **Quality-Gated Workflow**: Intelligent scoring system prevents bad research queries
- **Professional Design**: Segoe UI typography system, structured color palette
- **Accessibility**: Full keyboard navigation, screen reader support

```bash
# View component architecture
grep -E "^class " src/scraper_gui.py
# ProfessionalStyles, WizardNav, LivePreview, ChipInput,
# ChipSelector, ChipMultiSelect, PromptComposer,
# AITransparencyPanel, QueryQualityGate, ConnectionManager,
# ResearchPlatform
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

**World-class research platform** • **5-step wizard workflow** • **Quality-gated progression** • **No YouTube API quotas**
