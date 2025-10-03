"""Result cards for displaying video results in a grid."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Callable, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING

class ResultCard(tk.Frame):
    """Individual result card showing thumbnail, title, and snippet."""

    def __init__(self, parent, result_data: Dict[str, Any],
                 on_click: Optional[Callable] = None):
        super().__init__(parent, bg='white', width=280, height=320,
                        highlightbackground=COLORS['border'], highlightthickness=1)
        self.result_data = result_data
        self.on_click = on_click
        self.selected = False
        self._build_ui()

    def _build_ui(self):
        """Build the result card UI."""
        self.pack_propagate(False)

        # Thumbnail placeholder (YouTube thumbnails would load here)
        thumb_frame = tk.Frame(self, bg=COLORS['surface'], height=157)  # 16:9 ratio
        thumb_frame.pack(fill='x')
        thumb_frame.pack_propagate(False)

        thumb_label = tk.Label(thumb_frame, text='🎬',
                              font=('Segoe UI', 48), bg=COLORS['surface'],
                              fg=COLORS['text_secondary'])
        thumb_label.place(relx=0.5, rely=0.5, anchor='center')

        # Duration badge (overlay on thumbnail)
        duration = self.result_data.get('duration', '0:00')
        duration_badge = tk.Label(thumb_frame, text=duration,
                                 font=FONTS['small'], bg='black', fg='white',
                                 padx=4, pady=2)
        duration_badge.place(relx=0.95, rely=0.95, anchor='se')

        # Content area
        content_frame = tk.Frame(self, bg='white')
        content_frame.pack(fill='both', expand=True, padx=SPACING['sm'],
                          pady=SPACING['sm'])

        # Title
        title = self.result_data.get('title', 'Untitled Video')
        title_label = tk.Label(content_frame, text=title,
                              font=FONTS['body'], bg='white',
                              fg=COLORS['text'], wraplength=260,
                              justify='left', anchor='w')
        title_label.pack(fill='x', pady=(0, SPACING['xs']))

        # Channel name
        channel = self.result_data.get('channel', 'Unknown Channel')
        channel_label = tk.Label(content_frame, text=channel,
                                font=FONTS['small'], bg='white',
                                fg=COLORS['text_secondary'], anchor='w')
        channel_label.pack(fill='x')

        # Stats
        stats_frame = tk.Frame(content_frame, bg='white')
        stats_frame.pack(fill='x', pady=SPACING['xs'])

        views = self.result_data.get('views', '0')
        upload_date = self.result_data.get('upload_date', 'Unknown')

        stats_text = f"👁️ {views} • 📅 {upload_date}"
        stats_label = tk.Label(stats_frame, text=stats_text,
                              font=FONTS['small'], bg='white',
                              fg=COLORS['text_secondary'])
        stats_label.pack(side='left')

        # Snippet/description preview
        snippet = self.result_data.get('snippet', '')[:100] + '...'
        snippet_label = tk.Label(content_frame, text=snippet,
                                font=FONTS['small'], bg='white',
                                fg=COLORS['text_secondary'], wraplength=260,
                                justify='left', anchor='w')
        snippet_label.pack(fill='both', expand=True)

        # Action buttons
        actions_frame = tk.Frame(content_frame, bg='white')
        actions_frame.pack(fill='x', pady=(SPACING['xs'], 0))

        # Checkbox for selection
        self.selected_var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(actions_frame, text='Include',
                           variable=self.selected_var, font=FONTS['small'],
                           bg='white', command=self._on_select)
        cb.pack(side='left')

        # View button
        view_btn = tk.Button(actions_frame, text='View',
                           font=FONTS['small'], bg=COLORS['surface'],
                           fg=COLORS['text'], relief='flat', padx=8, pady=2,
                           command=self._on_view)
        view_btn.pack(side='right')

        # Hover effects
        self.bind('<Enter>', self._on_hover)
        self.bind('<Leave>', self._on_leave)

    def _on_select(self):
        """Handle selection checkbox change."""
        self.selected = self.selected_var.get()

        if self.selected:
            self.configure(highlightbackground=COLORS['primary'],
                          highlightthickness=2)
        else:
            self.configure(highlightbackground=COLORS['border'],
                          highlightthickness=1)

    def _on_view(self):
        """Handle view button click."""
        if self.on_click:
            self.on_click(self.result_data)

    def _on_hover(self, event):
        """Mouse enter effect."""
        if not self.selected:
            self.configure(highlightbackground=COLORS['primary'],
                          highlightthickness=2)

    def _on_leave(self, event):
        """Mouse leave effect."""
        if not self.selected:
            self.configure(highlightbackground=COLORS['border'],
                          highlightthickness=1)

    def is_selected(self) -> bool:
        """Check if card is selected."""
        return self.selected


class ResultCardGrid(ttk.Frame):
    """Grid of result cards with batch actions."""

    def __init__(self, parent, on_card_click: Optional[Callable] = None):
        super().__init__(parent)
        self.on_card_click = on_card_click
        self.cards = []
        self._build_ui()

    def _build_ui(self):
        """Build the result grid UI."""
        # Toolbar
        toolbar = tk.Frame(self, bg=COLORS['surface'])
        toolbar.pack(fill='x', pady=(0, SPACING['sm']))

        tk.Label(toolbar, text='Search Results',
                font=FONTS['h3'], bg=COLORS['surface'],
                fg=COLORS['text']).pack(side='left', padx=SPACING['md'],
                                       pady=SPACING['xs'])

        # Batch actions
        tk.Button(toolbar, text='Select All', font=FONTS['small'],
                 bg=COLORS['surface'], fg=COLORS['text'],
                 relief='flat', command=self.select_all).pack(side='right',
                                                              padx=SPACING['xs'])

        tk.Button(toolbar, text='Deselect All', font=FONTS['small'],
                 bg=COLORS['surface'], fg=COLORS['text'],
                 relief='flat', command=self.deselect_all).pack(side='right',
                                                                padx=SPACING['xs'])

        # Scrollable grid container
        canvas = tk.Canvas(self, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)

        self.grid_frame = tk.Frame(canvas, bg=COLORS['bg'])

        self.grid_frame.bind('<Configure>',
                            lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        canvas.create_window((0, 0), window=self.grid_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def add_results(self, results: List[Dict[str, Any]]):
        """Add multiple result cards to grid."""
        # Clear existing cards
        for card in self.cards:
            card.destroy()
        self.cards = []

        # Create new cards in 3-column grid
        for i, result in enumerate(results):
            row = i // 3
            col = i % 3

            card = ResultCard(self.grid_frame, result, self.on_card_click)
            card.grid(row=row, column=col, padx=SPACING['sm'],
                     pady=SPACING['sm'], sticky='n')

            self.cards.append(card)

    def select_all(self):
        """Select all cards."""
        for card in self.cards:
            card.selected_var.set(True)
            card._on_select()

    def deselect_all(self):
        """Deselect all cards."""
        for card in self.cards:
            card.selected_var.set(False)
            card._on_select()

    def get_selected_results(self) -> List[Dict[str, Any]]:
        """Get all selected result data."""
        return [card.result_data for card in self.cards if card.is_selected()]
