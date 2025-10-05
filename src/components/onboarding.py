"""Onboarding banner for first-time users."""

import tkinter as tk
from tkinter import ttk
import json
import os
from typing import Callable, Optional
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING


class OnboardingBanner(ttk.Frame):
    """First-run banner with sample project seeding."""

    CONFIG_FILE = os.path.expanduser("~/.youtube_scraper_onboarding.json")

    def __init__(self, parent, on_try_sample: Optional[Callable] = None):
        super().__init__(parent)
        self.on_try_sample = on_try_sample
        self.dismissed = self._load_dismissed_state()

        if not self.dismissed:
            self._build_ui()

    def _build_ui(self):
        """Build the onboarding banner UI."""
        self.configure(style="Onboarding.TFrame", height=80)

        # Main container
        container = tk.Frame(self, bg=COLORS["primary"], height=80)
        container.pack(fill="both", expand=True)

        # Icon/emoji
        icon = tk.Label(
            container, text="🎯", font=("Segoe UI", 24), bg=COLORS["primary"], fg="white"
        )
        icon.pack(side="left", padx=SPACING["md"])

        # Message content
        content = tk.Frame(container, bg=COLORS["primary"])
        content.pack(side="left", fill="both", expand=True)

        title = tk.Label(
            content,
            text="Welcome to YouTube Transcript Scraper Pro",
            font=FONTS["h3"],
            bg=COLORS["primary"],
            fg="white",
        )
        title.pack(anchor="w", pady=(SPACING["xs"], 0))

        desc = tk.Label(
            content,
            text="Try our BRCGS automation sample to see the power of structured research",
            font=FONTS["body"],
            bg=COLORS["primary"],
            fg="white",
        )
        desc.pack(anchor="w")

        # Action buttons
        buttons = tk.Frame(container, bg=COLORS["primary"])
        buttons.pack(side="right", padx=SPACING["md"])

        try_btn = tk.Button(
            buttons,
            text="Try Sample",
            font=FONTS["body"],
            bg="white",
            fg=COLORS["primary"],
            relief="flat",
            padx=16,
            pady=6,
            command=self._try_sample,
        )
        try_btn.pack(side="left", padx=(0, SPACING["xs"]))

        learn_btn = tk.Button(
            buttons,
            text="Learn More",
            font=FONTS["body"],
            bg=COLORS["primary"],
            fg="white",
            relief="flat",
            bd=1,
            padx=16,
            pady=6,
            command=self._learn_more,
        )
        learn_btn.pack(side="left", padx=(0, SPACING["xs"]))

        dismiss_btn = tk.Button(
            buttons,
            text="✕",
            font=("Segoe UI", 12),
            bg=COLORS["primary"],
            fg="white",
            relief="flat",
            padx=8,
            pady=4,
            command=self._dismiss,
        )
        dismiss_btn.pack(side="left")

    def _try_sample(self):
        """Load BRCGS automation sample project."""
        sample_config = {
            "query": "BRCGS workflow automation manufacturing standards",
            "max_results": 10,
            "filters": {"upload_date": 90, "sort_by": "relevance"},
            "template": "Topic Overview",
            "output_dir": "BRCGS_Research",
        }

        if self.on_try_sample:
            self.on_try_sample(sample_config)

        self._dismiss()

    def _learn_more(self):
        """Open documentation or tutorial."""
        import webbrowser

        webbrowser.open("https://github.com/Ox-in-Chair/OHiSee_Youtube_Transcipt_Scraper#readme")

    def _dismiss(self):
        """Dismiss banner and save state."""
        self.dismissed = True
        self._save_dismissed_state()
        self.pack_forget()

    def _load_dismissed_state(self) -> bool:
        """Check if banner was previously dismissed."""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    return data.get("dismissed", False)
            except:
                pass
        return False

    def _save_dismissed_state(self):
        """Persist dismissed state."""
        data = {"dismissed": True}
        try:
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(data, f)
        except:
            pass
