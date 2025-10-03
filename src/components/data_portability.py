"""Data portability for export/import of research library."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Any
import json
import zipfile
import os
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING

class DataPortability:
    """Handles export/import of research data."""

    @staticmethod
    def export_to_zip(data: Dict[str, Any], output_path: str) -> bool:
        """Export research library to ZIP archive."""
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Export metadata
                metadata = {
                    'export_date': datetime.now().isoformat(),
                    'version': '1.0',
                    'transcript_count': len(data.get('transcripts', []))
                }
                zipf.writestr('metadata.json', json.dumps(metadata, indent=2))

                # Export transcripts
                zipf.writestr('transcripts.json',
                            json.dumps(data.get('transcripts', []), indent=2))

                # Export search history
                zipf.writestr('searches.json',
                            json.dumps(data.get('searches', []), indent=2))

                # Export configurations
                zipf.writestr('configs.json',
                            json.dumps(data.get('configs', []), indent=2))

            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False

    @staticmethod
    def import_from_zip(zip_path: str, merge: bool = True) -> Dict[str, Any]:
        """Import research library from ZIP archive."""
        try:
            imported_data = {
                'transcripts': [],
                'searches': [],
                'configs': []
            }

            with zipfile.ZipFile(zip_path, 'r') as zipf:
                # Load metadata
                if 'metadata.json' in zipf.namelist():
                    metadata = json.loads(zipf.read('metadata.json'))
                    print(f"Importing data from {metadata.get('export_date', 'unknown date')}")

                # Load transcripts
                if 'transcripts.json' in zipf.namelist():
                    imported_data['transcripts'] = json.loads(
                        zipf.read('transcripts.json')
                    )

                # Load searches
                if 'searches.json' in zipf.namelist():
                    imported_data['searches'] = json.loads(
                        zipf.read('searches.json')
                    )

                # Load configs
                if 'configs.json' in zipf.namelist():
                    imported_data['configs'] = json.loads(
                        zipf.read('configs.json')
                    )

            return imported_data
        except Exception as e:
            print(f"Import error: {e}")
            return None


class DataPortabilityPanel(tk.Frame):
    """UI panel for data import/export."""

    def __init__(self, parent, on_export: callable, on_import: callable):
        super().__init__(parent, bg='white')
        self.on_export = on_export
        self.on_import = on_import
        self._build_ui()

    def _build_ui(self):
        """Build data portability UI."""
        # Header
        tk.Label(self, text='Data Portability', font=FONTS['h2'],
                bg='white', fg=COLORS['text']).pack(pady=SPACING['md'],
                                                     anchor='w',
                                                     padx=SPACING['md'])

        # Export section
        export_frame = tk.Frame(self, bg=COLORS['surface'],
                               bd=1, relief='solid')
        export_frame.pack(fill='x', padx=SPACING['md'], pady=SPACING['sm'])

        tk.Label(export_frame, text='📤 Export Library',
                font=FONTS['h3'], bg=COLORS['surface'],
                fg=COLORS['text']).pack(pady=SPACING['sm'],
                                       padx=SPACING['md'], anchor='w')

        tk.Label(export_frame,
                text='Create a ZIP archive of all your research data',
                font=FONTS['body'], bg=COLORS['surface'],
                fg=COLORS['text_secondary'], wraplength=400,
                justify='left').pack(padx=SPACING['md'], anchor='w')

        tk.Button(export_frame, text='Export to ZIP',
                 font=FONTS['body'], bg=COLORS['primary'],
                 fg='white', relief='flat',
                 padx=SPACING['md'], pady=SPACING['xs'],
                 command=self._handle_export,
                 cursor='hand2').pack(pady=SPACING['md'],
                                     padx=SPACING['md'], anchor='w')

        # Import section
        import_frame = tk.Frame(self, bg=COLORS['surface'],
                               bd=1, relief='solid')
        import_frame.pack(fill='x', padx=SPACING['md'], pady=SPACING['sm'])

        tk.Label(import_frame, text='📥 Import Library',
                font=FONTS['h3'], bg=COLORS['surface'],
                fg=COLORS['text']).pack(pady=SPACING['sm'],
                                       padx=SPACING['md'], anchor='w')

        tk.Label(import_frame,
                text='Import research data from a ZIP archive (merges with existing data)',
                font=FONTS['body'], bg=COLORS['surface'],
                fg=COLORS['text_secondary'], wraplength=400,
                justify='left').pack(padx=SPACING['md'], anchor='w')

        tk.Button(import_frame, text='Import from ZIP',
                 font=FONTS['body'], bg=COLORS['success'],
                 fg='white', relief='flat',
                 padx=SPACING['md'], pady=SPACING['xs'],
                 command=self._handle_import,
                 cursor='hand2').pack(pady=SPACING['md'],
                                     padx=SPACING['md'], anchor='w')

    def _handle_export(self):
        """Handle export action."""
        filename = filedialog.asksaveasfilename(
            defaultextension='.zip',
            filetypes=[('ZIP Archive', '*.zip')],
            initialfile=f'research_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        )

        if filename:
            success = self.on_export(filename)
            if success:
                messagebox.showinfo('Export Successful',
                                  f'Research library exported to:\n{filename}')

    def _handle_import(self):
        """Handle import action."""
        filename = filedialog.askopenfilename(
            filetypes=[('ZIP Archive', '*.zip'), ('All Files', '*.*')]
        )

        if filename:
            imported_data = self.on_import(filename)
            if imported_data:
                count = len(imported_data.get('transcripts', []))
                messagebox.showinfo('Import Successful',
                                  f'Imported {count} transcripts from archive')
