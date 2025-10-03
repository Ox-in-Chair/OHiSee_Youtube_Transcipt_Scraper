"""Results slider with presets and runtime estimates."""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING

class ResultsSlider(ttk.Frame):
    """Interactive slider for selecting number of results with quick presets."""

    PRESETS = [
        {'value': 5, 'label': 'Quick scan', 'runtime': '~2 min'},
        {'value': 15, 'label': 'Balanced', 'runtime': '~5 min'},
        {'value': 50, 'label': 'Deep dive', 'runtime': '~17 min'}
    ]

    def __init__(self, parent, on_change: Optional[Callable] = None):
        super().__init__(parent)
        self.on_change = on_change
        self.current_value = 15  # Default to Balanced
        self._build_ui()

    def _build_ui(self):
        """Build the results slider UI."""
        # Title
        title = tk.Label(self, text='Number of Results',
                        font=FONTS['h3'], bg=COLORS['bg'], fg=COLORS['text'])
        title.pack(anchor='w', pady=(SPACING['sm'], SPACING['xs']))

        # Preset buttons
        presets_frame = tk.Frame(self, bg=COLORS['bg'])
        presets_frame.pack(fill='x', pady=SPACING['xs'])

        for preset in self.PRESETS:
            btn = tk.Button(presets_frame, text=f"{preset['label']} ({preset['value']})",
                          font=FONTS['body'], bg=COLORS['surface'],
                          fg=COLORS['text'], relief='flat',
                          padx=SPACING['sm'], pady=SPACING['xs'],
                          command=lambda v=preset['value']: self._set_value(v))
            btn.pack(side='left', padx=(0, SPACING['xs']))

        # Slider container
        slider_frame = tk.Frame(self, bg=COLORS['bg'])
        slider_frame.pack(fill='x', pady=SPACING['sm'])

        # Current value label
        self.value_label = tk.Label(slider_frame, text='15 videos',
                                    font=FONTS['h2'], bg=COLORS['bg'],
                                    fg=COLORS['primary'])
        self.value_label.pack()

        # Slider
        self.slider = tk.Scale(slider_frame, from_=1, to=100,
                              orient='horizontal', font=FONTS['body'],
                              bg=COLORS['bg'], fg=COLORS['text'],
                              highlightthickness=0, relief='flat',
                              command=self._on_slider_change)
        self.slider.set(15)
        self.slider.pack(fill='x', pady=SPACING['xs'])

        # Runtime estimate
        self.runtime_label = tk.Label(slider_frame, text='Estimated runtime: ~5 min',
                                     font=FONTS['small'], bg=COLORS['bg'],
                                     fg=COLORS['text_secondary'])
        self.runtime_label.pack()

    def _set_value(self, value: int):
        """Set slider to preset value."""
        self.current_value = value
        self.slider.set(value)
        self._update_labels()

        if self.on_change:
            self.on_change(value)

    def _on_slider_change(self, value):
        """Handle slider value change."""
        self.current_value = int(float(value))
        self._update_labels()

        if self.on_change:
            self.on_change(self.current_value)

    def _update_labels(self):
        """Update value and runtime labels."""
        # Update value label
        self.value_label.config(text=f'{self.current_value} videos')

        # Calculate runtime (~20 seconds per video)
        runtime_seconds = self.current_value * 20
        if runtime_seconds < 60:
            runtime = f'~{runtime_seconds}s'
        else:
            minutes = runtime_seconds // 60
            runtime = f'~{minutes} min'

        self.runtime_label.config(text=f'Estimated runtime: {runtime}')

    def get_value(self) -> int:
        """Get current slider value."""
        return self.current_value

    def set_value(self, value: int):
        """Set slider value programmatically."""
        self._set_value(value)
