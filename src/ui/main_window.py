"""Main Application Window

Orchestrates the complete YouTube Transcript Scraper application.
Integrates SearchPanel, ResultsPanel, and coordinates background
operations (search, download).

Target: ~300 lines
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import traceback
from typing import List, Dict

from ui.search_panel import SearchPanel
from ui.results_panel import ResultsPanel
from scraper import TranscriptScraper
from config import Config, open_settings_dialog
from core.search_optimizer import optimize_search_query
from shared import COLORS, FONTS


class MainWindow(tk.Tk):
    """Main application orchestrator.

    Coordinates:
    - Search panel (query input, filters)
    - Results panel (video list, selection)
    - Progress tracking (progress bar, status)
    - Background threads (search, download)
    - Settings dialog (API key, output dir)

    Attributes:
        config_manager: Config instance for settings
        scraper: TranscriptScraper instance
        search_panel: SearchPanel component
        results_panel: ResultsPanel component
        is_searching: Flag to prevent concurrent searches
        is_downloading: Flag to prevent concurrent downloads
    """

    def __init__(self):
        """Initialize main window and components."""
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
        """Configure main window properties."""
        self.title("YouTube Transcript Scraper")
        self.geometry("800x700")
        self.configure(bg=COLORS['bg'])
        self.resizable(True, True)

        # Configure ttk style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', padding=6)
        style.configure('TCheckbutton', font=FONTS['body'])
        style.configure('TLabel', font=FONTS['body'])

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
        """Build top bar with title and settings button."""
        top_frame = tk.Frame(self, bg=COLORS['primary'], height=50)
        top_frame.pack(fill='x')
        top_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(
            top_frame,
            text="YouTube Transcript Scraper",
            font=FONTS['title'],
            bg=COLORS['primary'],
            fg='white'
        )
        title_label.pack(side='left', padx=15, pady=10)

        # Settings button
        self.settings_btn = ttk.Button(
            top_frame,
            text="⚙ Settings",
            command=self._open_settings
        )
        self.settings_btn.pack(side='right', padx=15, pady=10)

    def _build_progress_panel(self):
        """Build progress tracking panel."""
        progress_frame = tk.Frame(self, bg=COLORS['bg'])
        progress_frame.pack(fill='x', padx=15, pady=5)

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill='x', pady=2)

        # Status label
        self.status_label = ttk.Label(
            progress_frame,
            text="Ready",
            font=FONTS['small'],
            foreground=COLORS['secondary']
        )
        self.status_label.pack(anchor='w')

    def _build_action_buttons(self):
        """Build action buttons panel."""
        button_frame = tk.Frame(self, bg=COLORS['bg'])
        button_frame.pack(fill='x', padx=15, pady=10)

        self.download_btn = ttk.Button(
            button_frame,
            text="Download Selected",
            command=self._on_download_selected,
            state='disabled'
        )
        self.download_btn.pack(side='left', padx=5)

        self.export_btn = ttk.Button(
            button_frame,
            text="Export All (.md)",
            command=self._on_export_all,
            state='disabled'
        )
        self.export_btn.pack(side='left', padx=5)

        # Selection count label
        self.selection_label = ttk.Label(
            button_frame,
            text="0 selected",
            font=FONTS['small']
        )
        self.selection_label.pack(side='left', padx=20)

    def _open_settings(self):
        """Open settings dialog."""
        open_settings_dialog(self, self.config_manager)

    def on_search(self, query: str, filters: Dict):
        """Handle search request from SearchPanel.

        Args:
            query: Search query string
            filters: Dict with max_results, upload_date, use_ai keys
        """
        if not query:
            messagebox.showwarning("Input Required", "Please enter a search query")
            return

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

    def _search_thread(self, query: str, filters: Dict):
        """Background search thread.

        Args:
            query: Search query string
            filters: Search filters dict
        """
        try:
            # AI optimization if enabled
            final_query = query
            if filters.get('use_ai', False):
                self.after(0, self._update_status, "Optimizing query with GPT-4...")
                api_key = self.config_manager.load_api_key()

                if not api_key:
                    self.after(0, messagebox.showwarning, "API Key Required",
                              "Please set your OpenAI API key in Settings to use AI optimization.")
                    return

                try:
                    final_query = optimize_search_query(query, api_key)
                    self.after(0, self._log_message,
                              f"Optimized: '{query}' → '{final_query}'")
                except Exception as e:
                    self.after(0, self._log_message,
                              f"Optimization failed: {e}")
                    final_query = query

            # Search via TranscriptScraper
            self.after(0, self._update_status, "Searching videos...")

            self.scraper = TranscriptScraper(
                callback=lambda msg: self.after(0, self._log_message, msg)
            )

            # Build search filters
            search_filters = {
                'upload_date': filters.get('upload_date', 'any'),
                'sort_by': 'relevance'
            }

            max_results = filters.get('max_results', 15)

            results = self.scraper.search_videos(
                final_query,
                max_results=max_results,
                filters=search_filters
            )

            # Update UI on main thread
            self.after(0, self._display_results, results)

        except Exception as e:
            error_msg = f"Search failed: {str(e)}\n{traceback.format_exc()}"
            self.after(0, messagebox.showerror, "Search Error", error_msg)
            self.after(0, self._update_status, "Search failed")
        finally:
            self.after(0, self._restore_search_ui)

    def _restore_search_ui(self):
        """Restore search UI after search completes."""
        self.is_searching = False
        self.search_panel.set_loading(False)

    def _display_results(self, results: List[Dict]):
        """Display search results.

        Args:
            results: List of video dicts
        """
        self.results_panel.display_results(results)

        if results:
            # Enable download buttons
            self.download_btn.config(state='normal')
            self.export_btn.config(state='normal')
            self._update_status(f"Found {len(results)} videos")
        else:
            self._update_status("No videos found")

    def _update_selection_count(self):
        """Update selection count label."""
        selected_count = len(self.results_panel.get_selected_videos())
        self.selection_label.config(text=f"{selected_count} selected")

    def _on_download_selected(self):
        """Download transcripts for selected videos."""
        selected_videos = self.results_panel.get_selected_videos()

        if not selected_videos:
            messagebox.showwarning("No Selection",
                                  "Please select at least one video to download")
            return

        if self.is_downloading:
            return

        # Disable buttons
        self.is_downloading = True
        self.download_btn.config(state='disabled')
        self.export_btn.config(state='disabled')
        self.search_panel.set_loading(True)

        # Run download in background
        threading.Thread(
            target=self._download_thread,
            args=(selected_videos,),
            daemon=True
        ).start()

    def _download_thread(self, videos: List[Dict]):
        """Background download thread with progress updates.

        Args:
            videos: List of video dicts to download
        """
        total = len(videos)
        saved = 0
        skipped = 0

        # Get output directory
        config = self.config_manager.load_config()
        output_dir = config.get('output_dir', 'transcripts')

        # Setup browser
        self.after(0, self._update_status, "Setting up browser...")
        try:
            self.scraper.setup_browser()
        except Exception as e:
            self.after(0, messagebox.showerror, "Browser Error",
                      f"Failed to setup browser: {e}\n\nMake sure Chrome is installed.")
            self.after(0, self._restore_download_ui)
            return

        try:
            for idx, video in enumerate(videos):
                # Update progress
                progress = (idx / total) * 100
                title_short = video['title'][:40]
                self.after(0, self._update_progress, progress,
                          f"Downloading {idx+1}/{total}: {title_short}...")

                try:
                    # Extract transcript
                    transcript = self.scraper.get_transcript(video['id'])

                    if transcript:
                        # Save to file
                        self.scraper.output_dir = output_dir
                        filename = self.scraper.save_transcript(video, transcript)
                        self.after(0, self._log_message, f"✓ Saved: {filename}")
                        saved += 1
                    else:
                        self.after(0, self._log_message,
                                  f"⊘ Skipped: {title_short} (no transcript)")
                        skipped += 1

                except Exception as e:
                    self.after(0, self._log_message,
                              f"⊗ Error: {title_short} - {str(e)}")
                    skipped += 1

            # Complete
            self.after(0, self._update_progress, 100, "Download complete!")
            self.after(0, messagebox.showinfo, "Download Complete",
                      f"Saved {saved} transcripts\nSkipped {skipped} videos\n\nFiles saved to: {output_dir}")

        finally:
            # Cleanup browser
            if self.scraper and self.scraper.driver:
                self.scraper.driver.quit()

            self.after(0, self._restore_download_ui)

    def _restore_download_ui(self):
        """Restore UI after download completes."""
        self.is_downloading = False
        self.download_btn.config(state='normal')
        self.export_btn.config(state='normal')
        self.search_panel.set_loading(False)
        self._update_progress(0, "Ready")

    def _on_export_all(self):
        """Export all search results to markdown files."""
        all_videos = self.results_panel.get_selected_videos()

        if not all_videos:
            messagebox.showwarning("No Results", "No search results to export")
            return

        if messagebox.askyesno("Export All",
                               f"This will download {len(all_videos)} transcripts. Continue?"):
            self._on_download_selected()

    def _update_progress(self, value: float, status: str):
        """Update progress bar and status.

        Args:
            value: Progress percentage (0-100)
            status: Status message string
        """
        self.progress_var.set(value)
        self.status_label.config(text=status)

    def _update_status(self, message: str):
        """Update status label.

        Args:
            message: Status message string
        """
        self.status_label.config(text=message)

    def _log_message(self, message: str):
        """Log a message to console.

        Args:
            message: Message to log
        """
        print(f"[LOG] {message}")
