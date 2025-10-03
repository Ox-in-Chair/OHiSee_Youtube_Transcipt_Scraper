"""Live preview panel - 400px right column."""
import tkinter as tk
from tkinter import ttk, scrolledtext
import yaml
from typing import Dict, Any, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING

class LivePreview(ttk.Frame):
    """Fixed 400px right column with summary, config, and validation."""

    def __init__(self, parent):
        super().__init__(parent, width=400)
        self.config_data = {}
        self.validation_score = 0
        self._build_ui()

    def _build_ui(self):
        """Build the preview panel UI."""
        self.configure(style='Preview.TFrame')

        # Title bar
        title_frame = tk.Frame(self, bg=COLORS['surface'], height=56)
        title_frame.pack(fill='x', padx=SPACING['sm'], pady=(SPACING['sm'], 0))

        title = tk.Label(title_frame, text='Configuration Preview',
                        font=FONTS['h3'], bg=COLORS['surface'], fg=COLORS['text'])
        title.pack(side='left', padx=SPACING['xs'])

        # Validation badge
        self.badge = tk.Label(title_frame, text='✅ Valid',
                            font=FONTS['small'], bg=COLORS['success'],
                            fg='white', padx=8, pady=2)
        self.badge.pack(side='right', padx=SPACING['xs'])

        # Summary section
        summary_frame = tk.LabelFrame(self, text='Summary', font=FONTS['body'],
                                     bg='white', fg=COLORS['text'])
        summary_frame.pack(fill='x', padx=SPACING['sm'], pady=SPACING['xs'])

        self.summary_text = tk.Text(summary_frame, height=4, wrap='word',
                                   font=FONTS['body'], bg='white',
                                   fg=COLORS['text_secondary'], relief='flat')
        self.summary_text.pack(fill='both', padx=SPACING['xs'], pady=SPACING['xs'])

        # YAML Config section
        config_frame = tk.LabelFrame(self, text='Configuration (YAML)',
                                    font=FONTS['body'], bg='white', fg=COLORS['text'])
        config_frame.pack(fill='both', expand=True, padx=SPACING['sm'],
                         pady=SPACING['xs'])

        self.yaml_text = scrolledtext.ScrolledText(config_frame, wrap='word',
                                                  font=('Consolas', 11), bg='white',
                                                  fg=COLORS['text'], relief='flat')
        self.yaml_text.pack(fill='both', expand=True, padx=SPACING['xs'],
                           pady=SPACING['xs'])

        # Action buttons
        button_frame = tk.Frame(self, bg=COLORS['bg'], height=48)
        button_frame.pack(fill='x', padx=SPACING['sm'], pady=SPACING['sm'])

        copy_btn = tk.Button(button_frame, text='Copy Config',
                           font=FONTS['body'], bg=COLORS['primary'],
                           fg='white', relief='flat', padx=16, pady=6,
                           command=self.copy_config)
        copy_btn.pack(side='left', padx=(0, SPACING['xs']))

        export_btn = tk.Button(button_frame, text='Export',
                             font=FONTS['body'], bg=COLORS['surface'],
                             fg=COLORS['text'], relief='flat', padx=16, pady=6,
                             command=self.export_config)
        export_btn.pack(side='left')

    def update_preview(self, config: Dict[str, Any]):
        """Update preview with new configuration."""
        self.config_data = config

        # Update summary
        summary = self._generate_summary(config)
        self.summary_text.delete('1.0', 'end')
        self.summary_text.insert('1.0', summary)

        # Update YAML
        yaml_str = yaml.dump(config, default_flow_style=False, sort_keys=False)
        self.yaml_text.delete('1.0', 'end')
        self.yaml_text.insert('1.0', yaml_str)

        # Update validation
        self._validate_config(config)

    def _generate_summary(self, config: Dict[str, Any]) -> str:
        """Generate human-readable summary."""
        lines = []
        if 'query' in config:
            lines.append(f"Search: {config['query']}")
        if 'max_results' in config:
            lines.append(f"Videos: {config['max_results']}")
        if 'filters' in config and config['filters']:
            lines.append(f"Filters: {len(config['filters'])} active")
        if 'template' in config:
            lines.append(f"Template: {config['template']}")
        return '\n'.join(lines) if lines else 'No configuration set'

    def _validate_config(self, config: Dict[str, Any]):
        """Validate configuration and update badge."""
        score = 0
        if config.get('query'):
            score += 40
        if config.get('max_results', 0) > 0:
            score += 20
        if config.get('template'):
            score += 20
        if config.get('filters'):
            score += 20

        self.validation_score = score
        if score >= 60:
            self.badge.config(text='✅ Valid', bg=COLORS['success'])
        else:
            self.badge.config(text='⚠️ Incomplete', bg=COLORS['warning'])

    def copy_config(self):
        """Copy YAML to clipboard."""
        yaml_content = self.yaml_text.get('1.0', 'end-1c')
        self.clipboard_clear()
        self.clipboard_append(yaml_content)

    def export_config(self):
        """Export configuration to file."""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension='.yaml',
            filetypes=[('YAML files', '*.yaml'), ('All files', '*.*')]
        )
        if filename:
            with open(filename, 'w') as f:
                yaml.dump(self.config_data, f)
