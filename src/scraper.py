"""YouTube Transcript Scraper Module

This module provides a simplified adapter over the core scraper engine.
It wraps core.scraper_engine.TranscriptScraper with a clean API suitable
for UI integration.

Target: ~200 lines
"""

from typing import List, Dict, Optional, Callable
from pathlib import Path

# Import existing core functionality (absolute from src/)
from core.scraper_engine import TranscriptScraper as CoreScraper


class TranscriptScraper:
    """Simplified API wrapper around core.scraper_engine.

    This adapter provides a clean interface for UI components while
    delegating all scraping logic to the existing core engine.

    Attributes:
        engine: The underlying CoreScraper instance
        output_dir: Directory where transcripts are saved
        callback: Optional callback function for logging
    """

    def __init__(self, output_dir: str = 'transcripts',
                 callback: Optional[Callable[[str], None]] = None):
        """Initialize the transcript scraper.

        Args:
            output_dir: Directory for saved transcripts (default: 'transcripts')
            callback: Optional logging callback function
        """
        self.output_dir = Path(output_dir)
        self.callback = callback or print

        # Create core engine instance
        self.engine = CoreScraper(str(self.output_dir), callback)

    def search_videos(self, query: str, max_results: int = 10,
                     filters: Optional[Dict] = None) -> List[Dict]:
        """Search YouTube videos and return metadata.

        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 10)
            filters: Optional dict with keys:
                - upload_date: Upload date filter (7, 30, 90, 180, 365, 'any')
                - sort_by: Sort order ('relevance', 'date', 'views', 'rating')

        Returns:
            List of video dicts with keys:
                - id: YouTube video ID
                - title: Video title
                - channel: Channel name
                - url: Full YouTube URL
                - upload_date: Upload date (if available)

        Raises:
            Exception: If search fails or times out

        Example:
            >>> scraper = TranscriptScraper()
            >>> results = scraper.search_videos('Python tutorial', max_results=5)
            >>> print(f"Found {len(results)} videos")
        """
        if filters is None:
            filters = {}

        return self.engine.search_videos(query, max_results, filters)

    def get_transcript(self, video_id: str) -> str:
        """Extract transcript for a YouTube video.

        Uses Selenium to navigate to the video page and extract the transcript
        from the DOM after clicking the "Show transcript" button.

        Args:
            video_id: YouTube video ID (11-character string)

        Returns:
            Transcript text as formatted paragraphs

        Raises:
            Exception: If transcript unavailable or extraction fails

        Example:
            >>> scraper = TranscriptScraper()
            >>> scraper.setup_browser()
            >>> transcript = scraper.get_transcript('dQw4w9WgXcQ')
            >>> print(transcript[:100])
        """
        return self.engine.get_transcript(video_id)

    def setup_browser(self):
        """Initialize Selenium WebDriver for transcript extraction.

        This must be called before get_transcript() or save_transcript().
        The browser instance is reused across multiple transcript extractions
        for efficiency.

        Raises:
            Exception: If Chrome browser or ChromeDriver not found

        Example:
            >>> scraper = TranscriptScraper()
            >>> scraper.setup_browser()
            >>> # Now can extract transcripts
            >>> scraper.get_transcript('dQw4w9WgXcQ')
        """
        self.engine.setup_browser()

    def save_transcript(self, video: Dict, transcript: str) -> str:
        """Save transcript to markdown file.

        Creates a markdown file with metadata header and transcript content.
        Filename format: [Title]_[Channel]_[Date].md

        Args:
            video: Video dict with keys: id, title, channel, url
            transcript: Transcript text to save

        Returns:
            Filename of saved transcript (without path)

        Raises:
            Exception: If file write fails

        Example:
            >>> scraper = TranscriptScraper(output_dir='./transcripts')
            >>> video = {'id': 'abc', 'title': 'Test', 'channel': 'Channel', 'url': 'http://...'}
            >>> transcript = "This is the transcript..."
            >>> filename = scraper.save_transcript(video, transcript)
            >>> print(f"Saved to {filename}")
        """
        return self.engine.save_transcript(video, transcript)

    @property
    def driver(self):
        """Access the underlying Selenium WebDriver instance.

        Returns:
            Selenium WebDriver instance or None if not initialized

        Example:
            >>> scraper = TranscriptScraper()
            >>> scraper.setup_browser()
            >>> if scraper.driver:
            ...     scraper.driver.quit()
        """
        return self.engine.driver if hasattr(self.engine, 'driver') else None

    def close(self):
        """Close the browser and cleanup resources.

        This should be called when done with transcript extraction to
        properly cleanup the Selenium WebDriver instance.

        Example:
            >>> scraper = TranscriptScraper()
            >>> scraper.setup_browser()
            >>> # ... extract transcripts ...
            >>> scraper.close()
        """
        if self.driver:
            self.driver.quit()

    def __enter__(self):
        """Context manager entry.

        Example:
            >>> with TranscriptScraper() as scraper:
            ...     scraper.setup_browser()
            ...     transcript = scraper.get_transcript('dQw4w9WgXcQ')
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup browser."""
        self.close()
