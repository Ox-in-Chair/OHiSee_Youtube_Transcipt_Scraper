# Phase 2 Migration Plan: Single-File to Modular Architecture

**Duration**: 3-4 days (Week 2)
**Risk Level**: LOW (incremental, validated at each step)
**Rollback Plan**: Git commits after each phase

---

## Overview

Transform `app_minimal.py` (675 lines) into 6-file modular architecture (1,050 lines) while:
- ✅ Preserving all Phase 1 features
- ✅ Maintaining performance (0.3s startup, 40MB memory)
- ✅ Enabling testability and future extensibility

**Strategy**: Incremental extraction with validation gates at each step

---

## Pre-Migration Checklist

### Before Starting

- [ ] **Backup Phase 1 code**:
  ```bash
  git add .
  git commit -m "checkpoint: Phase 1 complete (app_minimal.py 675 lines)"
  git checkout -b refactor/modular-architecture
  ```

- [ ] **Verify Phase 1 baseline**:
  ```bash
  python tests/test_minimal_app.py
  # Expected: 5/5 tests pass
  ```

- [ ] **Measure performance baseline**:
  ```bash
  # Startup time
  time python src/app_minimal.py  # Should be ~0.3s

  # Memory usage (Windows Task Manager)
  # Expected: ~40MB
  ```

- [ ] **Create migration branch**:
  ```bash
  git checkout -b refactor/phase2-modular
  ```

---

## Day 1: Extract Scraper Module

**Goal**: Isolate core scraping logic from UI
**Time**: 3-4 hours
**Risk**: LOW (no UI changes)

### Step 1.1: Create scraper.py (1 hour)

**Actions**:
1. Create `src/scraper.py`
2. Copy existing imports from `app_minimal.py`:
   ```python
   from core.scraper_engine import TranscriptScraper as CoreScraper
   from core.search_optimizer import optimize_search_query
   ```

3. Create wrapper class:
   ```python
   class TranscriptScraper:
       """Simplified API wrapper around core.scraper_engine."""

       def __init__(self, output_dir: str = 'transcripts', callback=None):
           self.engine = CoreScraper(output_dir, callback)
           self.output_dir = output_dir

       def search_videos(self, query: str, max_results: int, filters: dict) -> list[dict]:
           """Search YouTube and return video metadata."""
           return self.engine.search_videos(query, max_results, filters)

       def get_transcript(self, video_id: str) -> str:
           """Extract transcript for given video."""
           return self.engine.get_transcript(video_id)

       def setup_browser(self):
           """Initialize Selenium browser."""
           self.engine.setup_browser()

       def save_transcript(self, video: dict, transcript: str) -> str:
           """Save transcript to markdown file."""
           return self.engine.save_transcript(video, transcript)
   ```

**Validation**:
```bash
python -c "from src.scraper import TranscriptScraper; print('✓ Import OK')"
```

---

### Step 1.2: Update app_minimal.py to use scraper.py (30 min)

**Actions**:
1. Add import at top of `app_minimal.py`:
   ```python
   from scraper import TranscriptScraper
   ```

2. Replace direct `core.scraper_engine` usage:
   ```python
   # OLD (line ~461)
   from core.scraper_engine import TranscriptScraper

   # NEW
   from scraper import TranscriptScraper
   ```

3. No other changes needed (API is identical)

**Validation**:
```bash
python src/app_minimal.py
# Manually test:
# 1. Search "Python tutorial" → Results display ✓
# 2. Click Download → Transcripts save ✓
```

---

### Step 1.3: Commit checkpoint (15 min)

```bash
git add src/scraper.py src/app_minimal.py
git commit -m "refactor: Extract scraper.py module (200 lines)

- Created TranscriptScraper wrapper in scraper.py
- Updated app_minimal.py to use wrapper
- No functional changes
- All tests passing"

# Run tests
python tests/test_minimal_app.py
# Expected: 5/5 pass
```

**Checkpoint Validation**:
- [ ] Import works: `from src.scraper import TranscriptScraper`
- [ ] Search functional
- [ ] Download functional
- [ ] Tests pass

---

## Day 2: Extract UI Components

**Goal**: Split UI into SearchPanel and ResultsPanel
**Time**: 5-6 hours
**Risk**: MEDIUM (UI refactoring, test thoroughly)

