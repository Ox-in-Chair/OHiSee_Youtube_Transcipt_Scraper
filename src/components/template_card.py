"""Template cards for research patterns."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING


class TemplateCard(tk.Frame):
    """Modern elevated card with hover effects (360x200px).

    Research-grade design: clean surface, subtle shadows, elevated on hover.
    """

    def __init__(
        self, parent, template_data: Dict[str, Any], on_preview: Optional[Callable] = None
    ):
        super().__init__(
            parent,
            width=360,
            height=200,
            bg=COLORS["surface"],  # Pure white surface
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            relief="flat",
        )
        self.template_data = template_data
        self.on_preview = on_preview
        self.selected = False
        self._build_ui()

    def _build_ui(self):
        """Build modern card with generous whitespace."""
        self.pack_propagate(False)
        self.configure(takefocus=True)

        # Content container with padding
        content = tk.Frame(self, bg=COLORS["surface"])
        content.pack(fill="both", expand=True, padx=SPACING["lg"], pady=SPACING["md"])

        # Icon (larger for visual impact)
        icon = tk.Label(
            content,
            text=self.template_data.get("icon", "📄"),
            font=("Segoe UI", 40),
            bg=COLORS["surface"]
        )
        icon.pack(pady=(SPACING["xs"], SPACING["sm"]))

        # Title (H2 semibold)
        title = tk.Label(
            content,
            text=self.template_data.get("name", "Template"),
            font=FONTS["h2"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        )
        title.pack(pady=(0, SPACING["xs"]))

        # Short description
        desc = tk.Label(
            content,
            text=self.template_data.get("promise", ""),
            font=FONTS["caption"],
            bg=COLORS["surface"],
            fg=COLORS["text_secondary"],
            wraplength=300,
        )
        desc.pack(pady=(0, SPACING["md"]))

        # View Details micro-link
        details_btn = tk.Label(
            content,
            text="Select Template →",
            font=("Inter", 11, "normal"),
            bg=COLORS["surface"],
            fg=COLORS["primary"],
            cursor="hand2",
        )
        details_btn.pack()
        details_btn.bind("<Button-1>", lambda e: self._activate_card())

        # Interaction bindings
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Return>", self._on_activate)  # Keyboard activation
        self.bind("<space>", self._on_activate)  # Alternative activation
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _handle_preview(self):
        """Handle preview button click."""
        self._activate_card()

    def _build_config(self) -> Dict[str, Any]:
        """Build configuration from template and toggles."""
        config = {"template": self.template_data["name"], "settings": {}}

        # Add toggle states
        if "toggles" in self.template_data:
            for toggle in self.template_data["toggles"]:
                key = toggle["key"]
                if hasattr(self, f"toggle_{key}"):
                    var = getattr(self, f"toggle_{key}")
                    config["settings"][key] = var.get()

        # Add template-specific config
        if "config" in self.template_data:
            config.update(self.template_data["config"])

        return config

    def _on_hover(self, event):
        """Hover elevation effect with 150ms transition."""
        if not self.selected:
            # Smooth color transition on hover (simulates 150ms ease-in-out)
            self.configure(
                bg=COLORS["background"],  # Slight background shift
                highlightbackground=COLORS["primary"],  # Blue border on hover
                highlightthickness=2,
                relief="raised"  # Simulates elevation
            )

    def _on_leave(self, event):
        """Remove elevation on mouse leave with 150ms transition."""
        if not self.selected:
            # Return to default state
            self.configure(
                bg=COLORS["surface"],
                highlightbackground=COLORS["border"],
                highlightthickness=1,
                relief="flat"
            )

    def _on_click(self, event):
        """Handle card click."""
        self._activate_card()

    def _on_activate(self, event):
        """Keyboard activation."""
        self._activate_card()
        return "break"

    def _activate_card(self):
        """Activate template selection."""
        self.selected = True
        self.configure(
            highlightbackground=COLORS["accent"],  # Green tick mark effect
            highlightthickness=3,
            relief="flat"
        )
        if self.on_preview:
            config = self._build_config()
            self.on_preview(self.template_data["name"], config)

    def _on_focus_in(self, event):
        """Keyboard focus ring."""
        if not self.selected:
            self.configure(
                highlightbackground=COLORS["primary"],
                highlightthickness=2
            )

    def _on_focus_out(self, event):
        """Remove focus ring."""
        if not self.selected:
            self.configure(
                highlightbackground=COLORS["border"],
                highlightthickness=1
            )


class TemplateGrid(ttk.Frame):
    """Grid of template cards (2x2 layout for focused selection)."""

    TEMPLATES = [
        {
            "name": "Citation Harvest",
            "icon": "📚",
            "promise": "Extract all citations and references",
        },
        {
            "name": "Course Outline",
            "icon": "🎓",
            "promise": "Structure educational content",
        },
        {
            "name": "Topic Overview",
            "icon": "🎯",
            "promise": "Comprehensive research on any topic",
        },
        {
            "name": "Custom",
            "icon": "⚙️",
            "promise": "Create your own research template",
        },
    ]

    def __init__(self, parent, on_template_preview: Optional[Callable] = None):
        super().__init__(parent)
        self.on_template_preview = on_template_preview
        self._build_grid()

    def _build_grid(self):
        """Build modern 2x2 card grid."""
        for i, template in enumerate(self.TEMPLATES):
            row = i // 2
            col = i % 2

            card = TemplateCard(self, template, self.on_template_preview)
            card.grid(row=row, column=col, padx=SPACING["md"], pady=SPACING["md"])
