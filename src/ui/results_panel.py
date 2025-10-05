"""Results Panel Component

Displays search results in a scrollable list with checkboxes for selection.
Each result shows the video title (truncated) with an info button for
full details.

This component manages result display, selection tracking, and notifies
the parent when selection changes.

Target: ~150 lines
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Callable

from shared import COLORS, FONTS, VideoResultItem


class ResultsPanel(ttk.Frame):
    """Search results display panel with scrollable list.

    Components:
    - Results count label
    - Scrollable canvas container
    - VideoResultItem widgets for each result
    - Selection tracking

    Attributes:
        on_selection_change_callback: Function called when selection changes
        result_items: List of VideoResultItem components
        count_label: Label showing results count
        container: Frame holding result items
    """

    def __init__(self, parent,
                 on_selection_change_callback: Callable[[], None]):
        """Initialize results panel.

        Args:
            parent: Parent tkinter widget
            on_selection_change_callback: Function called when selection changes
        """
        super().__init__(parent)
        self.on_selection_change_callback = on_selection_change_callback
        self.result_items = []

        # Build UI
        self._build_ui()

    def _build_ui(self):
        """Build results panel UI components."""
        # Label frame container
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

        # Scrollable canvas for results
        canvas = tk.Canvas(results_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            results_frame,
            orient='vertical',
            command=canvas.yview
        )

        # Container frame for result items
        self.container = tk.Frame(canvas, bg='white')

        # Configure canvas scrolling
        self.container.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )

        canvas.create_window((0, 0), window=self.container, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        # Enable mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

    def display_results(self, videos: List[Dict]):
        """Display search results.

        Args:
            videos: List of video dicts with keys: id, title, channel, url
        """
        self.clear()

        if not videos:
            # Show "no results" message
            ttk.Label(
                self.container,
                text="No videos found. Try a different search.",
                foreground=COLORS['secondary']
            ).pack(pady=20)
            return

        # Create result items
        for idx, video in enumerate(videos, 1):
            item = VideoResultItem(
                self.container,
                video,
                idx,
                self.on_selection_change_callback
            )
            self.result_items.append(item)

        # Update count label
        self.count_label.config(text=f"Results ({len(videos)}):")

    def get_selected_videos(self) -> List[Dict]:
        """Get list of selected videos.

        Returns:
            List of video dicts for selected items
        """
        return [
            item.get_video()
            for item in self.result_items
            if item.is_selected()
        ]

    def clear(self):
        """Clear all results and reset panel state."""
        # Destroy all result item frames
        for widget in self.container.winfo_children():
            widget.destroy()

        # Reset state
        self.result_items = []
        self.count_label.config(text="Results (0):")