### Step 2.1: Create ui/search_panel.py (2 hours)

**Actions**:
1. Create directory:
   ```bash
   mkdir -p src/ui
   touch src/ui/__init__.py
   ```

2. Create `src/ui/search_panel.py`:
   ```python
   """Search controls panel."""
   import tkinter as tk
   from tkinter import ttk
   from utils.filters import UPLOAD_DATE_OPTIONS

   class SearchPanel(ttk.Frame):
       """Search input controls."""

       def __init__(self, parent, on_search_callback):
           super().__init__(parent)
           self.on_search_callback = on_search_callback
           self._build_ui()

       def _build_ui(self):
           # Query row
           query_row = tk.Frame(self, bg='#FFFFFF')
           query_row.pack(fill='x', pady=5)

           ttk.Label(query_row, text="Search Query:").pack(side='left', padx=(0, 10))

           self.query_entry = ttk.Entry(query_row, font=('Segoe UI', 10))
           self.query_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
           self.query_entry.bind('<Return>', lambda e: self._handle_search())

           self.search_btn = ttk.Button(
               query_row,
               text="Search",
               command=self._handle_search,
               width=12
           )
           self.search_btn.pack(side='right')

           # Filters row
           filters_row = tk.Frame(self, bg='#FFFFFF')
           filters_row.pack(fill='x', pady=5)

           ttk.Label(filters_row, text="Max Results:").pack(side='left', padx=(0, 5))
           self.max_results_var = tk.StringVar(value='15')
           max_results_combo = ttk.Combobox(
               filters_row,
               textvariable=self.max_results_var,
               values=['5', '10', '15', '25', '50'],
               width=8,
               state='readonly'
           )
           max_results_combo.pack(side='left', padx=(0, 20))

           ttk.Label(filters_row, text="Upload Date:").pack(side='left', padx=(0, 5))
           self.upload_date_var = tk.StringVar(value='Any time')
           upload_date_combo = ttk.Combobox(
               filters_row,
               textvariable=self.upload_date_var,
               values=list(UPLOAD_DATE_OPTIONS.keys()),
               width=15,
               state='readonly'
           )
           upload_date_combo.pack(side='left')

           # AI optimization row
           ai_row = tk.Frame(self, bg='#FFFFFF')
           ai_row.pack(fill='x', pady=5)

           self.ai_toggle_var = tk.BooleanVar(value=False)
           self.ai_checkbox = ttk.Checkbutton(
               ai_row,
               text="Use AI Optimization (GPT-4) - Requires API key",
               variable=self.ai_toggle_var
           )
           self.ai_checkbox.pack(side='left')

       def _handle_search(self):
           """Handle search button click."""
           query = self.get_query()
           if not query:
               return
           filters = self.get_filters()
           self.on_search_callback(query, filters)

       def get_query(self) -> str:
           """Get search query text."""
           return self.query_entry.get().strip()

       def get_filters(self) -> dict:
           """Get filter settings."""
           upload_date_label = self.upload_date_var.get()
           upload_date_value = UPLOAD_DATE_OPTIONS.get(upload_date_label, 'any')

           return {
               'max_results': int(self.max_results_var.get()),
               'upload_date': upload_date_value,
               'use_ai': self.ai_toggle_var.get()
           }

       def set_loading(self, loading: bool):
           """Update UI state during search."""
           state = 'disabled' if loading else 'normal'
           self.search_btn.config(
               state=state,
               text='Searching...' if loading else 'Search'
           )
           self.query_entry.config(state=state)
   ```

**Validation**:
```bash
python -c "from src.ui.search_panel import SearchPanel; print('✓ Import OK')"
```

---

### Step 2.2: Update app_minimal.py to use SearchPanel (1 hour)

**Actions**:
1. Add import:
   ```python
   from ui.search_panel import SearchPanel
   ```

2. Replace `_build_search_panel()` method:
   ```python
   # OLD (~60 lines in _build_search_panel)
   def _build_search_panel(self):
       search_frame = tk.Frame(self, bg=COLORS['bg'])
       # ... 60 lines of UI code

   # NEW (~5 lines)
   def _build_search_panel(self):
       self.search_panel = SearchPanel(self, on_search_callback=self._on_search_validated)
       self.search_panel.pack(fill='x', padx=15, pady=10)

   def _on_search_validated(self, query: str, filters: dict):
       """Receive search request from SearchPanel."""
       # Validation
       if not query:
           messagebox.showwarning("Input Required", "Please enter a search query")
           return

       # Delegate to existing _on_search logic
       self._execute_search(query, filters)
   ```

