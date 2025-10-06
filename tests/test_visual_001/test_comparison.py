"""
Unit tests for ComparisonGenerator.
"""

import pytest
from src.modules.visual_001.comparison_generator import ComparisonGenerator


class TestComparisonGenerator:
    """Test suite for ComparisonGenerator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = ComparisonGenerator()
        self.sample_tools = ["Claude Code", "Cursor", "Windsurf"]
        self.sample_attributes = ["MCP Support", "Agentic Workflows", "Price"]
        self.sample_data = {
            "Claude Code": {
                "MCP Support": True,
                "Agentic Workflows": True,
                "Price": "Free"
            },
            "Cursor": {
                "MCP Support": False,
                "Agentic Workflows": True,
                "Price": "$20/mo"
            },
            "Windsurf": {
                "MCP Support": True,
                "Agentic Workflows": False,
                "Price": "$10/mo"
            }
        }

    def test_generate_comparison(self):
        """Test comparison generation."""
        result = self.generator.generate(
            self.sample_tools,
            self.sample_attributes,
            self.sample_data
        )

        assert result is not None
        assert "mermaid_code" in result
        assert result["entities"] == self.sample_tools
        assert result["attributes"] == self.sample_attributes

    def test_empty_comparison(self):
        """Test comparison with no data."""
        result = self.generator.generate([], [], {})

        assert result["entities"] == []
        assert result["attributes"] == []
        assert "No Comparison Data" in result["mermaid_code"]

    def test_calculate_winner_clear(self):
        """Test winner calculation with clear winner."""
        winner = self.generator.calculate_winner(self.sample_data)

        assert winner == "Claude Code"  # Has 2 True values

    def test_calculate_winner_tie(self):
        """Test winner calculation with tie."""
        tied_data = {
            "Tool A": {"Feature 1": True, "Feature 2": False},
            "Tool B": {"Feature 1": False, "Feature 2": True}
        }

        winner = self.generator.calculate_winner(tied_data)

        assert winner is None  # Tie should return None

    def test_calculate_winner_partial_support(self):
        """Test winner calculation with partial support."""
        partial_data = {
            "Tool A": {"Feature 1": "supported", "Feature 2": "partial"},
            "Tool B": {"Feature 1": "not supported", "Feature 2": "supported"}
        }

        winner = self.generator.calculate_winner(partial_data)

        assert winner == "Tool A"  # 1.5 points vs 1.0 points

    def test_format_feature_status_bool(self):
        """Test feature status formatting for booleans."""
        assert self.generator.format_feature_status(True) == "✅"
        assert self.generator.format_feature_status(False) == "❌"

    def test_format_feature_status_string(self):
        """Test feature status formatting for strings."""
        assert self.generator.format_feature_status("supported") == "✅"
        assert self.generator.format_feature_status("partial") == "⚠️"
        assert self.generator.format_feature_status("not supported") == "❌"
        assert self.generator.format_feature_status("$20/mo") == "$20/mo"

    def test_format_feature_status_number(self):
        """Test feature status formatting for numbers."""
        assert self.generator.format_feature_status(42) == "42"
        assert self.generator.format_feature_status(3.14) == "3.14"

    def test_subgraph_comparison(self):
        """Test subgraph-based comparison for complex data."""
        # 4+ attributes should trigger subgraph
        many_attributes = ["Attr1", "Attr2", "Attr3", "Attr4", "Attr5"]
        data = {
            "Tool A": {attr: True for attr in many_attributes}
        }

        result = self.generator.generate(["Tool A"], many_attributes, data)

        assert "subgraph" in result["mermaid_code"]

    def test_table_comparison(self):
        """Test table-based comparison for simple data."""
        # 3 or fewer attributes should trigger table
        result = self.generator.generate(
            self.sample_tools,
            self.sample_attributes,
            self.sample_data
        )

        # Should use table format (no subgraphs)
        assert "graph TD" in result["mermaid_code"]

    def test_sanitize_id(self):
        """Test ID sanitization."""
        assert self.generator._sanitize_id("Claude Code") == "Claude_Code"
        assert self.generator._sanitize_id("Tool-v2") == "Tool_v2"
        assert self.generator._sanitize_id("123Tool") == "T_123Tool"

    def test_comparison_with_missing_attributes(self):
        """Test comparison when tools have missing attributes."""
        incomplete_data = {
            "Tool A": {"Feature 1": True},
            "Tool B": {"Feature 2": False}
        }

        result = self.generator.generate(
            ["Tool A", "Tool B"],
            ["Feature 1", "Feature 2"],
            incomplete_data
        )

        assert result is not None
        # Should handle missing attributes gracefully

    def test_numeric_scoring(self):
        """Test numeric value scoring."""
        numeric_data = {
            "Tool A": {"Performance": 95, "Reliability": 88},
            "Tool B": {"Performance": 75, "Reliability": 92}
        }

        winner = self.generator.calculate_winner(numeric_data)

        assert winner == "Tool A"  # Higher total score
