# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Repository**: https://github.com/Ox-in-Chair/OHiSee_Youtube_Transcipt_Scraper.git

## Project Overview

**YouTube Transcript Scraper** - World-class desktop research platform that searches YouTube videos and extracts transcripts with professional UX patterns. Features 5-step wizard workflow, research templates, quality-gated progression, AI transparency, smart prompt composer, live preview, and can be built as a standalone Windows .exe.

**Architecture**: Modular 794-line GUI with integrated components (WizardNav, LivePreview, PromptComposer, AITransparencyPanel, ConnectionManager, QueryQualityGate). Built with professional typography system (Segoe UI hierarchy) and structured color palette.

## Quick Start Commands

```bash
# Launch GUI application
python src/scraper_gui.py

# Or use batch launcher
scripts/Launch_Scraper.bat

# Build standalone .exe (requires PyInstaller)
python scripts/build_exe.py

# Output: dist/YouTubeTranscriptScraper.exe (~150-200MB)
```

## Architecture

### World-Class Research Platform (794 Lines)

**Main Files**:
- `scraper_gui.py` (794 lines) - Complete research platform with wizard workflow
- `scraper_core.py` (171 lines) - Core scraping engine, reusable library
- `filters.py` (22 lines) - YouTube filter configurations
- `search_optimizer.py` (43 lines) - GPT-4 query optimization

**Utility Files**:
- `config.py` (29 lines) - API key persistence to `~/.youtube_scraper_config.json`
- `prompts.py` (45 lines) - GPT-4 "godly" search optimization prompt
- `build_exe.py` (28 lines) - PyInstaller build configuration

**GUI Component Architecture** (`scraper_gui.py`):
- `ProfessionalStyles` - Typography system (Segoe UI 24pt → 10pt) and color palette
- `WizardNav` - 5-step visual journey map (Define → Refine → Review → Run → Export)
- `LivePreview` - Real-time plain language summary + exportable JSON config
- `ChipInput/ChipSelector/ChipMultiSelect` - Structured input components
- `PromptComposer` - Smart prompt builder with 6 chips (topic, audience, time, quality, sources, goals)
- `AITransparencyPanel` - Expandable panel showing model, cost, technique, parameters
- `QueryQualityGate` - Scoring system (60/100 minimum to proceed)
- `ConnectionManager` - Modal for API key management, test connection, model picker
- `ResearchPlatform` - Main app with three-column layout (wizard | content | preview)

**Backup File**:
- `scraper_gui_v2_backup.py` (499 lines) - Previous three-panel accordion implementation

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

### World-Class Research Platform Features

**9 Integrated Phases** (794-line implementation):

**Phase 1: Visual Journey Map + Live Preview** (200 lines)
- Left rail wizard: 5 steps with visual indicators (Define 🎯, Refine ⚙️, Review 👁️, Run ▶️, Export 📦)
- Right panel live preview: Plain language summary + exportable JSON config
- Color-coded step states: Green (completed), Blue (current), Gray (pending)
- Copy to clipboard and export config functionality

**Phase 2: Smart Prompt Composer with Chips** (180 lines)
- Structured input via 6 chips: Topic, Audience, Time Window, Quality Bar, Sources, Output Goals
- Chip types: text input, dropdown selector, multi-checkbox
- Real-time query construction: "How {topic} applies to {audience}"
- Placeholder guidance for each component
- Live preview updates on every keystroke

**Phase 3: Research Templates** (120 lines)
- 6 opinionated presets with visual grid layout:
  - **Topic Overview**: 15 results, last 90 days, balanced depth
  - **Fact Check**: 10 results, last 30 days, high relevance
  - **Competitor Scan**: 25 results, last 6 months, sorted by views
  - **Citation Harvest**: 30 results, any time, sorted by rating
  - **Course Outline**: 40 results, any time, long videos only
  - **Custom**: User-defined settings
- Each template pre-populates chips, filters, and results slider

**Phase 4: AI Transparency Panel** (150 lines)
- Expandable section showing:
  - Model: GPT-4 (gpt-4-0613)
  - Technique: Semantic keyword expansion
  - Cost estimate: ~$0.02-0.04 per optimization
  - Before/After example transformation
  - Advanced parameters: Temperature slider (0.0-1.0), Max tokens spinbox
- Full transparency into AI optimization process

