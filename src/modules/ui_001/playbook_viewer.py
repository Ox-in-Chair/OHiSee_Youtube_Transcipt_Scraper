"""Playbook Viewer Component

Provides interactive step-by-step playbook display with:
- Sequential step navigation
- Code snippet highlighting
- Checklist progress tracking
- Copy-paste functionality
- Troubleshooting tips
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, List, Optional, Callable


class PlaybookViewer:
    """Interactive playbook viewer widget"""

    def __init__(self, parent, callback: Optional[Callable] = None):
        """Initialize playbook viewer

        Args:
            parent: Parent tkinter widget
            callback: Optional logging callback function
        """
        self.parent = parent
        self.callback = callback or (lambda x: None)
        self.playbooks = []
        self.current_playbook = None
        self.current_step = 0

        # Create main container
        self.container = ttk.Frame(parent)

        # Build UI
        self._build_header()
        self._build_playbook_selector()
        self._build_step_viewer()
        self._build_navigation()
        self._build_actions()

    def _build_header(self):
        """Build header section"""
        header_frame = ttk.Frame(self.container)
        header_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(
            header_frame, text="Implementation Playbooks", font=("Segoe UI", 14, "bold")
        ).pack(anchor="w")

        ttk.Label(
            header_frame,
            text="Step-by-step guides with copy-paste ready code",
            font=("Segoe UI", 9),
            foreground="#6B7280",
        ).pack(anchor="w")

        ttk.Separator(self.container, orient="horizontal").pack(fill="x", padx=20, pady=10)

    def _build_playbook_selector(self):
        """Build playbook selector"""
        selector_frame = ttk.Frame(self.container)
        selector_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(selector_frame, text="Select Playbook:", font=("Segoe UI", 10)).pack(
            side="left", padx=5
        )

        self.playbook_var = tk.StringVar()
        self.playbook_combo = ttk.Combobox(
            selector_frame,
            textvariable=self.playbook_var,
            state="readonly",
            width=50,
            font=("Segoe UI", 10),
        )
        self.playbook_combo.pack(side="left", padx=10, fill="x", expand=True)
        self.playbook_combo.bind("<<ComboboxSelected>>", self._on_playbook_selected)

    def _build_step_viewer(self):
        """Build step viewer area"""
        # Progress indicator
        progress_frame = ttk.Frame(self.container)
        progress_frame.pack(fill="x", padx=20, pady=5)

        self.progress_label = ttk.Label(
            progress_frame, text="No playbook selected", foreground="#6B7280"
        )
        self.progress_label.pack(side="left", padx=5)

        self.progress_bar = ttk.Progressbar(progress_frame, mode="determinate", length=300)
        self.progress_bar.pack(side="left", padx=10, fill="x", expand=True)

        # Step content frame
        content_frame = ttk.LabelFrame(self.container, text="Current Step", padding=10)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Step title
        self.step_title = ttk.Label(
            content_frame, text="", font=("Segoe UI", 12, "bold"), wraplength=700
        )
        self.step_title.pack(anchor="w", pady=5)

        # Step description
        desc_frame = ttk.Frame(content_frame)
        desc_frame.pack(fill="x", pady=5)

        ttk.Label(desc_frame, text="Description:", font=("Segoe UI", 10)).pack(anchor="w", pady=2)

        self.step_description = tk.Text(desc_frame, wrap="word", height=3, font=("Segoe UI", 9))
        self.step_description.pack(fill="x", pady=2)

        # Instructions
        instructions_frame = ttk.Frame(content_frame)
        instructions_frame.pack(fill="both", expand=True, pady=5)

        ttk.Label(instructions_frame, text="Instructions:", font=("Segoe UI", 10)).pack(
            anchor="w", pady=2
        )

        # Scrollable instructions
        scroll_frame = ttk.Frame(instructions_frame)
        scroll_frame.pack(fill="both", expand=True, pady=2)

        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side="right", fill="y")

        self.instructions_text = tk.Text(
            scroll_frame,
            wrap="word",
            yscrollcommand=scrollbar.set,
            font=("Consolas", 9),
            height=10,
        )
        self.instructions_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.instructions_text.yview)

        # Code snippet section
        code_frame = ttk.Frame(content_frame)
        code_frame.pack(fill="x", pady=5)

        self.code_label = ttk.Label(code_frame, text="Code Snippet:", font=("Segoe UI", 10))
        self.code_label.pack(anchor="w", pady=2)

        code_scroll_frame = ttk.Frame(code_frame)
        code_scroll_frame.pack(fill="x", pady=2)

        code_scrollbar = ttk.Scrollbar(code_scroll_frame)
        code_scrollbar.pack(side="right", fill="y")

        self.code_text = tk.Text(
            code_scroll_frame,
            wrap="none",
            yscrollcommand=code_scrollbar.set,
            font=("Consolas", 9),
            height=8,
            background="#f7f9fc",
        )
        self.code_text.pack(side="left", fill="x", expand=True)
        code_scrollbar.config(command=self.code_text.yview)

        ttk.Button(code_frame, text="Copy Code", command=self._copy_code).pack(anchor="e", pady=2)

        # Troubleshooting section
        trouble_frame = ttk.Frame(content_frame)
        trouble_frame.pack(fill="x", pady=5)

        self.trouble_label = ttk.Label(
            trouble_frame, text="Troubleshooting:", font=("Segoe UI", 10)
        )

        self.trouble_text = tk.Text(trouble_frame, wrap="word", height=4, font=("Segoe UI", 9))

    def _build_navigation(self):
        """Build step navigation controls"""
        nav_frame = ttk.Frame(self.container)
        nav_frame.pack(fill="x", padx=20, pady=10)

        # Previous button
        self.prev_btn = ttk.Button(
            nav_frame,
            text="← Previous Step",
            command=self._previous_step,
            state="disabled",
        )
        self.prev_btn.pack(side="left", padx=5)

        # Step indicator
        self.step_indicator = ttk.Label(nav_frame, text="Step 0 of 0", font=("Segoe UI", 10))
        self.step_indicator.pack(side="left", padx=20)

        # Next button
        self.next_btn = ttk.Button(
            nav_frame,
            text="Next Step →",
            command=self._next_step,
            state="disabled",
        )
        self.next_btn.pack(side="left", padx=5)

        # Jump to step
        ttk.Label(nav_frame, text="Jump to:").pack(side="left", padx=10)

        self.jump_var = tk.StringVar()
        self.jump_combo = ttk.Combobox(
            nav_frame, textvariable=self.jump_var, state="readonly", width=5
        )
        self.jump_combo.pack(side="left", padx=5)
        self.jump_combo.bind("<<ComboboxSelected>>", self._on_jump_selected)

        # Mark complete checkbox
        self.complete_var = tk.BooleanVar()
        self.complete_check = ttk.Checkbutton(
            nav_frame,
            text="Mark step complete",
            variable=self.complete_var,
            command=self._on_complete_changed,
        )
        self.complete_check.pack(side="right", padx=10)

    def _build_actions(self):
        """Build action buttons"""
        action_frame = ttk.Frame(self.container)
        action_frame.pack(fill="x", padx=20, pady=10)

        ttk.Button(action_frame, text="Export Playbook", command=self._export_playbook).pack(
            side="left", padx=5
        )

        ttk.Button(action_frame, text="Print Checklist", command=self._print_checklist).pack(
            side="left", padx=5
        )

        ttk.Button(action_frame, text="Reset Progress", command=self._reset_progress).pack(
            side="left", padx=5
        )

    def load_playbooks(self, playbooks: List[Dict]):
        """Load playbooks data

        Args:
            playbooks: List of playbook dictionaries from EXEC-001
        """
        self.playbooks = playbooks

        # Update combo box
        playbook_titles = [pb.get("title", f"Playbook {i}") for i, pb in enumerate(playbooks, 1)]
        self.playbook_combo["values"] = playbook_titles

        if playbook_titles:
            self.playbook_combo.current(0)
            self._on_playbook_selected()
            self.callback(f"Loaded {len(playbooks)} playbooks")

    def _on_playbook_selected(self, event=None):
        """Handle playbook selection"""
        selection = self.playbook_var.get()
        if not selection:
            return

        # Find matching playbook
        for pb in self.playbooks:
            if pb.get("title") == selection:
                self.current_playbook = pb
                self.current_step = 0
                self._update_viewer()
                break

    def _update_viewer(self):
        """Update viewer with current step"""
        if not self.current_playbook:
            return

        steps = self.current_playbook.get("steps", [])
        total_steps = len(steps)

        if total_steps == 0:
            self.step_title.config(text="No steps available")
            return

        # Update progress
        progress = ((self.current_step + 1) / total_steps) * 100
        self.progress_bar["value"] = progress
        self.progress_label.config(text=f"Progress: {self.current_step + 1}/{total_steps} steps")

        # Update step indicator
        self.step_indicator.config(text=f"Step {self.current_step + 1} of {total_steps}")

        # Update jump combo
        self.jump_combo["values"] = [str(i + 1) for i in range(total_steps)]

        # Get current step data
        step = steps[self.current_step]

        # Update step title
        self.step_title.config(text=step.get("title", "Untitled Step"))

        # Update description
        self.step_description.delete("1.0", "end")
        self.step_description.insert("1.0", step.get("description", ""))

        # Update instructions
        self.instructions_text.delete("1.0", "end")
        instructions = step.get("instructions", [])
        if isinstance(instructions, list):
            for i, inst in enumerate(instructions, 1):
                self.instructions_text.insert("end", f"{i}. {inst}\n")
        else:
            self.instructions_text.insert("1.0", instructions)

        # Update code snippet
        code = step.get("code", "")
        if code:
            self.code_label.pack(anchor="w", pady=2)
            self.code_text.delete("1.0", "end")
            self.code_text.insert("1.0", code)
        else:
            self.code_label.pack_forget()

        # Update troubleshooting
        troubleshooting = step.get("troubleshooting", "")
        if troubleshooting:
            self.trouble_label.pack(anchor="w", pady=2)
            self.trouble_text.pack(fill="x", pady=2)
            self.trouble_text.delete("1.0", "end")
            self.trouble_text.insert("1.0", troubleshooting)
        else:
            self.trouble_label.pack_forget()
            self.trouble_text.pack_forget()

        # Update navigation buttons
        self.prev_btn.config(state="normal" if self.current_step > 0 else "disabled")
        self.next_btn.config(state="normal" if self.current_step < total_steps - 1 else "disabled")

        # Update complete checkbox
        self.complete_var.set(step.get("completed", False))

    def _previous_step(self):
        """Navigate to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self._update_viewer()

    def _next_step(self):
        """Navigate to next step"""
        steps = self.current_playbook.get("steps", [])
        if self.current_step < len(steps) - 1:
            self.current_step += 1
            self._update_viewer()

    def _on_jump_selected(self, event=None):
        """Handle jump to step selection"""
        try:
            step_num = int(self.jump_var.get())
            self.current_step = step_num - 1
            self._update_viewer()
        except (ValueError, IndexError):
            pass

    def _on_complete_changed(self):
        """Handle step completion checkbox"""
        if not self.current_playbook:
            return

        steps = self.current_playbook.get("steps", [])
        if 0 <= self.current_step < len(steps):
            steps[self.current_step]["completed"] = self.complete_var.get()
            status = "complete" if self.complete_var.get() else "incomplete"
            self.callback(f"Step {self.current_step + 1} marked {status}")

    def _copy_code(self):
        """Copy code snippet to clipboard"""
        code = self.code_text.get("1.0", "end-1c")
        if code.strip():
            self.parent.clipboard_clear()
            self.parent.clipboard_append(code)
            self.parent.update()
            messagebox.showinfo("Copied", "Code copied to clipboard!")
            self.callback("Code snippet copied to clipboard")

    def _export_playbook(self):
        """Export playbook as markdown"""
        if not self.current_playbook:
            messagebox.showwarning("No Playbook", "Please select a playbook first")
            return

        title = self.current_playbook.get("title", "unknown").replace(" ", "_")
        filepath = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
            initialfile=f"playbook_{title}.md",
        )

        if not filepath:
            return

        # Generate markdown
        content = self._generate_playbook_markdown()

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        messagebox.showinfo("Export Success", f"Playbook exported to:\n{filepath}")
        self.callback(f"Exported playbook to: {filepath}")

    def _generate_playbook_markdown(self) -> str:
        """Generate markdown content for current playbook"""
        if not self.current_playbook:
            return ""

        lines = []
        lines.append(f"# {self.current_playbook.get('title', 'Playbook')}\n")
        lines.append(f"{self.current_playbook.get('description', '')}\n")
        lines.append("")

        for i, step in enumerate(self.current_playbook.get("steps", []), 1):
            lines.append(f"## Step {i}: {step.get('title', 'Untitled')}\n")
            lines.append(f"{step.get('description', '')}\n")
            lines.append("")

            lines.append("### Instructions\n")
            for j, inst in enumerate(step.get("instructions", []), 1):
                lines.append(f"{j}. {inst}")
            lines.append("")

            if step.get("code"):
                lines.append("### Code\n")
                lines.append("```")
                lines.append(step["code"])
                lines.append("```\n")

            if step.get("troubleshooting"):
                lines.append("### Troubleshooting\n")
                lines.append(step["troubleshooting"])
                lines.append("")

        return "\n".join(lines)

    def _print_checklist(self):
        """Print checklist view of playbook"""
        if not self.current_playbook:
            messagebox.showwarning("No Playbook", "Please select a playbook first")
            return

        # Generate checklist
        checklist = []
        checklist.append(f"# Checklist: {self.current_playbook.get('title', 'Playbook')}\n")
        checklist.append("")

        for i, step in enumerate(self.current_playbook.get("steps", []), 1):
            status = "✓" if step.get("completed") else "☐"
            checklist.append(f"{status} Step {i}: {step.get('title', 'Untitled')}")

        checklist_text = "\n".join(checklist)

        # Show in dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Playbook Checklist")
        dialog.geometry("600x400")

        text_widget = tk.Text(dialog, wrap="word", font=("Segoe UI", 10))
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", checklist_text)

        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

    def _reset_progress(self):
        """Reset all step completion status"""
        if not self.current_playbook:
            return

        if messagebox.askyesno(
            "Reset Progress", "Are you sure you want to reset all step progress?"
        ):
            for step in self.current_playbook.get("steps", []):
                step["completed"] = False

            self._update_viewer()
            self.callback("Playbook progress reset")

    def pack(self, **kwargs):
        """Pack the viewer container"""
        self.container.pack(**kwargs)

    def grid(self, **kwargs):
        """Grid the viewer container"""
        self.container.grid(**kwargs)
