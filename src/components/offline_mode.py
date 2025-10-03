"""Offline mode with local caching for persistent research library."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING

class OfflineCache:
    """Manages offline cache storage and retrieval."""

    def __init__(self, cache_dir: str = None):
        self.cache_dir = cache_dir or os.path.join(
            Path.home(), '.youtube_scraper_cache'
        )
        os.makedirs(self.cache_dir, exist_ok=True)
        self.index_file = os.path.join(self.cache_dir, 'index.json')
        self._load_index()

    def _load_index(self):
        """Load cache index from disk."""
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
        else:
            self.index = {'searches': [], 'transcripts': []}

    def _save_index(self):
        """Save cache index to disk."""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2)

    def cache_search(self, query: str, results: List[Dict[str, Any]]):
        """Cache search results."""
        entry = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'result_count': len(results),
            'results': results
        }
        self.index['searches'].append(entry)
        self._save_index()

    def cache_transcript(self, video_id: str, transcript: Dict[str, Any]):
        """Cache transcript data."""
        entry = {
            'video_id': video_id,
            'title': transcript.get('title', 'Unknown'),
            'timestamp': datetime.now().isoformat(),
            'transcript': transcript
        }
        self.index['transcripts'].append(entry)
        self._save_index()

    def search_cache(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Search for cached query results."""
        for search in reversed(self.index['searches']):
            if search['query'].lower() == query.lower():
                return search['results']
        return None

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'searches': len(self.index['searches']),
            'transcripts': len(self.index['transcripts']),
            'size_mb': self._calculate_size() / (1024 * 1024)
        }

    def _calculate_size(self) -> int:
        """Calculate total cache size in bytes."""
        total_size = 0
        for root, dirs, files in os.walk(self.cache_dir):
            for file in files:
                total_size += os.path.getsize(os.path.join(root, file))
        return total_size

    def clear_cache(self):
        """Clear all cached data."""
        self.index = {'searches': [], 'transcripts': []}
        self._save_index()


class OfflineModePanel(tk.Frame):
    """UI panel for offline mode management."""

    def __init__(self, parent, cache: OfflineCache):
        super().__init__(parent, bg='white')
        self.cache = cache
        self._build_ui()

    def _build_ui(self):
        """Build offline mode UI."""
        # Header
        header = tk.Label(self, text='Offline Mode', font=FONTS['h2'],
                         bg='white', fg=COLORS['text'])
        header.pack(pady=SPACING['md'], anchor='w', padx=SPACING['md'])

        # Status indicator
        stats = self.cache.get_cache_stats()
        status_frame = tk.Frame(self, bg=COLORS['surface'],
                               bd=1, relief='solid')
        status_frame.pack(fill='x', padx=SPACING['md'], pady=SPACING['sm'])

        tk.Label(status_frame, text='📦', font=('Segoe UI', 20),
                bg=COLORS['surface']).pack(side='left', padx=SPACING['sm'])

        info_frame = tk.Frame(status_frame, bg=COLORS['surface'])
        info_frame.pack(side='left', fill='both', expand=True, pady=SPACING['sm'])

        tk.Label(info_frame,
                text=f"{stats['searches']} searches cached, {stats['transcripts']} transcripts",
                font=FONTS['body'], bg=COLORS['surface'],
                fg=COLORS['text']).pack(anchor='w')

        tk.Label(info_frame,
                text=f"Cache size: {stats['size_mb']:.1f} MB",
                font=FONTS['small'], bg=COLORS['surface'],
                fg=COLORS['text_secondary']).pack(anchor='w')

        # Actions
        action_frame = tk.Frame(self, bg='white')
        action_frame.pack(pady=SPACING['md'], padx=SPACING['md'])

        tk.Button(action_frame, text='Clear Cache',
                 font=FONTS['body'], bg=COLORS['error'],
                 fg='white', relief='flat',
                 padx=SPACING['md'], pady=SPACING['xs'],
                 command=self._clear_cache,
                 cursor='hand2').pack(side='left', padx=SPACING['xs'])

        tk.Button(action_frame, text='Refresh Stats',
                 font=FONTS['body'], bg=COLORS['primary'],
                 fg='white', relief='flat',
                 padx=SPACING['md'], pady=SPACING['xs'],
                 command=self._refresh_stats,
                 cursor='hand2').pack(side='left', padx=SPACING['xs'])

    def _clear_cache(self):
        """Clear cache and refresh UI."""
        self.cache.clear_cache()
        self._refresh_stats()

    def _refresh_stats(self):
        """Refresh cache statistics."""
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
