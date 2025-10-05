"""Smart prompt composer with chips that expand inline."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable, Optional, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING


class PromptComposer(ttk.Frame):
    """Chips expand inline, collapse to readable sentence."""

    CHIPS = [
        {
            "id": "topic",
            "prompt": "What are you researching?",
            "type": "text",
            "required": True,
            "placeholder": "e.g., BRCGS automation",
        },
        {
            "id": "audience",
            "prompt": "Who is this for?",
            "type": "text",
            "required": False,
            "placeholder": "e.g., food manufacturers",
        },
        {
            "id": "time_window",
            "prompt": "When published?",
            "type": "select",
            "options": ["Last week", "Last month", "Last 90 days", "Last year", "Any time"],
        },
        {
            "id": "quality_bar",
            "prompt": "How deep?",
            "type": "select",
            "options": ["Quick scan (5 videos)", "Balanced (15 videos)", "Deep dive (50 videos)"],
        },
        {
            "id": "sources",
            "prompt": "What kind of sources?",
            "type": "multi",
            "options": ["Tutorials", "Reviews", "Case studies", "Interviews", "Documentation"],
        },
        {
            "id": "output",
            "prompt": "What to extract?",
            "type": "multi",
            "options": [
                "Key concepts",
                "Implementation steps",
                "Best practices",
                "Common mistakes",
                "Tool recommendations",
            ],
        },
    ]

    def __init__(self, parent, on_update: Optional[Callable] = None):
        super().__init__(parent)
        self.on_update = on_update
        self.chip_values = {}
        self.expanded_chip = None
        self._build_ui()

    def _build_ui(self):
        """Build the prompt composer UI."""
        # Title
        title = tk.Label(
            self,
            text="Research Query Builder",
            font=FONTS["h2"],
            bg=COLORS["bg"],
            fg=COLORS["text"],
        )
        title.pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], SPACING["xs"]))

        # Container for collapsed/expanded view
        self.content_frame = tk.Frame(self, bg=COLORS["bg"])
        self.content_frame.pack(fill="both", expand=True, padx=SPACING["md"])

        self._render_collapsed()

    def _render_collapsed(self):
        """Show readable English sentence with clickable phrases."""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Build readable sentence
        sentence = self._build_readable_sentence()

        # Sentence display
        sentence_frame = tk.Frame(self.content_frame, bg=COLORS["surface"], bd=1, relief="solid")
        sentence_frame.pack(fill="x", pady=SPACING["sm"])

        sentence_label = tk.Label(
            sentence_frame,
            text=sentence,
            font=FONTS["body"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
            wraplength=600,
            justify="left",
        )
        sentence_label.pack(padx=SPACING["md"], pady=SPACING["md"])

        # Chip buttons grid
        chips_frame = tk.Frame(self.content_frame, bg=COLORS["bg"])
        chips_frame.pack(fill="x", pady=SPACING["sm"])

        for i, chip in enumerate(self.CHIPS):
            chip_btn = self._create_chip_button(chips_frame, chip)
            row = i // 2
            col = i % 2
            chip_btn.grid(row=row, column=col, padx=SPACING["xs"], pady=SPACING["xs"], sticky="ew")

        chips_frame.columnconfigure(0, weight=1)
        chips_frame.columnconfigure(1, weight=1)

    def _create_chip_button(self, parent, chip: Dict[str, Any]) -> tk.Button:
        """Create clickable chip button."""
        value = self.chip_values.get(chip["id"], None)

        if value:
            if isinstance(value, list):
                display = f"{chip['prompt']}: {', '.join(value)}"
            else:
                display = f"{chip['prompt']}: {value}"
            bg_color = COLORS["primary"]
            fg_color = "white"
        else:
            display = f"+ {chip['prompt']}"
            bg_color = COLORS["surface"]
            fg_color = COLORS["text"]

        btn = tk.Button(
            parent,
            text=display,
            font=FONTS["body"],
            bg=bg_color,
            fg=fg_color,
            relief="flat",
            padx=SPACING["sm"],
            pady=SPACING["xs"],
            command=lambda: self._expand_chip(chip["id"]),
        )

        return btn

    def _build_readable_sentence(self) -> str:
        """Construct English sentence from chip values."""
        topic = self.chip_values.get("topic", "[topic]")
        audience = self.chip_values.get("audience", "[audience]")
        time = self.chip_values.get("time_window", "any time")
        quality = self.chip_values.get("quality_bar", "balanced depth")
        sources = self.chip_values.get("sources", [])
        output_goals = self.chip_values.get("output", [])

        sources_str = ", ".join(sources) if sources else "various sources"
        output_str = ", ".join(output_goals) if output_goals else "general insights"

        return f"Research {topic} for {audience} from {time} with {quality}, focusing on {sources_str} to extract {output_str}."

    def _expand_chip(self, chip_id: str):
        """Show inline editor for this chip."""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        chip = next(c for c in self.CHIPS if c["id"] == chip_id)
        self.expanded_chip = chip_id

        # Header
        header = tk.Label(
            self.content_frame,
            text=chip["prompt"],
            font=FONTS["h3"],
            bg=COLORS["bg"],
            fg=COLORS["text"],
        )
        header.pack(anchor="w", pady=(SPACING["sm"], SPACING["xs"]))

        # Input based on type
        if chip["type"] == "text":
            self._render_text_input(chip)
        elif chip["type"] == "select":
            self._render_select_input(chip)
        elif chip["type"] == "multi":
            self._render_multi_input(chip)

        # Actions
        actions_frame = tk.Frame(self.content_frame, bg=COLORS["bg"])
        actions_frame.pack(pady=SPACING["md"])

        tk.Button(
            actions_frame,
            text="Done",
            font=FONTS["body"],
            bg=COLORS["primary"],
            fg="white",
            relief="flat",
            padx=SPACING["md"],
            pady=SPACING["xs"],
            command=self._collapse_chip,
        ).pack(side="left", padx=SPACING["xs"])

        tk.Button(
            actions_frame,
            text="Clear",
            font=FONTS["body"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
            relief="flat",
            padx=SPACING["md"],
            pady=SPACING["xs"],
            command=lambda: self._clear_chip(chip_id),
        ).pack(side="left")

    def _render_text_input(self, chip: Dict[str, Any]):
        """Render text entry field."""
        entry = tk.Entry(
            self.content_frame,
            font=FONTS["body"],
            bg="white",
            fg=COLORS["text"],
            relief="solid",
            bd=1,
        )
        entry.pack(fill="x", pady=SPACING["xs"])

        current_value = self.chip_values.get(chip["id"], "")
        entry.insert(0, current_value)

        if "placeholder" in chip and not current_value:
            entry.insert(0, chip["placeholder"])
            entry.config(fg=COLORS["text_secondary"])

        entry.focus()

        # Store reference
        setattr(self, f"input_{chip['id']}", entry)

        # Save on Enter
        entry.bind("<Return>", lambda e: self._collapse_chip())

    def _render_select_input(self, chip: Dict[str, Any]):
        """Render dropdown select."""
        var = tk.StringVar(value=self.chip_values.get(chip["id"], chip["options"][0]))

        for option in chip["options"]:
            rb = tk.Radiobutton(
                self.content_frame,
                text=option,
                variable=var,
                value=option,
                font=FONTS["body"],
                bg=COLORS["bg"],
                fg=COLORS["text"],
            )
            rb.pack(anchor="w", pady=2)

        setattr(self, f"input_{chip['id']}", var)

    def _render_multi_input(self, chip: Dict[str, Any]):
        """Render multi-select checkboxes."""
        current_values = self.chip_values.get(chip["id"], [])
        vars_dict = {}

        for option in chip["options"]:
            var = tk.BooleanVar(value=option in current_values)
            vars_dict[option] = var

            cb = tk.Checkbutton(
                self.content_frame,
                text=option,
                variable=var,
                font=FONTS["body"],
                bg=COLORS["bg"],
                fg=COLORS["text"],
            )
            cb.pack(anchor="w", pady=2)

        setattr(self, f"input_{chip['id']}", vars_dict)

    def _collapse_chip(self):
        """Save current input and return to collapsed view."""
        if not self.expanded_chip:
            return

        chip = next(c for c in self.CHIPS if c["id"] == self.expanded_chip)
        input_widget = getattr(self, f"input_{chip['id']}", None)

        if chip["type"] == "text" and input_widget:
            value = input_widget.get()
            if value and value != chip.get("placeholder", ""):
                self.chip_values[chip["id"]] = value
        elif chip["type"] == "select" and input_widget:
            self.chip_values[chip["id"]] = input_widget.get()
        elif chip["type"] == "multi" and input_widget:
            selected = [k for k, v in input_widget.items() if v.get()]
            if selected:
                self.chip_values[chip["id"]] = selected

        self.expanded_chip = None
        self._render_collapsed()

        # Notify parent of update
        if self.on_update:
            self.on_update(self.chip_values)

    def _clear_chip(self, chip_id: str):
        """Clear value for this chip."""
        if chip_id in self.chip_values:
            del self.chip_values[chip_id]

        self.expanded_chip = None
        self._render_collapsed()

        if self.on_update:
            self.on_update(self.chip_values)

    def get_values(self) -> Dict[str, Any]:
        """Get current chip values."""
        return self.chip_values.copy()

    def set_values(self, values: Dict[str, Any]):
        """Set chip values programmatically."""
        self.chip_values = values.copy()
        self._render_collapsed()

        if self.on_update:
            self.on_update(self.chip_values)
