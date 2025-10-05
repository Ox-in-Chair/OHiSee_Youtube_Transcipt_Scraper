"""Multi-format export for research data integration."""

import tkinter as tk
from tkinter import ttk, filedialog
from typing import Dict, Any, List
import json
import csv
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING


class ExportFormats:
    """Handles export to multiple formats."""

    @staticmethod
    def export_markdown(transcripts: List[Dict[str, Any]], filepath: str) -> bool:
        """Export to Markdown format."""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# YouTube Research Export\n\n")
                f.write(f"*Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")
                f.write("---\n\n")

                for transcript in transcripts:
                    f.write(f"## {transcript.get('title', 'Untitled')}\n\n")
                    f.write(f"**Channel**: {transcript.get('channel', 'Unknown')}\n")
                    f.write(f"**URL**: {transcript.get('url', 'N/A')}\n")
                    f.write(f"**Date**: {transcript.get('upload_date', 'Unknown')}\n\n")
                    f.write(f"### Transcript\n\n")
                    f.write(f"{transcript.get('transcript', 'No transcript available')}\n\n")
                    f.write("---\n\n")

            return True
        except Exception as e:
            print(f"Markdown export error: {e}")
            return False

    @staticmethod
    def export_csv(transcripts: List[Dict[str, Any]], filepath: str) -> bool:
        """Export to CSV format."""
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f, fieldnames=["title", "channel", "url", "upload_date", "transcript"]
                )
                writer.writeheader()
                for transcript in transcripts:
                    writer.writerow(
                        {
                            "title": transcript.get("title", ""),
                            "channel": transcript.get("channel", ""),
                            "url": transcript.get("url", ""),
                            "upload_date": transcript.get("upload_date", ""),
                            "transcript": transcript.get("transcript", ""),
                        }
                    )
            return True
        except Exception as e:
            print(f"CSV export error: {e}")
            return False

    @staticmethod
    def export_json(transcripts: List[Dict[str, Any]], filepath: str) -> bool:
        """Export to JSON format."""
        try:
            export_data = {
                "export_date": datetime.now().isoformat(),
                "count": len(transcripts),
                "transcripts": transcripts,
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"JSON export error: {e}")
            return False

    @staticmethod
    def export_obsidian(transcripts: List[Dict[str, Any]], folder_path: str) -> bool:
        """Export as individual Obsidian notes."""
        try:
            os.makedirs(folder_path, exist_ok=True)

            for transcript in transcripts:
                title = transcript.get("title", "Untitled").replace("/", "-")
                filename = f"{title[:100]}.md"  # Limit filename length
                filepath = os.path.join(folder_path, filename)

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# {transcript.get('title', 'Untitled')}\n\n")
                    f.write(f"**Channel**: [[{transcript.get('channel', 'Unknown')}]]\n")
                    f.write(f"**URL**: {transcript.get('url', 'N/A')}\n")
                    f.write(f"**Date**: {transcript.get('upload_date', 'Unknown')}\n\n")
                    f.write("#youtube #transcript\n\n")
                    f.write("## Transcript\n\n")
                    f.write(transcript.get("transcript", "No transcript available"))

            return True
        except Exception as e:
            print(f"Obsidian export error: {e}")
            return False

    @staticmethod
    def export_roam(transcripts: List[Dict[str, Any]], filepath: str) -> bool:
        """Export to Roam Research JSON format."""
        try:
            roam_pages = []

            for transcript in transcripts:
                page = {
                    "title": transcript.get("title", "Untitled"),
                    "children": [
                        {"string": f"Channel:: [[{transcript.get('channel', 'Unknown')}]]"},
                        {"string": f"URL:: {transcript.get('url', 'N/A')}"},
                        {"string": f"Date:: {transcript.get('upload_date', 'Unknown')}"},
                        {"string": "#youtube #transcript"},
                        {
                            "string": "Transcript",
                            "children": [
                                {"string": transcript.get("transcript", "No transcript available")}
                            ],
                        },
                    ],
                }
                roam_pages.append(page)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(roam_pages, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Roam export error: {e}")
            return False


class ExportPanel(tk.Frame):
    """UI panel for multi-format export."""

    EXPORT_FORMATS = {
        "Markdown (.md)": ("markdown", ".md", ExportFormats.export_markdown),
        "CSV (.csv)": ("csv", ".csv", ExportFormats.export_csv),
        "JSON (.json)": ("json", ".json", ExportFormats.export_json),
        "Obsidian Notes": ("obsidian", "", ExportFormats.export_obsidian),
        "Roam Research (.json)": ("roam", ".json", ExportFormats.export_roam),
    }

    def __init__(self, parent, get_transcripts: callable):
        super().__init__(parent, bg="white")
        self.get_transcripts = get_transcripts
        self._build_ui()

    def _build_ui(self):
        """Build export UI."""
        # Header
        tk.Label(self, text="Export Formats", font=FONTS["h2"], bg="white", fg=COLORS["text"]).pack(
            pady=SPACING["md"], anchor="w", padx=SPACING["md"]
        )

        # Format selection
        format_frame = tk.Frame(self, bg="white")
        format_frame.pack(fill="both", expand=True, padx=SPACING["md"])

        self.selected_format = tk.StringVar(value="Markdown (.md)")

        for format_name in self.EXPORT_FORMATS.keys():
            rb = tk.Radiobutton(
                format_frame,
                text=format_name,
                variable=self.selected_format,
                value=format_name,
                font=FONTS["body"],
                bg="white",
            )
            rb.pack(anchor="w", pady=4)

        # Export button
        tk.Button(
            self,
            text="Export Transcripts",
            font=FONTS["h3"],
            bg=COLORS["primary"],
            fg="white",
            relief="flat",
            padx=SPACING["lg"],
            pady=SPACING["sm"],
            command=self._handle_export,
            cursor="hand2",
        ).pack(pady=SPACING["md"])

    def _handle_export(self):
        """Handle export action."""
        format_name = self.selected_format.get()
        format_id, ext, export_func = self.EXPORT_FORMATS[format_name]

        transcripts = self.get_transcripts()

        if not transcripts:
            tk.messagebox.showwarning("No Data", "No transcripts to export")
            return

        # Handle folder vs file selection
        if format_id == "obsidian":
            path = filedialog.askdirectory(title="Select Obsidian vault folder")
        else:
            path = filedialog.asksaveasfilename(
                defaultextension=ext, filetypes=[(format_name, f"*{ext}"), ("All Files", "*.*")]
            )

        if path:
            success = export_func(transcripts, path)
            if success:
                tk.messagebox.showinfo(
                    "Export Successful", f"Exported {len(transcripts)} transcripts"
                )
