"""Review sheet showing complete configuration before execution."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING

class ReviewSheet(ttk.Frame):
    """Comprehensive pre-run checklist and configuration summary."""

    def __init__(self, parent, on_run: Optional[Callable] = None):
        super().__init__(parent)
        self.on_run = on_run
        self.config_data = {}
        self.validation_status = {}
        self._build_ui()

    def _build_ui(self):
        """Build the review sheet UI."""
        # Title
        title = tk.Label(self, text='Review Configuration',
                        font=FONTS['h2'], bg=COLORS['bg'], fg=COLORS['text'])
        title.pack(anchor='w', padx=SPACING['md'], pady=(SPACING['md'], SPACING['xs']))

        # Scrollable content area
        canvas = tk.Canvas(self, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        self.content_frame = tk.Frame(canvas, bg='white')

        self.content_frame.bind('<Configure>',
                               lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        canvas.create_window((0, 0), window=self.content_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True, padx=SPACING['md'])
        scrollbar.pack(side='right', fill='y')

        # Action buttons
        button_frame = tk.Frame(self, bg=COLORS['bg'])
        button_frame.pack(fill='x', padx=SPACING['md'], pady=SPACING['md'])

        self.run_btn = tk.Button(button_frame, text='▶ Start Research',
                                font=FONTS['h3'], bg=COLORS['primary'],
                                fg='white', relief='flat',
                                padx=SPACING['lg'], pady=SPACING['sm'],
                                command=self._on_run)
        self.run_btn.pack(side='right')

        tk.Button(button_frame, text='← Back to Edit',
                 font=FONTS['body'], bg=COLORS['surface'],
                 fg=COLORS['text'], relief='flat',
                 padx=SPACING['md'], pady=SPACING['xs'],
                 command=self._go_back).pack(side='left')

    def update_config(self, config: Dict[str, Any]):
        """Update review sheet with configuration."""
        self.config_data = config
        self._render_sections()
        self._validate_config()

    def _render_sections(self):
        """Render configuration sections."""
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        sections = [
            ('Research Query', self._render_query_section),
            ('Filters & Settings', self._render_filters_section),
            ('Output Configuration', self._render_output_section),
            ('Estimates', self._render_estimates_section)
        ]

        for section_title, render_func in sections:
            self._render_section_header(section_title)
            render_func()

    def _render_section_header(self, title: str):
        """Render section header."""
        header = tk.Label(self.content_frame, text=title,
                         font=FONTS['h3'], bg='white', fg=COLORS['text'])
        header.pack(anchor='w', padx=SPACING['md'],
                   pady=(SPACING['md'], SPACING['xs']))

    def _render_query_section(self):
        """Render query configuration."""
        items = [
            ('Original Query', self.config_data.get('original_query', 'Not set')),
            ('Optimized Query', self.config_data.get('optimized_query', 'Not optimized')),
            ('Template', self.config_data.get('template', 'None'))
        ]

        for label, value in items:
            self._render_config_item(label, value)

    def _render_filters_section(self):
        """Render filters configuration."""
        filters = self.config_data.get('filters', {})

        items = [
            ('Upload Date', filters.get('upload_date', 'Any time')),
            ('Sort By', filters.get('sort_by', 'Relevance')),
            ('Duration', filters.get('duration', 'Any length')),
            ('Features', ', '.join(filters.get('features', [])) or 'None')
        ]

        for label, value in items:
            self._render_config_item(label, value)

    def _render_output_section(self):
        """Render output configuration."""
        items = [
            ('Number of Results', self.config_data.get('max_results', 15)),
            ('Output Directory', self.config_data.get('output_dir', './transcripts')),
            ('File Format', 'Markdown (.md)')
        ]

        for label, value in items:
            self._render_config_item(label, value)

    def _render_estimates_section(self):
        """Render estimates."""
        num_results = self.config_data.get('max_results', 15)
        use_ai = self.config_data.get('use_ai_optimization', True)

        runtime_minutes = (num_results * 20) // 60
        cost = num_results * 0.01 if use_ai else 0.0

        items = [
            ('Estimated Runtime', f'~{runtime_minutes} minutes'),
            ('Estimated Cost', f'${cost:.2f}'),
            ('Expected Files', f'{num_results} markdown files')
        ]

        for label, value in items:
            self._render_config_item(label, value, highlight=True)

    def _render_config_item(self, label: str, value: Any, highlight: bool = False):
        """Render a single configuration item."""
        item_frame = tk.Frame(self.content_frame,
                             bg=COLORS['surface'] if highlight else 'white',
                             bd=1 if highlight else 0, relief='solid' if highlight else 'flat')
        item_frame.pack(fill='x', padx=SPACING['md'], pady=2)

        tk.Label(item_frame, text=label, font=FONTS['body'],
                bg=COLORS['surface'] if highlight else 'white',
                fg=COLORS['text_secondary']).pack(side='left',
                                                  padx=SPACING['sm'], pady=SPACING['xs'])

        tk.Label(item_frame, text=str(value), font=FONTS['body'],
                bg=COLORS['surface'] if highlight else 'white',
                fg=COLORS['text']).pack(side='right',
                                       padx=SPACING['sm'], pady=SPACING['xs'])

    def _validate_config(self):
        """Validate configuration and update run button state."""
        issues = []

        if not self.config_data.get('query'):
            issues.append('No query specified')

        if not self.config_data.get('max_results'):
            issues.append('Number of results not set')

        if issues:
            self.run_btn.config(state='disabled', bg=COLORS['text_secondary'])
            self.validation_status = {'valid': False, 'issues': issues}
        else:
            self.run_btn.config(state='normal', bg=COLORS['primary'])
            self.validation_status = {'valid': True, 'issues': []}

    def _on_run(self):
        """Handle run button click."""
        if self.on_run and self.validation_status.get('valid', False):
            self.on_run(self.config_data)

    def _go_back(self):
        """Navigate back to editing."""
        # This would be handled by parent wizard navigation
        pass
