"""Query transformation view showing Original → AI Optimized → YouTube flow."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING


class QueryTransformationView(ttk.Frame):
    """Visual flow diagram showing query transformation chain."""

    def __init__(self, parent):
        super().__init__(parent)
        self.original_query = ""
        self.optimized_query = ""
        self.youtube_query = ""
        self.bypass_ai = False
        self._build_ui()

    def _build_ui(self):
        """Build the transformation view UI."""
        # Title
        title = tk.Label(
            self, text="Query Transformation", font=FONTS["h3"], bg=COLORS["bg"], fg=COLORS["text"]
        )
        title.pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], SPACING["xs"]))

        # Bypass toggle
        toggle_frame = tk.Frame(self, bg=COLORS["bg"])
        toggle_frame.pack(fill="x", padx=SPACING["md"], pady=SPACING["xs"])

        self.bypass_var = tk.BooleanVar(value=False)
        bypass_cb = tk.Checkbutton(
            toggle_frame,
            text="Bypass AI optimization",
            variable=self.bypass_var,
            font=FONTS["body"],
            bg=COLORS["bg"],
            fg=COLORS["text"],
            command=self._toggle_bypass,
        )
        bypass_cb.pack(side="left")

        # Flow diagram container
        self.flow_frame = tk.Frame(self, bg="white", bd=1, relief="solid")
        self.flow_frame.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])

        self._render_flow()

    def _render_flow(self):
        """Render the transformation flow diagram."""
        # Clear existing content
        for widget in self.flow_frame.winfo_children():
            widget.destroy()

        # Stage 1: Original
        self._render_stage(
            "Original Query",
            self.original_query or "Enter your query...",
            COLORS["text_secondary"],
            0,
        )

        # Arrow
        if not self.bypass_ai:
            self._render_arrow(1)

            # Stage 2: AI Optimized
            self._render_stage(
                "AI Optimized", self.optimized_query or "AI will optimize...", COLORS["primary"], 2
            )

        # Arrow
        self._render_arrow(3 if not self.bypass_ai else 1)

        # Stage 3: YouTube
        youtube_display = (
            self.youtube_query
            or self.optimized_query
            or self.original_query
            or "Final YouTube query..."
        )
        self._render_stage(
            "YouTube Search", youtube_display, COLORS["success"], 4 if not self.bypass_ai else 2
        )

    def _render_stage(self, label: str, query: str, color: str, grid_row: int):
        """Render a single transformation stage."""
        stage_frame = tk.Frame(self.flow_frame, bg="white")
        stage_frame.grid(
            row=grid_row, column=0, sticky="ew", padx=SPACING["md"], pady=SPACING["xs"]
        )

        # Label
        label_widget = tk.Label(stage_frame, text=label, font=FONTS["body"], bg="white", fg=color)
        label_widget.pack(anchor="w")

        # Query display
        query_frame = tk.Frame(stage_frame, bg=COLORS["surface"], bd=1, relief="solid")
        query_frame.pack(fill="x", pady=(4, 0))

        query_text = tk.Text(
            query_frame,
            height=2,
            wrap="word",
            font=FONTS["body"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
            relief="flat",
            padx=8,
            pady=4,
        )
        query_text.insert("1.0", query)
        query_text.config(state="disabled")
        query_text.pack(fill="x")

        # Copy button
        copy_btn = tk.Button(
            query_frame,
            text="📋 Copy",
            font=FONTS["small"],
            bg=COLORS["surface"],
            fg=COLORS["text_secondary"],
            relief="flat",
            padx=4,
            pady=2,
            command=lambda q=query: self._copy_to_clipboard(q),
        )
        copy_btn.pack(anchor="e", padx=4, pady=2)

    def _render_arrow(self, grid_row: int):
        """Render arrow between stages."""
        arrow_frame = tk.Frame(self.flow_frame, bg="white", height=24)
        arrow_frame.grid(row=grid_row, column=0, sticky="ew")

        canvas = tk.Canvas(arrow_frame, bg="white", height=24, highlightthickness=0)
        canvas.pack(fill="x", padx=SPACING["lg"])

        # Draw arrow line
        canvas.create_line(20, 12, 200, 12, fill=COLORS["border"], width=2, arrow="last")

    def _toggle_bypass(self):
        """Toggle AI optimization bypass."""
        self.bypass_ai = self.bypass_var.get()
        self._render_flow()

    def _copy_to_clipboard(self, text: str):
        """Copy query to clipboard."""
        self.clipboard_clear()
        self.clipboard_append(text)

    def update_queries(self, original: str, optimized: str = None, youtube: str = None):
        """Update the transformation chain."""
        self.original_query = original
        self.optimized_query = optimized or original
        self.youtube_query = youtube or optimized or original
        self._render_flow()

    def get_final_query(self) -> str:
        """Get the final query to use for YouTube search."""
        if self.bypass_ai:
            return self.original_query
        return self.youtube_query or self.optimized_query or self.original_query
