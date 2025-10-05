# ADR-002: Modular Component Architecture

**Status**: PROPOSED (for Phase 2)
**Date**: 2025-10-05
**Deciders**: Architecture Team
**Context Owner**: Architecture Specialist

---

## Context

Phase 1 delivered a successful 675-line single-file application (`app_minimal.py`) that validated the 80/20 principle. However, as we plan for Phase 2 enhancements, we need to address maintainability concerns:

**Current State (app_minimal.py)**:
- ✅ Simple to understand (single file)
- ✅ Fast to navigate (no import hunting)
- ✅ Proven stable (all tests pass)
- ⚠️ Growing complexity (675 lines approaching readability limit)
- ⚠️ Limited extensibility (hard to add features without file bloat)
- ⚠️ Testing challenges (can't unit test individual panels)

**Problem Statement**: How do we maintain Phase 1's simplicity while enabling future growth?

---

## Decision

Split `app_minimal.py` into **6 focused modules** with clear responsibilities:

### Module Structure

```
youtube_scraper/
├── app.py                   # Entry point (50 lines)
│   └── main() → launches MainWindow
│
├── scraper.py               # Core engine adapter (200 lines)
│   ├── TranscriptScraper (existing, imported from core/)
│   ├── SearchAPI (wrapper)
│   └── DownloadAPI (wrapper)
│
├── ui/
│   ├── __init__.py
│   │
│   ├── main_window.py       # Main application (300 lines)
│   │   ├── MainWindow(tk.Tk)
│   │   ├── _build_layout()
│   │   ├── Event handlers (on_search, on_download)
│   │   └── State coordination
│   │
│   ├── search_panel.py      # Search controls (150 lines)
│   │   ├── SearchPanel(ttk.Frame)
│   │   ├── get_query() → str
│   │   ├── get_filters() → dict
│   │   └── set_loading(bool)
│   │
│   └── results_panel.py     # Results display (150 lines)
│       ├── ResultsPanel(ttk.Frame)
│       ├── display_results(videos: list)
│       ├── get_selected_videos() → list
│       └── clear()
│
├── config.py                # Settings (100 lines)
│   ├── Config (existing, imported from utils/)
│   └── Settings dialog logic
│
├── utils.py                 # Helpers (100 lines)
│   ├── Colors, Fonts (constants)
│   ├── VideoResultItem (widget)
│   └── Common utilities
│
└── tests/
    ├── test_scraper.py      # Unit tests for scraper.py
    ├── test_ui.py           # Unit tests for UI components
    └── test_integration.py  # End-to-end tests
```

**Total**: ~1,050 lines (56% increase from Phase 1 for maintainability gains)

---

## Rationale

### Why 6 Modules (Not More, Not Less)?

**Psychology of Code Navigation**:
- **1 file**: Simple but monolithic (Phase 1) ✅ for MVP
- **3-6 files**: "Small team" mental model - easy to remember structure
- **7-12 files**: Requires directory structure, mental map
- **13+ files**: Navigation overhead, import complexity

**Our Choice: 6 Files**
- **1 entry point** (app.py) - obvious starting point
- **1 core adapter** (scraper.py) - reuses existing engine
- **3 UI components** (main, search, results) - single responsibility each
- **1 config/utils** - shared resources

**Rule of Thumb**: Each file <200 lines = fits on one screen, easy to understand

### Why Component Boundaries?

**Separation of Concerns**:
```
SearchPanel:
├── Knows: How to collect search inputs
├── Doesn't Know: What happens after search button clicked
└── Interface: on_search_callback(query, filters)

ResultsPanel:
├── Knows: How to display videos, manage selection
├── Doesn't Know: How to download transcripts
└── Interface: on_selection_change_callback()

MainWindow:
├── Knows: Workflow orchestration (search → results → download)
├── Doesn't Know: UI widget implementation details
└── Role: Connect components via callbacks
```

**Benefits**:
1. **Bug Isolation**: Search bug? Only touch `search_panel.py` (1 file, not 5)
2. **Unit Testing**: Test `ResultsPanel.display_results()` without launching full app
3. **Parallel Development**: One dev works on search, another on results
4. **Code Reuse**: `SearchPanel` could be reused in future "advanced search" feature

### Why NOT More Modules?

**Avoided Over-Engineering**:
- ❌ **Separate state manager** (75 lines) → Python dict is sufficient
- ❌ **Separate constants file** (20 lines) → Inline in `utils.py`
- ❌ **Separate validators** (50 lines) → Inline in components
- ❌ **Separate router/controller** (100 lines) → `MainWindow` handles it

**Principle**: Only create a module when it prevents duplication or improves testability

---

## Consequences

### Positive ✅

1. **Maintainability**:
   - Bug fix: Touch 1-2 files (vs. single 675-line file scanning)
   - Each module <200 lines (fits on one screen)
   - Clear responsibility boundaries

2. **Testability**:
   - Unit test `SearchPanel.get_query()` in isolation
   - Mock `on_search_callback` for testing
   - Integration tests validate component connections

3. **Extensibility**:
   - Add new panel: Create `filters_panel.py`, wire to `MainWindow`
   - Swap implementations: Replace `SearchPanel` without touching results
   - Phase 3 features slot in cleanly

4. **Code Quality**:
   - Single Responsibility Principle enforced
   - Low coupling (components communicate via callbacks)
   - High cohesion (related code stays together)

### Negative ❌

1. **Slightly More Files (6 vs 1)**:
   - Navigation overhead (need to know which file has what)
   - Import statements required (vs. single-file simplicity)
   - Mitigation: Clear naming convention, good IDE navigation

2. **Abstraction Layers**:
   - `MainWindow` becomes orchestrator (not just UI)
   - Risk of over-abstracting if taken too far
   - Mitigation: Keep interfaces simple (callbacks only, no complex protocols)

3. **Testing Complexity**:
   - Need both unit tests (components) AND integration tests (full app)
   - Phase 1: Only integration tests needed
   - Mitigation: Worth it for long-term maintainability

### Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Circular imports | High | Strict dependency hierarchy (app → ui → scraper) |
| Fragmented code (too many files) | Medium | Limit to 6 files, no further splitting |
| Lost simplicity of Phase 1 | Medium | Keep each file <200 lines, clear interfaces |
| Integration bugs at boundaries | Low | Comprehensive integration tests, clear contracts |

---

## Alternatives Considered

### Option A: Keep Single File (app_minimal.py) ❌
**Pros**: Simplest, no imports, Phase 1 validated
**Cons**: 675 lines growing → readability degrades, hard to test units
**Rejected**: Not sustainable for Phase 2+ features

### Option B: Full MVC Architecture (10+ files) ❌
**Pros**: Industry standard, highly modular
**Cons**: Overkill for 1,200-line project, import hell, over-engineering
**Rejected**: Violates "simpler is better" principle from Phase 1

### Option C: Two-File Split (UI + Logic) ❌
**Pros**: Minimal files
**Cons**: Each file >300 lines, still monolithic within modules
**Rejected**: Doesn't solve testability problem

### Option D: Six-Module Architecture ✅ (SELECTED)
**Pros**: Balance simplicity vs. modularity, testable, extensible
**Cons**: 6 files to learn (vs. 1)
**Selected**: Sweet spot for maintainability without over-engineering

---

## Component Interfaces

### 1. app.py (Entry Point)
```python
from ui.main_window import MainWindow

def main():
    """Launch the application."""
    app = MainWindow()
    app.mainloop()

if __name__ == '__main__':
    main()
```
**Purpose**: Single entry point, no logic

---

### 2. scraper.py (Core Adapter)
```python
class TranscriptScraper:
    """Wrapper around core.scraper_engine with simplified API."""

    def __init__(self, output_dir: str, callback=None):
        self.engine = CoreTranscriptScraper(output_dir, callback)

    def search_videos(self, query: str, max_results: int, filters: dict) -> list[dict]:
        """Search YouTube and return video metadata."""
        pass

    def get_transcript(self, video_id: str) -> str:
        """Extract transcript for given video."""
        pass

    def scrape(self, query: str, ...) -> dict:
        """Full scrape workflow (search + download)."""
        pass
```
**Purpose**: Thin adapter over existing `core/scraper_engine.py`, no duplication

---

### 3. ui/main_window.py (Orchestrator)
```python
class MainWindow(tk.Tk):
    """Main application window - coordinates components."""

    def __init__(self):
        super().__init__()
        self._setup_window()
        self._build_layout()

    def _build_layout(self):
        # Top bar
        self.search_panel = SearchPanel(self, on_search=self.on_search)
        self.search_panel.pack(...)

        # Results
        self.results_panel = ResultsPanel(self, on_selection_change=self._update_buttons)
        self.results_panel.pack(...)

        # Progress + buttons
        ...

    def on_search(self, query: str, filters: dict):
        """Handle search request from SearchPanel."""
        threading.Thread(target=self._search_thread, args=(query, filters)).start()

    def on_download_selected(self):
        """Handle download request."""
        videos = self.results_panel.get_selected_videos()
        threading.Thread(target=self._download_thread, args=(videos,)).start()

    def update_progress(self, percent: float, message: str):
        """Update progress bar (called from threads)."""
        self.after(0, self._update_progress_ui, percent, message)
```
**Purpose**: Workflow orchestration, event routing, thread management

---

### 4. ui/search_panel.py (Input Collection)
```python
class SearchPanel(ttk.Frame):
    """Search controls panel."""

    def __init__(self, parent, on_search_callback):
        super().__init__(parent)
        self.on_search_callback = on_search_callback
        self._build_ui()

    def _build_ui(self):
        # Query entry
        self.query_entry = ttk.Entry(...)
        # Filters
        self.max_results_combo = ttk.Combobox(...)
        # Search button
        ttk.Button(..., command=self._handle_search).pack()

    def _handle_search(self):
        query = self.query_entry.get()
        filters = self.get_filters()
        self.on_search_callback(query, filters)  # Notify parent

    def get_query(self) -> str:
        return self.query_entry.get()

    def get_filters(self) -> dict:
        return {
            'max_results': int(self.max_results_combo.get()),
            'upload_date': self.upload_date_combo.get()
        }

    def set_loading(self, loading: bool):
        state = 'disabled' if loading else 'normal'
        self.search_btn.config(state=state)
```
**Purpose**: Collect search inputs, notify parent via callback

---

### 5. ui/results_panel.py (Output Display)
```python
class ResultsPanel(ttk.Frame):
    """Results display panel with selection."""

    def __init__(self, parent, on_selection_change_callback):
        super().__init__(parent)
        self.on_selection_change_callback = on_selection_change_callback
        self._build_ui()
        self.result_items = []

    def display_results(self, videos: list[dict]):
        """Display search results."""
        self.clear()
        for idx, video in enumerate(videos):
            item = VideoResultItem(
                self.container,
                video,
                idx,
                self.on_selection_change_callback
            )
            self.result_items.append(item)

    def get_selected_videos(self) -> list[dict]:
        return [item.get_video() for item in self.result_items if item.is_selected()]

    def clear(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        self.result_items = []
```
**Purpose**: Display results, manage selection, notify on changes

---

## Migration Strategy (Phase 1 → Phase 2)

### Step 1: Extract Scraper (No UI Changes)
1. Copy `TranscriptScraper` logic from `app_minimal.py` → `scraper.py`
2. Import and use in `app_minimal.py`
3. Run tests → verify no regression

### Step 2: Extract UI Components
1. Create `ui/search_panel.py` with `SearchPanel` class
2. Replace search UI code in `app_minimal.py` with `SearchPanel` instance
3. Run tests → verify search still works
4. Repeat for `ResultsPanel`

### Step 3: Extract Main Window
1. Create `ui/main_window.py` with `MainWindow` class
2. Move orchestration logic from `app_minimal.py`
3. Wire `SearchPanel` + `ResultsPanel` together

### Step 4: Create Entry Point
1. Create `app.py` with `main()` function
2. Import `MainWindow` and launch
3. Update `launch_minimal.bat` to use `app.py`

### Step 5: Testing & Validation
1. Run all automated tests
2. Manual testing (search, download, settings)
3. Performance benchmarks (startup, memory)

**Constraint**: Each step must pass tests before proceeding

---

## Quality Gates

### Must Pass Before Phase 2 Complete

- [ ] **Line Count**: 1,000-1,200 total (target: 1,050)
- [ ] **Files**: ≤6 (excluding tests)
- [ ] **All Phase 1 Features Work**: Search, download, settings, AI optimization
- [ ] **Performance Same or Better**: Startup <0.5s, memory <50MB
- [ ] **Bug Fixes Touch <3 Files**: Validate with 5 hypothetical scenarios
- [ ] **Test Coverage >70%**: Unit tests + integration tests
- [ ] **No Circular Imports**: Verify with import graph tool

### Code Quality Standards

```python
# Each file max lines
app.py:          50 lines   (entry point only)
scraper.py:      200 lines  (core adapter)
main_window.py:  300 lines  (orchestration)
search_panel.py: 150 lines  (input UI)
results_panel.py:150 lines  (output UI)
config.py:       100 lines  (settings)
utils.py:        100 lines  (helpers)
─────────────────────────────
Total:         1,050 lines
```

---

## Future Evolution (Phase 3+)

### When to Add More Modules?

**Only if**:
1. File exceeds 200 lines AND has clear split points
2. Code duplication exists across 3+ places
3. Testing requires mocking complex internal logic

**Example Triggers**:
- Add `filters_panel.py` if filters grow to 100+ lines
- Add `history_manager.py` if we add search history feature (not before)
- Add `export_formats.py` if we support 5+ export formats

**Rule**: Resist premature splitting. 6 files is enough for 1,200-line project.

---

## References

- Phase 1 Implementation: `src/app_minimal.py` (675 lines)
- Core Modules (Reused): `core/scraper_engine.py`, `utils/config.py`
- Testing Strategy: `tests/test_minimal_app.py`
- Memory Notes: 2025-10-05 refactoring patterns

---

## Decision Log

| Date | Change | Reason |
|------|--------|--------|
| 2025-10-05 | Proposed 6-module architecture | Balance simplicity vs. maintainability |
| TBD | Review after Phase 2 implementation | Assess if further splitting needed |

---

## Tags
#architecture #modularity #components #phase2 #maintainability #testing #separation-of-concerns