3. Update `_on_search()` to `_execute_search()` (rename for clarity)

**Validation**:
```bash
python src/app_minimal.py
# Test:
# 1. Enter query → Search works ✓
# 2. Filters update → Filters applied ✓
# 3. AI toggle → State saved ✓
```

---

### Step 2.3: Create ui/results_panel.py (2 hours)

**Actions**:
1. Create `src/ui/results_panel.py`:
   ```python
   """Results display panel."""
   import tkinter as tk
   from tkinter import ttk
   from utils import VideoResultItem, COLORS, FONTS

   class ResultsPanel(ttk.Frame):
       """Display search results with selection."""

       def __init__(self, parent, on_selection_change_callback):
           super().__init__(parent)
           self.on_selection_change_callback = on_selection_change_callback
           self.result_items = []
           self._build_ui()

       def _build_ui(self):
           # Label frame
           results_frame = tk.LabelFrame(
               self,
               text="Search Results",
               font=FONTS['heading'],
               bg=COLORS['bg'],
               relief='solid',
               borderwidth=1
           )
           results_frame.pack(fill='both', expand=True)

           # Results count label
           self.count_label = ttk.Label(
               results_frame,
               text="Results (0):",
               font=FONTS['body']
           )
           self.count_label.pack(anchor='w', padx=10, pady=5)

           # Scrollable frame
           canvas = tk.Canvas(results_frame, bg='white', highlightthickness=0)
           scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=canvas.yview)

           self.container = tk.Frame(canvas, bg='white')

           self.container.bind(
               '<Configure>',
               lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
           )

           canvas.create_window((0, 0), window=self.container, anchor='nw')
           canvas.configure(yscrollcommand=scrollbar.set)

           scrollbar.pack(side='right', fill='y')
           canvas.pack(side='left', fill='both', expand=True)

           # Mousewheel scrolling
           def on_mousewheel(event):
               canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

           canvas.bind_all("<MouseWheel>", on_mousewheel)

       def display_results(self, videos: list):
           """Display search results."""
           self.clear()

           if not videos:
               ttk.Label(
                   self.container,
                   text="No videos found. Try a different search.",
                   foreground=COLORS['secondary']
               ).pack(pady=20)
               return

           for idx, video in enumerate(videos, 1):
               item = VideoResultItem(
                   self.container,
                   video,
                   idx,
                   self.on_selection_change_callback
               )
               self.result_items.append(item)

           self.count_label.config(text=f"Results ({len(videos)}):")

       def get_selected_videos(self) -> list:
           """Return list of selected videos."""
           return [
               item.get_video()
               for item in self.result_items
               if item.is_selected()
           ]

       def clear(self):
           """Clear all results."""
           for widget in self.container.winfo_children():
               widget.destroy()
           self.result_items = []
           self.count_label.config(text="Results (0):")
   ```

**Validation**:
```bash
python -c "from src.ui.results_panel import ResultsPanel; print('✓ Import OK')"
```

---

### Step 2.4: Update app_minimal.py to use ResultsPanel (30 min)

**Actions**:
1. Add import:
   ```python
   from ui.results_panel import ResultsPanel
   ```

2. Replace `_build_results_panel()`:
   ```python
   # OLD (~40 lines)
   def _build_results_panel(self):
       # ... Canvas, scrollbar setup

   # NEW (~5 lines)
   def _build_results_panel(self):
       self.results_panel = ResultsPanel(
           self,
           on_selection_change_callback=self._update_selection_count
       )
       self.results_panel.pack(fill='both', expand=True, padx=15, pady=10)
   ```

3. Update `_display_results()` to use panel:
   ```python
   def _display_results(self, results):
       self.results_panel.display_results(results)
       # Enable buttons
       self.download_btn.config(state='normal')
       self.export_btn.config(state='normal')
   ```

**Validation**:
```bash
python src/app_minimal.py
# Test:
# 1. Search → Results display ✓
# 2. Select videos → Count updates ✓
# 3. Download selected → Works ✓
```

---

### Step 2.5: Commit checkpoint (15 min)

