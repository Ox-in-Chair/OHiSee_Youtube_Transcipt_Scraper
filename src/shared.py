"""Shared utilities and constants for YouTube Transcript Scraper.

This module contains reusable UI components, constants, and helper functions
used across the application.

Target: ~100 lines
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable


# Color palette - Professional blue theme
COLORS = {
    'bg': '#FFFFFF',           # Background white
    'primary': '#1E40AF',      # Primary blue (buttons, headers)
    'success': '#10B981',      # Success green
    'text': '#0F172A',         # Primary text color
    'border': '#E2E8F0',       # Border/divider color
    'secondary': '#6B7280',    # Secondary text/hints
    'hover': '#3B82F6'         # Hover state blue
}


# Typography system - Segoe UI hierarchy
FONTS = {
    'title': ('Segoe UI', 16, 'bold'),     # Window titles, main headings
    'heading': ('Segoe UI', 12, 'bold'),   # Section headings
    'body': ('Segoe UI', 10),              # Normal text, inputs
    'small': ('Segoe UI', 9)               # Helper text, labels
}


class VideoResultItem:
    """Represents a single video search result with checkbox and info button.

    This component displays a video title with:
    - Checkbox for selection (default: selected)
    - Truncated title text (max 60 chars)
    - Info button to show full video details

    Attributes:
        video: Dict with video metadata (id, title, channel, url)
        callback: Function called when selection changes
        frame: Container tkinter Frame
        selected: BooleanVar tracking selection state
    """

    def __init__(self, parent, video: Dict, index: int,
                 callback: Callable[[], None]):
        """Initialize video result item.

        Args:
            parent: Parent tkinter widget
            video: Video dict with keys: id, title, channel, url
            index: Display index (1-based)
            callback: Function to call when selection changes
        """
        self.video = video
        self.callback = callback

        # Container frame
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill='x', padx=5, pady=2)

        # Selection variable (default: selected for quick download)
        self.selected = tk.BooleanVar(value=True)

        # Checkbox with title (truncated at 60 chars)
        title_text = f"{index}. {video['title'][:60]}" + \
                    ('...' if len(video['title']) > 60 else '')

        self.checkbox = ttk.Checkbutton(
            self.frame,
            text=title_text,
            variable=self.selected,
            command=self._on_toggle
        )
        self.checkbox.pack(side='left', fill='x', expand=True)

        # Info button to show full details
        self.info_btn = ttk.Button(
            self.frame,
            text='Info',
            width=8,
            command=self._show_info
        )
        self.info_btn.pack(side='right', padx=2)

    def _on_toggle(self):
        """Handle checkbox toggle - notify parent of selection change."""
        self.callback()

    def _show_info(self):
        """Show video information dialog with full title, channel, and URL."""
        info_win = tk.Toplevel()
        info_win.title("Video Information")
        info_win.geometry("500x200")
        info_win.transient(info_win.master)

        # Title section
        ttk.Label(
            info_win,
            text="Title:",
            font=FONTS['heading']
        ).pack(anchor='w', padx=10, pady=(10, 0))

        ttk.Label(
            info_win,
            text=self.video['title'],
            wraplength=480
        ).pack(anchor='w', padx=20)

        # Channel section
        ttk.Label(
            info_win,
            text="Channel:",
            font=FONTS['heading']
        ).pack(anchor='w', padx=10, pady=(10, 0))

        ttk.Label(
            info_win,
            text=self.video['channel']
        ).pack(anchor='w', padx=20)

        # URL section (read-only text widget for easy copying)
        ttk.Label(
            info_win,
            text="URL:",
            font=FONTS['heading']
        ).pack(anchor='w', padx=10, pady=(10, 0))

        url_text = tk.Text(info_win, height=2, wrap='word')
        url_text.insert('1.0', self.video['url'])
        url_text.config(state='disabled')
        url_text.pack(anchor='w', padx=20, fill='x')

        # Close button
        ttk.Button(
            info_win,
            text='Close',
            command=info_win.destroy
        ).pack(pady=10)

    def is_selected(self) -> bool:
        """Check if this video is currently selected.

        Returns:
            True if checkbox is checked, False otherwise
        """
        return self.selected.get()

    def get_video(self) -> Dict:
        """Get video metadata dictionary.

        Returns:
            Video dict with keys: id, title, channel, url
        """
        return self.video
