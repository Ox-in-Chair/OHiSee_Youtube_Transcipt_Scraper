"""Persistent top bar with progress tracker and status icons.

Research-grade navigation anchor with project context and system status.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, SPACING


class TopBar(tk.Frame):
    """Persistent top bar for navigation and status display.

    Features:
    - Project title and branding
    - Step progress indicator (1 Define → 5 Export)
    - Status icons (AI status, API connection, cache active)
    - Clean horizontal layout with subtle border
    """

    STEPS = [
        ("1", "Define"),
        ("2", "Refine"),
        ("3", "Review"),
        ("4", "Run"),
        ("5", "Export")
    ]

    def __init__(
        self,
        parent,
        on_new_research: Optional[Callable] = None,
        on_help: Optional[Callable] = None
    ):
        super().__init__(
            parent,
            bg=COLORS["surface"],
            relief="flat",
            borderwidth=0
        )

        self.current_step = 0
        self.status = {
            "ai_enabled": False,
            "api_connected": False,
            "cache_active": True
        }

        self.on_new_research = on_new_research
        self.on_help = on_help

        self._build_ui()

    def _build_ui(self):
        """Build top bar layout."""
        # Add bottom border
        border = tk.Frame(self, bg=COLORS["border"], height=1)
        border.pack(side="bottom", fill="x")

        # Left: Project title + New Research button
        left_section = tk.Frame(self, bg=COLORS["surface"])
        left_section.pack(side="left", padx=SPACING["lg"], pady=SPACING["sm"])

        tk.Label(
            left_section,
            text="YouTube Research Platform",
            font=FONTS["h2"],
            bg=COLORS["surface"],
            fg=COLORS["text"]
        ).pack(side="left", padx=(0, SPACING["md"]))

        if self.on_new_research:
            new_btn = tk.Button(
                left_section,
                text="+ New Research",
                font=FONTS["body"],
                bg=COLORS["accent"],
                fg="white",
                relief="flat",
                padx=SPACING["md"],
                pady=SPACING["xs"],
                cursor="hand2",
                command=self.on_new_research
            )
            new_btn.pack(side="left")

        # Center: Step Progress Tracker
        center_section = tk.Frame(self, bg=COLORS["surface"])
        center_section.pack(side="left", expand=True, padx=SPACING["xl"])

        self.step_labels = []
        for i, (num, name) in enumerate(self.STEPS):
            step_container = tk.Frame(center_section, bg=COLORS["surface"])
            step_container.pack(side="left", padx=SPACING["xs"])

            # Step number circle
            step_num = tk.Label(
                step_container,
                text=num,
                font=("Inter", 11, "bold"),
                bg=COLORS["border"],
                fg=COLORS["text_secondary"],
                width=3,
                height=1
            )
            step_num.pack(side="left", padx=(0, SPACING["xs"]//2))

            # Step name
            step_name = tk.Label(
                step_container,
                text=name,
                font=FONTS["body"],
                bg=COLORS["surface"],
                fg=COLORS["text_secondary"]
            )
            step_name.pack(side="left")

            self.step_labels.append((step_num, step_name))

            # Arrow separator (except last step)
            if i < len(self.STEPS) - 1:
                tk.Label(
                    center_section,
                    text="→",
                    font=FONTS["body"],
                    bg=COLORS["surface"],
                    fg=COLORS["border"]
                ).pack(side="left", padx=SPACING["xs"])

        # Right: Status icons + Help
        right_section = tk.Frame(self, bg=COLORS["surface"])
        right_section.pack(side="right", padx=SPACING["lg"], pady=SPACING["sm"])

        # Status indicators
        self.status_frame = tk.Frame(right_section, bg=COLORS["surface"])
        self.status_frame.pack(side="left", padx=(0, SPACING["md"]))

        self.ai_indicator = self._create_status_icon("AI", self.status["ai_enabled"])
        self.api_indicator = self._create_status_icon("API", self.status["api_connected"])
        self.cache_indicator = self._create_status_icon("Cache", self.status["cache_active"])

        # Help button
        if self.on_help:
            help_btn = tk.Button(
                right_section,
                text="?",
                font=("Inter", 12, "bold"),
                bg=COLORS["secondary"],
                fg="white",
                relief="flat",
                width=3,
                height=1,
                cursor="hand2",
                command=self.on_help
            )
            help_btn.pack(side="left")

    def _create_status_icon(self, label: str, active: bool) -> tk.Label:
        """Create status indicator icon."""
        color = COLORS["success"] if active else COLORS["border"]

        status_label = tk.Label(
            self.status_frame,
            text=f"● {label}",
            font=("Inter", 10),
            bg=COLORS["surface"],
            fg=color
        )
        status_label.pack(side="left", padx=SPACING["xs"])

        return status_label

    def update_step(self, step: int):
        """Update active step highlighting."""
        self.current_step = step

        for i, (num_label, name_label) in enumerate(self.step_labels):
            if i == step:
                # Active step - primary blue
                num_label.config(bg=COLORS["primary"], fg="white")
                name_label.config(fg=COLORS["text"], font=("Inter", 13, "bold"))
            elif i < step:
                # Completed step - success green
                num_label.config(bg=COLORS["success"], fg="white")
                name_label.config(fg=COLORS["text"], font=FONTS["body"])
            else:
                # Future step - gray
                num_label.config(bg=COLORS["border"], fg=COLORS["text_secondary"])
                name_label.config(fg=COLORS["text_secondary"], font=FONTS["body"])

    def update_status(self, key: str, value: bool):
        """Update status indicator."""
        self.status[key] = value
        color = COLORS["success"] if value else COLORS["border"]

        if key == "ai_enabled":
            self.ai_indicator.config(fg=color)
        elif key == "api_connected":
            self.api_indicator.config(fg=color)
        elif key == "cache_active":
            self.cache_indicator.config(fg=color)
