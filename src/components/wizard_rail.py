"""Compact wizard navigation rail - 80px left sidebar."""
import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid

class WizardRail(ttk.Frame):
    """5-step wizard with progress dots and navigation."""

    STEPS = ['Search', 'Filters', 'Templates', 'Preview', 'Export']

    def __init__(self, parent, on_step_change: Optional[Callable] = None):
        super().__init__(parent, width=80)
        self.current_step = 0
        self.completed_steps = set()
        self.on_step_change = on_step_change
        self._build_ui()

    def _build_ui(self):
        """Build the wizard rail UI."""
        self.configure(style='Rail.TFrame')

        # Create step indicators
        for i, step in enumerate(self.STEPS):
            frame = tk.Frame(self, bg=COLORS['surface'], width=80, height=60)
            frame.pack(fill='x', pady=grid(1))

            # Progress dot
            dot = tk.Canvas(frame, width=24, height=24, bg=COLORS['surface'],
                          highlightthickness=0)
            dot.place(relx=0.5, rely=0.3, anchor='center')
            self._draw_dot(dot, i)

            # Step label
            label = tk.Label(frame, text=step, font=('Segoe UI', 9),
                           bg=COLORS['surface'], fg=COLORS['text_secondary'])
            label.place(relx=0.5, rely=0.7, anchor='center')

            # Click handler
            frame.bind('<Button-1>', lambda e, idx=i: self.go_to_step(idx))
            dot.bind('<Button-1>', lambda e, idx=i: self.go_to_step(idx))

            # Store references
            setattr(self, f'dot_{i}', dot)
            setattr(self, f'frame_{i}', frame)

    def _draw_dot(self, canvas: tk.Canvas, step: int):
        """Draw progress dot with appropriate state color."""
        if step in self.completed_steps:
            color = COLORS['success']
        elif step == self.current_step:
            color = COLORS['primary']
        else:
            color = COLORS['border']
        canvas.create_oval(4, 4, 20, 20, fill=color, outline='')

    def go_to_step(self, step: int):
        """Navigate to a specific step."""
        if step <= max(self.completed_steps, default=-1) + 1:
            self.current_step = step
            self._update_dots()
            if self.on_step_change:
                self.on_step_change(step)

    def mark_completed(self, step: int):
        """Mark a step as completed."""
        self.completed_steps.add(step)
        self._update_dots()

    def _update_dots(self):
        """Refresh all dot states."""
        for i in range(len(self.STEPS)):
            dot = getattr(self, f'dot_{i}')
            dot.delete('all')
            self._draw_dot(dot, i)
