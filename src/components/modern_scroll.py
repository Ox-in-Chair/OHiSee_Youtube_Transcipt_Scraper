"""Modern scrollable frame with styled scrollbars.

Provides lightweight, accessible scrolling with modern visual design.
Replaces OS-default scrollbars with theme-compliant custom styling.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, SPACING


class ModernScrollFrame(tk.Frame):
    """Canvas-based scrollable frame with modern styled scrollbars.

    Features:
    - Custom scrollbar styling (rose_taupe track, medium_slate_blue thumb)
    - Mousewheel and touchpad gesture support
    - Keyboard navigation (arrow keys, Page Up/Down, Home/End)
    - Auto-hide scrollbars when not needed
    - Cross-platform compatible

    Usage:
        scroll_frame = ModernScrollFrame(parent)
        scroll_frame.pack(fill="both", expand=True)

        # Add widgets to scroll_frame.scrollable_frame instead of scroll_frame
        tk.Label(scroll_frame.scrollable_frame, text="Content").pack()
    """

    def __init__(self, parent, bg="white", **kwargs):
        super().__init__(parent, bg=bg, **kwargs)

        # Create canvas for scrolling
        self.canvas = tk.Canvas(
            self,
            bg=bg,
            highlightthickness=0,
            borderwidth=0
        )
        self.canvas.pack(side="left", fill="both", expand=True)

        # Custom styled vertical scrollbar
        self.scrollbar = ModernScrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview
        )
        self.scrollbar.pack(side="right", fill="y")

        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create frame inside canvas for content
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg)
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        # Bind events for dynamic scrolling
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Mousewheel support (cross-platform)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        # Keyboard navigation
        self.canvas.bind("<Up>", lambda e: self._scroll(-1))
        self.canvas.bind("<Down>", lambda e: self._scroll(1))
        self.canvas.bind("<Prior>", lambda e: self._scroll(-10))  # Page Up
        self.canvas.bind("<Next>", lambda e: self._scroll(10))   # Page Down
        self.canvas.bind("<Home>", lambda e: self.canvas.yview_moveto(0))
        self.canvas.bind("<End>", lambda e: self.canvas.yview_moveto(1))

        # Make canvas focusable for keyboard nav
        self.canvas.configure(takefocus=True)

    def _on_frame_configure(self, event):
        """Update scroll region when content size changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Auto-hide scrollbar if content fits
        if self.scrollable_frame.winfo_reqheight() <= self.canvas.winfo_height():
            self.scrollbar.pack_forget()
        else:
            self.scrollbar.pack(side="right", fill="y")

    def _on_canvas_configure(self, event):
        """Update canvas window width when canvas resizes."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _bind_mousewheel(self, event):
        """Bind mousewheel events when mouse enters canvas."""
        # Windows and MacOS use different events
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # Windows
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)    # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)    # Linux scroll down

    def _unbind_mousewheel(self, event):
        """Unbind mousewheel when mouse leaves canvas."""
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        """Handle mousewheel scroll events (cross-platform)."""
        if event.num == 4:  # Linux scroll up
            delta = 1
        elif event.num == 5:  # Linux scroll down
            delta = -1
        else:  # Windows/MacOS
            delta = int(event.delta / 120)

        self.canvas.yview_scroll(-delta, "units")

    def _scroll(self, units):
        """Scroll by specified units."""
        self.canvas.yview_scroll(units, "units")

    def scroll_to_top(self):
        """Scroll to top of content."""
        self.canvas.yview_moveto(0)

    def scroll_to_bottom(self):
        """Scroll to bottom of content."""
        self.canvas.yview_moveto(1)


class ModernScrollbar(tk.Canvas):
    """Custom-styled scrollbar with modern appearance.

    Features:
    - Slim design (8px width)
    - Rose taupe track, medium slate blue thumb
    - Hover state feedback
    - Smooth dragging
    """

    def __init__(self, parent, orient="vertical", command=None, **kwargs):
        super().__init__(
            parent,
            width=8 if orient == "vertical" else 100,
            height=100 if orient == "vertical" else 8,
            bg=COLORS["surface"],
            highlightthickness=0,
            borderwidth=0,
            **kwargs
        )

        self.orient = orient
        self.command = command
        self.pressed = False

        # Scrollbar thumb
        self.thumb = self.create_rectangle(
            0, 0, 8, 40,
            fill=COLORS["border"],  # rose_taupe
            outline="",
            tags="thumb"
        )

        # Bindings
        self.tag_bind("thumb", "<Enter>", self._on_hover)
        self.tag_bind("thumb", "<Leave>", self._on_leave)
        self.tag_bind("thumb", "<Button-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Button-1>", self._on_track_click)

        # Initial state
        self.thumb_pos = 0.0
        self.thumb_size = 0.2

    def set(self, first, last):
        """Update scrollbar position (called by scrolled widget).

        Args:
            first: Top of visible region (0.0 to 1.0)
            last: Bottom of visible region (0.0 to 1.0)
        """
        first = float(first)
        last = float(last)

        # Hide scrollbar if all content is visible
        if first <= 0.0 and last >= 1.0:
            self.itemconfig(self.thumb, state="hidden")
            return
        else:
            self.itemconfig(self.thumb, state="normal")

        # Calculate thumb position and size
        height = self.winfo_height()
        self.thumb_pos = first
        self.thumb_size = last - first

        # Update thumb rectangle
        top = int(first * height)
        bottom = int(last * height)
        self.coords(self.thumb, 0, top, 8, bottom)

    def _on_hover(self, event):
        """Visual feedback on hover."""
        self.itemconfig(self.thumb, fill=COLORS["primary"])  # medium_slate_blue

    def _on_leave(self, event):
        """Remove hover state."""
        if not self.pressed:
            self.itemconfig(self.thumb, fill=COLORS["border"])  # rose_taupe

    def _on_press(self, event):
        """Handle mouse press on thumb."""
        self.pressed = True
        self.press_y = event.y
        self.itemconfig(self.thumb, fill=COLORS["secondary"])  # lavender_pink

    def _on_drag(self, event):
        """Handle thumb dragging."""
        if not self.pressed:
            return

        height = self.winfo_height()
        delta = event.y - self.press_y
        scroll_delta = delta / height

        # Update scroll position via command
        if self.command:
            new_pos = self.thumb_pos + scroll_delta
            new_pos = max(0.0, min(1.0 - self.thumb_size, new_pos))
            self.command("moveto", new_pos)

        self.press_y = event.y

    def _on_release(self, event):
        """Handle mouse release."""
        self.pressed = False
        coords = self.coords(self.thumb)
        if coords:
            x1, y1, x2, y2 = coords
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.itemconfig(self.thumb, fill=COLORS["primary"])
            else:
                self.itemconfig(self.thumb, fill=COLORS["border"])

    def _on_track_click(self, event):
        """Handle click on scrollbar track (jump to position)."""
        # Check if click is on thumb
        coords = self.coords(self.thumb)
        if coords:
            x1, y1, x2, y2 = coords
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                return  # Click is on thumb, let drag handle it

        # Click is on track - jump to that position
        if self.command:
            height = self.winfo_height()
            position = event.y / height
            # Center thumb on click position
            position = max(0.0, min(1.0 - self.thumb_size, position - self.thumb_size / 2))
            self.command("moveto", position)


# Export components
__all__ = ["ModernScrollFrame", "ModernScrollbar"]
