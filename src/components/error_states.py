"""Error state components with recovery guidance."""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, List
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING

class ErrorState(tk.Frame):
    """Reusable error state with icon, message, and recovery actions."""

    def __init__(self, parent, error_type: str, title: str, message: str,
                 recovery_actions: List[dict] = None):
        super().__init__(parent, bg='white', bd=1, relief='solid',
                        highlightbackground=COLORS['error'], highlightthickness=2)
        self.error_type = error_type
        self.title = title
        self.message = message
        self.recovery_actions = recovery_actions or []
        self._build_ui()

    def _build_ui(self):
        """Build the error state UI."""
        # Error header
        header = tk.Frame(self, bg=COLORS['error'])
        header.pack(fill='x')

        tk.Label(header, text='❌', font=('Segoe UI', 24),
                bg=COLORS['error'], fg='white').pack(side='left',
                                                     padx=SPACING['sm'],
                                                     pady=SPACING['xs'])

        tk.Label(header, text=self.title, font=FONTS['h3'],
                bg=COLORS['error'], fg='white').pack(side='left',
                                                     pady=SPACING['xs'])

        # Error message
        message_frame = tk.Frame(self, bg='white')
        message_frame.pack(fill='both', expand=True, padx=SPACING['md'],
                          pady=SPACING['md'])

        tk.Label(message_frame, text=self.message, font=FONTS['body'],
                bg='white', fg=COLORS['text'], wraplength=500,
                justify='left').pack(anchor='w')

        # Recovery actions
        if self.recovery_actions:
            actions_label = tk.Label(message_frame, text='Try these solutions:',
                                    font=FONTS['body'], bg='white',
                                    fg=COLORS['text'])
            actions_label.pack(anchor='w', pady=(SPACING['md'], SPACING['xs']))

            for action in self.recovery_actions:
                action_frame = tk.Frame(message_frame, bg='white')
                action_frame.pack(fill='x', pady=2)

                tk.Label(action_frame, text='•', font=FONTS['body'],
                        bg='white', fg=COLORS['primary']).pack(side='left')

                btn = tk.Button(action_frame, text=action['text'],
                               font=FONTS['body'], bg='white',
                               fg=COLORS['primary'], relief='flat',
                               cursor='hand2', anchor='w',
                               command=action.get('callback'))
                btn.pack(side='left', padx=SPACING['xs'])


class NetworkError(ErrorState):
    """Network connection error."""

    def __init__(self, parent, on_retry: Callable):
        super().__init__(
            parent,
            error_type='network',
            title='Network Connection Error',
            message='Could not connect to YouTube or OpenAI. Please check your internet connection and try again.',
            recovery_actions=[
                {'text': 'Retry', 'callback': on_retry},
                {'text': 'Check connection', 'callback': self._check_connection}
            ]
        )

    def _check_connection(self):
        """Guide user to check network connection."""
        import webbrowser
        webbrowser.open('https://www.google.com')


class APIKeyError(ErrorState):
    """API key validation error."""

    def __init__(self, parent, on_update_key: Callable):
        super().__init__(
            parent,
            error_type='api_key',
            title='Invalid API Key',
            message='The OpenAI API key is invalid or has expired. Please update your API key in settings.',
            recovery_actions=[
                {'text': 'Update API Key', 'callback': on_update_key},
                {'text': 'Disable AI optimization', 'callback': self._disable_ai}
            ]
        )

    def _disable_ai(self):
        """Disable AI optimization to bypass API key requirement."""
        # This would be handled by parent application
        pass


class SearchError(ErrorState):
    """Search execution error."""

    def __init__(self, parent, error_message: str, on_modify: Callable):
        super().__init__(
            parent,
            error_type='search',
            title='Search Failed',
            message=f'Search could not be completed: {error_message}',
            recovery_actions=[
                {'text': 'Modify search query', 'callback': on_modify},
                {'text': 'Try simpler query', 'callback': lambda: None}
            ]
        )


class TranscriptError(ErrorState):
    """Transcript extraction error."""

    def __init__(self, parent, video_title: str, on_skip: Callable):
        super().__init__(
            parent,
            error_type='transcript',
            title='Transcript Not Available',
            message=f'Could not extract transcript for "{video_title}". The video may not have captions enabled.',
            recovery_actions=[
                {'text': 'Skip this video', 'callback': on_skip},
                {'text': 'Try next video', 'callback': on_skip}
            ]
        )


class QuotaExceededError(ErrorState):
    """API quota exceeded error."""

    def __init__(self, parent, on_view_usage: Callable):
        super().__init__(
            parent,
            error_type='quota',
            title='Monthly Quota Exceeded',
            message='You have reached your monthly API usage limit. Upgrade your plan or wait until next month.',
            recovery_actions=[
                {'text': 'View usage details', 'callback': on_view_usage},
                {'text': 'Disable AI optimization', 'callback': lambda: None}
            ]
        )


class InlineErrorMessage(tk.Frame):
    """Inline error message for form validation."""

    def __init__(self, parent, message: str):
        super().__init__(parent, bg=COLORS['bg'])
        self.message = message
        self._build_ui()

    def _build_ui(self):
        """Build inline error message."""
        container = tk.Frame(self, bg='#FEE2E2', bd=1, relief='solid')
        container.pack(fill='x', pady=SPACING['xs'])

        tk.Label(container, text='⚠️', font=FONTS['body'],
                bg='#FEE2E2', fg=COLORS['error']).pack(side='left',
                                                      padx=SPACING['xs'],
                                                      pady=4)

        tk.Label(container, text=self.message, font=FONTS['small'],
                bg='#FEE2E2', fg=COLORS['error'],
                wraplength=400, justify='left').pack(side='left',
                                                    padx=(0, SPACING['xs']),
                                                    pady=4)

    def update_message(self, message: str):
        """Update error message."""
        self.message = message
        # Rebuild to show new message
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