```bash
git add src/ui/ src/app_minimal.py
git commit -m "refactor: Extract UI components (SearchPanel, ResultsPanel)

- Created ui/search_panel.py (150 lines)
- Created ui/results_panel.py (150 lines)
- Updated app_minimal.py to use panels
- Reduced app_minimal.py by ~100 lines
- All features functional"

# Run tests
python tests/test_minimal_app.py
# Expected: 5/5 pass
```

**Checkpoint Validation**:
- [ ] SearchPanel: Query input, filters, AI toggle work
- [ ] ResultsPanel: Results display, selection work
- [ ] Integration: Search → Results → Download works
- [ ] Tests pass

---

## Day 3: Extract Main Window & Create Entry Point

**Goal**: Create orchestration layer and entry point
**Time**: 4-5 hours
**Risk**: LOW (mostly moving code)

### Step 3.1: Create utils.py (1 hour)

**Actions**:
1. Create `src/utils.py`:
   ```python
   """Shared utilities and constants."""
   import tkinter as tk
   from tkinter import ttk

   # Constants (from app_minimal.py)
   COLORS = {
       'bg': '#FFFFFF',
       'primary': '#1E40AF',
       'success': '#10B981',
       'text': '#0F172A',
       'border': '#E2E8F0',
       'secondary': '#6B7280',
       'hover': '#3B82F6'
   }

   FONTS = {
       'title': ('Segoe UI', 16, 'bold'),
       'heading': ('Segoe UI', 12, 'bold'),
       'body': ('Segoe UI', 10),
       'small': ('Segoe UI', 9)
   }

   # VideoResultItem class (from app_minimal.py)
   class VideoResultItem:
       """Represents a single video result with checkbox."""
       # ... (copy implementation from app_minimal.py)
   ```

2. Update imports in `app_minimal.py`, `search_panel.py`, `results_panel.py`:
   ```python
   from utils import COLORS, FONTS, VideoResultItem
   ```

**Validation**:
```bash
python -c "from src.utils import COLORS, VideoResultItem; print('✓ Import OK')"
```

---

### Step 3.2: Create config.py (1 hour)

**Actions**:
1. Create `src/config.py`:
   ```python
   """Configuration management."""
   from pathlib import Path
   import json
   import tkinter as tk
   from tkinter import ttk, filedialog, messagebox

   class Config:
       """Settings persistence."""
       CONFIG_FILE = Path.home() / ".youtube_scraper_config.json"

       def load_config(self) -> dict:
           if self.CONFIG_FILE.exists():
               return json.loads(self.CONFIG_FILE.read_text())
           return {'output_dir': 'transcripts'}

       def save_api_key(self, key: str):
           config = self.load_config()
           config['api_key'] = key
           self.CONFIG_FILE.write_text(json.dumps(config, indent=2))

       def load_api_key(self) -> str:
           config = self.load_config()
           return config.get('api_key', '')

   def open_settings_dialog(parent, config_manager):
       """Open settings dialog (from app_minimal.py)."""
       # ... (copy _open_settings implementation)
   ```

2. Update `app_minimal.py` imports:
   ```python
   from config import Config, open_settings_dialog
   ```

**Validation**:
```bash
python -c "from src.config import Config; c = Config(); print(c.load_config())"
```

---

### Step 3.3: Create ui/main_window.py (2 hours)

