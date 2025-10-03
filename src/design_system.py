"""Professional design system with Poppins font and 8pt grid."""
from typing import Tuple, Dict, Any

# Typography - Poppins with Segoe UI fallback
FONTS: Dict[str, Tuple[str, int, str]] = {
    'h1': ('Poppins', 28, 'bold'),      # Major headings
    'h2': ('Poppins', 22, 'normal'),    # Section headings
    'h3': ('Poppins', 18, 'normal'),    # Subsections
    'body': ('Poppins', 14, 'normal'),  # Body text
    'meta': ('Segoe UI', 14, 'normal'), # Metadata
    'small': ('Segoe UI', 12, 'normal') # Small text
}

# High-contrast color palette (WCAG AA compliant)
COLORS: Dict[str, str] = {
    'bg': '#FFFFFF',           # White background
    'surface': '#F8F9FA',      # Light gray surface
    'text': '#1A1D23',         # Near-black text (contrast 16:1)
    'text_secondary': '#6B7280', # Gray text (contrast 4.5:1)
    'primary': '#2563EB',      # Professional blue
    'success': '#16A34A',      # Green for success
    'warning': '#F59E0B',      # Orange for warnings
    'error': '#DC2626',        # Red for errors
    'border': '#E5E7EB',       # Light border
    'hover': '#F3F4F6'         # Hover state
}

def grid(multiplier: int = 1) -> int:
    """8pt grid system helper."""
    return 8 * multiplier

# Component spacing presets
SPACING = {
    'xs': grid(1),   # 8px
    'sm': grid(2),   # 16px
    'md': grid(3),   # 24px
    'lg': grid(4),   # 32px
    'xl': grid(6)    # 48px
}
