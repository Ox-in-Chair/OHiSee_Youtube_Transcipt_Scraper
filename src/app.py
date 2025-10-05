#!/usr/bin/env python3
"""YouTube Transcript Scraper - Application Entry Point

Launches the main application window.

This is the single entry point for the modular Phase 2 architecture.
All application logic is delegated to ui/main_window.py and its components.

Target: ~50 lines
"""

from ui.main_window import MainWindow


def main():
    """Launch the YouTube Transcript Scraper application.

    Creates and runs the main application window with all integrated
    components (search panel, results panel, download functionality).
    """
    app = MainWindow()
    app.mainloop()


if __name__ == '__main__':
    main()
