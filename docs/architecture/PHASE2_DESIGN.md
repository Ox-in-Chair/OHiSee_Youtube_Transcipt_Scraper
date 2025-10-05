# PHASE 2: Modular Architecture Design

**Status**: DESIGN COMPLETE - Ready for Implementation
**Date**: 2025-10-05
**Target**: Week 2 Delivery (3-4 days)

---

## Executive Summary

Transform Phase 1's successful 675-line single-file MVP into a sustainable 1,200-line modular architecture that:
- ✅ Preserves all Phase 1 features and performance
- ✅ Improves maintainability (bug fixes touch <3 files)
- ✅ Enables future extensibility without code bloat
- ✅ Maintains simplicity (no over-engineering)

**Key Metrics**:
- **Line Budget**: 1,000-1,200 lines (56% growth for long-term sustainability)
- **File Count**: 6 core files + tests
- **Performance**: Same or better than Phase 1 (0.3s startup, 40MB memory)

---

## Phase 1 Success Validation

### What We Achieved (Week 1)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Code Reduction | 85% | 90% | ✅ EXCEEDED |
| Startup Time | <0.5s | 0.3s | ✅ EXCEEDED |
| Memory Usage | <50MB | 40MB | ✅ EXCEEDED |
| Line Count | 600-800 | 675 | ✅ MET |
| Test Coverage | All pass | 5/5 | ✅ MET |

**Lessons Learned**:
1. ✅ Single-window UI beats wizard pattern for simple workflows
2. ✅ Background threading essential for responsive UI
3. ✅ Reusing core modules prevents duplication
4. ✅ Direct stdlib usage (no abstractions) = 1,100 lines saved
5. ✅ 80/20 principle works: Core scraper (171 lines) + minimal UI (500 lines) = 80% value

### What Needs Improvement (Week 2 Goals)

**Current Limitations**:
- ❌ **Single file growing**: 675 lines approaching readability limit (800-line threshold)
- ❌ **Testing gaps**: Cannot unit test individual UI panels (integration tests only)
- ❌ **Extensibility constraints**: Hard to add features without file bloat
- ❌ **Bug fix scope**: Entire file reloaded on any change (no isolation)

**Phase 2 Solution**: Modular components without sacrificing simplicity

---

## Architecture Design

### Directory Structure

```
youtube_scraper/
├── app.py                      # Entry point (50 lines)
├── scraper.py                  # Core engine adapter (200 lines)
├── ui/
│   ├── __init__.py
│   ├── main_window.py          # Main application (300 lines)
│   ├── search_panel.py         # Search controls (150 lines)
│   └── results_panel.py        # Results display (150 lines)
├── config.py                   # Settings (100 lines)
├── utils.py                    # Helpers (100 lines)
└── tests/
    ├── test_scraper.py         # Unit tests
    ├── test_ui.py              # Component tests
    └── test_integration.py     # E2E tests
```

**Total**: 1,050 lines (50-line buffer for adjustments)

### Module Responsibilities

#### 1. app.py (Entry Point - 50 lines)
```python
"""Application entry point."""
from ui.main_window import MainWindow

def main():
    app = MainWindow()
    app.mainloop()

if __name__ == '__main__':
    main()
```

**Purpose**: Single entry point, no business logic

---

#### 2. scraper.py (Core Adapter - 200 lines)
```python
"""Wrapper around core.scraper_engine with simplified API."""
from core.scraper_engine import TranscriptScraper as CoreScraper

class TranscriptScraper:
    def __init__(self, output_dir: str, callback=None):
        self.engine = CoreScraper(output_dir, callback)

    def search_videos(self, query: str, max_results: int, filters: dict) -> list[dict]:
        """Search YouTube and return video metadata."""
        return self.engine.search_videos(query, max_results, filters)

    def get_transcript(self, video_id: str) -> str:
        """Extract transcript for given video."""
        return self.engine.get_transcript(video_id)
```

