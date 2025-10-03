"""Template cards for research patterns."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING

class TemplateCard(tk.Frame):
    """Large visual template card (280x180px)."""

    def __init__(self, parent, template_data: Dict[str, Any],
                 on_preview: Optional[Callable] = None):
        super().__init__(parent, width=280, height=180, bg='white',
                        highlightbackground=COLORS['border'], highlightthickness=1)
        self.template_data = template_data
        self.on_preview = on_preview
        self.selected = False
        self._build_ui()

    def _build_ui(self):
        """Build the template card UI."""
        self.pack_propagate(False)

        # Icon area
        icon_frame = tk.Frame(self, bg='white', height=60)
        icon_frame.pack(fill='x', pady=(SPACING['sm'], 0))

        icon = tk.Label(icon_frame, text=self.template_data.get('icon', '📄'),
                       font=('Segoe UI', 32), bg='white')
        icon.pack()

        # Title
        title = tk.Label(self, text=self.template_data.get('name', 'Template'),
                        font=FONTS['h3'], bg='white', fg=COLORS['text'])
        title.pack(pady=(0, SPACING['xs']))

        # Promise/description
        desc = tk.Label(self, text=self.template_data.get('promise', ''),
                       font=FONTS['small'], bg='white', fg=COLORS['text_secondary'],
                       wraplength=240)
        desc.pack(padx=SPACING['sm'])

        # Toggles area
        toggle_frame = tk.Frame(self, bg='white')
        toggle_frame.pack(fill='x', padx=SPACING['sm'], pady=SPACING['xs'])

        if 'toggles' in self.template_data:
            for toggle in self.template_data['toggles'][:2]:  # Max 2 toggles
                var = tk.BooleanVar(value=toggle.get('default', False))
                cb = tk.Checkbutton(toggle_frame, text=toggle['label'],
                                   font=FONTS['small'], bg='white',
                                   variable=var)
                cb.pack(side='left', padx=(0, SPACING['xs']))
                setattr(self, f"toggle_{toggle['key']}", var)

        # Preview button
        preview_btn = tk.Button(self, text='Preview →', font=FONTS['body'],
                              bg=COLORS['primary'], fg='white', relief='flat',
                              padx=12, pady=4, command=self._handle_preview)
        preview_btn.pack(pady=SPACING['xs'])

        # Hover effects
        self.bind('<Enter>', self._on_hover)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)

    def _handle_preview(self):
        """Handle preview button click."""
        if self.on_preview:
            config = self._build_config()
            self.on_preview(config)

    def _build_config(self) -> Dict[str, Any]:
        """Build configuration from template and toggles."""
        config = {
            'template': self.template_data['name'],
            'settings': {}
        }

        # Add toggle states
        if 'toggles' in self.template_data:
            for toggle in self.template_data['toggles']:
                key = toggle['key']
                if hasattr(self, f"toggle_{key}"):
                    var = getattr(self, f"toggle_{key}")
                    config['settings'][key] = var.get()

        # Add template-specific config
        if 'config' in self.template_data:
            config.update(self.template_data['config'])

        return config

    def _on_hover(self, event):
        """Mouse enter effect."""
        self.configure(highlightbackground=COLORS['primary'], highlightthickness=2)

    def _on_leave(self, event):
        """Mouse leave effect."""
        if not self.selected:
            self.configure(highlightbackground=COLORS['border'], highlightthickness=1)

    def _on_click(self, event):
        """Handle card selection."""
        self.selected = not self.selected
        if self.selected:
            self.configure(highlightbackground=COLORS['primary'], highlightthickness=2)
        else:
            self.configure(highlightbackground=COLORS['border'], highlightthickness=1)


class TemplateGrid(ttk.Frame):
    """Grid of template cards (3x2 layout)."""

    TEMPLATES = [
        {
            'name': 'Topic Overview',
            'icon': '🎯',
            'promise': 'Comprehensive research on any topic',
            'toggles': [
                {'key': 'citations', 'label': 'Include citations', 'default': True},
                {'key': 'summary', 'label': 'Auto-summary', 'default': True}
            ]
        },
        {
            'name': 'Fact Check',
            'icon': '✓',
            'promise': 'Verify claims with multiple sources',
            'toggles': [
                {'key': 'confidence', 'label': 'Show confidence', 'default': True}
            ]
        },
        {
            'name': 'Competitor Scan',
            'icon': '🔍',
            'promise': 'Analyze competitor strategies',
            'toggles': [
                {'key': 'swot', 'label': 'SWOT analysis', 'default': False}
            ]
        },
        {
            'name': 'Citation Harvest',
            'icon': '📚',
            'promise': 'Extract all citations and references',
            'toggles': [
                {'key': 'bibtex', 'label': 'BibTeX format', 'default': False}
            ]
        },
        {
            'name': 'Course Outline',
            'icon': '🎓',
            'promise': 'Structure educational content',
            'toggles': [
                {'key': 'exercises', 'label': 'Add exercises', 'default': True}
            ]
        },
        {
            'name': 'Custom',
            'icon': '⚙️',
            'promise': 'Create your own template',
            'toggles': []
        }
    ]

    def __init__(self, parent, on_template_preview: Optional[Callable] = None):
        super().__init__(parent)
        self.on_template_preview = on_template_preview
        self._build_grid()

    def _build_grid(self):
        """Build the 3x2 template grid."""
        for i, template in enumerate(self.TEMPLATES):
            row = i // 3
            col = i % 3

            card = TemplateCard(self, template, self.on_template_preview)
            card.grid(row=row, column=col, padx=SPACING['sm'], pady=SPACING['sm'])
