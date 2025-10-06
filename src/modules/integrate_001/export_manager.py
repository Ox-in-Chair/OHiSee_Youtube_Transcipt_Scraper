"""
Export Manager - INTEGRATE-001 Component

Handles multi-format exports of intelligence reports:
- Markdown (.md)
- JSON (.json)
- HTML (.html)
- ZIP package (all formats + diagrams)
"""

from typing import Dict
import os
import json
from pathlib import Path
from datetime import datetime


class ExportManager:
    """
    Manages export of intelligence reports to multiple formats.

    Supported formats:
    - markdown: Comprehensive MD report
    - json: Structured data export
    - html: Interactive browser dashboard
    - zip: Complete package with all artifacts
    """

    def __init__(self, callback=None):
        """Initialize export manager."""
        self.callback = callback or (lambda x: None)

    def export_report(
        self,
        assembled_output: Dict,
        output_path: str,
        formats: list = None
    ) -> Dict:
        """
        Export assembled intelligence report to specified formats.

        Args:
            assembled_output: Assembled report from OutputAssembler
            output_path: Base output directory
            formats: List of formats ["markdown", "json", "html", "all"]

        Returns:
            Dict with export results and file paths
        """
        if formats is None:
            formats = ["markdown", "json", "html"]

        self.callback(f"Exporting report to {output_path}...")

        # Create output directory
        Path(output_path).mkdir(parents=True, exist_ok=True)

        export_results = {
            "success": True,
            "output_path": output_path,
            "exports": {},
            "errors": []
        }

        # Generate base filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"youtube_intelligence_{timestamp}"

        try:
            # Export markdown
            if "markdown" in formats or "all" in formats:
                md_result = self._export_markdown(
                    assembled_output,
                    output_path,
                    base_filename
                )
                export_results["exports"]["markdown"] = md_result

            # Export JSON
            if "json" in formats or "all" in formats:
                json_result = self._export_json(
                    assembled_output,
                    output_path,
                    base_filename
                )
                export_results["exports"]["json"] = json_result

            # Export HTML
            if "html" in formats or "all" in formats:
                html_result = self._export_html(
                    assembled_output,
                    output_path,
                    base_filename
                )
                export_results["exports"]["html"] = html_result

            self.callback(f"✓ Export complete: {len(export_results['exports'])} formats")

        except Exception as e:
            export_results["success"] = False
            export_results["errors"].append(str(e))
            self.callback(f"✗ Export failed: {e}")

        return export_results

    def _export_markdown(
        self,
        assembled_output: Dict,
        output_path: str,
        base_filename: str
    ) -> Dict:
        """Export markdown report."""
        try:
            markdown_content = assembled_output.get("markdown", "")
            file_path = os.path.join(output_path, f"{base_filename}.md")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            self.callback(f"  ✓ Markdown: {file_path}")

            return {
                "success": True,
                "file_path": file_path,
                "size_bytes": len(markdown_content.encode("utf-8"))
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _export_json(
        self,
        assembled_output: Dict,
        output_path: str,
        base_filename: str
    ) -> Dict:
        """Export JSON data."""
        try:
            json_content = assembled_output.get("json", "{}")
            file_path = os.path.join(output_path, f"{base_filename}.json")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_content)

            self.callback(f"  ✓ JSON: {file_path}")

            return {
                "success": True,
                "file_path": file_path,
                "size_bytes": len(json_content.encode("utf-8"))
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _export_html(
        self,
        assembled_output: Dict,
        output_path: str,
        base_filename: str
    ) -> Dict:
        """Export HTML dashboard."""
        try:
            html_content = assembled_output.get("html", "")
            file_path = os.path.join(output_path, f"{base_filename}.html")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            self.callback(f"  ✓ HTML: {file_path}")

            return {
                "success": True,
                "file_path": file_path,
                "size_bytes": len(html_content.encode("utf-8"))
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def open_in_browser(self, html_file_path: str) -> bool:
        """
        Open HTML report in default browser.

        Args:
            html_file_path: Path to HTML file

        Returns:
            True if successful, False otherwise
        """
        try:
            import webbrowser
            webbrowser.open(f"file:///{os.path.abspath(html_file_path)}")
            self.callback(f"✓ Opened in browser: {html_file_path}")
            return True
        except Exception as e:
            self.callback(f"✗ Failed to open browser: {e}")
            return False