**Purpose**: Thin adapter over existing `core/scraper_engine.py`, no duplication

**Why Needed**: Isolates UI from core engine changes, provides testing seam

---

#### 3. ui/main_window.py (Orchestrator - 300 lines)
```python
"""Main application window - coordinates components."""
class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._build_layout()

    def _build_layout(self):
        # Top bar with title + settings
        self._build_top_bar()

        # Search panel
        self.search_panel = SearchPanel(self, on_search=self.on_search)
        self.search_panel.pack(fill='x', padx=15, pady=10)

        # Results panel
        self.results_panel = ResultsPanel(
            self,
            on_selection_change=self._update_selection_count
        )
        self.results_panel.pack(fill='both', expand=True, padx=15, pady=10)

        # Progress + buttons
        self._build_progress_panel()
        self._build_action_buttons()

    def on_search(self, query: str, filters: dict):
        """Handle search request from SearchPanel."""
        threading.Thread(
            target=self._search_thread,
            args=(query, filters),
            daemon=True
        ).start()

    def on_download_selected(self):
        """Handle download request."""
        videos = self.results_panel.get_selected_videos()
        threading.Thread(
            target=self._download_thread,
            args=(videos,),
            daemon=True
        ).start()
```

**Purpose**: Workflow orchestration, event routing, thread management

**Key Methods**:
- `_build_layout()` - Compose UI from panels
- `on_search()` - Handle search events
- `on_download_selected()` - Handle download events
- `update_progress()` - Thread-safe UI updates

---

#### 4. ui/search_panel.py (Input Collection - 150 lines)
```python
"""Search controls panel."""
class SearchPanel(ttk.Frame):
    def __init__(self, parent, on_search_callback):
        super().__init__(parent)
        self.on_search_callback = on_search_callback
        self._build_ui()

    def _build_ui(self):
        # Query row
        query_row = tk.Frame(self)
        query_row.pack(fill='x', pady=5)

        ttk.Label(query_row, text="Search Query:").pack(side='left', padx=(0, 10))

        self.query_entry = ttk.Entry(query_row, font=FONTS['body'])
        self.query_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.query_entry.bind('<Return>', lambda e: self._handle_search())

        self.search_btn = ttk.Button(
            query_row,
            text="Search",
            command=self._handle_search,
            width=12
        )
        self.search_btn.pack(side='right')

        # Filters row (max results, upload date)
        # AI toggle row

    def _handle_search(self):
        query = self.get_query()
        filters = self.get_filters()
        self.on_search_callback(query, filters)

    def get_query(self) -> str:
        return self.query_entry.get().strip()

    def get_filters(self) -> dict:
        return {
            'max_results': int(self.max_results_var.get()),
            'upload_date': UPLOAD_DATE_OPTIONS.get(self.upload_date_var.get())
        }

    def set_loading(self, loading: bool):
        state = 'disabled' if loading else 'normal'
        self.search_btn.config(state=state, text='Searching...' if loading else 'Search')
        self.query_entry.config(state=state)
```

**Purpose**: Collect search inputs, notify parent via callback

**Public Interface**:
- `get_query()` - Returns search query string
- `get_filters()` - Returns filters dict
- `set_loading(bool)` - Update UI state during search

---

#### 5. ui/results_panel.py (Output Display - 150 lines)
```python
"""Results display panel with selection."""
class ResultsPanel(ttk.Frame):
    def __init__(self, parent, on_selection_change_callback):
        super().__init__(parent)
        self.on_selection_change_callback = on_selection_change_callback
        self._build_ui()
        self.result_items = []

    def _build_ui(self):
        # Label frame
        self.frame = tk.LabelFrame(
            self,
            text="Search Results",
            font=FONTS['heading']
        )
        self.frame.pack(fill='both', expand=True)

        # Results count
        self.count_label = ttk.Label(self.frame, text="Results (0):")
        self.count_label.pack(anchor='w', padx=10, pady=5)

        # Scrollable canvas
        canvas = tk.Canvas(self.frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=canvas.yview)

        self.container = tk.Frame(canvas, bg='white')
        self.container.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )

        canvas.create_window((0, 0), window=self.container, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

    def display_results(self, videos: list[dict]):
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

    def get_selected_videos(self) -> list[dict]:
        return [
            item.get_video()
            for item in self.result_items
            if item.is_selected()
        ]

    def clear(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        self.result_items = []
        self.count_label.config(text="Results (0):")
```

