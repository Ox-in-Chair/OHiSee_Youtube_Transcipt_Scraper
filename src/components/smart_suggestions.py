"""Smart suggestions based on learning patterns and context."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING


class SmartSuggestions:
    """Generates context-aware suggestions for research."""

    def __init__(self, learning_loop=None):
        self.learning_loop = learning_loop

    def get_query_suggestions(self, partial_query: str) -> List[Dict[str, str]]:
        """Generate query suggestions based on input."""
        suggestions = []

        # Suggest query improvements
        if len(partial_query) < 5:
            suggestions.append(
                {"text": "Try adding more specific keywords", "type": "tip", "action": None}
            )
        elif not any(op in partial_query for op in ['"', "OR", "-"]):
            suggestions.append(
                {"text": 'Use "exact phrases" for precise matches', "type": "tip", "action": None}
            )

        # Suggest related topics (based on patterns)
        if self.learning_loop:
            patterns = self.learning_loop.detect_patterns()
            if patterns.get("total_feedback", 0) > 0:
                suggestions.append(
                    {
                        "text": "Apply your preferred filters",
                        "type": "filter",
                        "action": "apply_learned_filters",
                    }
                )

        return suggestions

    def get_filter_suggestions(self, current_filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest filter improvements."""
        suggestions = []

        # No date filter
        if not current_filters.get("upload_date"):
            suggestions.append(
                {
                    "filter": "upload_date",
                    "value": "Last 30 days",
                    "reason": "Recent videos often have better quality",
                }
            )

        # No sort specified
        if not current_filters.get("sort_by"):
            suggestions.append(
                {
                    "filter": "sort_by",
                    "value": "rating",
                    "reason": "Highly-rated videos are usually more helpful",
                }
            )

        # Use learning patterns
        if self.learning_loop:
            optimized = self.learning_loop.get_optimized_filters()
            for key, value in optimized.items():
                if current_filters.get(key) != value:
                    suggestions.append(
                        {"filter": key, "value": value, "reason": "Based on your past preferences"}
                    )

        return suggestions

    def get_template_suggestions(self, query: str) -> List[str]:
        """Suggest relevant templates based on query."""
        query_lower = query.lower()

        # Keyword mapping to templates
        template_keywords = {
            "tutorial": ["Tutorial Deep Dive", "Implementation Guide"],
            "review": ["Product Review Analysis"],
            "comparison": ["Product Review Analysis"],
            "guide": ["Tutorial Deep Dive", "Implementation Guide"],
            "research": ["Industry Research", "Academic Research"],
            "trend": ["Industry Research", "Trend Analysis"],
        }

        suggestions = []
        for keyword, templates in template_keywords.items():
            if keyword in query_lower:
                suggestions.extend(templates)

        return list(set(suggestions))  # Remove duplicates


class SuggestionPanel(tk.Frame):
    """UI panel showing smart suggestions."""

    def __init__(self, parent, suggestions_engine: SmartSuggestions):
        super().__init__(parent, bg=COLORS["surface"])
        self.suggestions_engine = suggestions_engine
        self.suggestions = []
        self._build_ui()

    def _build_ui(self):
        """Build suggestions UI."""
        # Header
        header = tk.Frame(self, bg=COLORS["surface"])
        header.pack(fill="x", pady=SPACING["xs"], padx=SPACING["sm"])

        tk.Label(header, text="💡", font=("Segoe UI", 16), bg=COLORS["surface"]).pack(
            side="left", padx=SPACING["xs"]
        )

        tk.Label(
            header,
            text="Smart Suggestions",
            font=FONTS["body"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).pack(side="left")

        # Suggestions list
        self.suggestions_frame = tk.Frame(self, bg=COLORS["surface"])
        self.suggestions_frame.pack(
            fill="both", expand=True, padx=SPACING["sm"], pady=SPACING["xs"]
        )

    def update_suggestions(self, query: str = "", filters: Dict[str, Any] = None):
        """Update displayed suggestions."""
        # Clear existing
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()

        # Get new suggestions
        query_suggestions = self.suggestions_engine.get_query_suggestions(query)
        filter_suggestions = self.suggestions_engine.get_filter_suggestions(filters or {})

        # Display query suggestions
        for sugg in query_suggestions[:3]:  # Limit to 3
            self._render_suggestion(sugg["text"], sugg["type"])

        # Display filter suggestions
        for sugg in filter_suggestions[:2]:  # Limit to 2
            text = f"Try {sugg['filter']}={sugg['value']}: {sugg['reason']}"
            self._render_suggestion(text, "filter")

    def _render_suggestion(self, text: str, suggestion_type: str):
        """Render a single suggestion."""
        sugg_frame = tk.Frame(self.suggestions_frame, bg="white", bd=1, relief="solid")
        sugg_frame.pack(fill="x", pady=2)

        # Type icon
        icons = {"tip": "💡", "filter": "🎯", "template": "📋"}
        icon = icons.get(suggestion_type, "•")

        tk.Label(sugg_frame, text=icon, font=FONTS["body"], bg="white").pack(
            side="left", padx=SPACING["xs"]
        )

        # Suggestion text
        tk.Label(
            sugg_frame,
            text=text,
            font=FONTS["small"],
            bg="white",
            fg=COLORS["text"],
            wraplength=300,
            justify="left",
        ).pack(side="left", padx=SPACING["xs"], pady=4, fill="x", expand=True)
