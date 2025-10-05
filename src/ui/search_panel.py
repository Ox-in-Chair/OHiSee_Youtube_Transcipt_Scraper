"""Search Panel Component

Provides search input controls including query entry, filters (max results,
upload date), and AI optimization toggle.

This component handles user input collection and notifies the parent
via callback when a search is requested.

Target: ~150 lines
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable

from utils.filters import UPLOAD_DATE_OPTIONS
from shared import COLORS, FONTS


class SearchPanel(ttk.Frame):
    """Search controls panel with query input and filters.

    Components:
    - Query text entry with Enter key binding
    - Max results dropdown (5, 10, 15, 25, 50)
    - Upload date filter dropdown
    - AI optimization toggle checkbox
    - Search button

    Attributes:
        on_search_callback: Function(query, filters) called when search requested
        query_entry: Entry widget for search query
        max_results_var: StringVar for max results selection
        upload_date_var: StringVar for upload date filter
        ai_toggle_var: BooleanVar for AI optimization toggle
        search_btn: Search button widget
    """

    def __init__(self, parent, on_search_callback: Callable[[str, Dict], None]):
        """Initialize search panel.

        Args:
            parent: Parent tkinter widget
            on_search_callback: Function(query: str, filters: dict) to call
                when search is requested
        """
        super().__init__(parent)
        self.on_search_callback = on_search_callback

        # Initialize variables
        self.max_results_var = tk.StringVar(value='15')
        self.upload_date_var = tk.StringVar(value='Any time')
        self.ai_toggle_var = tk.BooleanVar(value=False)

        # Build UI
        self._build_ui()

    def _build_ui(self):
        """Build search panel UI components."""
        # Query row
        query_row = tk.Frame(self, bg=COLORS['bg'])
        query_row.pack(fill='x', pady=5)

        ttk.Label(
            query_row,
            text="Search Query:"
        ).pack(side='left', padx=(0, 10))

        self.query_entry = ttk.Entry(query_row, font=FONTS['body'])
        self.query_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.query_entry.bind('<Return>', lambda e: self._handle_search())

        self.search_btn = ttk.Button(
            query_row,
            text="Search",
            command=self._handle_search,
            width=12
        )
        self.search_btn.pack(side='right')

        # Filters row
        filters_row = tk.Frame(self, bg=COLORS['bg'])
        filters_row.pack(fill='x', pady=5)

        # Max results dropdown
        ttk.Label(
            filters_row,
            text="Max Results:"
        ).pack(side='left', padx=(0, 5))

        max_results_combo = ttk.Combobox(
            filters_row,
            textvariable=self.max_results_var,
            values=['5', '10', '15', '25', '50'],
            width=8,
            state='readonly'
        )
        max_results_combo.pack(side='left', padx=(0, 20))

        # Upload date filter dropdown
        ttk.Label(
            filters_row,
            text="Upload Date:"
        ).pack(side='left', padx=(0, 5))

        upload_date_combo = ttk.Combobox(
            filters_row,
            textvariable=self.upload_date_var,
            values=list(UPLOAD_DATE_OPTIONS.keys()),
            width=15,
            state='readonly'
        )
        upload_date_combo.pack(side='left')

        # AI optimization row
        ai_row = tk.Frame(self, bg=COLORS['bg'])
        ai_row.pack(fill='x', pady=5)

        self.ai_checkbox = ttk.Checkbutton(
            ai_row,
            text="Use AI Optimization (GPT-4) - Requires API key",
            variable=self.ai_toggle_var
        )
        self.ai_checkbox.pack(side='left')

    def _handle_search(self):
        """Handle search button click or Enter key press.

        Collects query and filters, then invokes callback.
        """
        query = self.get_query()
        if not query:
            return

        filters = self.get_filters()
        self.on_search_callback(query, filters)

    def get_query(self) -> str:
        """Get the search query text.

        Returns:
            Trimmed search query string
        """
        return self.query_entry.get().strip()

    def get_filters(self) -> Dict:
        """Get current filter settings.

        Returns:
            Dict with keys:
                - max_results: int (5, 10, 15, 25, or 50)
                - upload_date: str (7, 30, 90, 180, 365, or 'any')
                - use_ai: bool (True if AI optimization enabled)
        """
        # Map upload date label to value
        upload_date_label = self.upload_date_var.get()
        upload_date_value = UPLOAD_DATE_OPTIONS.get(upload_date_label, 'any')

        return {
            'max_results': int(self.max_results_var.get()),
            'upload_date': upload_date_value,
            'use_ai': self.ai_toggle_var.get()
        }

    def set_loading(self, loading: bool):
        """Update UI state during search operation.

        Args:
            loading: True to disable inputs (searching), False to enable
        """
        state = 'disabled' if loading else 'normal'
        text = 'Searching...' if loading else 'Search'

        self.search_btn.config(state=state, text=text)
        self.query_entry.config(state=state)