**Purpose**: Display results, manage selection, notify on changes

**Public Interface**:
- `display_results(videos: list)` - Render search results
- `get_selected_videos()` - Returns selected videos
- `clear()` - Reset panel

---

#### 6. config.py (Settings - 100 lines)
```python
"""Configuration management."""
from pathlib import Path
import json

class Config:
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

# Settings dialog logic (from app_minimal.py)
def open_settings_dialog(parent, config_manager):
    """Open settings dialog."""
    # Implementation from Phase 1
```

**Purpose**: Configuration persistence + settings UI

---

#### 7. utils.py (Helpers - 100 lines)
```python
"""Shared utilities and constants."""

# Constants
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

# Reusable widget
class VideoResultItem:
    """Checkbox + title + info button for each result."""
    # Implementation from Phase 1

# Helper functions
def update_ui_from_thread(window, func, *args):
    """Thread-safe UI update."""
    window.after(0, func, *args)
```

**Purpose**: Shared constants, reusable widgets, utility functions

---

## Component Communication

### Callback-Based Architecture

```
User Action → Component → Callback → MainWindow → Business Logic
```

**Example Flow (Search)**:
```
1. User types query, clicks Search button
   ↓
2. SearchPanel._handle_search() called
   ↓
3. SearchPanel.on_search_callback(query, filters)
   ↓
4. MainWindow.on_search(query, filters) receives event
   ↓
5. MainWindow spawns background thread
   ↓
6. Thread calls scraper.search_videos()
   ↓
7. Thread updates UI via self.after(0, ...)
   ↓
8. MainWindow.results_panel.display_results(videos)
```

