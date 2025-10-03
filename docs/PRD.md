# Product Requirements Document: YouTube Transcript Scraper

## Overview
A lightweight, portable desktop application to search YouTube videos by topic and extract their transcripts based on user-defined filters.

## Project Scope
- **Type**: Standalone executable desktop application
- **Complexity**: Simple, <400 lines of code
- **Users**: Single user (personal use)
- **Platform**: Windows desktop application
- **Distribution**: GitHub repository for sharing and version control

## Core Features

### 1. Search Functionality
- Search YouTube videos by keyword/topic
- Return list of video results (title, URL, duration, channel)
- Limit results to configurable number (default: 10)

### 2. Filtering System
- **Results count**: Adjustable number of videos to scrape (1-50)
- **Duration filter**: Min/max video length
- **Date filter**: Videos from last X days/months
- **Channel filter**: Include/exclude specific channels
- **Language filter**: English transcripts only (initially)
- **Authenticity filters**:
  - Verified channel badge priority
  - Minimum subscriber count threshold (e.g., >100K)
  - Channel category filtering (Education, Howto, Entertainment, etc.)
  - Whitelist of trusted channels/creators
  - Blacklist of unwanted channels
- **Source priority system**:
  - Tier 1: Verified official channels
  - Tier 2: High subscriber count channels (>1M)
  - Tier 3: Medium subscriber count (100K-1M)
  - Optional: Filter out channels below threshold
- **Personal subscription filter**:
  - Option to limit search to subscribed channels only
  - Requires YouTube API key or channel list input

### 3. Transcript Extraction
- Fetch transcripts for filtered videos
- Handle videos with auto-generated captions
- Skip videos without available transcripts
- Display extraction progress

### 4. Output Options
- **Individual markdown files per video** (required format)
- **No timestamps in transcript text** (clean, readable text only)
- **Proper markdown formatting**:
  - Clean headers with video title
  - Metadata section (channel, URL, date)
  - Evenly spaced paragraphs
  - No special characters (ASCII-safe filenames)
  - Consistent line spacing throughout
- **File naming convention**:
  - `[VideoTitle]_[Channel]_[Date].md`
  - Sanitized filenames (no special characters)
  - Max 100 characters per filename
- **Optional**: Create index file listing all scraped videos

## Technical Requirements
- **Language**: Python 3.8+
- **Libraries**: youtube-transcript-api, pytube/yt-dlp, pandas, requests
- **Storage**: Local file system
- **Packaging**: PyInstaller for Windows executable
- **API Access**:
  - Public YouTube Data API for channel metadata
  - Optional: YouTube API key for enhanced features
  - No authentication required for basic operation

## Distribution Requirements

### Executable Package
- Single .exe file for Windows
- No Python installation required for end user
- Desktop shortcut creation capability
- Icon file for visual identification

### Portability
- Self-contained executable with all dependencies
- No registry modifications required
- Settings stored in local config file
- Can run from USB drive or any directory

### GitHub Repository Structure
```
youtube-transcript-scraper/
├── main.py                 # Main application code
├── requirements.txt        # Python dependencies
├── build.bat              # Build script for executable
├── README.md              # Usage instructions
├── LICENSE                # MIT or similar
├── config.json            # Default configuration
└── dist/                  # Compiled executable directory
    └── YouTubeTranscriptScraper.exe
```

## User Interface
- Command-line interface (CLI)
- Simple prompts for:
  - Search query
  - Filter preferences
  - Output format selection
  - Save location
- Clear console output with progress indicators

## Installation Methods

### Method 1: Executable (For End Users)
1. Download .exe from GitHub releases
2. Place in desired folder
3. Create desktop shortcut
4. Double-click to run

### Method 2: Source Code (For Developers)
1. Clone GitHub repository
2. Install Python dependencies
3. Run python script directly
4. Optional: Build own executable

## Constraints
- No GUI required
- Single-threaded operation acceptable
- Rate limiting compliance with YouTube
- No video downloading (transcripts only)
- Windows-focused (cross-platform not required)

## Success Criteria
- Successfully searches and returns YouTube videos
- Applies filters accurately
- **Prioritizes content from verified/legitimate creators**
- **Filters out low-quality or amateur content based on thresholds**
- **Successfully retrieves channel metadata for authenticity checks**
- Extracts transcripts for 80%+ of filtered videos
- **Removes all timestamps from transcript text**
- **Saves each video transcript as separate markdown file**
- **Maintains clean formatting with proper spacing**
- **Uses ASCII-safe filenames without special characters**
- Saves output in readable format with source attribution
- Runs without errors on standard videos
- Executable runs without Python installed
- Can be shared via GitHub download
- **Respects user's subscribed channels when option enabled**

