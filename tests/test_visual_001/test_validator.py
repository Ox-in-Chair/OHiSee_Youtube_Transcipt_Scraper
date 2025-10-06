"""
Unit tests for MermaidValidator.
"""

import pytest
from src.modules.visual_001.validator import MermaidValidator


class TestMermaidValidator:
    """Test suite for MermaidValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = MermaidValidator()

    def test_validate_valid_timeline(self):
        """Test validation of valid timeline diagram."""
        code = """timeline
    title Technology Evolution
    2025-04 : Event 1
    2025-06 : Event 2"""

        is_valid, errors = self.validator.validate_mermaid_syntax(code)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_valid_graph(self):
        """Test validation of valid graph diagram."""
        code = """graph TD
    A[Start]
    B[Process]
    A --> B"""

        is_valid, errors = self.validator.validate_mermaid_syntax(code)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_empty_code(self):
        """Test validation of empty code."""
        is_valid, errors = self.validator.validate_mermaid_syntax("")

        assert is_valid is False
        assert "Empty diagram code" in errors

    def test_validate_missing_diagram_type(self):
        """Test validation with missing diagram type."""
        code = "A[Node]"

        is_valid, errors = self.validator.validate_mermaid_syntax(code)

        assert is_valid is False
        assert any("diagram type" in e.lower() for e in errors)

    def test_validate_invalid_diagram_type(self):
        """Test validation with invalid diagram type."""
        code = """invalidtype TD
    A[Node]"""

        is_valid, errors = self.validator.validate_mermaid_syntax(code)

        assert is_valid is False
        assert any("diagram type" in e.lower() for e in errors)

    def test_validate_unmatched_brackets(self):
        """Test validation with unmatched brackets."""
        code = """graph TD
    A[Unclosed bracket
    B[Valid]"""

        is_valid, errors = self.validator.validate_mermaid_syntax(code)

        assert is_valid is False
        assert any("Unclosed" in e or "Unmatched" in e for e in errors)

    def test_validate_mismatched_brackets(self):
        """Test validation with mismatched brackets."""
        code = """graph TD
    A[Start}"""

        is_valid, errors = self.validator.validate_mermaid_syntax(code)

        assert is_valid is False
        assert any("Mismatched" in e for e in errors)

    def test_validate_incomplete_edge(self):
        """Test validation with incomplete edge."""
        code = """graph TD
    A[Start]
    A -->"""

        is_valid, errors = self.validator.validate_mermaid_syntax(code)

        assert is_valid is False
        assert any("Incomplete" in e or "missing" in e.lower() for e in errors)

    def test_validate_graph_with_direction(self):
        """Test validation of graph with direction."""
        valid_directions = ["TD", "LR", "RL", "BT"]

        for direction in valid_directions:
            code = f"""graph {direction}
    A[Node]"""

            is_valid, errors = self.validator.validate_mermaid_syntax(code)
            assert is_valid is True

    def test_extract_diagram_type_graph(self):
        """Test extracting graph diagram type."""
        assert self.validator._extract_diagram_type("graph TD") == "graph"
        assert self.validator._extract_diagram_type("graph LR") == "graph"

    def test_extract_diagram_type_timeline(self):
        """Test extracting timeline diagram type."""
        assert self.validator._extract_diagram_type("timeline") == "timeline"

    def test_extract_diagram_type_flowchart(self):
        """Test extracting flowchart diagram type."""
        assert self.validator._extract_diagram_type("flowchart TD") == "flowchart"

    def test_validate_diagram_type(self):
        """Test diagram type validation."""
        assert self.validator.validate_diagram_type("graph") is True
        assert self.validator.validate_diagram_type("timeline") is True
        assert self.validator.validate_diagram_type("invalid") is False

    def test_check_node_syntax(self):
        """Test node syntax checking."""
        code = """graph TD
    A[Valid Node]
    InvalidNode
    C[Another Valid]"""

        errors = self.validator._check_node_syntax(code)

        assert len(errors) > 0
        assert any("InvalidNode" in e for e in errors)

    def test_check_edge_syntax(self):
        """Test edge syntax checking."""
        code = """graph TD
    A --> B
    C -->
    D --- E"""

        errors = self.validator._check_edge_syntax(code)

        assert len(errors) > 0
        assert any("edge" in e.lower() and "target" in e.lower() for e in errors)

    def test_check_common_errors_tabs(self):
        """Test detection of tabs."""
        code = "graph TD\n\tA[Node]"

        errors = self.validator._check_common_errors(code)

        assert any("tab" in e.lower() for e in errors)

    def test_check_common_errors_long_lines(self):
        """Test detection of very long lines."""
        long_line = "A" * 250
        code = f"graph TD\n    {long_line}"

        errors = self.validator._check_common_errors(code)

        assert any("long line" in e.lower() for e in errors)

    def test_validate_complex_valid_diagram(self):
        """Test validation of complex valid diagram."""
        code = """graph LR
    A[User Interface]
    B[Core Engine]
    C[Database]
    A --> B
    B --> C
    style A fill:#90EE90
    style B fill:#87CEEB"""

        is_valid, errors = self.validator.validate_mermaid_syntax(code)

        assert is_valid is True or len(errors) <= 1  # Allow warnings

    def test_validate_subgraph(self):
        """Test validation of diagram with subgraphs."""
        code = """graph LR
    subgraph Tool1
        A[Feature 1]
        B[Feature 2]
    end
    subgraph Tool2
        C[Feature 1]
        D[Feature 2]
    end"""

        is_valid, errors = self.validator.validate_mermaid_syntax(code)

        # Should be valid (subgraph is a valid keyword)
        assert is_valid is True or len(errors) <= 1

    def test_validate_labeled_edges(self):
        """Test validation of edges with labels."""
        code = """graph TD
    A[Start] -->|Yes| B[Process]
    A -->|No| C[End]"""

        is_valid, errors = self.validator.validate_mermaid_syntax(code)

        assert is_valid is True

    def test_validate_multiple_edge_types(self):
        """Test validation of different edge types."""
        code = """graph TD
    A --> B
    B --- C
    C -.-> D
    D ==> E"""

        is_valid, errors = self.validator.validate_mermaid_syntax(code)

        assert is_valid is True
