"""Toast notification system for user feedback."""

import tkinter as tk
from tkinter import ttk
from typing import Literal
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING

ToastType = Literal["success", "info", "warning", "error"]


class Toast(tk.Toplevel):
    """Individual toast notification."""

    ICONS = {"success": "✅", "info": "ℹ️", "warning": "⚠️", "error": "❌"}

    COLORS_MAP = {
        "success": COLORS["success"],
        "info": COLORS["primary"],
        "warning": COLORS["warning"],
        "error": COLORS["error"],
    }

    def __init__(self, parent, message: str, toast_type: ToastType = "info", duration: int = 4000):
        super().__init__(parent)

        self.message = message
        self.toast_type = toast_type
        self.duration = duration

        self._setup_window()
        self._build_ui()
        self._position_toast()
        self._auto_dismiss()

    def _setup_window(self):
        """Configure toast window."""
        self.overrideredirect(True)  # Remove window decorations
        self.attributes("-topmost", True)  # Always on top
        self.configure(bg=self.COLORS_MAP[self.toast_type])

    def _build_ui(self):
        """Build toast UI."""
        container = tk.Frame(
            self, bg=self.COLORS_MAP[self.toast_type], padx=SPACING["md"], pady=SPACING["sm"]
        )
        container.pack()

        # Icon
        icon_label = tk.Label(
            container,
            text=self.ICONS[self.toast_type],
            font=("Segoe UI", 20),
            bg=self.COLORS_MAP[self.toast_type],
            fg="white",
        )
        icon_label.pack(side="left", padx=(0, SPACING["xs"]))

        # Message
        message_label = tk.Label(
            container,
            text=self.message,
            font=FONTS["body"],
            bg=self.COLORS_MAP[self.toast_type],
            fg="white",
            wraplength=300,
            justify="left",
        )
        message_label.pack(side="left")

        # Close button
        close_btn = tk.Label(
            container,
            text="✕",
            font=FONTS["body"],
            bg=self.COLORS_MAP[self.toast_type],
            fg="white",
            cursor="hand2",
        )
        close_btn.pack(side="right", padx=(SPACING["sm"], 0))
        close_btn.bind("<Button-1>", lambda e: self.dismiss())

    def _position_toast(self):
        """Position toast in bottom-right corner."""
        self.update_idletasks()

        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Get toast dimensions
        toast_width = self.winfo_width()
        toast_height = self.winfo_height()

        # Position in bottom-right with margin
        x = screen_width - toast_width - 20
        y = screen_height - toast_height - 60

        self.geometry(f"+{x}+{y}")

        # Slide-in animation
        self._slide_in(x, screen_height)

    def _slide_in(self, target_x: int, start_y: int):
        """Animate toast sliding in from bottom."""
        current_y = start_y
        target_y = start_y - self.winfo_height() - 60

        def animate():
            nonlocal current_y
            if current_y > target_y:
                current_y -= 10
                self.geometry(f"+{target_x}+{current_y}")
                self.after(10, animate)

        animate()

    def _auto_dismiss(self):
        """Auto-dismiss toast after duration."""
        self.after(self.duration, self.dismiss)

    def dismiss(self):
        """Dismiss toast with fade-out animation."""
        self._fade_out()

    def _fade_out(self):
        """Fade out animation."""
        # Simple destroy for now - could add opacity animation
        self.destroy()


class ToastManager:
    """Manage toast notifications for the application."""

    def __init__(self, parent):
        self.parent = parent
        self.active_toasts = []
        self.toast_offset = 0

    def show(self, message: str, toast_type: ToastType = "info", duration: int = 4000):
        """Show a toast notification."""
        toast = Toast(self.parent, message, toast_type, duration)
        self.active_toasts.append(toast)

        # Stack toasts vertically
        self._reposition_toasts()

        # Remove from active list when dismissed
        toast.bind("<Destroy>", lambda e: self._remove_toast(toast))

    def _reposition_toasts(self):
        """Reposition all active toasts."""
        offset_y = 0
        for toast in reversed(self.active_toasts):
            if toast.winfo_exists():
                # Get current position
                current_geo = toast.geometry()
                x_pos = int(current_geo.split("+")[1])

                # New Y position with offset
                screen_height = toast.winfo_screenheight()
                new_y = screen_height - toast.winfo_height() - 60 - offset_y

                toast.geometry(f"+{x_pos}+{new_y}")
                offset_y += toast.winfo_height() + 10

    def _remove_toast(self, toast: Toast):
        """Remove toast from active list."""
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)
            self._reposition_toasts()

    def success(self, message: str, duration: int = 4000):
        """Show success toast."""
        self.show(message, "success", duration)

    def info(self, message: str, duration: int = 4000):
        """Show info toast."""
        self.show(message, "info", duration)

    def warning(self, message: str, duration: int = 4000):
        """Show warning toast."""
        self.show(message, "warning", duration)

    def error(self, message: str, duration: int = 5000):
        """Show error toast (5s for critical messages)."""
        self.show(message, "error", duration)

    def clear_all(self):
        """Dismiss all active toasts."""
        for toast in self.active_toasts[:]:
            if toast.winfo_exists():
                toast.dismiss()
        self.active_toasts = []