## Out of Scope
- Video/audio downloading
- Real-time transcript streaming
- Multi-language support (v1)
- Browser extension
- Database storage
- User authentication
- Batch scheduling
- Auto-update functionality
- MacOS/Linux executables (v1)

## Example Usage Flow
1. Double-click desktop shortcut
2. Console window opens
3. Enter search term: "how to make peanut butter and jelly sandwich"
4. Select number of videos: 5
5. Apply filters:
   - Videos from last week
   - Minimum 100K subscribers
   - Verified channels preferred
   - Category: Cooking/Food
6. System prioritizes results:
   - Checks for verified badges
   - Filters by subscriber count
   - Matches against trusted cooking channels list
7. Returns 5 videos from legitimate sources (e.g., Gordon Ramsay, Jamie Oliver, Food Network)
8. Extracts available transcripts (removes all timestamps)
9. Saves each transcript as separate markdown file:
   - `How_to_Make_PBJ_GordonRamsay_2025-01-15.md`
   - `Perfect_PBJ_Sandwich_JamieOliver_2025-01-14.md`
10. Press Enter to exit or search again

## Error Handling
- Gracefully skip videos without transcripts
- Display clear error messages
- Continue processing remaining videos on individual failures
- Log skipped videos to separate file
- Catch and handle network timeouts
- Provide retry option for failed operations

## Content Authenticity Strategy

### Verification Methods
1. **Channel Verification Check**: Prioritize YouTube verified badge channels
2. **Subscriber Threshold**: Filter channels below configurable minimum (default: 100K)
3. **Channel Age**: Consider account creation date (>1 year preferred)
4. **Upload Consistency**: Regular upload schedule indicates legitimate creator
5. **View-to-Subscriber Ratio**: Flag suspicious ratios

### Trusted Source Management
- **Pre-configured trusted lists by category**:
  - Cooking: Gordon Ramsay, Jamie Oliver, Bon Appetit, Food Network, America's Test Kitchen
  - Tech: MKBHD, Linus Tech Tips, Unbox Therapy, CNET, The Verge
  - Education: Khan Academy, CrashCourse, TED, Veritasium, MIT OpenCourseWare
- **User-customizable whitelist**: Add personal trusted channels
- **Blacklist functionality**: Exclude specific channels permanently
- **Category-specific rules**: Different thresholds for different content types

### Subscription Integration
- **Option 1**: Manual channel list input (privacy-focused)
- **Option 2**: YouTube API integration for automatic subscription fetch
- **Hybrid mode**: Combine subscriptions with public trusted sources

## Performance Targets
- Search results: <5 seconds
- Transcript extraction: <2 seconds per video
- Total operation for 10 videos: <30 seconds
- Executable size: <50MB
- Startup time: <3 seconds

## Configuration File
- JSON format for easy editing
- Default search parameters
- Output directory preference
- Filter presets
- API rate limiting settings
- **Trusted sources lists**:
  - Whitelist of verified channels (e.g., "Gordon Ramsay", "Jamie Oliver", "Bon Appetit")
  - Category-specific trusted sources
  - Minimum subscriber thresholds by category
- **Personal channel lists**:
  - Manual list of subscribed channels
  - Import option for channel URLs/IDs

## Sample Output Format

### Markdown File Example: `How_to_Make_PBJ_GordonRamsay_2025-01-15.md`

```markdown
# How to Make the Perfect PBJ Sandwich

## Video Information
- **Channel**: Gordon Ramsay
- **URL**: https://youtube.com/watch/example123
- **Published**: January 15, 2025
- **Duration**: 8 minutes
- **Subscribers**: 21.5M

## Transcript

Right, let me show you how to make a proper peanut butter and jelly sandwich. This isnt just slapping two pieces of bread together. Were going to do this properly.

First, you need quality ingredients. Get yourself a decent whole grain bread, none of that processed white nonsense. The peanut butter should be natural, no added sugars or oils. And the jam, please, get a proper preserve with actual fruit in it.

Start by toasting your bread lightly. This creates a barrier that prevents the sandwich from going soggy. While the bread is still warm, spread your peanut butter on one slice. The warmth helps it spread evenly.

[Content continues with clean, formatted paragraphs...]
```

## Build and Release Process
1. Update version number
2. Run PyInstaller build script
3. Test executable on clean Windows system
4. Create GitHub release with:
   - Executable file
   - Source code
   - Release notes
   - Usage instructions

---

**Deliverables**:
1. Python source code with clear comments
2. Windows executable file
3. GitHub repository with documentation
4. Build instructions for creating executable
5. Desktop shortcut creation guide