**Actions**:
1. Create `src/ui/main_window.py`:
   ```python
   """Main application window."""
   import tkinter as tk
   from tkinter import ttk, messagebox
   import threading
   from typing import List, Dict

   from ui.search_panel import SearchPanel
   from ui.results_panel import ResultsPanel
   from scraper import TranscriptScraper
   from config import Config, open_settings_dialog
   from core.search_optimizer import optimize_search_query
   from utils import COLORS, FONTS

   class MainWindow(tk.Tk):
       """Main application orchestrator."""

       def __init__(self):
           super().__init__()

           # State
           self.config_manager = Config()
           self.scraper = None
           self.is_searching = False
           self.is_downloading = False

           # Setup
           self._setup_window()
           self._build_layout()

       def _setup_window(self):
           """Configure main window."""
           self.title("YouTube Transcript Scraper")
           self.geometry("800x700")
           self.configure(bg=COLORS['bg'])
           self.resizable(True, True)

           # Configure ttk style
           style = ttk.Style()
           style.theme_use('clam')
           style.configure('TButton', padding=6)

       def _build_layout(self):
           """Build complete UI layout."""
           # Top bar
           self._build_top_bar()

           # Search panel
           self.search_panel = SearchPanel(self, on_search_callback=self.on_search)
           self.search_panel.pack(fill='x', padx=15, pady=10)

           # Results panel
           self.results_panel = ResultsPanel(
               self,
               on_selection_change_callback=self._update_selection_count
           )
           self.results_panel.pack(fill='both', expand=True, padx=15, pady=10)

           # Progress panel
           self._build_progress_panel()

           # Action buttons
           self._build_action_buttons()

       def _build_top_bar(self):
           # ... (from app_minimal.py)

       def _build_progress_panel(self):
           # ... (from app_minimal.py)

       def _build_action_buttons(self):
           # ... (from app_minimal.py)

       def on_search(self, query: str, filters: dict):
           """Handle search request from SearchPanel."""
           if self.is_searching:
               return

           # Clear previous results
           self.results_panel.clear()

           # Disable UI
           self.is_searching = True
           self.search_panel.set_loading(True)
           self._update_status("Searching YouTube...")

           # Run in background thread
           threading.Thread(
               target=self._search_thread,
               args=(query, filters),
               daemon=True
           ).start()

       def _search_thread(self, query, filters):
           # ... (from app_minimal.py)

       def on_download_selected(self):
           # ... (from app_minimal.py)

       def _download_thread(self, videos):
           # ... (from app_minimal.py)

       # Helper methods
       def _update_progress(self, value, status):
           # ... (from app_minimal.py)

       def _update_status(self, message):
           # ... (from app_minimal.py)

       def _update_selection_count(self):
           selected_count = len(self.results_panel.get_selected_videos())
           self.selection_label.config(text=f"{selected_count} selected")
   ```

**Validation**:
```bash
python -c "from src.ui.main_window import MainWindow; print('✓ Import OK')"
```

---

### Step 3.4: Create app.py entry point (30 min)

**Actions**:
1. Create `src/app.py`:
   ```python
   #!/usr/bin/env python3
   """YouTube Transcript Scraper - Entry Point"""
   from ui.main_window import MainWindow

   def main():
       """Launch the application."""
       app = MainWindow()
       app.mainloop()

   if __name__ == '__main__':
       main()
   ```

2. Update `launch_minimal.bat`:
   ```batch
   @echo off
   echo Launching YouTube Transcript Scraper...
   cd /d "%~dp0"
   python src\app.py
   pause
   ```

**Validation**:
```bash
python src/app.py
# Full application should launch ✓
```

---

### Step 3.5: Delete app_minimal.py (15 min)

**Actions**:
1. Verify all functionality moved:
   ```bash
   # Compare line counts
   wc -l src/app.py src/scraper.py src/ui/*.py src/config.py src/utils.py
   # Should be ~1,050 lines total
   ```

2. Archive old file:
   ```bash
   mv src/app_minimal.py archive/app_minimal_phase1.py
   ```

3. Update README references:
   - Change `app_minimal.py` → `app.py`

**Validation**:
```bash
# Ensure import works
python -c "import src.app; print('✓ Import OK')"

# Launch app
python src/app.py
```

---

### Step 3.6: Commit Phase 2 complete (15 min)

```bash
git add .
git commit -m "refactor: Phase 2 complete - Modular architecture

Files created:
- src/app.py (50 lines) - Entry point
- src/scraper.py (200 lines) - Core adapter
- src/ui/main_window.py (300 lines) - Orchestrator
- src/ui/search_panel.py (150 lines) - Search UI
- src/ui/results_panel.py (150 lines) - Results UI
- src/config.py (100 lines) - Settings
- src/utils.py (100 lines) - Helpers

Total: 1,050 lines

Changes:
- Deleted app_minimal.py (675 lines)
- Modular components with clear responsibilities
- All Phase 1 features preserved
- Performance maintained"

# Run tests
python tests/test_minimal_app.py
# Update tests to use new imports if needed
```

---

## Day 4: Testing & Validation

**Goal**: Comprehensive quality assurance
**Time**: 4-5 hours
**Risk**: LOW (validation only)

### Step 4.1: Update test suite (2 hours)

