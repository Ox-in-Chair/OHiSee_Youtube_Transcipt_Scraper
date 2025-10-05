"""AI transparency panel showing confidence scores and decision breakdowns."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING


class AITransparencyPanel(ttk.Frame):
    """Expandable panel showing AI decision-making transparency."""

    def __init__(self, parent):
        super().__init__(parent)
        self.expanded = False
        self.current_data = None
        self._build_ui()

    def _build_ui(self):
        """Build the transparency panel UI."""
        # Header (always visible)
        header_frame = tk.Frame(self, bg=COLORS["surface"], height=48)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        # Toggle button
        self.toggle_btn = tk.Button(
            header_frame,
            text="▶ AI Decision Breakdown",
            font=FONTS["body"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
            relief="flat",
            anchor="w",
            padx=SPACING["sm"],
            command=self._toggle_expanded,
        )
        self.toggle_btn.pack(side="left", fill="both", expand=True)

        # Confidence badge
        self.confidence_label = tk.Label(
            header_frame,
            text="85% confidence",
            font=FONTS["small"],
            bg=COLORS["success"],
            fg="white",
            padx=8,
            pady=4,
        )
        self.confidence_label.pack(side="right", padx=SPACING["sm"])

        # Expandable content frame
        self.content_frame = tk.Frame(self, bg="white")

    def _toggle_expanded(self):
        """Toggle expanded/collapsed state."""
        self.expanded = not self.expanded

        if self.expanded:
            self.toggle_btn.config(text="▼ AI Decision Breakdown")
            self.content_frame.pack(fill="both", expand=True, pady=(0, SPACING["sm"]))
            self._render_content()
        else:
            self.toggle_btn.config(text="▶ AI Decision Breakdown")
            self.content_frame.pack_forget()

    def _render_content(self):
        """Render expanded content with decision tree."""
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if not self.current_data:
            # Default example data
            self.current_data = {
                "confidence": 85,
                "model": "GPT-4",
                "factors": [
                    {"name": "Query Clarity", "score": 90, "impact": "high"},
                    {"name": "Time Relevance", "score": 85, "impact": "medium"},
                    {"name": "Source Quality", "score": 80, "impact": "high"},
                    {"name": "Content Depth", "score": 75, "impact": "medium"},
                ],
                "optimizations": [
                    "Simplified technical jargon",
                    "Added time constraint (Last 90 days)",
                    "Prioritized verified channels",
                ],
            }

        # Model info
        model_frame = tk.Frame(self.content_frame, bg="white")
        model_frame.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])

        tk.Label(
            model_frame, text="Model:", font=FONTS["body"], bg="white", fg=COLORS["text_secondary"]
        ).pack(side="left")
        tk.Label(
            model_frame,
            text=self.current_data.get("model", "GPT-4"),
            font=FONTS["body"],
            bg="white",
            fg=COLORS["text"],
        ).pack(side="left", padx=SPACING["xs"])

        # Confidence factors
        factors_label = tk.Label(
            self.content_frame,
            text="Confidence Factors",
            font=FONTS["h3"],
            bg="white",
            fg=COLORS["text"],
        )
        factors_label.pack(anchor="w", padx=SPACING["md"], pady=(SPACING["sm"], SPACING["xs"]))

        for factor in self.current_data.get("factors", []):
            self._render_factor(factor)

        # Optimizations applied
        opt_label = tk.Label(
            self.content_frame,
            text="Optimizations Applied",
            font=FONTS["h3"],
            bg="white",
            fg=COLORS["text"],
        )
        opt_label.pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], SPACING["xs"]))

        for opt in self.current_data.get("optimizations", []):
            opt_item = tk.Frame(self.content_frame, bg="white")
            opt_item.pack(fill="x", padx=SPACING["md"], pady=2)

            tk.Label(opt_item, text="•", font=FONTS["body"], bg="white", fg=COLORS["primary"]).pack(
                side="left"
            )
            tk.Label(opt_item, text=opt, font=FONTS["body"], bg="white", fg=COLORS["text"]).pack(
                side="left", padx=SPACING["xs"]
            )

    def _render_factor(self, factor: Dict[str, Any]):
        """Render a single confidence factor with score bar."""
        factor_frame = tk.Frame(self.content_frame, bg="white")
        factor_frame.pack(fill="x", padx=SPACING["md"], pady=SPACING["xs"])

        # Factor name and score
        info_frame = tk.Frame(factor_frame, bg="white")
        info_frame.pack(fill="x")

        tk.Label(
            info_frame, text=factor["name"], font=FONTS["body"], bg="white", fg=COLORS["text"]
        ).pack(side="left")

        score_label = tk.Label(
            info_frame,
            text=f"{factor['score']}%",
            font=FONTS["small"],
            bg="white",
            fg=COLORS["text_secondary"],
        )
        score_label.pack(side="right")

        # Impact badge
        impact_colors = {
            "high": COLORS["error"],
            "medium": COLORS["warning"],
            "low": COLORS["text_secondary"],
        }
        impact_bg = impact_colors.get(factor.get("impact", "medium"), COLORS["text_secondary"])

        tk.Label(
            info_frame,
            text=factor.get("impact", "medium").upper(),
            font=FONTS["small"],
            bg=impact_bg,
            fg="white",
            padx=6,
            pady=2,
        ).pack(side="right", padx=SPACING["xs"])

        # Score bar
        bar_frame = tk.Frame(factor_frame, bg=COLORS["border"], height=8)
        bar_frame.pack(fill="x", pady=(4, 0))

        bar_width = factor["score"]  # Percentage
        fill_frame = tk.Frame(bar_frame, bg=COLORS["primary"], height=8)
        fill_frame.place(x=0, y=0, relwidth=bar_width / 100, relheight=1)

    def update_data(self, data: Dict[str, Any]):
        """Update panel with new AI decision data."""
        self.current_data = data

        # Update confidence badge
        confidence = data.get("confidence", 0)
        self.confidence_label.config(text=f"{confidence}% confidence")

        # Update badge color based on confidence
        if confidence >= 80:
            self.confidence_label.config(bg=COLORS["success"])
        elif confidence >= 60:
            self.confidence_label.config(bg=COLORS["warning"])
        else:
            self.confidence_label.config(bg=COLORS["error"])

        # Re-render if expanded
        if self.expanded:
            self._render_content()

    def show_optimization_details(self, original: str, optimized: str, reasoning: str):
        """Show detailed optimization explanation."""
        if not self.expanded:
            self._toggle_expanded()

        # Add optimization explanation to content
        detail_frame = tk.Frame(self.content_frame, bg=COLORS["surface"], bd=1, relief="solid")
        detail_frame.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])

        tk.Label(
            detail_frame,
            text="Query Transformation",
            font=FONTS["h3"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).pack(anchor="w", padx=SPACING["sm"], pady=(SPACING["xs"], 0))

        tk.Label(
            detail_frame,
            text=f"Original: {original}",
            font=FONTS["body"],
            bg=COLORS["surface"],
            fg=COLORS["text_secondary"],
            wraplength=400,
            justify="left",
        ).pack(anchor="w", padx=SPACING["sm"], pady=2)

        tk.Label(
            detail_frame,
            text=f"Optimized: {optimized}",
            font=FONTS["body"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
            wraplength=400,
            justify="left",
        ).pack(anchor="w", padx=SPACING["sm"], pady=2)

        tk.Label(
            detail_frame,
            text=f"Why: {reasoning}",
            font=FONTS["small"],
            bg=COLORS["surface"],
            fg=COLORS["text_secondary"],
            wraplength=400,
            justify="left",
        ).pack(anchor="w", padx=SPACING["sm"], pady=(2, SPACING["xs"]))