**Benefits**:
- ✅ Loose coupling (components don't know about each other)
- ✅ Easy to test (mock callbacks)
- ✅ Clear data flow (one direction)

---

## Migration Plan

### Step-by-Step Refactoring (Phase 1 → Phase 2)

#### Day 1: Extract Scraper Module
**Goal**: Isolate core logic from UI

1. Create `scraper.py` with `TranscriptScraper` wrapper
2. Import `core.scraper_engine` (existing)
3. Replace direct engine usage in `app_minimal.py`
4. **Validation**: Run tests, verify search still works

**Risk**: Low (no UI changes)

---

#### Day 2: Extract UI Components
**Goal**: Split UI into panels

**Morning (2-3 hours)**:
1. Create `ui/search_panel.py` with `SearchPanel` class
2. Move search UI code from `app_minimal.py`
3. Wire callback: `SearchPanel(parent, on_search=main.on_search)`
4. **Validation**: Search functionality works

**Afternoon (2-3 hours)**:
1. Create `ui/results_panel.py` with `ResultsPanel` class
2. Move results UI code from `app_minimal.py`
3. Wire callback: `ResultsPanel(parent, on_selection_change=main._update_count)`
4. **Validation**: Results display + selection works

**Risk**: Medium (UI refactoring) → Mitigate with incremental testing

---

#### Day 3: Extract Main Window
**Goal**: Orchestration layer

**Morning (2-3 hours)**:
1. Create `ui/main_window.py` with `MainWindow` class
2. Move orchestration logic from `app_minimal.py`
3. Wire `SearchPanel` + `ResultsPanel` together
4. **Validation**: Full workflow (search → select → download)

**Afternoon (1-2 hours)**:
1. Create `app.py` entry point
2. Update `launch_minimal.bat` to use `app.py`
3. **Validation**: Launch works, all features functional

**Risk**: Low (mostly moving code)

---

#### Day 4: Testing & Optimization
**Goal**: Quality assurance

**Morning (2-3 hours)**:
1. Write unit tests (`test_scraper.py`, `test_ui.py`)
2. Update integration tests (`test_integration.py`)
3. Achieve >70% test coverage

**Afternoon (2-3 hours)**:
1. Performance benchmarks (startup, memory)
2. Code review (check line counts, imports)
3. Documentation updates
4. Final validation against quality gates

**Risk**: Low (validation only)

---

### Quality Gates (Day 4 Checklist)

**Must Pass Before Phase 2 Complete**:

- [ ] **Line Count**: 1,000-1,200 total
  - Measured: `wc -l app.py scraper.py ui/*.py config.py utils.py`

- [ ] **Files**: ≤6 core files (excluding tests)
  - app.py, scraper.py, main_window.py, search_panel.py, results_panel.py, config.py, utils.py

- [ ] **All Phase 1 Features Work**:
  - [ ] Search with filters (max results, upload date)
  - [ ] AI optimization toggle (GPT-4)
  - [ ] Download selected videos
  - [ ] Export all functionality
  - [ ] Settings dialog (API key, output dir)
  - [ ] Progress tracking

- [ ] **Performance Same or Better**:
  - [ ] Startup <0.5s (measured with `time python app.py`)
  - [ ] Memory <50MB (measured with Task Manager)
  - [ ] Search <5s for 15 results

- [ ] **Bug Fixes Touch <3 Files**:
  - Test scenario: "Search button stuck disabled"
  - Expected: Fix in `search_panel.py` only (1 file)

- [ ] **Test Coverage >70%**:
  - Run: `pytest --cov=. tests/`
  - Minimum: 70% line coverage

- [ ] **No Circular Imports**:
  - Verify: `python -c "import app"` (should not raise ImportError)

- [ ] **Code Quality**:
  - [ ] No linter errors (if flake8 installed)
  - [ ] All imports resolve
  - [ ] Proper error handling (try/except)

---

## Dependency Management

### Import Hierarchy (No Cycles)

```
app.py
  └─→ ui/main_window.py
        ├─→ ui/search_panel.py
        ├─→ ui/results_panel.py
        ├─→ scraper.py
        │     └─→ core/scraper_engine.py (existing)
        ├─→ config.py
        │     └─→ utils/config.py (existing)
        └─→ utils.py
```

**Rule**: Lower layers never import higher layers

**Validation**: Run `import app` → no circular import errors

---

## Testing Strategy

### Test Levels

#### 1. Unit Tests (Isolated Components)
```python
# test_scraper.py
def test_search_videos():
    scraper = TranscriptScraper(output_dir='test')
    results = scraper.search_videos('Python', max_results=5, filters={})
    assert len(results) <= 5
    assert all('title' in v for v in results)

# test_ui.py
def test_search_panel_get_query():
    root = tk.Tk()
    panel = SearchPanel(root, on_search_callback=lambda q, f: None)
    panel.query_entry.insert(0, 'test query')
    assert panel.get_query() == 'test query'
    root.destroy()
```

#### 2. Integration Tests (Full Workflow)
```python
# test_integration.py
def test_search_and_display():
    app = MainWindow()
    app.search_panel.query_entry.insert(0, 'Python tutorial')
    app.on_search('Python tutorial', {'max_results': 5})
    # Wait for thread
    time.sleep(5)
    results = app.results_panel.get_selected_videos()
    assert len(results) > 0
    app.destroy()
```

**Target**: 70% line coverage

---

## Risk Assessment & Mitigation

### Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Circular imports | Medium | High | Strict hierarchy, validation script |
| Integration bugs at boundaries | Medium | Medium | Comprehensive integration tests |
| Performance regression | Low | Medium | Benchmark before/after |
| Lost simplicity of Phase 1 | Medium | Medium | Keep each file <200 lines |
| Over-engineering creep | Low | High | Enforce "no abstractions" ADR-003 |

### Contingency Plans

**If import errors occur**:
1. Rollback to Phase 1 (`app_minimal.py`)
2. Debug import chain with `python -v app.py`
3. Restructure if needed (move utils to separate package)

**If performance degrades**:
1. Profile with `cProfile`
2. Identify bottleneck (likely import overhead)
3. Lazy imports if needed (`from typing import TYPE_CHECKING`)

**If line count exceeds 1,200**:
1. Identify bloat (likely in `main_window.py`)
2. Extract helpers to `utils.py`
3. Consolidate duplicate code

---

## Success Criteria

### Phase 2 Complete When:

✅ **All deliverables created**:
- [ ] app.py (50 lines)
- [ ] scraper.py (200 lines)
- [ ] ui/main_window.py (300 lines)
- [ ] ui/search_panel.py (150 lines)
- [ ] ui/results_panel.py (150 lines)
- [ ] config.py (100 lines)
- [ ] utils.py (100 lines)

✅ **Quality gates pass**:
- [ ] Line count: 1,000-1,200
- [ ] Performance: Startup <0.5s, memory <50MB
- [ ] Tests: >70% coverage, all passing
- [ ] Features: All Phase 1 functionality preserved

✅ **Documentation complete**:
- [ ] This PHASE2_DESIGN.md
- [ ] MIGRATION_PLAN.md (step-by-step guide)
- [ ] ADR-001, ADR-002, ADR-003 (architecture decisions)

✅ **Validated by backend-developer**:
- [ ] Code review completed
- [ ] Manual testing passed
- [ ] Committed to `refactor/modular-architecture` branch

---

## Next Steps (After Phase 2)

### Phase 3: Selective Feature Additions (Week 3)

**Only add if user requests**:
- Batch operations
- Search history
- Advanced filters
- Export formats (CSV, JSON)

**Constraint**: Each feature <100 lines, total <1,500 lines

### Future Enhancements (Post-MVP)

**Potential (not committed)**:
- Tabs for advanced features
- Side panel for video metadata
- Offline mode with caching

**Rule**: Only build when user asks, not speculatively

---

## References

- **Phase 1**: `src/app_minimal.py` (675 lines, validated)
- **Core Modules**: `core/scraper_engine.py`, `utils/config.py`
- **Tests**: `tests/test_minimal_app.py` (5/5 passing)
- **ADRs**: `docs/architecture/ADR-001-*.md` (3 decisions)
- **Memory Notes**: 2025-10-05 refactoring patterns

---

## Appendix: File Templates

### Template: app.py
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

### Template: scraper.py
```python
"""Core scraper module - adapter over scraper_engine."""
from core.scraper_engine import TranscriptScraper as CoreScraper

class TranscriptScraper:
    """Simplified API for YouTube transcript scraping."""

    def __init__(self, output_dir: str = 'transcripts', callback=None):
        self.engine = CoreScraper(output_dir, callback)

    def search_videos(self, query: str, max_results: int, filters: dict) -> list[dict]:
        """Search YouTube and return video metadata."""
        return self.engine.search_videos(query, max_results, filters)
```

### Template: ui/main_window.py
```python
"""Main application window."""
import tkinter as tk
from ui.search_panel import SearchPanel
from ui.results_panel import ResultsPanel

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._build_layout()

    def _build_layout(self):
        self.search_panel = SearchPanel(self, on_search=self.on_search)
        self.search_panel.pack(...)

        self.results_panel = ResultsPanel(self, on_selection_change=self._update_count)
        self.results_panel.pack(...)
```

---

**Design Complete**: 2025-10-05
**Ready for**: Backend Developer Agent Implementation
**Target Delivery**: Day 3-4 (Phase 2 Week 2)