**Phase 5: Quality-Gated Progression** (100 lines)
- Real-time scoring algorithm (0-100 scale):
  - Topic required: 60 points
  - Audience bonus: 20 points
  - Time window bonus: 10 points
  - Output goals bonus: 10 points
- Minimum 60/100 to proceed to next step
- Actionable feedback list: "Add a topic to your research", "Specify your audience for +20 points"
- Visual progress bar showing score
- Next button disabled until quality gate passed

**Phase 6: Connection Manager Modal** (130 lines)
- Tabbed dialog (API Key | Security & Privacy):
  - API Key tab: paste field, test connection, model selection dropdown, save button
  - Security tab: encryption details, data usage policy, privacy promise
- Test connection validates with OpenAI API
- Model picker: gpt-4, gpt-3.5-turbo, gpt-4-turbo
- Usage caps and billing transparency

**Phase 7: Results Slider with Estimates** (60 lines)
- Slider with 3 presets:
  - **Quick scan**: 5 results (~2-3 min runtime, ~1K tokens)
  - **Balanced**: 15 results (~5-7 min runtime, ~3K tokens)
  - **Deep dive**: 50 results (~15-20 min runtime, ~10K tokens)
- Real-time runtime and cost estimates
- Visual labels at preset positions

**Phase 8: Typography & Visual Hierarchy** (80 lines)
- Professional typography system (Segoe UI):
  - Display: 24pt bold (main headings)
  - Heading1: 18pt bold (section headers)
  - Heading2: 14pt bold (subsections)
  - Body: 12pt (normal text)
  - Caption: 10pt (helper text)
  - Code: Consolas 11pt (technical details)
- Structured color palette:
  - Primary: #2563EB (Interactive Blue)
  - Success: #059669 (Green)
  - Warning: #D97706 (Orange)
  - Danger: #DC2626 (Red)
  - Text hierarchy: #111827 (primary), #6B7280 (secondary), #9CA3AF (tertiary)
  - Backgrounds: #F9FAFB (light), #FFFFFF (white), #F3F4F6 (gray)
- Generous whitespace: 20px section padding, 10px component spacing

**Phase 9: Sample Project + Help Drawer** (120 lines)
- First-run onboarding with sample research project
- Context-sensitive help for each step
- Keyboard navigation: Tab (next field), Enter (submit), Escape (cancel)
- Audit trail: All configurations logged to activity log

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
    filters={'upload_date': 7, 'sort_by': 'rating'}  # 7 days
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

**Implemented via post-processing**:
- Upload date: Days-based filtering (7, 30, 90, 180, 365 days)
- Sort by: Uses yt-dlp's `playlistsort` option (date, views, rating)
- Fetch 3x results, filter by upload_date, return max_results
- Filter options defined in `filters.py`: "Last 7 days", "Last 30 days", "Last 90 days", "Last 6 months", "Last year"

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

## Architecture Statistics

**Current Implementation**:
```
scraper_gui.py:      794 lines (world-class research platform)
scraper_core.py:     171 lines (core engine)
filters.py:           22 lines (filter configs)
search_optimizer.py:  43 lines (GPT-4 integration)
─────────────────────────────
TOTAL:              1030 lines
```

**Component Breakdown** (`scraper_gui.py`):
- Research templates dictionary: 37 lines
- ProfessionalStyles class: 35 lines
- WizardNav component: 37 lines
- LivePreview component: 45 lines
- Chip components (Input/Selector/MultiSelect): 43 lines
- PromptComposer component: 44 lines
- AITransparencyPanel component: 38 lines
- QueryQualityGate scoring system: 22 lines
- ConnectionManager modal: 54 lines
- ResearchPlatform main app: 374 lines (5 step frames + layout)

**Verification**:
```bash
wc -l src/scraper_gui.py src/scraper_core.py src/filters.py src/search_optimizer.py
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

1. **Modular architecture**: Components organized for clarity and maintainability
2. **Professional UX patterns**: Wizard workflow, quality gates, live preview, AI transparency
3. **Simpler is better**: YouTube search works best with 6-10 word queries
4. **Chrome required**: Selenium needs Chrome browser installed
5. **GPT-4 cost**: ~$0.03 per optimization (required for query accuracy)
6. **Quality-first**: 60/100 minimum score required to proceed with research
