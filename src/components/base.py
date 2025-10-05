"""Base UI component primitives for consistent styling.

Provides standardized widgets with built-in design system compliance:
- BaseButton: Modern flat button with hover states
- BaseCard: Container with rounded corners and optional border
- BaseEntry: Text input with focus states
- BaseLabel: Styled label with typography hierarchy
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, SPACING


class BaseButton(tk.Button):
    """Modern button with standardized styling and hover effects.

    Features:
    - Flat design with 4px corner radius
    - Hover state transitions (lavender_pink)
    - Consistent padding (12×16px)
    - Primary/secondary/danger variants
    """

    def __init__(
        self,
        parent,
        text: str = "",
        command: Optional[Callable] = None,
        variant: str = "primary",  # primary, secondary, danger, ghost
        **kwargs
    ):
        # Style configuration by variant
        styles = {
            "primary": {
                "bg": COLORS["primary"],
                "fg": "white",
                "activebackground": COLORS["hover"],
                "activeforeground": COLORS["text"],
            },
            "secondary": {
                "bg": COLORS["surface"],
                "fg": COLORS["text"],
                "activebackground": COLORS["hover"],
                "activeforeground": COLORS["text"],
            },
            "danger": {
                "bg": COLORS["error"],
                "fg": "white",
                "activebackground": "#B91C1C",
                "activeforeground": "white",
            },
            "ghost": {
                "bg": "white",
                "fg": COLORS["text"],
                "activebackground": COLORS["surface"],
                "activeforeground": COLORS["text"],
                "highlightbackground": COLORS["border"],
                "highlightthickness": 1,
            },
        }

        style = styles.get(variant, styles["primary"])

        super().__init__(
            parent,
            text=text,
            command=command,
            font=FONTS["body"],
            relief="flat",
            padx=SPACING["md"],
            pady=SPACING["sm"],
            cursor="hand2",
            **{**style, **kwargs}
        )

        # Hover effects
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        self.default_bg = style["bg"]
        self.variant = variant

    def _on_hover(self, event):
        """Apply hover state."""
        if self.variant == "primary":
            self.configure(bg=COLORS["medium_slate_blue"])  # Slight variation
        elif self.variant == "ghost":
            self.configure(bg=COLORS["hover"], highlightbackground=COLORS["secondary"])
        else:
            self.configure(bg=COLORS["hover"])

    def _on_leave(self, event):
        """Remove hover state."""
        self.configure(bg=self.default_bg)
        if self.variant == "ghost":
            self.configure(highlightbackground=COLORS["border"])


class BaseCard(tk.Frame):
    """Container with rounded appearance and optional border.

    Features:
    - 4px visual corner radius (via highlight)
    - Optional elevated shadow (via border)
    - Consistent padding (SPACING['md'])
    - Hover state support
    """

    def __init__(
        self,
        parent,
        elevated: bool = False,
        hoverable: bool = False,
        **kwargs
    ):
        super().__init__(
            parent,
            bg=kwargs.pop("bg", "white"),
            highlightbackground=COLORS["border"],
            highlightthickness=1 if not elevated else 2,
            **kwargs
        )

        self.elevated = elevated
        self.hoverable = hoverable

        if hoverable:
            self.bind("<Enter>", self._on_hover)
            self.bind("<Leave>", self._on_leave)

    def _on_hover(self, event):
        """Visual feedback on hover."""
        self.configure(
            highlightbackground=COLORS["secondary"],  # lavender_pink
            highlightthickness=2
        )

    def _on_leave(self, event):
        """Remove hover state."""
        self.configure(
            highlightbackground=COLORS["border"],
            highlightthickness=1 if not self.elevated else 2
        )


class BaseEntry(tk.Entry):
    """Text input with focus states and validation support.

    Features:
    - Focus ring (lavender_pink)
    - Consistent padding and font
    - Optional placeholder text
    - Validation state colors
    """

    def __init__(
        self,
        parent,
        placeholder: str = "",
        validate_fn: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(
            parent,
            font=FONTS["body"],
            relief="solid",
            borderwidth=1,
            bg="white",
            fg=COLORS["text"],
            insertbackground=COLORS["primary"],
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["secondary"],  # lavender_pink focus
            highlightthickness=1,
            **kwargs
        )

        self.placeholder = placeholder
        self.validate_fn = validate_fn
        self.is_valid = True

        # Placeholder support
        if placeholder:
            self.insert(0, placeholder)
            self.configure(fg=COLORS["text_secondary"])
            self.bind("<FocusIn>", self._clear_placeholder)
            self.bind("<FocusOut>", self._restore_placeholder)

        # Validation on change
        if validate_fn:
            self.bind("<KeyRelease>", self._validate)

        # Focus states
        self.bind("<FocusIn>", self._on_focus)
        self.bind("<FocusOut>", self._on_blur)

    def _clear_placeholder(self, event):
        """Remove placeholder on focus."""
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.configure(fg=COLORS["text"])

    def _restore_placeholder(self, event):
        """Restore placeholder if empty."""
        if not self.get():
            self.insert(0, self.placeholder)
            self.configure(fg=COLORS["text_secondary"])

    def _validate(self, event):
        """Run validation function."""
        if self.validate_fn:
            value = self.get()
            if value != self.placeholder:
                self.is_valid = self.validate_fn(value)
                self.configure(
                    highlightbackground=COLORS["border"] if self.is_valid else COLORS["error"],
                    highlightcolor=COLORS["secondary"] if self.is_valid else COLORS["error"]
                )

    def _on_focus(self, event):
        """Enhanced focus ring."""
        if self.is_valid:
            self.configure(highlightthickness=2)

    def _on_blur(self, event):
        """Remove focus ring."""
        self.configure(highlightthickness=1)


class BaseLabel(tk.Label):
    """Styled label with typography hierarchy.

    Simplifies creation of labels that follow design system.
    """

    def __init__(
        self,
        parent,
        text: str = "",
        level: str = "body",  # display, h1, h2, h3, body, caption
        color: str = "text",  # text, text_secondary, primary, etc.
        **kwargs
    ):
        super().__init__(
            parent,
            text=text,
            font=FONTS.get(level, FONTS["body"]),
            fg=COLORS.get(color, COLORS["text"]),
            bg=kwargs.pop("bg", "white"),
            **kwargs
        )


class BaseCheckbox(tk.Checkbutton):
    """Styled checkbox with consistent appearance.

    Features:
    - Primary color accent
    - Proper spacing
    - Hover states
    """

    def __init__(
        self,
        parent,
        text: str = "",
        variable: Optional[tk.BooleanVar] = None,
        **kwargs
    ):
        if variable is None:
            variable = tk.BooleanVar()

        super().__init__(
            parent,
            text=text,
            variable=variable,
            font=FONTS["body"],
            bg=kwargs.pop("bg", "white"),
            fg=COLORS["text"],
            activebackground=COLORS["hover"],
            activeforeground=COLORS["text"],
            selectcolor="white",
            cursor="hand2",
            **kwargs
        )

        self.variable = variable


class BaseSeparator(tk.Frame):
    """Visual separator/divider line for section boundaries.

    Features:
    - 1px or 2px horizontal line
    - Uses border color from design system
    - Automatic horizontal fill
    - Optional vertical spacing
    """

    def __init__(
        self,
        parent,
        thickness: int = 1,  # 1px or 2px
        color: str = None,  # Defaults to COLORS["border"]
        pady: int = None,  # Vertical spacing (defaults to SPACING["md"])
        **kwargs
    ):
        if color is None:
            color = COLORS["border"]
        if pady is None:
            pady = SPACING["md"]

        super().__init__(
            parent,
            bg=color,
            height=thickness,
            **kwargs
        )

        # Pack with vertical spacing
        self.pack(fill="x", pady=pady)


# Export all base components
__all__ = [
    "BaseButton",
    "BaseCard",
    "BaseEntry",
    "BaseLabel",
    "BaseCheckbox",
    "BaseSeparator",
]
