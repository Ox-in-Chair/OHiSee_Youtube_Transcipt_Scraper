"""YouTube Research Platform - Integrated Application

World-class research platform with 25 integrated components.
Transformation from basic scraper to professional research tool.
"""

import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from design_system import COLORS, FONTS, grid, SPACING
from state_manager import ApplicationState

# Import all components
from components import (
    # Base primitives
    BaseSeparator,
    ModernScrollFrame,
    # Phase 1
    TopBar,
    WizardRail,
    LivePreview,
    OnboardingBanner,
    TemplateGrid,
    # Phase 2
    PromptComposer,
    AITransparencyPanel,
    QueryTransformationView,
    CredentialsManager,
    # Phase 3
    FacetsBar,
    ResultsSlider,
    ReviewSheet,
    ActivityLog,
    ResultCardGrid,
    # Phase 4
    KeyboardNavigationManager,
    ToastManager,
    AccessibilityHelper,
    NoConfigState,
    LoadingState,
    NetworkError,
    # Phase 5
    OfflineCache,
    LearningLoop,
    SmartSuggestions,
    CitationGenerator,
    ExportFormats,
    ExportPanel,
)

# Import core functionality
from core import TranscriptScraper, optimize_search_query
from utils import Config


class YouTubeResearchPlatform(tk.Tk):
    """Main integrated application window."""

    def __init__(self):
        super().__init__()

        # Initialize state management
        self.app_state = ApplicationState()
        self.offline_cache = OfflineCache()
        self.learning_loop = LearningLoop()

        # Initialize UI managers
        self.toast_manager = None
        self.keyboard_nav = None

        # Component references
        self.top_bar = None
        self.wizard_rail = None
        self.live_preview = None
        self.content_area = None

        # Setup window
        self._setup_window()
        self._build_ui()
        self._setup_accessibility()
        self._bind_state_observers()

        # Check for first run
        self._check_first_run()

    def _setup_window(self):
        """Configure main window with modern color scheme."""
        self.title("YouTube Research Platform")
        self.geometry("1400x900")
        self.minsize(1200, 700)
        self.configure(bg=COLORS["surface"])  # alice_blue background

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.winfo_screenheight() // 2) - (900 // 2)
        self.geometry(f"1400x900+{x}+{y}")

    def _build_ui(self):
        """Build main UI with research-grade layout: top bar | 72px rail | 60% content | collapsible drawer."""
        # Top Bar (persistent navigation anchor)
        self.top_bar = TopBar(
            self,
            on_new_research=self._new_research,
            on_help=self._show_help
        )
        self.top_bar.pack(side="top", fill="x")

        # Main container with grid geometry
        main_container = tk.Frame(self, bg=COLORS["background"])  # Soft white background
        main_container.pack(fill="both", expand=True)

        # Configure grid weights: 72px rail | 60% content | 40% preview
        main_container.grid_columnconfigure(0, weight=0, minsize=72)  # Wizard rail (fixed 72px)
        main_container.grid_columnconfigure(1, weight=6)  # Content area (60%, weight=6)
        main_container.grid_columnconfigure(2, weight=4, minsize=350)  # Preview drawer (40%, collapsible)
        main_container.grid_rowconfigure(0, weight=1)

        # Left: Wizard Rail (72px fixed width, refined icons)
        self.wizard_rail = WizardRail(main_container, on_step_change=self._handle_step_change)
        self.wizard_rail.grid(row=0, column=0, sticky="nsew")

        # Center: Content Area (60% width, white surface with generous whitespace)
        self.content_area = tk.Frame(main_container, bg=COLORS["surface"])  # Pure white surface
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=SPACING["lg"], pady=SPACING["lg"])

        # Right: Live Preview Drawer (collapsible, layered with shadow)
        preview_container = tk.Frame(main_container, bg=COLORS["background"])
        preview_container.grid(row=0, column=2, sticky="nsew")

        self.live_preview = LivePreview(preview_container)
        self.live_preview.pack(fill="both", expand=True, padx=(0, SPACING["md"]), pady=SPACING["md"])

        # Render initial step
        self._render_step(0)

    def _setup_accessibility(self):
        """Setup accessibility features."""
        # Keyboard navigation
        self.keyboard_nav = KeyboardNavigationManager(self)

        # Toast notifications
        self.toast_manager = ToastManager(self)

        # Global keyboard shortcuts
        self.bind("<Control-n>", lambda e: self._new_research())
        self.bind("<Control-s>", lambda e: self._save_config())
        self.bind("<Control-r>", lambda e: self._run_scraper())
        self.bind("<F1>", lambda e: self._show_help())
        self.bind("<Escape>", lambda e: self._cancel_operation())

    def _bind_state_observers(self):
        """Bind state change observers."""
        self.app_state.state.subscribe(self._handle_state_change)

    def _handle_state_change(self, key: str, value):
        """Handle state changes."""
        if key == "current_step":
            self.wizard_rail.set_step(value)
            self.top_bar.update_step(value)  # Update top bar progress tracker
            self._render_step(value)
        elif key == "prompt_config" or key == "filters":
            self._update_preview()
        elif key == "is_running":
            self._update_run_state(value)
        elif key == "ai_enabled":
            self.top_bar.update_status("ai_enabled", value)
        elif key == "api_connected":
            self.top_bar.update_status("api_connected", value)

    def _handle_step_change(self, step: int):
        """Handle wizard step change."""
        if self.app_state.can_advance() or step < self.app_state.state.get("current_step"):
            self.app_state.go_to_step(step)
        else:
            self.toast_manager.warning("Please complete current step first")

    def _render_step(self, step: int):
        """Render content for current step."""
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()

        if step == 0:
            self._render_define_step()
        elif step == 1:
            self._render_refine_step()
        elif step == 2:
            self._render_review_step()
        elif step == 3:
            self._render_run_step()
        elif step == 4:
            self._render_export_step()

    # ==================== STEP 1: DEFINE ====================

    def _render_define_step(self):
        """Render Define Research step."""
        # Create scrollable container
        scroll_container = ModernScrollFrame(self.content_area, bg="white")
        scroll_container.pack(fill="both", expand=True, padx=SPACING["lg"], pady=SPACING["lg"])

        # Use scrollable_frame for content
        container = scroll_container.scrollable_frame

        # Header
        tk.Label(
            container, text="Define Your Research", font=FONTS["h1"], bg="white", fg=COLORS["text"]
        ).pack(anchor="w", pady=(0, SPACING["md"]))

        # Separator after header
        BaseSeparator(container)

        # Template Grid
        template_grid = TemplateGrid(container, on_template_preview=self._handle_template_select)
        template_grid.pack(fill="both", expand=True, pady=SPACING["md"])

        # Separator between sections
        BaseSeparator(container)

        # Prompt Composer
        self.prompt_composer = PromptComposer(container, on_update=self._handle_prompt_change)
        self.prompt_composer.pack(fill="x", pady=SPACING["md"])

        # Next button
        btn_frame = tk.Frame(container, bg="white")
        btn_frame.pack(anchor="e", pady=SPACING["md"])

        tk.Button(
            btn_frame,
            text="Next: Refine Filters →",
            font=FONTS["h3"],
            bg=COLORS["primary"],
            fg="white",
            padx=SPACING["lg"],
            pady=SPACING["sm"],
            relief="flat",
            cursor="hand2",
            command=lambda: self.app_state.advance_step(),
        ).pack()

    def _handle_template_select(self, template_name: str, template_config: dict):
        """Handle template selection."""
        self.app_state.state.set("template", template_name)
        self.app_state.state.update(
            {
                "prompt_config": template_config.get("prompt", {}),
                "filters": template_config.get("filters", {}),
            }
        )
        self.toast_manager.success(f"Template '{template_name}' applied")

    def _handle_prompt_change(self, prompt_config: dict):
        """Handle prompt composer changes."""
        self.app_state.state.set("prompt_config", prompt_config)

    # ==================== STEP 2: REFINE ====================

    def _render_refine_step(self):
        """Render Refine Filters step."""
        # Create scrollable container
        scroll_container = ModernScrollFrame(self.content_area, bg="white")
        scroll_container.pack(fill="both", expand=True, padx=SPACING["lg"], pady=SPACING["lg"])

        # Use scrollable_frame for content
        container = scroll_container.scrollable_frame

        # Header
        tk.Label(
            container, text="Refine Your Filters", font=FONTS["h1"], bg="white", fg=COLORS["text"]
        ).pack(anchor="w", pady=(0, SPACING["md"]))

        # Separator after header
        BaseSeparator(container)

        # Facets Bar (active filters)
        facets_bar = FacetsBar(
            container,
            active_facets=self.app_state.state.get("filters"),
            on_change=self._handle_filters_change,
        )
        facets_bar.pack(fill="x", pady=SPACING["md"])

        # Separator between sections
        BaseSeparator(container)

        # Results Slider
        results_slider = ResultsSlider(container, on_change=self._handle_results_change)
        results_slider.pack(fill="x", pady=SPACING["md"])

        # Separator between sections
        BaseSeparator(container)

        # AI Optimization Toggle
        ai_frame = tk.Frame(container, bg="white")
        ai_frame.pack(fill="x", pady=SPACING["md"])

        self.ai_var = tk.BooleanVar(value=self.app_state.state.get("use_ai_optimization"))
        tk.Checkbutton(
            ai_frame,
            text="Use AI Query Optimization (GPT-4)",
            variable=self.ai_var,
            font=FONTS["body"],
            bg="white",
            command=self._toggle_ai,
        ).pack(anchor="w")

        # Credentials Manager Button
        tk.Button(
            container,
            text="⚙️ Manage API Credentials",
            font=FONTS["body"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
            relief="flat",
            cursor="hand2",
            command=self._show_credentials,
        ).pack(anchor="w", pady=SPACING["sm"])

        # Navigation
        nav_frame = tk.Frame(container, bg="white")
        nav_frame.pack(anchor="e", pady=SPACING["lg"])

        tk.Button(
            nav_frame,
            text="← Back",
            font=FONTS["body"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
            padx=SPACING["md"],
            pady=SPACING["xs"],
            relief="flat",
            cursor="hand2",
            command=lambda: self.app_state.go_to_step(0),
        ).pack(side="left", padx=SPACING["xs"])

        tk.Button(
            nav_frame,
            text="Next: Review →",
            font=FONTS["h3"],
            bg=COLORS["primary"],
            fg="white",
            padx=SPACING["lg"],
            pady=SPACING["sm"],
            relief="flat",
            cursor="hand2",
            command=lambda: self.app_state.advance_step(),
        ).pack(side="left")

    def _handle_filters_change(self, filters: dict):
        """Handle filter changes."""
        current = self.app_state.state.get("filters")
        current.update(filters)
        self.app_state.state.set("filters", current)

    def _handle_results_change(self, max_results: int):
        """Handle results slider change."""
        filters = self.app_state.state.get("filters")
        filters["max_results"] = max_results
        self.app_state.state.set("filters", filters)

    def _toggle_ai(self):
        """Toggle AI optimization."""
        self.app_state.state.set("use_ai_optimization", self.ai_var.get())

    def _show_credentials(self):
        """Show credentials manager dialog."""
        CredentialsManager(self, on_save=self._save_credentials)

    def _save_credentials(self, api_key: str):
        """Save API credentials."""
        self.app_state.state.set("api_key", api_key)
        Config().save_api_key(api_key)
        self.toast_manager.success("API key saved successfully")

    # ==================== STEP 3: REVIEW ====================

    def _render_review_step(self):
        """Render Review Configuration step."""
        # Create scrollable container
        scroll_container = ModernScrollFrame(self.content_area, bg="white")
        scroll_container.pack(fill="both", expand=True, padx=SPACING["lg"], pady=SPACING["lg"])

        # Use scrollable_frame for content
        container = scroll_container.scrollable_frame

        # Header
        tk.Label(
            container,
            text="Review Your Configuration",
            font=FONTS["h1"],
            bg="white",
            fg=COLORS["text"],
        ).pack(anchor="w", pady=(0, SPACING["md"]))

        # Separator after header
        BaseSeparator(container)

        # Review Sheet
        review_sheet = ReviewSheet(container, config=self.app_state.export_current_config())
        review_sheet.pack(fill="both", expand=True, pady=SPACING["md"])

        # Smart Suggestions (temporarily disabled - will integrate later)
        # TODO: Integrate SuggestionPanel properly
        pass

        # Navigation
        nav_frame = tk.Frame(container, bg="white")
        nav_frame.pack(anchor="e", pady=SPACING["lg"])

        tk.Button(
            nav_frame,
            text="← Back",
            font=FONTS["body"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
            padx=SPACING["md"],
            pady=SPACING["xs"],
            relief="flat",
            cursor="hand2",
            command=lambda: self.app_state.go_to_step(1),
        ).pack(side="left", padx=SPACING["xs"])

        tk.Button(
            nav_frame,
            text="Start Research →",
            font=FONTS["h3"],
            bg=COLORS["success"],
            fg="white",
            padx=SPACING["lg"],
            pady=SPACING["sm"],
            relief="flat",
            cursor="hand2",
            command=lambda: self.app_state.advance_step(),
        ).pack(side="left")

    # ==================== STEP 4: RUN ====================

    def _render_run_step(self):
        """Render Run Scraping step."""
        # Create scrollable container
        scroll_container = ModernScrollFrame(self.content_area, bg="white")
        scroll_container.pack(fill="both", expand=True, padx=SPACING["lg"], pady=SPACING["lg"])

        # Use scrollable_frame for content
        container = scroll_container.scrollable_frame

        # Header
        tk.Label(
            container, text="Scraping In Progress", font=FONTS["h1"], bg="white", fg=COLORS["text"]
        ).pack(anchor="w", pady=(0, SPACING["md"]))

        # Separator after header
        BaseSeparator(container)

        # Activity Log
        self.activity_log = ActivityLog(container)
        self.activity_log.pack(fill="both", expand=True, pady=SPACING["md"])

        # Start scraping automatically
        if not self.app_state.state.get("is_running"):
            self.after(500, self._run_scraper)

    def _run_scraper(self):
        """Execute the scraping operation."""
        self.app_state.state.set("is_running", True)
        self.activity_log.log("Starting research...", "info")

        try:
            # Get configuration
            config = self.app_state.export_current_config()
            query = config.get("prompt_config", {}).get("topic", "")
            filters = config.get("filters", {})

            # Optimize query if AI enabled
            if config.get("use_ai_optimization") and self.app_state.state.get("api_key"):
                self.activity_log.log("Optimizing query with GPT-4...", "info")
                query = optimize_search_query(query, api_key=self.app_state.state.get("api_key"))
                self.activity_log.log(f"Optimized query: {query}", "success")

            # Initialize scraper
            scraper = TranscriptScraper(
                output_dir="./transcripts", callback=lambda msg: self.activity_log.log(msg, "info")
            )

            # Execute scraping
            self.activity_log.log(f"Searching YouTube for: {query}", "info")
            result = scraper.scrape(
                query=query, max_results=filters.get("max_results", 15), filters=filters
            )

            # Store results
            self.app_state.state.set("transcripts", result.get("files", []))
            self.activity_log.log(
                f"✅ Complete! Saved {result.get('saved', 0)} transcripts", "success"
            )

            # Advance to export
            self.app_state.state.set("is_running", False)
            self.toast_manager.success(
                f"Research complete! {result.get('saved', 0)} transcripts saved"
            )
            self.app_state.advance_step()

        except Exception as e:
            self.activity_log.log(f"❌ Error: {str(e)}", "error")
            self.app_state.state.set("is_running", False)
            self.toast_manager.error(f"Scraping failed: {str(e)}")

    # ==================== STEP 5: EXPORT ====================

    def _render_export_step(self):
        """Render Export Results step."""
        # Create scrollable container
        scroll_container = ModernScrollFrame(self.content_area, bg="white")
        scroll_container.pack(fill="both", expand=True, padx=SPACING["lg"], pady=SPACING["lg"])

        # Use scrollable_frame for content
        container = scroll_container.scrollable_frame

        # Header
        tk.Label(
            container, text="Export Your Results", font=FONTS["h1"], bg="white", fg=COLORS["text"]
        ).pack(anchor="w", pady=(0, SPACING["md"]))

        # Separator after header
        BaseSeparator(container)

        # Results summary
        transcripts = self.app_state.state.get("transcripts", [])
        tk.Label(
            container,
            text=f"{len(transcripts)} transcripts ready for export",
            font=FONTS["h2"],
            bg="white",
            fg=COLORS["text_secondary"],
        ).pack(anchor="w", pady=SPACING["sm"])

        # Separator between sections
        BaseSeparator(container)

        # Export panel
        export_panel = ExportPanel(
            container, get_transcripts=lambda: self.app_state.state.get("transcripts", [])
        )
        export_panel.pack(fill="both", expand=True, pady=SPACING["md"])

        # New Research button
        tk.Button(
            container,
            text="Start New Research",
            font=FONTS["h3"],
            bg=COLORS["primary"],
            fg="white",
            padx=SPACING["lg"],
            pady=SPACING["sm"],
            relief="flat",
            cursor="hand2",
            command=self._new_research,
        ).pack(pady=SPACING["lg"])

    # ==================== HELPER METHODS ====================

    def _update_preview(self):
        """Update live preview with current config."""
        config = self.app_state.export_current_config()
        self.live_preview.update_preview(config)

    def _update_run_state(self, is_running: bool):
        """Update UI based on running state."""
        if is_running:
            self.config(cursor="watch")
        else:
            self.config(cursor="")

    def _export_config(self):
        """Export current configuration."""
        config = self.app_state.export_current_config()
        # Trigger export dialog
        self.toast_manager.info("Config export not yet implemented")

    def _copy_config(self):
        """Copy configuration to clipboard."""
        import json

        config = self.app_state.export_current_config()
        self.clipboard_clear()
        self.clipboard_append(json.dumps(config, indent=2))
        self.toast_manager.success("Configuration copied to clipboard")

    def _save_config(self):
        """Save current configuration."""
        self.app_state.save_session()
        self.toast_manager.success("Configuration saved")

    def _new_research(self):
        """Start new research (reset state) - shows confirmation toast."""
        # For now, just show warning toast and proceed
        # Could create custom confirmation dialog later
        self.toast_manager.warning("Starting new research - current progress will be reset")
        self.app_state.state.reset()
        self.app_state.go_to_step(0)
        self.toast_manager.info("New research started")

    def _cancel_operation(self):
        """Cancel current operation."""
        if self.app_state.state.get("is_running"):
            self.app_state.state.set("is_running", False)
            self.toast_manager.warning("Operation cancelled")

    def _show_help(self):
        """Show help dialog - displays keyboard shortcuts."""
        shortcuts = self.keyboard_nav.get_shortcuts_help()
        # Create simple help overlay instead of messagebox
        help_window = tk.Toplevel(self)
        help_window.title("Keyboard Shortcuts")
        help_window.geometry("500x400")
        help_window.configure(bg=COLORS["surface"])

        # Title
        tk.Label(
            help_window,
            text="⌨️ Keyboard Shortcuts",
            font=FONTS["h1"],
            bg=COLORS["surface"],
            fg=COLORS["text"]
        ).pack(pady=SPACING["md"])

        # Shortcuts text
        text_widget = tk.Text(
            help_window,
            font=FONTS["body"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
            relief="flat",
            wrap="word"
        )
        text_widget.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])
        text_widget.insert("1.0", shortcuts)
        text_widget.config(state="disabled")

        # Close button
        tk.Button(
            help_window,
            text="Close",
            font=FONTS["body"],
            bg=COLORS["primary"],
            fg="white",
            relief="flat",
            padx=SPACING["lg"],
            pady=SPACING["xs"],
            command=help_window.destroy
        ).pack(pady=SPACING["md"])

    def _check_first_run(self):
        """Check if this is first run and show onboarding."""
        config = self.app_state.config_manager.load_config("first_run_complete")
        if not config:
            OnboardingBanner(self, on_try_sample=self._complete_onboarding)

    def _complete_onboarding(self):
        """Complete onboarding wizard."""
        self.app_state.config_manager.save_config({"completed": True}, "first_run_complete")
        self.toast_manager.success("Welcome to YouTube Research Platform!")


def main():
    """Application entry point."""
    app = YouTubeResearchPlatform()
    app.mainloop()


if __name__ == "__main__":
    main()
