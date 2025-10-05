"""Dynamic facets bar showing active filters and estimates."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING


class FacetsBar(ttk.Frame):
    """Horizontal bar showing active filters with badges and estimates."""

    def __init__(self, parent, on_facet_click: Optional[Callable] = None):
        super().__init__(parent)
        self.on_facet_click = on_facet_click
        self.active_facets = {}
        self.estimates = {"runtime": "~5 min", "cost": "$0.15", "videos": "15"}
        self._build_ui()

    def _build_ui(self):
        """Build the facets bar UI."""
        # Container with subtle background
        self.configure(style="Facets.TFrame")

        # Left side: Active facets
        self.facets_container = tk.Frame(self, bg=COLORS["surface"])
        self.facets_container.pack(
            side="left", fill="x", expand=True, padx=SPACING["md"], pady=SPACING["sm"]
        )

        # Right side: Estimates
        self.estimates_frame = tk.Frame(self, bg=COLORS["surface"])
        self.estimates_frame.pack(side="right", padx=SPACING["md"], pady=SPACING["sm"])

        self._render_facets()
        self._render_estimates()

    def _render_facets(self):
        """Render active filter badges."""
        # Clear existing facets
        for widget in self.facets_container.winfo_children():
            widget.destroy()

        if not self.active_facets:
            # Show placeholder
            placeholder = tk.Label(
                self.facets_container,
                text="No filters applied • Click to add filters",
                font=FONTS["body"],
                bg=COLORS["surface"],
                fg=COLORS["text_secondary"],
            )
            placeholder.pack(side="left")
            return

        # Render each active facet as a badge
        for facet_id, facet_value in self.active_facets.items():
            self._create_facet_badge(facet_id, facet_value)

    def _create_facet_badge(self, facet_id: str, value: Any):
        """Create a single facet badge with remove button."""
        badge_frame = tk.Frame(self.facets_container, bg=COLORS["primary"], bd=0, relief="flat")
        badge_frame.pack(side="left", padx=(0, SPACING["xs"]))

        # Facet label
        label_text = f"{self._format_facet_name(facet_id)}: {self._format_value(value)}"
        label = tk.Label(
            badge_frame,
            text=label_text,
            font=FONTS["small"],
            bg=COLORS["primary"],
            fg="white",
            padx=8,
            pady=4,
        )
        label.pack(side="left")

        # Remove button
        remove_btn = tk.Label(
            badge_frame,
            text="✕",
            font=FONTS["small"],
            bg=COLORS["primary"],
            fg="white",
            padx=4,
            pady=4,
            cursor="hand2",
        )
        remove_btn.pack(side="left")
        remove_btn.bind("<Button-1>", lambda e: self._remove_facet(facet_id))

        # Click to edit
        label.bind("<Button-1>", lambda e: self._edit_facet(facet_id))
        label.config(cursor="hand2")

    def _format_facet_name(self, facet_id: str) -> str:
        """Convert facet ID to readable name."""
        name_map = {
            "upload_date": "Upload Date",
            "duration": "Duration",
            "sort_by": "Sort By",
            "features": "Features",
            "quality": "Quality",
            "language": "Language",
        }
        return name_map.get(facet_id, facet_id.replace("_", " ").title())

    def _format_value(self, value: Any) -> str:
        """Format facet value for display."""
        if isinstance(value, list):
            return ", ".join(str(v) for v in value[:2]) + (
                f" +{len(value)-2}" if len(value) > 2 else ""
            )
        elif isinstance(value, int):
            if value == 7:
                return "Last week"
            elif value == 30:
                return "Last month"
            elif value == 90:
                return "Last 90 days"
            elif value == 365:
                return "Last year"
            return str(value)
        return str(value)

    def _remove_facet(self, facet_id: str):
        """Remove a facet from active filters."""
        if facet_id in self.active_facets:
            del self.active_facets[facet_id]
            self._render_facets()
            self._update_estimates()

            if self.on_facet_click:
                self.on_facet_click("remove", facet_id)

    def _edit_facet(self, facet_id: str):
        """Trigger facet editing."""
        if self.on_facet_click:
            self.on_facet_click("edit", facet_id)

    def _render_estimates(self):
        """Render runtime, cost, and video count estimates."""
        # Clear existing
        for widget in self.estimates_frame.winfo_children():
            widget.destroy()

        estimates_data = [
            ("⏱️", self.estimates["runtime"], "Runtime"),
            ("💰", self.estimates["cost"], "Cost"),
            ("🎬", self.estimates["videos"], "Videos"),
        ]

        for icon, value, label in estimates_data:
            est_item = tk.Frame(self.estimates_frame, bg=COLORS["surface"])
            est_item.pack(side="left", padx=SPACING["sm"])

            tk.Label(est_item, text=icon, font=FONTS["body"], bg=COLORS["surface"]).pack(
                side="left"
            )

            tk.Label(
                est_item, text=value, font=FONTS["body"], bg=COLORS["surface"], fg=COLORS["text"]
            ).pack(side="left", padx=(4, 2))

            tk.Label(
                est_item,
                text=label,
                font=FONTS["small"],
                bg=COLORS["surface"],
                fg=COLORS["text_secondary"],
            ).pack(side="left")

    def update_facets(self, facets: Dict[str, Any]):
        """Update active facets."""
        self.active_facets = facets.copy()
        self._render_facets()
        self._update_estimates()

    def add_facet(self, facet_id: str, value: Any):
        """Add a new facet."""
        self.active_facets[facet_id] = value
        self._render_facets()
        self._update_estimates()

    def _update_estimates(self):
        """Recalculate estimates based on active facets."""
        # Base estimates
        num_results = self.active_facets.get("max_results", 15)

        # Runtime: ~20 seconds per video
        runtime_seconds = num_results * 20
        if runtime_seconds < 60:
            runtime = f"~{runtime_seconds}s"
        else:
            runtime = f"~{runtime_seconds // 60} min"

        # Cost: $0.01 per video (GPT-4 optimization)
        use_ai = self.active_facets.get("use_ai_optimization", True)
        cost = num_results * 0.01 if use_ai else 0.0

        self.estimates = {"runtime": runtime, "cost": f"${cost:.2f}", "videos": str(num_results)}

        self._render_estimates()

    def get_active_facets(self) -> Dict[str, Any]:
        """Get current active facets."""
        return self.active_facets.copy()

    def clear_all(self):
        """Clear all active facets."""
        self.active_facets = {}
        self._render_facets()
        self._update_estimates()
