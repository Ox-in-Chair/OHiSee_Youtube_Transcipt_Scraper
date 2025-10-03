"""Citation generator for academic and professional use."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING

class CitationGenerator:
    """Generates citations in multiple academic formats."""

    @staticmethod
    def generate_apa(video_data: Dict[str, Any]) -> str:
        """Generate APA 7th edition citation."""
        channel = video_data.get('channel', 'Unknown')
        title = video_data.get('title', 'Untitled')
        year = video_data.get('upload_date', datetime.now()).split('-')[0]
        url = video_data.get('url', '')

        return f"{channel}. ({year}). {title} [Video]. YouTube. {url}"

    @staticmethod
    def generate_mla(video_data: Dict[str, Any]) -> str:
        """Generate MLA 9th edition citation."""
        channel = video_data.get('channel', 'Unknown')
        title = video_data.get('title', 'Untitled')
        date = video_data.get('upload_date', datetime.now().strftime('%Y-%m-%d'))
        url = video_data.get('url', '')

        return f'"{title}." YouTube, uploaded by {channel}, {date}, {url}.'

    @staticmethod
    def generate_chicago(video_data: Dict[str, Any]) -> str:
        """Generate Chicago 17th edition citation."""
        channel = video_data.get('channel', 'Unknown')
        title = video_data.get('title', 'Untitled')
        date = video_data.get('upload_date', datetime.now().strftime('%B %d, %Y'))
        url = video_data.get('url', '')

        return f'{channel}. "{title}." YouTube video, {date}. {url}.'

    @staticmethod
    def generate_bibtex(video_data: Dict[str, Any]) -> str:
        """Generate BibTeX citation."""
        video_id = video_data.get('id', 'unknown')
        channel = video_data.get('channel', 'Unknown').replace(' ', '')
        title = video_data.get('title', 'Untitled')
        year = video_data.get('upload_date', datetime.now()).split('-')[0]
        url = video_data.get('url', '')

        return f"""@misc{{{channel}{year},
  author = {{{channel}}},
  title = {{{title}}},
  year = {{{year}}},
  howpublished = {{\\url{{{url}}}}},
  note = {{YouTube video}}
}}"""


class CitationPanel(tk.Frame):
    """UI panel for citation generation."""

    CITATION_FORMATS = ['APA', 'MLA', 'Chicago', 'BibTeX']

    def __init__(self, parent, video_data: Dict[str, Any] = None):
        super().__init__(parent, bg='white')
        self.video_data = video_data or {}
        self.generator = CitationGenerator()
        self._build_ui()

    def _build_ui(self):
        """Build citation UI."""
        # Header
        tk.Label(self, text='Citation Generator', font=FONTS['h3'],
                bg='white', fg=COLORS['text']).pack(pady=SPACING['sm'],
                                                     anchor='w',
                                                     padx=SPACING['md'])

        # Format selector
        format_frame = tk.Frame(self, bg='white')
        format_frame.pack(fill='x', padx=SPACING['md'], pady=SPACING['xs'])

        tk.Label(format_frame, text='Format:', font=FONTS['body'],
                bg='white', fg=COLORS['text']).pack(side='left',
                                                     padx=SPACING['xs'])

        self.format_var = tk.StringVar(value='APA')
        for fmt in self.CITATION_FORMATS:
            tk.Radiobutton(format_frame, text=fmt, variable=self.format_var,
                          value=fmt, font=FONTS['body'], bg='white',
                          command=self._update_citation).pack(side='left',
                                                              padx=SPACING['xs'])

        # Citation display
        self.citation_text = tk.Text(self, height=4, font=FONTS['body'],
                                     bg=COLORS['surface'], fg=COLORS['text'],
                                     wrap='word', relief='solid', bd=1)
        self.citation_text.pack(fill='both', expand=True, padx=SPACING['md'],
                               pady=SPACING['sm'])

        # Actions
        action_frame = tk.Frame(self, bg='white')
        action_frame.pack(pady=SPACING['sm'], padx=SPACING['md'])

        tk.Button(action_frame, text='Copy Citation',
                 font=FONTS['body'], bg=COLORS['primary'],
                 fg='white', relief='flat',
                 padx=SPACING['md'], pady=SPACING['xs'],
                 command=self._copy_citation,
                 cursor='hand2').pack(side='left', padx=SPACING['xs'])

        # Update citation
        self._update_citation()

    def _update_citation(self):
        """Update displayed citation."""
        format_name = self.format_var.get()

        # Generate citation
        if format_name == 'APA':
            citation = self.generator.generate_apa(self.video_data)
        elif format_name == 'MLA':
            citation = self.generator.generate_mla(self.video_data)
        elif format_name == 'Chicago':
            citation = self.generator.generate_chicago(self.video_data)
        elif format_name == 'BibTeX':
            citation = self.generator.generate_bibtex(self.video_data)
        else:
            citation = 'Unknown format'

        # Display
        self.citation_text.delete('1.0', 'end')
        self.citation_text.insert('1.0', citation)

    def _copy_citation(self):
        """Copy citation to clipboard."""
        citation = self.citation_text.get('1.0', 'end-1c')
        self.clipboard_clear()
        self.clipboard_append(citation)
        # Visual feedback (could use toast)
        print(f"Citation copied: {self.format_var.get()} format")

    def set_video_data(self, video_data: Dict[str, Any]):
        """Update video data and refresh citation."""
        self.video_data = video_data
        self._update_citation()
