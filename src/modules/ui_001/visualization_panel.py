"""Visualization Panel Component

Provides HTML-based Mermaid diagram display with:
- Timeline diagram rendering
- Architecture diagram display
- Comparison matrix visualization
- Flowchart rendering
- Export functionality
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Optional, Callable
import webbrowser
import tempfile


class VisualizationPanel:
    """Mermaid diagram visualization widget with HTML preview"""

    def __init__(self, parent, callback: Optional[Callable] = None):
        """Initialize visualization panel

        Args:
            parent: Parent tkinter widget
            callback: Optional logging callback function
        """
        self.parent = parent
        self.callback = callback or (lambda x: None)
        self.diagrams = {}
        self.current_diagram = None

        # Create main container
        self.container = ttk.Frame(parent)

        # Create header
        self._build_header()

        # Create diagram selector
        self._build_selector()

        # Create preview area
        self._build_preview()

        # Create action buttons
        self._build_actions()

    def _build_header(self):
        """Build header section"""
        header_frame = ttk.Frame(self.container)
        header_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(header_frame, text="Visual Diagrams", font=("Segoe UI", 14, "bold")).pack(
            anchor="w"
        )

        ttk.Label(
            header_frame,
            text="Interactive Mermaid diagrams for better understanding",
            font=("Segoe UI", 9),
            foreground="#6B7280",
        ).pack(anchor="w")

        ttk.Separator(self.container, orient="horizontal").pack(fill="x", padx=20, pady=10)

    def _build_selector(self):
        """Build diagram type selector"""
        selector_frame = ttk.Frame(self.container)
        selector_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(selector_frame, text="Select Diagram:", font=("Segoe UI", 10)).pack(
            side="left", padx=5
        )

        self.diagram_var = tk.StringVar()
        self.diagram_combo = ttk.Combobox(
            selector_frame,
            textvariable=self.diagram_var,
            state="readonly",
            width=40,
            font=("Segoe UI", 10),
        )
        self.diagram_combo.pack(side="left", padx=10, fill="x", expand=True)
        self.diagram_combo.bind("<<ComboboxSelected>>", self._on_diagram_selected)

        ttk.Button(selector_frame, text="Refresh", command=self._refresh_preview).pack(
            side="left", padx=5
        )

    def _build_preview(self):
        """Build diagram preview area"""
        preview_frame = ttk.LabelFrame(self.container, text="Diagram Preview", padding=10)
        preview_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Info label
        self.preview_info = ttk.Label(
            preview_frame,
            text="Select a diagram to preview",
            foreground="#6B7280",
            font=("Segoe UI", 9),
        )
        self.preview_info.pack(anchor="w", pady=5)

        # Diagram code preview
        code_label = ttk.Label(preview_frame, text="Mermaid Code:", font=("Segoe UI", 10))
        code_label.pack(anchor="w", pady=5)

        # Scrollable text area
        text_frame = ttk.Frame(preview_frame)
        text_frame.pack(fill="both", expand=True, pady=5)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        self.code_text = tk.Text(
            text_frame,
            wrap="word",
            yscrollcommand=scrollbar.set,
            font=("Consolas", 9),
            height=15,
        )
        self.code_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.code_text.yview)

        # Complexity indicator
        self.complexity_label = ttk.Label(
            preview_frame, text="Complexity: N/A", foreground="#6B7280"
        )
        self.complexity_label.pack(anchor="w", pady=5)

    def _build_actions(self):
        """Build action buttons"""
        action_frame = ttk.Frame(self.container)
        action_frame.pack(fill="x", padx=20, pady=10)

        ttk.Button(action_frame, text="Open in Browser", command=self._open_in_browser).pack(
            side="left", padx=5
        )

        ttk.Button(action_frame, text="Export as HTML", command=self._export_html).pack(
            side="left", padx=5
        )

        ttk.Button(action_frame, text="Export as Markdown", command=self._export_markdown).pack(
            side="left", padx=5
        )

        ttk.Button(action_frame, text="Copy Code", command=self._copy_code).pack(
            side="left", padx=5
        )

    def load_diagrams(self, diagrams: Dict):
        """Load diagrams data

        Args:
            diagrams: Dictionary of diagram data from VISUAL-001
        """
        self.diagrams = diagrams

        # Update combo box
        diagram_names = []
        for dtype, ddata in diagrams.items():
            if isinstance(ddata, dict) and "mermaid" in ddata:
                name = f"{dtype.replace('_', ' ').title()}"
                diagram_names.append(name)

        self.diagram_combo["values"] = diagram_names

        if diagram_names:
            self.diagram_combo.current(0)
            self._on_diagram_selected()
            self.callback(f"Loaded {len(diagram_names)} diagrams")

    def _on_diagram_selected(self, event=None):
        """Handle diagram selection change"""
        selection = self.diagram_var.get()
        if not selection:
            return

        # Find matching diagram
        dtype_key = selection.lower().replace(" ", "_")
        for key, data in self.diagrams.items():
            if key == dtype_key:
                self.current_diagram = data
                self._update_preview()
                break

    def _update_preview(self):
        """Update preview with selected diagram"""
        if not self.current_diagram:
            return

        # Update info
        dtype = self.current_diagram.get("type", "unknown")
        complexity = self.current_diagram.get("complexity", "N/A")

        generated_at = self.current_diagram.get("generated_at", "N/A")
        self.preview_info.config(
            text=f"Type: {dtype.replace('_', ' ').title()} | Generated: {generated_at}"
        )

        # Update code
        mermaid_code = self.current_diagram.get("mermaid", "")
        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", mermaid_code)

        # Update complexity
        self.complexity_label.config(text=f"Complexity: {complexity}")

    def _refresh_preview(self):
        """Refresh current diagram preview"""
        if self.current_diagram:
            self._update_preview()
            self.callback("Preview refreshed")

    def _open_in_browser(self):
        """Open diagram in browser with Mermaid Live"""
        if not self.current_diagram:
            messagebox.showwarning("No Diagram", "Please select a diagram to preview")
            return

        mermaid_code = self.current_diagram.get("mermaid", "")

        # Create HTML with Mermaid.js
        html_content = self._generate_html(mermaid_code)

        # Save to temp file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, encoding="utf-8"
        ) as f:
            f.write(html_content)
            temp_path = f.name

        # Open in browser
        webbrowser.open(f"file://{temp_path}")
        self.callback(f"Opened diagram in browser: {temp_path}")

    def _export_html(self):
        """Export diagram as standalone HTML"""
        if not self.current_diagram:
            messagebox.showwarning("No Diagram", "Please select a diagram to export")
            return

        # Ask for save location
        filepath = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
            initialfile=f"diagram_{self.current_diagram.get('type', 'unknown')}.html",
        )

        if not filepath:
            return

        mermaid_code = self.current_diagram.get("mermaid", "")
        html_content = self._generate_html(mermaid_code)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        messagebox.showinfo("Export Success", f"Diagram exported to:\n{filepath}")
        self.callback(f"Exported HTML to: {filepath}")

    def _export_markdown(self):
        """Export diagram as markdown with Mermaid code block"""
        if not self.current_diagram:
            messagebox.showwarning("No Diagram", "Please select a diagram to export")
            return

        # Ask for save location
        filepath = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
            initialfile=f"diagram_{self.current_diagram.get('type', 'unknown')}.md",
        )

        if not filepath:
            return

        mermaid_code = self.current_diagram.get("mermaid", "")
        markdown_content = self.current_diagram.get("markdown", "")

        if not markdown_content:
            # Generate markdown if not provided
            dtype = self.current_diagram.get("type", "unknown").replace("_", " ").title()
            markdown_content = f"# {dtype} Diagram\n\n```mermaid\n{mermaid_code}\n```\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        messagebox.showinfo("Export Success", f"Markdown exported to:\n{filepath}")
        self.callback(f"Exported Markdown to: {filepath}")

    def _copy_code(self):
        """Copy Mermaid code to clipboard"""
        if not self.current_diagram:
            messagebox.showwarning("No Diagram", "Please select a diagram first")
            return

        mermaid_code = self.current_diagram.get("mermaid", "")

        # Copy to clipboard
        self.parent.clipboard_clear()
        self.parent.clipboard_append(mermaid_code)
        self.parent.update()

        messagebox.showinfo(
            "Copied", "Mermaid code copied to clipboard!\nPaste it into Mermaid Live or your docs."
        )
        self.callback("Copied Mermaid code to clipboard")

    def _generate_html(self, mermaid_code: str) -> str:
        """Generate standalone HTML with Mermaid diagram

        Args:
            mermaid_code: Mermaid diagram code

        Returns:
            HTML content string
        """
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mermaid Diagram</title>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
            background-color: #f7f9fc;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1e40af;
            margin-bottom: 20px;
        }}
        .mermaid {{
            text-align: center;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Visual Diagram</h1>
        <div class="mermaid">
{mermaid_code}
        </div>
    </div>
</body>
</html>"""

    def pack(self, **kwargs):
        """Pack the panel container"""
        self.container.pack(**kwargs)

    def grid(self, **kwargs):
        """Grid the panel container"""
        self.container.grid(**kwargs)
