"""Modern research-grade design system with Inter typography and 8pt grid.

Implements intellectual luxury aesthetic: minimalist, clarity-focused, research-driven.
Color palette optimized for cognitive clarity and WCAG AA compliance.
Typography system based on Inter font with 1.4-1.6 line-height ratios.
"""

from typing import Tuple, Dict, Any

# Modern typography system - Inter with system fallback
# Optimized for research-grade clarity and cognitive efficiency
FONTS: Dict[str, Tuple[str, int, str]] = {
    "display": ("Inter", 24, "bold"),  # Display text, major headings (line-height: 1.4)
    "h1": ("Inter", 20, "bold"),  # Primary headings (line-height: 1.5)
    "h2": ("Inter", 16, "normal"),  # Section headings (line-height: 1.5)
    "h3": ("Inter", 14, "normal"),  # Subsections (line-height: 1.5)
    "body": ("Inter", 12, "normal"),  # Body text (line-height: 1.6)
    "caption": ("Inter", 10, "normal"),  # Small text, captions (line-height: 1.6)
    "meta": ("Segoe UI", 12, "normal"),  # Metadata, system info

    # Legacy aliases for backward compatibility
    "small": ("Inter", 10, "normal"),  # Alias for caption
}

# Modern research-grade color palette (WCAG AA compliant)
# Inspired by intellectual luxury - minimalist, clarity-focused
COLORS: Dict[str, str] = {
    # Base palette (new modern system)
    "rose_taupe": "#7A5C61",  # Divider / neutral, inactive states
    "lavender_pink": "#F7ACCF",  # Secondary accent, hover states, active borders
    "alice_blue": "#E8F0FF",  # Background surface, wizard steps, modals
    "medium_slate_blue": "#6874E8",  # Primary accent, buttons, CTAs, progress
    "russian_violet": "#392759",  # Text primary, headings, configuration preview

    # Functional mappings (for component compatibility)
    "bg": "#FFFFFF",  # White background (unchanged)
    "surface": "#E8F0FF",  # alice_blue - base panels
    "text": "#392759",  # russian_violet - primary text
    "text_secondary": "#7A5C61",  # rose_taupe - secondary text
    "primary": "#6874E8",  # medium_slate_blue - interactive elements
    "secondary": "#F7ACCF",  # lavender_pink - accents
    "success": "#16A34A",  # Green for success (unchanged - proven UX)
    "warning": "#F59E0B",  # Orange for warnings (unchanged - proven UX)
    "error": "#DC2626",  # Red for errors (unchanged - proven UX)
    "border": "#7A5C61",  # rose_taupe - borders, inactive states
    "hover": "#F7ACCF",  # lavender_pink - hover transitions
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
