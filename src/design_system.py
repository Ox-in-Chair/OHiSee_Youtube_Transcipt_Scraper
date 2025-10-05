"""Modern research-grade design system with Inter typography and 8pt grid.

Implements intellectual luxury aesthetic: minimalist, clarity-focused, research-driven.
Color palette optimized for cognitive clarity and WCAG AA compliance.
Typography system based on Inter font with 1.4-1.6 line-height ratios.
"""

from typing import Tuple, Dict, Any

# Research-grade typography system - Inter with system fallback
# Optimized for intellectual clarity with 1.6 line-height for legibility
FONTS: Dict[str, Tuple[str, int, str]] = {
    "h1": ("Inter", 20, "bold"),  # H1 = 20pt Bold (main headings)
    "h2": ("Inter", 16, "bold"),  # H2 = 16pt Semibold (section headers) - tkinter only supports bold/normal
    "body": ("Inter", 13, "normal"),  # Body = 13pt Regular (line-height: 1.6)
    "caption": ("Inter", 11, "normal"),  # Caption/meta text
    "code": ("Consolas", 11, "normal"),  # Code/YAML display

    # Legacy aliases for backward compatibility
    "display": ("Inter", 20, "bold"),  # Alias for h1
    "h3": ("Inter", 14, "normal"),  # Subsections
    "meta": ("Inter", 11, "normal"),  # Alias for caption
    "small": ("Inter", 11, "normal"),  # Alias for caption
}

# Research-grade color palette (WCAG AA 4.5:1 minimum contrast)
# Neutral, calm whitespace with intentional color choices
COLORS: Dict[str, str] = {
    # Core neutral palette
    "background": "#F8FAFC",  # Background - soft white
    "surface": "#FFFFFF",  # Surface - pure white cards/panels
    "primary": "#1E40AF",  # Primary CTA - research blue
    "secondary": "#475569",  # Secondary elements - slate gray
    "accent": "#16A34A",  # Accent/CTA - confident green
    "border": "#E2E8F0",  # Border - subtle gray
    "text": "#0F172A",  # Text Primary - near black
    "text_secondary": "#475569",  # Text Secondary - slate

    # Functional states (proven UX colors)
    "success": "#16A34A",  # Success green
    "warning": "#F59E0B",  # Warning orange
    "error": "#DC2626",  # Error red
    "hover": "#1E40AF",  # Hover state (primary)

    # Legacy aliases for backward compatibility
    "bg": "#FFFFFF",
    "rose_taupe": "#475569",  # Now maps to secondary
    "lavender_pink": "#1E40AF",  # Now maps to primary
    "alice_blue": "#F8FAFC",  # Now maps to background
    "medium_slate_blue": "#1E40AF",  # Now maps to primary
    "russian_violet": "#0F172A",  # Now maps to text
}


def grid(multiplier: int = 1) -> int:
    """8pt grid system helper."""
    return 8 * multiplier


# Component spacing presets
SPACING = {
    "xs": grid(1),  # 8px
    "sm": grid(2),  # 16px
    "md": grid(3),  # 24px
    "lg": grid(4),  # 32px
    "xl": grid(6),  # 48px
}

# Animation constants (150ms ease-in-out as per UX spec)
ANIMATION = {
    "duration_fast": 150,  # 150ms for micro-interactions
    "duration_default": 200,  # 200ms for standard transitions
    "duration_slow": 300,  # 300ms for larger state changes
    "easing": "ease-in-out",  # Standard easing function
}


def animate_fade_in(widget, duration: int = 150, steps: int = 10):
    """Fade in animation for widget appearance.

    Args:
        widget: Tkinter widget to animate
        duration: Total duration in milliseconds (default 150ms)
        steps: Number of animation steps
    """
    step_duration = duration // steps
    alpha_step = 1.0 / steps
    current_alpha = 0.0

    def fade_step():
        nonlocal current_alpha
        if current_alpha < 1.0:
            current_alpha += alpha_step
            # Note: Tkinter doesn't support direct alpha on widgets
            # This is a placeholder - actual implementation would use
            # alternative methods like geometry changes or color transitions
            widget.after(step_duration, fade_step)

    fade_step()


def animate_slide_in(widget, direction: str = "left", duration: int = 150):
    """Slide in animation for widget appearance.

    Args:
        widget: Tkinter widget to animate
        direction: Direction to slide from ("left", "right", "top", "bottom")
        duration: Total duration in milliseconds (default 150ms)
    """
    # Placeholder for slide animation
    # Full implementation would manipulate widget geometry
    pass


def animate_button_hover(button, enter: bool = True):
    """Animate button on hover (background color transition).

    Args:
        button: Tkinter button widget
        enter: True for mouse enter, False for mouse leave
    """
    if enter:
        button.config(bg=COLORS["hover"])
    else:
        button.config(bg=COLORS["primary"])


def animate_step_transition(from_widget, to_widget, duration: int = 150):
    """Animate transition between wizard steps.

    Args:
        from_widget: Widget to fade out
        to_widget: Widget to fade in
        duration: Transition duration in milliseconds
    """
    # Fade out current, fade in next
    # Simplified implementation - pack_forget/pack with delay
    if from_widget:
        from_widget.pack_forget()

    if to_widget:
        to_widget.after(duration // 2, lambda: to_widget.pack(fill="both", expand=True))
