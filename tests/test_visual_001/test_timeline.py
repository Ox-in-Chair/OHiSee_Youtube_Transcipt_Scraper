"""
Unit tests for TimelineGenerator.
"""

import pytest
from src.modules.visual_001.timeline_generator import TimelineGenerator


class TestTimelineGenerator:
    """Test suite for TimelineGenerator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = TimelineGenerator()
        self.sample_events = [
            {
                "date": "2025-04-15",
                "event": "Claude Code 1.0 Released",
                "tool": "Claude Code",
                "version": "1.0"
            },
            {
                "date": "2025-06-20",
                "event": "MCP Protocol Introduced",
                "tool": "MCP",
                "version": "0.1"
            },
            {
                "date": "2025-08-10",
                "event": "Agent System Update",
                "tool": "Claude Code",
                "version": "1.5"
            }
        ]

    def test_generate_simple_timeline(self):
        """Test simple timeline generation."""
        result = self.generator.generate(self.sample_events, complexity="simple")

        assert result is not None
        assert "mermaid_code" in result
        assert "timeline" in result["mermaid_code"]
        assert result["events_count"] <= 5
        assert result["title"] == "Technology Evolution Timeline (Simple View)"

    def test_generate_detailed_timeline(self):
        """Test detailed timeline generation."""
        result = self.generator.generate(self.sample_events, complexity="detailed")

        assert result is not None
        assert "mermaid_code" in result
        assert "timeline" in result["mermaid_code"]
        assert result["events_count"] == 3
        assert "2025-04" in result["mermaid_code"]
        assert "2025-06" in result["mermaid_code"]

    def test_generate_comprehensive_timeline(self):
        """Test comprehensive timeline generation."""
        result = self.generator.generate(
            self.sample_events,
            complexity="comprehensive"
        )

        assert result is not None
        assert "mermaid_code" in result
        assert result["events_count"] == 3

    def test_empty_events(self):
        """Test timeline with no events."""
        result = self.generator.generate([], complexity="detailed")

        assert result["events_count"] == 0
        assert "No Events Available" in result["mermaid_code"]

    def test_invalid_complexity(self):
        """Test invalid complexity level."""
        with pytest.raises(ValueError):
            self.generator.generate(self.sample_events, complexity="invalid")

    def test_group_by_month(self):
        """Test monthly grouping."""
        grouped = self.generator.group_by_timeperiod(
            self.sample_events,
            granularity="month"
        )

        assert "2025-04" in grouped
        assert "2025-06" in grouped
        assert "2025-08" in grouped

    def test_group_by_week(self):
        """Test weekly grouping."""
        grouped = self.generator.group_by_timeperiod(
            self.sample_events,
            granularity="week"
        )

        assert len(grouped) >= 3

    def test_format_event(self):
        """Test event formatting."""
        event = self.sample_events[0]
        formatted = self.generator.format_event(event)

        assert "Claude Code 1.0 Released" in formatted
        assert "Claude Code" in formatted
        assert "v1.0" in formatted

    def test_format_event_no_version(self):
        """Test event formatting without version."""
        event = {
            "date": "2025-05-01",
            "event": "Test Event",
            "tool": "Test Tool"
        }
        formatted = self.generator.format_event(event)

        assert "Test Event" in formatted
        assert "Test Tool" in formatted

    def test_get_top_events(self):
        """Test top events selection."""
        # Add more events
        many_events = self.sample_events + [
            {"date": "2025-09-01", "event": "Event 4", "tool": "Tool4"},
            {"date": "2025-10-01", "event": "Event 5", "tool": "Tool5"},
            {"date": "2025-11-01", "event": "Event 6", "tool": "Tool6", "version": "2.0"},
        ]

        top_events = self.generator._get_top_events(many_events, limit=3)

        assert len(top_events) == 3
        # Events with versions should be prioritized
        assert any(e.get("version") for e in top_events)

    def test_mermaid_syntax_valid(self):
        """Test that generated Mermaid syntax is valid."""
        result = self.generator.generate(self.sample_events, complexity="detailed")
        code = result["mermaid_code"]

        # Check for valid timeline syntax
        assert code.startswith("timeline")
        assert "title" in code
        lines = code.split("\n")
        assert all(line.startswith("    ") or line.startswith("timeline")
                   for line in lines if line.strip())

    def test_description_generation(self):
        """Test description generation."""
        result = self.generator.generate(self.sample_events, complexity="detailed")

        assert "3 events" in result["description"]
        assert "from 2025-04-15 to 2025-08-10" in result["description"]
        assert "tools/technologies" in result["description"]

    def test_chronological_sorting(self):
        """Test that events are sorted chronologically."""
        unsorted_events = [
            self.sample_events[2],  # 2025-08-10
            self.sample_events[0],  # 2025-04-15
            self.sample_events[1]   # 2025-06-20
        ]

        result = self.generator.generate(unsorted_events, complexity="detailed")
        code = result["mermaid_code"]

        # Find positions of dates in code
        pos_april = code.find("2025-04")
        pos_june = code.find("2025-06")
        pos_august = code.find("2025-08")

        # Verify chronological order in output
        assert pos_april < pos_june < pos_august
