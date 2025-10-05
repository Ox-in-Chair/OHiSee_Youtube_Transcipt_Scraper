"""Learning loop that improves with user feedback."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List
import json
import os
from datetime import datetime
from pathlib import Path
from collections import Counter
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING


class LearningLoop:
    """Tracks user feedback and detects patterns to improve recommendations."""

    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(Path.home(), ".youtube_scraper_learning")
        os.makedirs(self.data_dir, exist_ok=True)
        self.feedback_file = os.path.join(self.data_dir, "feedback.json")
        self._load_feedback()

    def _load_feedback(self):
        """Load feedback history from disk."""
        if os.path.exists(self.feedback_file):
            with open(self.feedback_file, "r", encoding="utf-8") as f:
                self.feedback_history = json.load(f)
        else:
            self.feedback_history = []

    def _save_feedback(self):
        """Save feedback history to disk."""
        with open(self.feedback_file, "w", encoding="utf-8") as f:
            json.dump(self.feedback_history, f, indent=2)

    def record_feedback(self, video_id: str, rating: str, query: str, filters: Dict[str, Any]):
        """Record user feedback on a result."""
        entry = {
            "video_id": video_id,
            "rating": rating,  # 'positive' or 'negative'
            "query": query,
            "filters": filters,
            "timestamp": datetime.now().isoformat(),
        }
        self.feedback_history.append(entry)
        self._save_feedback()

    def detect_patterns(self) -> Dict[str, Any]:
        """Detect patterns in user feedback."""
        if not self.feedback_history:
            return {"patterns": [], "insights": "Not enough feedback yet"}

        # Count positive vs negative
        ratings = [f["rating"] for f in self.feedback_history]
        rating_counts = Counter(ratings)

        # Find preferred filters
        positive_filters = [
            f["filters"] for f in self.feedback_history if f["rating"] == "positive"
        ]

        # Detect most common filter combinations
        filter_patterns = {}
        for filters in positive_filters:
            for key, value in filters.items():
                if key not in filter_patterns:
                    filter_patterns[key] = Counter()
                filter_patterns[key][str(value)] += 1

        # Generate insights
        insights = []
        for key, value_counts in filter_patterns.items():
            most_common = value_counts.most_common(1)
            if most_common:
                value, count = most_common[0]
                if count >= 3:  # Pattern threshold
                    insights.append(f"You often prefer {key}={value}")

        return {
            "total_feedback": len(self.feedback_history),
            "positive": rating_counts.get("positive", 0),
            "negative": rating_counts.get("negative", 0),
            "patterns": filter_patterns,
            "insights": insights if insights else ["Keep providing feedback to see patterns"],
        }

    def get_optimized_filters(self) -> Dict[str, Any]:
        """Get filter recommendations based on learned patterns."""
        patterns = self.detect_patterns()
        optimized = {}

        for key, value_counts in patterns.get("patterns", {}).items():
            most_common = value_counts.most_common(1)
            if most_common:
                value, count = most_common[0]
                if count >= 3:
                    # Convert string back to original type
                    try:
                        optimized[key] = json.loads(value)
                    except:
                        optimized[key] = value

        return optimized


class LearningInsightsPanel(tk.Frame):
    """UI panel showing learning insights."""

    def __init__(self, parent, learning_loop: LearningLoop):
        super().__init__(parent, bg="white")
        self.learning_loop = learning_loop
        self._build_ui()

    def _build_ui(self):
        """Build learning insights UI."""
        # Header
        tk.Label(
            self, text="Learning Insights", font=FONTS["h2"], bg="white", fg=COLORS["text"]
        ).pack(pady=SPACING["md"], anchor="w", padx=SPACING["md"])

        # Get patterns
        patterns = self.learning_loop.detect_patterns()

        # Stats card
        stats_frame = tk.Frame(self, bg=COLORS["surface"], bd=1, relief="solid")
        stats_frame.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])

        tk.Label(stats_frame, text="📊", font=("Segoe UI", 20), bg=COLORS["surface"]).pack(
            side="left", padx=SPACING["sm"]
        )

        info_frame = tk.Frame(stats_frame, bg=COLORS["surface"])
        info_frame.pack(side="left", fill="both", expand=True, pady=SPACING["sm"])

        tk.Label(
            info_frame,
            text=f"{patterns.get('total_feedback', 0)} feedback entries",
            font=FONTS["body"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).pack(anchor="w")

        tk.Label(
            info_frame,
            text=f"👍 {patterns.get('positive', 0)} positive, 👎 {patterns.get('negative', 0)} negative",
            font=FONTS["small"],
            bg=COLORS["surface"],
            fg=COLORS["text_secondary"],
        ).pack(anchor="w")

        # Insights
        insights_frame = tk.Frame(self, bg="white")
        insights_frame.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])

        tk.Label(
            insights_frame,
            text="Detected Patterns:",
            font=FONTS["h3"],
            bg="white",
            fg=COLORS["text"],
        ).pack(anchor="w", pady=SPACING["xs"])

        for insight in patterns.get("insights", []):
            insight_label = tk.Label(
                insights_frame,
                text=f"• {insight}",
                font=FONTS["body"],
                bg="white",
                fg=COLORS["text_secondary"],
                wraplength=400,
                justify="left",
            )
            insight_label.pack(anchor="w", pady=2)


class FeedbackWidget(tk.Frame):
    """Inline feedback widget for results."""

    def __init__(self, parent, video_id: str, on_feedback: callable):
        super().__init__(parent, bg="white")
        self.video_id = video_id
        self.on_feedback = on_feedback
        self._build_ui()

    def _build_ui(self):
        """Build feedback UI."""
        tk.Label(
            self,
            text="Was this helpful?",
            font=FONTS["small"],
            bg="white",
            fg=COLORS["text_secondary"],
        ).pack(side="left", padx=SPACING["xs"])

        # Thumbs up
        up_btn = tk.Button(
            self,
            text="👍",
            font=FONTS["body"],
            bg="white",
            fg=COLORS["success"],
            relief="flat",
            cursor="hand2",
            command=lambda: self._handle_feedback("positive"),
        )
        up_btn.pack(side="left", padx=2)

        # Thumbs down
        down_btn = tk.Button(
            self,
            text="👎",
            font=FONTS["body"],
            bg="white",
            fg=COLORS["error"],
            relief="flat",
            cursor="hand2",
            command=lambda: self._handle_feedback("negative"),
        )
        down_btn.pack(side="left", padx=2)

    def _handle_feedback(self, rating: str):
        """Handle feedback submission."""
        self.on_feedback(self.video_id, rating)
        # Visual confirmation
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state="disabled")
