#!/usr/bin/env python3
"""YouTube Transcript Scraper - Application Entry Point

Launches the minimal application (app_minimal.py).

The modular ui/main_window.py has UX issues (can't deselect, scrolling, etc).
The working minimal app is clean and functional, so we use that instead.
"""

from app_minimal import YouTubeScraperApp


def main():
    """Launch the YouTube Transcript Scraper application.

    Uses the minimal app which has:
    - Working video selection/deselection
    - Proper scrolling
    - Clean compact UI
    - All core features
    """
    app = YouTubeScraperApp()
    app.mainloop()


if __name__ == '__main__':
    main()
