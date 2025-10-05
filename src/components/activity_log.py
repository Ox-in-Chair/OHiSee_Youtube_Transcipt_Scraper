"""Structured activity log with timestamped events."""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING


class ActivityLog(ttk.Frame):
    """Real-time activity log showing scraper progress."""

    def __init__(self, parent):
        super().__init__(parent)
        self.events = []
        self._build_ui()

    def _build_ui(self):
        """Build the activity log UI."""
        # Title bar
        title_frame = tk.Frame(self, bg=COLORS["surface"])
        title_frame.pack(fill="x")

        tk.Label(
            title_frame,
            text="Activity Log",
            font=FONTS["h3"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).pack(side="left", padx=SPACING["md"], pady=SPACING["xs"])

        # Clear button
        tk.Button(
            title_frame,
            text="Clear",
            font=FONTS["small"],
            bg=COLORS["surface"],
            fg=COLORS["text_secondary"],
            relief="flat",
            command=self.clear,
        ).pack(side="right", padx=SPACING["md"])

        # Scrollable log area
        log_container = tk.Frame(self, bg="white")
        log_container.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(log_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.log_text = tk.Text(
            log_container,
            wrap="word",
            font=("Consolas", 10),
            bg="white",
            fg=COLORS["text"],
            relief="flat",
            yscrollcommand=scrollbar.set,
            state="disabled",
        )
        self.log_text.pack(
            side="left", fill="both", expand=True, padx=SPACING["sm"], pady=SPACING["sm"]
        )

        scrollbar.config(command=self.log_text.yview)

        # Configure text tags for different event types
        self.log_text.tag_configure("info", foreground=COLORS["text"])
        self.log_text.tag_configure("success", foreground=COLORS["success"])
        self.log_text.tag_configure("warning", foreground=COLORS["warning"])
        self.log_text.tag_configure("error", foreground=COLORS["error"])
        self.log_text.tag_configure("timestamp", foreground=COLORS["text_secondary"])

    def log(self, message: str, level: str = "info"):
        """Add a log entry."""
        timestamp = datetime.now().strftime("%H:%M:%S")

        event = {"timestamp": timestamp, "message": message, "level": level}
        self.events.append(event)

        # Add to text widget
        self.log_text.config(state="normal")

        # Timestamp
        self.log_text.insert("end", f"[{timestamp}] ", "timestamp")

        # Icon based on level
        icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
        icon = icons.get(level, "ℹ️")
        self.log_text.insert("end", f"{icon} ")

        # Message
        self.log_text.insert("end", f"{message}\n", level)

        self.log_text.config(state="disabled")
        self.log_text.see("end")  # Auto-scroll to bottom

    def log_video_start(self, video_title: str, index: int, total: int):
        """Log video processing start."""
        self.log("info", f"Processing video {index}/{total}: {video_title}")

    def log_video_success(self, video_title: str):
        """Log successful video processing."""
        self.log(f"Saved transcript: {video_title}", "success")

    def log_video_skip(self, video_title: str, reason: str):
        """Log skipped video."""
        self.log(f"Skipped {video_title}: {reason}", "warning")

    def log_error(self, message: str):
        """Log error."""
        self.log(message, "error")

    def log_search_start(self, query: str):
        """Log search start."""
        self.log(f'Searching YouTube for: "{query}"', "info")

    def log_search_complete(self, count: int):
        """Log search completion."""
        self.log(f"Found {count} videos", "success")

    def log_optimization(self, original: str, optimized: str):
        """Log query optimization."""
        self.log(f'Optimized query: "{original}" → "{optimized}"', "info")

    def clear(self):
        """Clear all log entries."""
        self.events = []
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    def get_events(self) -> List[Dict[str, Any]]:
        """Get all logged events."""
        return self.events.copy()

    def export_log(self, filepath: str):
        """Export log to text file."""
        with open(filepath, "w", encoding="utf-8") as f:
            for event in self.events:
                f.write(f"[{event['timestamp']}] {event['level'].upper()}: {event['message']}\n")
