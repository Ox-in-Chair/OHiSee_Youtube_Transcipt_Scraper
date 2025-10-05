#!/usr/bin/env python3
"""YouTube Transcript Scraper - Minimal Application
Single-file implementation delivering 80/20 value.
Target: 600-800 lines total.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from typing import Dict
import traceback

# Import existing core functionality
from core.scraper_engine import TranscriptScraper
from core.search_optimizer import optimize_search_query
from utils.config import Config
from utils.filters import UPLOAD_DATE_OPTIONS

# Constants
COLORS = {
    "bg": "#FFFFFF",
    "primary": "#1E40AF",
    "success": "#10B981",
    "text": "#0F172A",
    "border": "#E2E8F0",
    "secondary": "#6B7280",
    "hover": "#3B82F6",
}

FONTS = {
    "title": ("Segoe UI", 16, "bold"),
    "heading": ("Segoe UI", 12, "bold"),
    "body": ("Segoe UI", 10),
    "small": ("Segoe UI", 9),
}


class VideoResultItem:
    """Represents a single video result with checkbox."""

    def __init__(self, parent, video: Dict, index: int, callback):
        self.video = video
        self.callback = callback

        # Container frame
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="x", padx=5, pady=2)

        # Selection variable
        self.selected = tk.BooleanVar(value=True)  # Default: selected

        # Checkbox with title
        title_text = f"{index}. {video['title'][:60]}{'...' if len(video['title']) > 60 else ''}"
        self.checkbox = ttk.Checkbutton(
            self.frame, text=title_text, variable=self.selected, command=self._on_toggle
        )
        self.checkbox.pack(side="left", fill="x", expand=True)

        # Info button
        self.info_btn = ttk.Button(self.frame, text="Info", width=8, command=self._show_info)
        self.info_btn.pack(side="right", padx=2)

    def _on_toggle(self):
        """Notify parent when selection changes."""
        self.callback()

    def _show_info(self):
        """Show video information dialog."""
        info_win = tk.Toplevel()
        info_win.title("Video Information")
        info_win.geometry("500x200")
        info_win.transient(info_win.master)

        # Title
        ttk.Label(info_win, text="Title:", font=FONTS["heading"]).pack(
            anchor="w", padx=10, pady=(10, 0)
        )
        ttk.Label(info_win, text=self.video["title"], wraplength=480).pack(anchor="w", padx=20)

        # Channel
        ttk.Label(info_win, text="Channel:", font=FONTS["heading"]).pack(
            anchor="w", padx=10, pady=(10, 0)
        )
        ttk.Label(info_win, text=self.video["channel"]).pack(anchor="w", padx=20)

        # URL
        ttk.Label(info_win, text="URL:", font=FONTS["heading"]).pack(
            anchor="w", padx=10, pady=(10, 0)
        )
        url_text = tk.Text(info_win, height=2, wrap="word")
        url_text.insert("1.0", self.video["url"])
        url_text.config(state="disabled")
        url_text.pack(anchor="w", padx=20, fill="x")

        # Close button
        ttk.Button(info_win, text="Close", command=info_win.destroy).pack(pady=10)

    def is_selected(self):
        """Check if this video is selected."""
        return self.selected.get()

    def get_video(self):
        """Get video data."""
        return self.video


class MinimalScraperApp(tk.Tk):
    """Main application window - single-window design."""

    def __init__(self):
        super().__init__()

        # State
        self.config_manager = Config()
        self.scraper = None
        self.search_results = []
        self.result_items = []
        self.is_searching = False
        self.is_downloading = False

        # Setup
        self._setup_window()
        self._build_ui()
        self._load_settings()

    def _setup_window(self):
        """Configure main window."""
        self.title("YouTube Transcript Scraper")
        self.geometry("800x700")
        self.configure(bg=COLORS["bg"])
        self.resizable(True, True)

        # Configure ttk style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", padding=6)
        style.configure("TCheckbutton", font=FONTS["body"])
        style.configure("TLabel", font=FONTS["body"])

    def _build_ui(self):
        """Build complete UI layout."""
        # Top bar
        self._build_top_bar()

        # Search panel
        self._build_search_panel()

        # Results panel
        self._build_results_panel()

        # Progress panel
        self._build_progress_panel()

        # Action buttons
        self._build_action_buttons()

    def _build_top_bar(self):
        """Build top bar with title and settings button."""
        top_frame = tk.Frame(self, bg=COLORS["primary"], height=50)
        top_frame.pack(fill="x")
        top_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(
            top_frame,
            text="YouTube Transcript Scraper",
            font=FONTS["title"],
            bg=COLORS["primary"],
            fg="white",
        )
        title_label.pack(side="left", padx=15, pady=10)

        # Settings button
        self.settings_btn = ttk.Button(top_frame, text="⚙ Settings", command=self._open_settings)
        self.settings_btn.pack(side="right", padx=15, pady=10)

    def _build_search_panel(self):
        """Build search controls panel."""
        search_frame = tk.Frame(self, bg=COLORS["bg"])
        search_frame.pack(fill="x", padx=15, pady=10)

        # Query row
        query_row = tk.Frame(search_frame, bg=COLORS["bg"])
        query_row.pack(fill="x", pady=5)

        ttk.Label(query_row, text="Search Query:").pack(side="left", padx=(0, 10))

        self.query_entry = ttk.Entry(query_row, font=FONTS["body"])
        self.query_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.query_entry.bind("<Return>", lambda e: self._on_search())

        self.search_btn = ttk.Button(query_row, text="Search", command=self._on_search, width=12)
        self.search_btn.pack(side="right")

        # Filters row
        filters_row = tk.Frame(search_frame, bg=COLORS["bg"])
        filters_row.pack(fill="x", pady=5)

        # Max results
        ttk.Label(filters_row, text="Max Results:").pack(side="left", padx=(0, 5))
        self.max_results_var = tk.StringVar(value="15")
        max_results_combo = ttk.Combobox(
            filters_row,
            textvariable=self.max_results_var,
            values=["5", "10", "15", "25", "50"],
            width=8,
            state="readonly",
        )
        max_results_combo.pack(side="left", padx=(0, 20))

        # Upload date
        ttk.Label(filters_row, text="Upload Date:").pack(side="left", padx=(0, 5))
        self.upload_date_var = tk.StringVar(value="Any time")
        upload_date_combo = ttk.Combobox(
            filters_row,
            textvariable=self.upload_date_var,
            values=list(UPLOAD_DATE_OPTIONS.keys()),
            width=15,
            state="readonly",
        )
        upload_date_combo.pack(side="left")

        # AI optimization row
        ai_row = tk.Frame(search_frame, bg=COLORS["bg"])
        ai_row.pack(fill="x", pady=5)

        self.ai_toggle_var = tk.BooleanVar(value=False)
        self.ai_checkbox = ttk.Checkbutton(
            ai_row,
            text="Use AI Optimization (GPT-4) - Requires API key",
            variable=self.ai_toggle_var,
        )
        self.ai_checkbox.pack(side="left")

    def _build_results_panel(self):
        """Build scrollable results panel."""
        results_frame = tk.LabelFrame(
            self,
            text="Search Results",
            font=FONTS["heading"],
            bg=COLORS["bg"],
            relief="solid",
            borderwidth=1,
        )
        results_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Results count label
        self.results_count_label = ttk.Label(results_frame, text="Results (0):", font=FONTS["body"])
        self.results_count_label.pack(anchor="w", padx=10, pady=5)

        # Scrollable frame for results
        canvas = tk.Canvas(results_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)

        self.results_container = tk.Frame(canvas, bg="white")

        # Configure scrolling
        self.results_container.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.results_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

    def _build_progress_panel(self):
        """Build progress tracking panel."""
        progress_frame = tk.Frame(self, bg=COLORS["bg"])
        progress_frame.pack(fill="x", padx=15, pady=5)

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=self.progress_var, maximum=100, mode="determinate"
        )
        self.progress_bar.pack(fill="x", pady=2)

        # Status label
        self.status_label = ttk.Label(
            progress_frame, text="Ready", font=FONTS["small"], foreground=COLORS["secondary"]
        )
        self.status_label.pack(anchor="w")

    def _build_action_buttons(self):
        """Build action buttons panel."""
        button_frame = tk.Frame(self, bg=COLORS["bg"])
        button_frame.pack(fill="x", padx=15, pady=10)

        self.download_btn = ttk.Button(
            button_frame,
            text="Download Selected",
            command=self._on_download_selected,
            state="disabled",
        )
        self.download_btn.pack(side="left", padx=5)

        self.export_btn = ttk.Button(
            button_frame, text="Export All (.md)", command=self._on_export_all, state="disabled"
        )
        self.export_btn.pack(side="left", padx=5)

        # Selection count label
        self.selection_label = ttk.Label(button_frame, text="0 selected", font=FONTS["small"])
        self.selection_label.pack(side="left", padx=20)

    def _load_settings(self):
        """Load settings from config."""
        # API key is loaded on-demand when needed

    def _open_settings(self):
        """Open settings dialog."""
        dialog = tk.Toplevel(self)
        dialog.title("Settings")
        dialog.geometry("500x300")
        dialog.transient(self)
        dialog.grab_set()

        # API Key section
        api_frame = tk.LabelFrame(dialog, text="OpenAI API Key", padx=10, pady=10)
        api_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(api_frame, text="Required for AI-powered query optimization (GPT-4):").pack(
            anchor="w"
        )

        api_key_entry = ttk.Entry(api_frame, width=50, show="*")
        current_key = self.config_manager.load_api_key()
        if current_key:
            api_key_entry.insert(0, current_key)
        api_key_entry.pack(pady=5, fill="x")

        # Output directory section
        output_frame = tk.LabelFrame(dialog, text="Output Directory", padx=10, pady=10)
        output_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(output_frame, text="Transcripts will be saved to:").pack(anchor="w")

        output_row = tk.Frame(output_frame)
        output_row.pack(fill="x", pady=5)

        output_entry = ttk.Entry(output_row)
        current_config = self.config_manager.load_config()
        output_entry.insert(0, current_config.get("output_dir", "transcripts"))
        output_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        def browse_dir():
            dir_path = filedialog.askdirectory()
            if dir_path:
                output_entry.delete(0, "end")
                output_entry.insert(0, dir_path)

        ttk.Button(output_row, text="Browse", command=browse_dir).pack(side="right")

        # Save button
        def save_settings():
            api_key = api_key_entry.get().strip()
            output_dir = output_entry.get().strip()

            # Save to config
            config = self.config_manager.load_config()
            if api_key:
                self.config_manager.save_api_key(api_key)
            config["output_dir"] = output_dir

            from pathlib import Path
            import json

            with open(Path.home() / ".youtube_scraper_config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

            dialog.destroy()
            messagebox.showinfo("Settings", "Settings saved successfully!")

        ttk.Button(dialog, text="Save Settings", command=save_settings).pack(pady=10)

    def _on_search(self):
        """Execute search with optional AI optimization."""
        query = self.query_entry.get().strip()

        if not query:
            messagebox.showwarning("Input Required", "Please enter a search query")
            return

        if self.is_searching:
            return

        # Clear previous results
        self._clear_results()

        # Disable UI
        self.is_searching = True
        self.search_btn.config(state="disabled", text="Searching...")
        self.query_entry.config(state="disabled")
        self._update_status("Searching YouTube...")

        # Run in background thread
        threading.Thread(target=self._search_thread, args=(query,), daemon=True).start()

    def _search_thread(self, query):
        """Background search thread."""
        try:
            # AI optimization if enabled
            final_query = query
            if self.ai_toggle_var.get():
                self.after(0, self._update_status, "Optimizing query with GPT-4...")
                api_key = self.config_manager.load_api_key()

                if not api_key:
                    self.after(
                        0,
                        messagebox.showwarning,
                        "API Key Required",
                        "Please set your OpenAI API key in Settings to use AI optimization.",
                    )
                    self.after(0, self._update_status, "Ready")
                    return

                try:
                    final_query = optimize_search_query(query, api_key)
                    self.after(0, self._log_message, f"Optimized: '{query}' → '{final_query}'")
                except Exception as e:
                    self.after(0, self._log_message, f"Optimization failed: {e}")
                    final_query = query

            # Search via TranscriptScraper
            self.after(0, self._update_status, "Searching videos...")

            self.scraper = TranscriptScraper(
                callback=lambda msg: self.after(0, self._log_message, msg)
            )

            # Build filters
            upload_date_label = self.upload_date_var.get()
            upload_date_value = UPLOAD_DATE_OPTIONS.get(upload_date_label, "any")

            filters = {"upload_date": upload_date_value, "sort_by": "relevance"}

            max_results = int(self.max_results_var.get())

            results = self.scraper.search_videos(
                final_query, max_results=max_results, filters=filters
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
        self.search_btn.config(state="normal", text="Search")
        self.query_entry.config(state="normal")

    def _display_results(self, results):
        """Display search results with checkboxes."""
        self._clear_results()

        if not results:
            self._update_status("No videos found")
            ttk.Label(
                self.results_container,
                text="No videos found for this query. Try a different search.",
                foreground=COLORS["secondary"],
            ).pack(pady=20)
            return

        self.search_results = results
        self.result_items = []

        # Create result items
        for idx, video in enumerate(results, 1):
            item = VideoResultItem(self.results_container, video, idx, self._update_selection_count)
            self.result_items.append(item)

        # Update counts
        self.results_count_label.config(text=f"Results ({len(results)}):")
        self._update_selection_count()

        # Enable download button
        self.download_btn.config(state="normal")
        self.export_btn.config(state="normal")

        self._update_status(f"Found {len(results)} videos")

    def _clear_results(self):
        """Clear all result items."""
        for widget in self.results_container.winfo_children():
            widget.destroy()

        self.search_results = []
        self.result_items = []
        self.results_count_label.config(text="Results (0):")
        self.selection_label.config(text="0 selected")
        self.download_btn.config(state="disabled")
        self.export_btn.config(state="disabled")

    def _update_selection_count(self):
        """Update selection count label."""
        selected_count = sum(1 for item in self.result_items if item.is_selected())
        self.selection_label.config(text=f"{selected_count} selected")

    def _on_download_selected(self):
        """Download transcripts for selected videos."""
        selected_videos = [item.get_video() for item in self.result_items if item.is_selected()]

        if not selected_videos:
            messagebox.showwarning("No Selection", "Please select at least one video to download")
            return

        if self.is_downloading:
            return

        # Disable buttons
        self.is_downloading = True
        self.download_btn.config(state="disabled")
        self.export_btn.config(state="disabled")
        self.search_btn.config(state="disabled")

        # Run download in background
        threading.Thread(target=self._download_thread, args=(selected_videos,), daemon=True).start()

    def _download_thread(self, videos):
        """Background download thread with progress updates."""
        total = len(videos)
        saved = 0
        skipped = 0

        # Get output directory
        config = self.config_manager.load_config()
        output_dir = config.get("output_dir", "transcripts")

        # Setup browser
        self.after(0, self._update_status, "Setting up browser...")
        try:
            self.scraper.setup_browser()
        except Exception as e:
            self.after(
                0,
                messagebox.showerror,
                "Browser Error",
                f"Failed to setup browser: {e}\n\nMake sure Chrome is installed.",
            )
            self.after(0, self._restore_download_ui)
            return

        try:
            for idx, video in enumerate(videos):
                # Update progress
                progress = (idx / total) * 100
                self.after(
                    0,
                    self._update_progress,
                    progress,
                    f"Downloading {idx+1}/{total}: {video['title'][:40]}...",
                )

                try:
                    # Extract transcript
                    transcript = self.scraper.get_transcript(video["id"])

                    if transcript:
                        # Save to file
                        self.scraper.output_dir = output_dir
                        filename = self.scraper.save_transcript(video, transcript)
                        self.after(0, self._log_message, f"✓ Saved: {filename}")
                        saved += 1
                    else:
                        self.after(
                            0,
                            self._log_message,
                            f"⊘ Skipped: {video['title'][:40]} (no transcript)",
                        )
                        skipped += 1

                except Exception as e:
                    self.after(0, self._log_message, f"⊗ Error: {video['title'][:40]} - {str(e)}")
                    skipped += 1

            # Complete
            self.after(0, self._update_progress, 100, "Download complete!")
            message = (
                f"Saved {saved} transcripts\n"
                f"Skipped {skipped} videos\n\n"
                f"Files saved to: {output_dir}"
            )
            self.after(0, messagebox.showinfo, "Download Complete", message)

        finally:
            # Cleanup browser
            if self.scraper and self.scraper.driver:
                self.scraper.driver.quit()

            self.after(0, self._restore_download_ui)

    def _restore_download_ui(self):
        """Restore UI after download completes."""
        self.is_downloading = False
        self.download_btn.config(state="normal")
        self.export_btn.config(state="normal")
        self.search_btn.config(state="normal")
        self._update_progress(0, "Ready")

    def _on_export_all(self):
        """Export all search results to markdown files."""
        if not self.search_results:
            messagebox.showwarning("No Results", "No search results to export")
            return

        # Use download logic with all videos
        all_videos = [item.get_video() for item in self.result_items]

        if messagebox.askyesno(
            "Export All", f"This will download {len(all_videos)} transcripts. Continue?"
        ):
            # Select all items
            for item in self.result_items:
                item.selected.set(True)
            self._update_selection_count()

            # Trigger download
            self._on_download_selected()

    def _update_progress(self, value, status):
        """Update progress bar and status."""
        self.progress_var.set(value)
        self.status_label.config(text=status)

    def _update_status(self, message):
        """Update status label."""
        self.status_label.config(text=message)

    def _log_message(self, message):
        """Log a message to status (could be expanded to a log window)."""
        print(f"[LOG] {message}")
        # For now, just print to console


def main():
    """Launch the application."""
    app = MinimalScraperApp()
    app.mainloop()


if __name__ == "__main__":
    main()
