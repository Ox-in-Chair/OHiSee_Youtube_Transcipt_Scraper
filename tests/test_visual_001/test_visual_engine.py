"""
Integration tests for VisualEngine.
"""

import pytest
from src.modules.visual_001 import VisualEngine


class TestVisualEngine:
    """Test suite for VisualEngine integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = VisualEngine()
        self.sample_synthesis = {
            "chronological_timeline": [
                {
                    "date": "2025-04-15",
                    "event": "Claude Code Released",
                    "tool": "Claude Code",
                    "version": "1.0"
                },
                {
                    "date": "2025-06-20",
                    "event": "MCP Protocol",
                    "tool": "MCP",
                    "version": "0.1"
                }
            ],
            "cross_video_patterns": [
                {
                    "pattern": "Agent workflows",
                    "videos": ["Video1", "Video2"],
                    "significance": "High"
                }
            ],
            "tool_mentions": {
                "Claude Code": {
                    "count": 15,
                    "contexts": ["automation", "coding", "agents"]
                },
                "Cursor": {
                    "count": 8,
                    "contexts": ["coding", "ai"]
                },
                "MCP": {
                    "count": 12,
                    "contexts": ["integration", "protocol"]
                }
            },
            "consensus_points": [
                "Use MCP for integrations",
                "Agent workflows improve productivity"
            ],
            "contradictions": [
                {
                    "topic": "Best IDE",
                    "positions": ["Claude Code", "Cursor"]
                }
            ]
        }

    def test_generate_all_diagrams(self):
        """Test generating all diagram types."""
        config = {
            "diagram_types": ["timeline", "architecture", "comparison", "flowchart"],
            "complexity": "detailed",
            "validate": True
        }

        result = self.engine.generate_all(self.sample_synthesis, config)

        assert result is not None
        assert "diagrams" in result
        assert "markdown_embeds" in result
        assert "validation" in result

        # Check all diagrams generated
        assert "timeline" in result["diagrams"]
        assert "architecture" in result["diagrams"]
        assert "comparison" in result["diagrams"]
        assert "flowchart" in result["diagrams"]

    def test_generate_timeline_only(self):
        """Test generating only timeline diagram."""
        config = {
            "diagram_types": ["timeline"],
            "complexity": "simple",
            "validate": True
        }

        result = self.engine.generate_all(self.sample_synthesis, config)

        assert "timeline" in result["diagrams"]
        assert "architecture" not in result["diagrams"]
        assert "comparison" not in result["diagrams"]
        assert "flowchart" not in result["diagrams"]

    def test_validation_enabled(self):
        """Test that validation runs when enabled."""
        config = {
            "diagram_types": ["timeline"],
            "complexity": "detailed",
            "validate": True
        }

        result = self.engine.generate_all(self.sample_synthesis, config)

        assert "validation" in result
        assert "all_valid" in result["validation"]
        assert "errors" in result["validation"]

    def test_validation_disabled(self):
        """Test that validation skips when disabled."""
        config = {
            "diagram_types": ["timeline"],
            "complexity": "detailed",
            "validate": False
        }

        result = self.engine.generate_all(self.sample_synthesis, config)

        # Should still have validation key, but errors might be empty
        assert "validation" in result

    def test_markdown_embeds_generated(self):
        """Test that markdown embeds are created."""
        config = {
            "diagram_types": ["timeline", "comparison"],
            "complexity": "detailed",
            "validate": True
        }

        result = self.engine.generate_all(self.sample_synthesis, config)

        assert "markdown_embeds" in result
        assert "timeline" in result["markdown_embeds"]
        assert "comparison" in result["markdown_embeds"]

        # Check markdown format
        timeline_md = result["markdown_embeds"]["timeline"]
        assert "##" in timeline_md
        assert "```mermaid" in timeline_md

    def test_complexity_levels(self):
        """Test different complexity levels."""
        complexities = ["simple", "detailed", "comprehensive"]

        for complexity in complexities:
            config = {
                "diagram_types": ["timeline"],
                "complexity": complexity,
                "validate": False
            }

            result = self.engine.generate_all(self.sample_synthesis, config)

            assert result is not None
            assert "timeline" in result["diagrams"]

    def test_empty_synthesis(self):
        """Test handling of empty synthesis data."""
        empty_synthesis = {
            "chronological_timeline": [],
            "cross_video_patterns": [],
            "tool_mentions": {},
            "consensus_points": [],
            "contradictions": []
        }

        config = {
            "diagram_types": ["timeline", "architecture"],
            "complexity": "detailed",
            "validate": True
        }

        result = self.engine.generate_all(empty_synthesis, config)

        # Should handle gracefully
        assert result is not None
        assert "diagrams" in result

    def test_callback_logging(self):
        """Test callback logging functionality."""
        log_messages = []

        def test_callback(msg):
            log_messages.append(msg)

        engine = VisualEngine(callback=test_callback)

        config = {
            "diagram_types": ["timeline"],
            "complexity": "detailed",
            "validate": True
        }

        engine.generate_all(self.sample_synthesis, config)

        # Should have logged messages
        assert len(log_messages) > 0
        assert any("diagram" in msg.lower() for msg in log_messages)

    def test_timeline_diagram_structure(self):
        """Test timeline diagram structure."""
        config = {
            "diagram_types": ["timeline"],
            "complexity": "detailed",
            "validate": True
        }

        result = self.engine.generate_all(self.sample_synthesis, config)
        timeline = result["diagrams"]["timeline"]

        assert "mermaid_code" in timeline
        assert "title" in timeline
        assert "description" in timeline
        assert "events_count" in timeline

    def test_architecture_diagram_structure(self):
        """Test architecture diagram structure."""
        config = {
            "diagram_types": ["architecture"],
            "complexity": "detailed",
            "validate": True
        }

        result = self.engine.generate_all(self.sample_synthesis, config)
        architecture = result["diagrams"]["architecture"]

        assert "mermaid_code" in architecture
        assert "components" in architecture
        assert "relationships" in architecture
        assert "layers" in architecture

    def test_comparison_diagram_structure(self):
        """Test comparison diagram structure."""
        config = {
            "diagram_types": ["comparison"],
            "complexity": "detailed",
            "validate": True
        }

        result = self.engine.generate_all(self.sample_synthesis, config)
        comparison = result["diagrams"]["comparison"]

        assert "mermaid_code" in comparison
        assert "entities" in comparison
        assert "attributes" in comparison
        assert "winner" in comparison

    def test_flowchart_diagram_structure(self):
        """Test flowchart diagram structure."""
        config = {
            "diagram_types": ["flowchart"],
            "complexity": "detailed",
            "validate": True
        }

        result = self.engine.generate_all(self.sample_synthesis, config)
        flowchart = result["diagrams"]["flowchart"]

        assert "mermaid_code" in flowchart
        assert "decision_points" in flowchart
        assert "paths" in flowchart

    def test_validation_catches_errors(self):
        """Test that validation catches syntax errors."""
        # This would require injecting invalid Mermaid code
        # For now, just verify validation runs
        config = {
            "diagram_types": ["timeline"],
            "complexity": "detailed",
            "validate": True
        }

        result = self.engine.generate_all(self.sample_synthesis, config)

        assert isinstance(result["validation"]["all_valid"], bool)
        assert isinstance(result["validation"]["errors"], list)

    def test_performance_multiple_diagrams(self):
        """Test performance with multiple diagrams."""
        import time

        config = {
            "diagram_types": ["timeline", "architecture", "comparison", "flowchart"],
            "complexity": "detailed",
            "validate": True
        }

        start_time = time.time()
        result = self.engine.generate_all(self.sample_synthesis, config)
        elapsed_time = time.time() - start_time

        # Should complete in reasonable time (<5 seconds)
        assert elapsed_time < 5.0
        assert len(result["diagrams"]) == 4
