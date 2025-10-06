"""
VISUAL-001: Timeline Generator
Generates Mermaid timeline diagrams for technology evolution visualization.
"""

from datetime import datetime
from typing import List, Dict
from collections import defaultdict


class TimelineGenerator:
    """
    Generate Mermaid timeline diagrams from chronological events.

    Supports three complexity levels:
    - simple: Major events only (top 5)
    - detailed: Monthly grouping (default)
    - comprehensive: Weekly granularity
    """

    def __init__(self):
        """Initialize timeline generator."""
        self.supported_complexities = ["simple", "detailed", "comprehensive"]

    def generate(self, events: List[Dict], complexity: str = "detailed") -> Dict:
        """
        Generate Mermaid timeline diagram.

        Args:
            events: List of event dictionaries with keys:
                - date: str (YYYY-MM-DD format)
                - event: str (event description)
                - tool: str (tool/technology name)
                - version: str (version number, optional)
            complexity: str ("simple"|"detailed"|"comprehensive")

        Returns:
            Dict with:
                - mermaid_code: str (Mermaid syntax)
                - title: str (diagram title)
                - description: str (summary)
                - events_count: int (number of events included)

        Raises:
            ValueError: If complexity level is invalid
        """
        if complexity not in self.supported_complexities:
            raise ValueError(
                f"Invalid complexity '{complexity}'. "
                f"Must be one of: {self.supported_complexities}"
            )

        if not events:
            return {
                "mermaid_code": "timeline\n    title No Events Available",
                "title": "No Events Available",
                "description": "No events provided for timeline generation",
                "events_count": 0,
            }

        # Sort events chronologically
        sorted_events = sorted(events, key=lambda e: e.get("date", ""))

        # Filter events based on complexity
        if complexity == "simple":
            filtered_events = self._get_top_events(sorted_events, limit=5)
        else:
            filtered_events = sorted_events

        # Group events by time period
        granularity = self._get_granularity(complexity)
        grouped_events = self.group_by_timeperiod(filtered_events, granularity)

        # Generate Mermaid code
        mermaid_code = self._build_mermaid_timeline(grouped_events, complexity)

        # Generate metadata
        title = f"Technology Evolution Timeline ({complexity.title()} View)"
        description = self._generate_description(filtered_events, complexity)

        return {
            "mermaid_code": mermaid_code,
            "title": title,
            "description": description,
            "events_count": len(filtered_events),
        }

    def group_by_timeperiod(self, events: List[Dict], granularity: str) -> Dict[str, List[Dict]]:
        """
        Group events by time period (month or week).

        Args:
            events: List of event dictionaries
            granularity: str ("month"|"week")

        Returns:
            Dict mapping period keys to event lists
        """
        grouped = defaultdict(list)

        for event in events:
            date_str = event.get("date", "")
            if not date_str:
                continue

            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")

                if granularity == "month":
                    period_key = date_obj.strftime("%Y-%m")
                elif granularity == "week":
                    # ISO week format (YYYY-Www)
                    period_key = date_obj.strftime("%Y-W%U")
                else:
                    period_key = date_str

                grouped[period_key].append(event)
            except ValueError:
                # Skip invalid dates
                continue

        return dict(grouped)

    def format_event(self, event: Dict) -> str:
        """
        Format single event for Mermaid timeline.

        Format: "Event : Tool version"

        Args:
            event: Event dictionary

        Returns:
            Formatted event string
        """
        event_text = event.get("event", "Unknown Event")
        tool = event.get("tool", "")
        version = event.get("version", "")

        # Build suffix (tool + version)
        suffix_parts = []
        if tool:
            suffix_parts.append(tool)
        if version:
            suffix_parts.append(f"v{version}")

        suffix = " ".join(suffix_parts) if suffix_parts else ""

        if suffix:
            return f"{event_text} : {suffix}"
        else:
            return event_text

    def _get_top_events(self, events: List[Dict], limit: int = 5) -> List[Dict]:
        """
        Get top N most important events.

        Priority:
        1. Events with version numbers
        2. Events with tool mentions
        3. Most recent events

        Args:
            events: List of all events
            limit: Maximum number of events to return

        Returns:
            List of top events
        """
        # Score events by importance
        scored_events = []
        for event in events:
            score = 0
            if event.get("version"):
                score += 3
            if event.get("tool"):
                score += 2
            # Recent events get higher score
            try:
                date_obj = datetime.strptime(event.get("date", ""), "%Y-%m-%d")
                days_old = (datetime.now() - date_obj).days
                recency_score = max(0, 365 - days_old) / 365
                score += recency_score
            except ValueError:
                pass

            scored_events.append((score, event))

        # Sort by score descending
        scored_events.sort(key=lambda x: x[0], reverse=True)

        # Return top N events
        return [event for score, event in scored_events[:limit]]

    def _get_granularity(self, complexity: str) -> str:
        """Get time granularity for complexity level."""
        if complexity == "comprehensive":
            return "week"
        else:
            return "month"

    def _build_mermaid_timeline(
        self, grouped_events: Dict[str, List[Dict]], complexity: str
    ) -> str:
        """
        Build Mermaid timeline syntax from grouped events.

        Args:
            grouped_events: Dict mapping period keys to events
            complexity: Complexity level

        Returns:
            Mermaid timeline code
        """
        lines = ["timeline"]
        lines.append("    title Technology Evolution Timeline")

        # Sort periods chronologically
        sorted_periods = sorted(grouped_events.keys())

        for period in sorted_periods:
            events = grouped_events[period]

            # Format period label
            period_label = self._format_period_label(period, complexity)

            # Add events for this period
            for event in events:
                event_text = self.format_event(event)
                # Escape special characters
                event_text = event_text.replace('"', '\\"')
                lines.append(f"    {period_label} : {event_text}")

        return "\n".join(lines)

    def _format_period_label(self, period_key: str, complexity: str) -> str:
        """
        Format period label for display.

        Args:
            period_key: Period identifier (YYYY-MM or YYYY-Www)
            complexity: Complexity level

        Returns:
            Formatted label
        """
        # For month periods (YYYY-MM)
        if len(period_key) == 7 and period_key[4] == "-":
            return period_key

        # For week periods (YYYY-Www)
        if "W" in period_key:
            year, week = period_key.split("-W")
            return f"{year}-W{week}"

        # Fallback
        return period_key

    def _generate_description(self, events: List[Dict], complexity: str) -> str:
        """
        Generate human-readable description of timeline.

        Args:
            events: List of events
            complexity: Complexity level

        Returns:
            Description string
        """
        if not events:
            return "No events available"

        event_count = len(events)

        # Get date range
        dates = [e.get("date", "") for e in events if e.get("date")]
        if dates:
            start_date = min(dates)
            end_date = max(dates)
            date_range = f"from {start_date} to {end_date}"
        else:
            date_range = "across all time"

        # Get unique tools
        tools = set(e.get("tool", "") for e in events if e.get("tool"))
        tool_count = len(tools)

        description = (
            f"Timeline showing {event_count} events {date_range}. "
            f"Covers {tool_count} tools/technologies. "
            f"View: {complexity}."
        )

        return description
