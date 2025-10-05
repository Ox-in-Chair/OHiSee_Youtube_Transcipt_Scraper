"""Empty state components with helpful guidance."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING


class EmptyState(tk.Frame):
    """Reusable empty state component with icon, message, and action."""

    def __init__(
        self,
        parent,
        icon: str,
        title: str,
        message: str,
        action_text: str = None,
        action_callback: Callable = None,
    ):
        super().__init__(parent, bg="white")
        self.icon = icon
        self.title = title
        self.message = message
        self.action_text = action_text
        self.action_callback = action_callback
        self._build_ui()

    def _build_ui(self):
        """Build the empty state UI."""
        # Center container
        container = tk.Frame(self, bg="white")
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Icon
        icon_label = tk.Label(
            container,
            text=self.icon,
            font=("Segoe UI", 64),
            bg="white",
            fg=COLORS["text_secondary"],
        )
        icon_label.pack(pady=SPACING["md"])

        # Title
        title_label = tk.Label(
            container, text=self.title, font=FONTS["h2"], bg="white", fg=COLORS["text"]
        )
        title_label.pack(pady=SPACING["xs"])

        # Message
        message_label = tk.Label(
            container,
            text=self.message,
            font=FONTS["body"],
            bg="white",
            fg=COLORS["text_secondary"],
            wraplength=400,
            justify="center",
        )
        message_label.pack(pady=SPACING["sm"])

        # Action button
        if self.action_text and self.action_callback:
            action_btn = tk.Button(
                container,
                text=self.action_text,
                font=FONTS["h3"],
                bg=COLORS["primary"],
                fg="white",
                relief="flat",
                padx=SPACING["lg"],
                pady=SPACING["sm"],
                command=self.action_callback,
                cursor="hand2",
            )
            action_btn.pack(pady=SPACING["md"])


class NoResultsState(EmptyState):
    """Empty state for no search results."""

    def __init__(self, parent, on_modify_search: Callable):
        super().__init__(
            parent,
            icon="🔍",
            title="No Results Found",
            message="We couldn't find any videos matching your search criteria. Try modifying your filters or search query.",
            action_text="Modify Search",
            action_callback=on_modify_search,
        )


class NoConfigState(EmptyState):
    """Empty state for missing configuration."""

    def __init__(self, parent, on_create_config: Callable):
        super().__init__(
            parent,
            icon="⚙️",
            title="No Configuration Set",
            message="Get started by creating a research configuration. Use templates for quick setup or build a custom query.",
            action_text="Create Configuration",
            action_callback=on_create_config,
        )


class NoTranscriptsState(EmptyState):
    """Empty state for no saved transcripts."""

    def __init__(self, parent, on_start_research: Callable):
        super().__init__(
            parent,
            icon="📄",
            title="No Transcripts Yet",
            message="You haven't saved any transcripts yet. Start a research project to extract video transcripts from YouTube.",
            action_text="Start Research",
            action_callback=on_start_research,
        )


class NoAPIKeyState(EmptyState):
    """Empty state for missing API key."""

    def __init__(self, parent, on_add_key: Callable):
        super().__init__(
            parent,
            icon="🔑",
            title="OpenAI API Key Required",
            message="To use AI-powered query optimization, add your OpenAI API key. You can skip this and use manual search instead.",
            action_text="Add API Key",
            action_callback=on_add_key,
        )


class LoadingState(tk.Frame):
    """Loading state with spinner and progress message."""

    def __init__(self, parent, message: str = "Loading..."):
        super().__init__(parent, bg="white")
        self.message = message
        self._build_ui()

    def _build_ui(self):
        """Build the loading state UI."""
        container = tk.Frame(self, bg="white")
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Spinner (animated in production)
        spinner_label = tk.Label(container, text="⏳", font=("Segoe UI", 64), bg="white")
        spinner_label.pack(pady=SPACING["md"])

        # Message
        self.message_label = tk.Label(
            container, text=self.message, font=FONTS["h3"], bg="white", fg=COLORS["text"]
        )
        self.message_label.pack()

    def update_message(self, message: str):
        """Update loading message."""
        self.message = message
        self.message_label.config(text=message)