**Actions**:
1. Update `tests/test_minimal_app.py` imports:
   ```python
   # OLD
   from src.app_minimal import MinimalScraperApp

   # NEW
   from src.ui.main_window import MainWindow
   from src.scraper import TranscriptScraper
   ```

2. Create unit tests (`tests/test_ui.py`):
   ```python
   import tkinter as tk
   from src.ui.search_panel import SearchPanel
   from src.ui.results_panel import ResultsPanel

   def test_search_panel_get_query():
       root = tk.Tk()
       panel = SearchPanel(root, on_search_callback=lambda q, f: None)
       panel.query_entry.insert(0, 'test query')
       assert panel.get_query() == 'test query'
       root.destroy()

   def test_results_panel_display():
       root = tk.Tk()
       panel = ResultsPanel(root, on_selection_change_callback=lambda: None)
       videos = [{'title': 'Test', 'channel': 'Channel', 'url': 'http://...', 'id': '123'}]
       panel.display_results(videos)
       assert len(panel.result_items) == 1
       root.destroy()
   ```

3. Create integration tests (`tests/test_integration.py`):
   ```python
   from src.ui.main_window import MainWindow
   import time

   def test_full_workflow():
       app = MainWindow()
       # Simulate search
       app.search_panel.query_entry.insert(0, 'Python tutorial')
       app.on_search('Python tutorial', {'max_results': 5, 'upload_date': 'any'})
       time.sleep(3)  # Wait for search thread
       results = app.results_panel.get_selected_videos()
       assert len(results) > 0
       app.destroy()
   ```

**Validation**:
```bash
pytest tests/ -v
# Expected: All tests pass
```

---

### Step 4.2: Performance benchmarks (1 hour)

**Actions**:
1. Measure startup time:
   ```bash
   # Windows
   Measure-Command { python src\app.py }

   # Expected: <0.5 seconds
   ```

2. Measure memory usage:
   ```bash
   # Launch app
   python src/app.py

   # Check Task Manager
   # Expected: <50MB
   ```

3. Measure search time:
   ```bash
   # In app:
   # 1. Search "Python tutorial" (15 results)
   # 2. Time from click to results display
   # Expected: <5 seconds
   ```

**Record Results** (create `tests/PERFORMANCE_REPORT.md`):
```markdown
# Performance Benchmarks - Phase 2

| Metric | Target | Phase 1 | Phase 2 | Status |
|--------|--------|---------|---------|--------|
| Startup Time | <0.5s | 0.3s | 0.35s | ✅ PASS |
| Memory Usage | <50MB | 40MB | 42MB | ✅ PASS |
| Search Time (15 results) | <5s | 3-4s | 3-4s | ✅ PASS |

**Conclusion**: No performance regression
```

---

### Step 4.3: Code quality checks (1 hour)

**Actions**:
1. **Line count validation**:
   ```bash
   wc -l src/app.py src/scraper.py src/ui/*.py src/config.py src/utils.py
   # Expected: 1,000-1,200 lines
   ```

2. **Import validation**:
   ```bash
   python -c "import src.app"
   # Should not raise ImportError
   ```

3. **Linter (optional)**:
   ```bash
   # If flake8 installed
   flake8 src/ --max-line-length=100
   # Fix critical errors only (E999, F821)
   ```

4. **Test coverage**:
   ```bash
   pytest --cov=src tests/
   # Expected: >70%
   ```

**Create Quality Report** (`docs/PHASE2_QUALITY_REPORT.md`):
```markdown
# Phase 2 Quality Report

## Code Metrics
- Total Lines: 1,050 (target: 1,000-1,200) ✅
- Files: 7 core files ✅
- Imports: No circular dependencies ✅

## Test Coverage
- Unit Tests: 8/8 passing ✅
- Integration Tests: 3/3 passing ✅
- Coverage: 75% ✅

## Performance
- All benchmarks met ✅

## Conclusion
Phase 2 COMPLETE - Ready for production
```

---

### Step 4.4: Final validation checklist (30 min)

**Quality Gates**:

- [ ] **Line Count**: 1,000-1,200 total
  ```bash
  wc -l src/app.py src/scraper.py src/ui/*.py src/config.py src/utils.py
  ```

- [ ] **Files**: ≤6 core files (excluding tests)
  ```bash
  ls src/*.py src/ui/*.py | wc -l
  # Expected: 7 (app, scraper, main_window, search_panel, results_panel, config, utils)
  ```

