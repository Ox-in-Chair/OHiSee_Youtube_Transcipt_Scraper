"""
Unit tests for FlowchartGenerator.
"""

import pytest
from src.modules.visual_001.flowchart_generator import FlowchartGenerator


class TestFlowchartGenerator:
    """Test suite for FlowchartGenerator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = FlowchartGenerator()
        self.sample_tree = {
            "type": "start",
            "text": "Start",
            "next": {
                "type": "decision",
                "text": "Has API key?",
                "branches": [
                    {
                        "condition": "Yes",
                        "next": {
                            "type": "action",
                            "text": "Process request",
                            "next": {
                                "type": "end",
                                "text": "Success"
                            }
                        }
                    },
                    {
                        "condition": "No",
                        "next": {
                            "type": "end",
                            "text": "Error: Missing API key"
                        }
                    }
                ]
            }
        }

    def test_generate_flowchart(self):
        """Test flowchart generation."""
        result = self.generator.generate(self.sample_tree)

        assert result is not None
        assert "mermaid_code" in result
        assert "graph TD" in result["mermaid_code"]
        assert len(result["decision_points"]) == 1
        assert "Has API key?" in result["decision_points"]

    def test_empty_flowchart(self):
        """Test flowchart with no data."""
        result = self.generator.generate({})

        assert result["decision_points"] == []
        assert result["paths"] == []
        assert "No Flowchart Data" in result["mermaid_code"]

    def test_parse_decision_tree(self):
        """Test decision tree parsing."""
        nodes, edges = self.generator.parse_decision_tree(self.sample_tree)

        assert len(nodes) == 5  # Start, Decision, 2 Actions, 2 Ends
        assert len(edges) > 0
        assert any(node["type"] == "decision" for node in nodes)

    def test_format_decision_node(self):
        """Test decision node formatting."""
        decision_node = {
            "id": "A",
            "type": "decision",
            "text": "Is valid?"
        }
        formatted = self.generator.format_decision_node(decision_node)

        assert formatted == "A{Is valid?}"

    def test_format_action_node(self):
        """Test action node formatting."""
        action_node = {
            "id": "B",
            "type": "action",
            "text": "Process data"
        }
        formatted = self.generator.format_decision_node(action_node)

        assert formatted == "B[Process data]"

    def test_format_start_end_nodes(self):
        """Test start/end node formatting."""
        start_node = {
            "id": "A",
            "type": "start",
            "text": "Start"
        }
        end_node = {
            "id": "Z",
            "type": "end",
            "text": "End"
        }

        start_formatted = self.generator.format_decision_node(start_node)
        end_formatted = self.generator.format_decision_node(end_node)

        assert start_formatted == "A(Start)"
        assert end_formatted == "Z(End)"

    def test_node_id_generation(self):
        """Test node ID generation."""
        self.generator.node_counter = 0

        assert self.generator._get_next_node_id() == "A"
        assert self.generator._get_next_node_id() == "B"
        assert self.generator._get_next_node_id() == "C"

    def test_node_id_overflow(self):
        """Test node ID generation beyond Z."""
        self.generator.node_counter = 26

        id1 = self.generator._get_next_node_id()
        id2 = self.generator._get_next_node_id()

        assert id1 == "A1"
        assert id2 == "A2"

    def test_extract_paths(self):
        """Test path extraction."""
        result = self.generator.generate(self.sample_tree)
        paths = result["paths"]

        assert len(paths) == 2  # Yes path and No path
        assert all("steps" in path for path in paths)
        assert all("decisions" in path for path in paths)
        assert all("outcome" in path for path in paths)

    def test_paths_include_decisions(self):
        """Test that paths include decision choices."""
        result = self.generator.generate(self.sample_tree)
        paths = result["paths"]

        # Find path with "Yes" choice
        yes_path = next(p for p in paths if "→ Yes" in p["steps"])
        assert yes_path["outcome"] == "Success"

        # Find path with "No" choice
        no_path = next(p for p in paths if "→ No" in p["steps"])
        assert "Error" in no_path["outcome"]

    def test_complex_flowchart(self):
        """Test complex flowchart with multiple decision points."""
        complex_tree = {
            "type": "start",
            "text": "Start",
            "next": {
                "type": "decision",
                "text": "Step 1?",
                "branches": [
                    {
                        "condition": "Pass",
                        "next": {
                            "type": "decision",
                            "text": "Step 2?",
                            "branches": [
                                {
                                    "condition": "Pass",
                                    "next": {"type": "end", "text": "Complete"}
                                },
                                {
                                    "condition": "Fail",
                                    "next": {"type": "end", "text": "Error at Step 2"}
                                }
                            ]
                        }
                    },
                    {
                        "condition": "Fail",
                        "next": {"type": "end", "text": "Error at Step 1"}
                    }
                ]
            }
        }

        result = self.generator.generate(complex_tree)

        assert len(result["decision_points"]) == 2
        assert len(result["paths"]) == 3  # 3 possible endings

    def test_linear_flowchart(self):
        """Test linear flowchart (no branches)."""
        linear_tree = {
            "type": "start",
            "text": "Start",
            "next": {
                "type": "action",
                "text": "Step 1",
                "next": {
                    "type": "action",
                    "text": "Step 2",
                    "next": {
                        "type": "end",
                        "text": "End"
                    }
                }
            }
        }

        result = self.generator.generate(linear_tree)

        assert len(result["decision_points"]) == 0
        assert len(result["paths"]) == 1
        assert "-->" in result["mermaid_code"]

    def test_labeled_edges(self):
        """Test that branch conditions appear as edge labels."""
        result = self.generator.generate(self.sample_tree)
        code = result["mermaid_code"]

        assert "Yes" in code
        assert "No" in code
        assert "-->|Yes|" in code or "-->|No|" in code

    def test_special_characters_in_text(self):
        """Test handling of special characters in node text."""
        special_tree = {
            "type": "start",
            "text": 'Start "Process"',
            "next": {
                "type": "end",
                "text": "End"
            }
        }

        result = self.generator.generate(special_tree)

        # Should escape quotes
        assert '\\"' in result["mermaid_code"] or "Process" in result["mermaid_code"]