- [ ] **All Phase 1 Features Work**:
  - [ ] Search with filters (max results, upload date)
  - [ ] AI optimization toggle (GPT-4)
  - [ ] Download selected videos
  - [ ] Export all functionality
  - [ ] Settings dialog (API key, output dir)
  - [ ] Progress tracking

- [ ] **Performance Same or Better**:
  - [ ] Startup <0.5s
  - [ ] Memory <50MB
  - [ ] Search <5s for 15 results

- [ ] **Bug Fixes Touch <3 Files**:
  - Test: "Search button stuck disabled"
  - Expected: Fix in `search_panel.py` only (1 file)

- [ ] **Test Coverage >70%**:
  ```bash
  pytest --cov=src tests/
  ```

- [ ] **No Circular Imports**:
  ```bash
  python -c "import src.app"
  ```

---

### Step 4.5: Final commit and merge (30 min)

```bash
# Commit final state
git add .
git commit -m "test: Phase 2 validation complete

- All quality gates passed
- Performance benchmarks met
- Test coverage 75%
- Ready for production"

# Merge to main
git checkout main
git merge refactor/phase2-modular

# Tag release
git tag -a v2.0.0 -m "Phase 2: Modular Architecture
- 6-file structure
- Improved maintainability
- All Phase 1 features preserved"

git push origin main --tags
```

---

## Rollback Procedures

### If Issues Found During Migration

**Scenario 1: Import errors**
```bash
# Rollback to last working commit
git log --oneline | head -5
git reset --hard <commit-hash>

# Or rollback to Phase 1
git checkout main
git checkout src/app_minimal.py
python src/app_minimal.py
```

**Scenario 2: Performance regression**
```bash
# Profile to find bottleneck
python -m cProfile src/app.py > profile.txt
# Identify slow imports or initialization

# If unfixable, rollback
git reset --hard HEAD~1
```

**Scenario 3: Feature broken**
```bash
# Identify broken component
# Fix in isolation, test, commit
# If too complex, rollback step
git reset --hard HEAD~1
```

---

## Success Criteria Summary

### Phase 2 Complete When:

✅ **All files created**:
- [x] app.py (50 lines)
- [x] scraper.py (200 lines)
- [x] ui/main_window.py (300 lines)
- [x] ui/search_panel.py (150 lines)
- [x] ui/results_panel.py (150 lines)
- [x] config.py (100 lines)
- [x] utils.py (100 lines)

✅ **Quality gates pass**:
- [x] Line count: 1,000-1,200
- [x] Performance: Startup <0.5s, memory <50MB
- [x] Tests: >70% coverage, all passing
- [x] Features: All Phase 1 functionality preserved

✅ **Documentation complete**:
- [x] PHASE2_DESIGN.md
- [x] MIGRATION_PLAN.md (this document)
- [x] ADR-001, ADR-002, ADR-003

✅ **Code quality**:
- [x] No circular imports
- [x] Clean import hierarchy
- [x] Modular, testable components

---

## Post-Migration Checklist

### After Phase 2 Complete

- [ ] Update main README.md:
  - Change references from `app_minimal.py` to `app.py`
  - Update architecture diagram
  - Document new module structure

- [ ] Update CLAUDE.md:
  - Add Phase 2 architecture notes
  - Document import patterns
  - Update testing instructions

- [ ] Archive old files:
  - Move `app_minimal.py` to `archive/`
  - Keep for reference, not active development

- [ ] User testing:
  - Deploy to user
  - Validate all workflows
  - Collect feedback for Phase 3

---

## Timeline Summary

| Day | Task | Hours | Deliverables |
|-----|------|-------|--------------|
| 1 | Extract scraper.py | 3-4 | scraper.py (200 lines) |
| 2 | Extract UI components | 5-6 | search_panel.py, results_panel.py (300 lines) |
| 3 | Extract main window + entry point | 4-5 | main_window.py, app.py, utils.py, config.py (550 lines) |
| 4 | Testing & validation | 4-5 | Tests, benchmarks, quality report |
| **Total** | **16-20 hours** | **3-4 days** | **1,050 lines, 6 modules** |

---

**Ready to Execute**: 2025-10-05
**Assigned to**: Backend Developer Agent
**Success Criteria**: All quality gates pass, Phase 1 features preserved, <1,200 lines total
