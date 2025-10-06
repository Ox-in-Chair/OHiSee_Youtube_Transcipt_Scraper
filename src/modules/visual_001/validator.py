"""
VISUAL-001: Mermaid Syntax Validator
Validates Mermaid diagram syntax for correctness.
"""

import re
from typing import Tuple, List


class MermaidValidator:
    """
    Validate Mermaid diagram syntax.

    Checks for:
    - Valid diagram types
    - Proper node syntax
    - Valid edge syntax
    - No syntax errors (unmatched brackets, etc.)
    """

    def __init__(self):
        """Initialize validator with syntax rules."""
        self.valid_diagram_types = [
            "graph",
            "flowchart",
            "sequenceDiagram",
            "classDiagram",
            "stateDiagram",
            "erDiagram",
            "journey",
            "gantt",
            "pie",
            "timeline",
        ]

        # Node shape patterns
        self.node_patterns = {
            "rectangle": r"\w+\[.*?\]",
            "rounded": r"\w+\(.*?\)",
            "stadium": r"\w+\(\[.*?\]\)",
            "subroutine": r"\w+\[\[.*?\]\]",
            "cylindrical": r"\w+\[\(.*?\)\]",
            "circle": r"\w+\(\(.*?\)\)",
            "diamond": r"\w+\{.*?\}",
            "hexagon": r"\w+\{\{.*?\}\}",
            "parallelogram": r"\w+\[/.*?/\]",
            "trapezoid": r"\w+\[\\.*?/\]",
        }

        # Edge patterns
        self.edge_patterns = [
            r"-->",  # Arrow
            r"---",  # Line
            r"-\.-",  # Dotted line
            r"==>",  # Thick arrow
            r"===",  # Thick line
            r"-\.\->",  # Dotted arrow
            r"--\w+-->",  # Labeled arrow
            r"--\w+---",  # Labeled line
            r"-->\|.*?\|",  # Text on arrow
            r"---\|.*?\|",  # Text on line
        ]

    def validate_mermaid_syntax(self, code: str) -> Tuple[bool, List[str]]:
        """
        Validate Mermaid diagram syntax.

        Args:
            code: Mermaid diagram code

        Returns:
            Tuple of (is_valid: bool, errors: list[str])

        Example:
            is_valid, errors = validator.validate_mermaid_syntax(mermaid_code)
            if not is_valid:
                print(f"Errors: {errors}")
        """
        errors = []

        if not code or not code.strip():
            return False, ["Empty diagram code"]

        lines = code.strip().split("\n")

        # Check diagram type (first line)
        if not lines:
            return False, ["No diagram type specified"]

        first_line = lines[0].strip()
        diagram_type = self._extract_diagram_type(first_line)

        if not diagram_type:
            errors.append(f"Invalid or missing diagram type: '{first_line}'")
        elif diagram_type not in self.valid_diagram_types:
            errors.append(
                f"Unknown diagram type: '{diagram_type}'. "
                f"Valid types: {', '.join(self.valid_diagram_types)}"
            )

        # Check for unmatched brackets
        bracket_errors = self._check_brackets(code)
        errors.extend(bracket_errors)

        # Check node syntax (for graph/flowchart diagrams)
        if diagram_type in ["graph", "flowchart"]:
            node_errors = self._check_node_syntax(code)
            errors.extend(node_errors)

            # Check edge syntax
            edge_errors = self._check_edge_syntax(code)
            errors.extend(edge_errors)

        # Check for common syntax errors
        common_errors = self._check_common_errors(code)
        errors.extend(common_errors)

        is_valid = len(errors) == 0
        return is_valid, errors

    def _extract_diagram_type(self, first_line: str) -> str:
        """
        Extract diagram type from first line.

        Args:
            first_line: First line of Mermaid code

        Returns:
            Diagram type string, or empty string if not found
        """
        # Remove whitespace
        first_line = first_line.strip()

        # Check for graph with direction (e.g., "graph TD", "graph LR")
        if first_line.startswith("graph"):
            return "graph"

        # Check for flowchart with direction
        if first_line.startswith("flowchart"):
            return "flowchart"

        # Check for other diagram types (exact match)
        for dtype in self.valid_diagram_types:
            if first_line.startswith(dtype):
                return dtype

        return ""

    def _check_brackets(self, code: str) -> List[str]:
        """
        Check for unmatched brackets, parentheses, braces.

        Args:
            code: Mermaid code

        Returns:
            List of error messages
        """
        errors = []

        # Stack-based bracket matching
        bracket_pairs = {"[": "]", "(": ")", "{": "}"}

        stack = []
        line_num = 0

        for line in code.split("\n"):
            line_num += 1

            for i, char in enumerate(line):
                if char in bracket_pairs:
                    # Opening bracket
                    stack.append((char, line_num, i))
                elif char in bracket_pairs.values():
                    # Closing bracket
                    if not stack:
                        errors.append(
                            f"Line {line_num}: Unmatched closing bracket '{char}' at position {i}"
                        )
                    else:
                        open_bracket, open_line, open_pos = stack.pop()
                        expected_close = bracket_pairs[open_bracket]

                        if char != expected_close:
                            errors.append(
                                f"Line {line_num}: Mismatched bracket - "
                                f"expected '{expected_close}' but found '{char}'"
                            )

        # Check for unclosed brackets
        if stack:
            for bracket, line_num, pos in stack:
                errors.append(f"Line {line_num}: Unclosed bracket '{bracket}' at position {pos}")

        return errors

    def _check_node_syntax(self, code: str) -> List[str]:
        """
        Check node definitions for syntax errors.

        Args:
            code: Mermaid code

        Returns:
            List of error messages
        """
        errors = []
        line_num = 0

        for line in code.split("\n"):
            line_num += 1
            stripped = line.strip()

            # Skip empty lines, comments, diagram type
            if not stripped or stripped.startswith("%%") or line_num == 1:
                continue

            # Check if line contains a node definition
            has_node = False
            for pattern in self.node_patterns.values():
                if re.search(pattern, stripped):
                    has_node = True
                    break

            # Check if line contains an edge
            has_edge = any(re.search(pattern, stripped) for pattern in self.edge_patterns)

            # If line has content but no valid node or edge, it might be an error
            # (unless it's a subgraph, style, or other directive)
            if stripped and not has_node and not has_edge:
                if not any(
                    keyword in stripped
                    for keyword in ["subgraph", "end", "style", "class", "click", "title"]
                ):
                    # This might be a node without proper brackets
                    if ":" in stripped and not stripped.startswith("    "):
                        # Likely a timeline or other special syntax
                        continue

                    # Check for common mistake: node without brackets
                    if re.match(r"^\s*\w+\s*$", stripped):
                        errors.append(
                            f"Line {line_num}: Node '{stripped}' missing shape brackets "
                            f"(e.g., [text], (text), {{text}})"
                        )

        return errors

    def _check_edge_syntax(self, code: str) -> List[str]:
        """
        Check edge definitions for syntax errors.

        Args:
            code: Mermaid code

        Returns:
            List of error messages
        """
        errors = []
        line_num = 0

        for line in code.split("\n"):
            line_num += 1
            stripped = line.strip()

            # Check for edges with potential syntax errors
            if "--" in stripped or "==" in stripped:
                # Check for incomplete arrows
                if stripped.endswith("--") or stripped.endswith("=="):
                    errors.append(f"Line {line_num}: Incomplete edge definition (missing arrow)")

                # Check for edges without target
                if "-->" in stripped or "---" in stripped:
                    parts = re.split(r"-->|---", stripped)
                    if len(parts) == 2 and not parts[1].strip():
                        errors.append(f"Line {line_num}: Edge missing target node")

        return errors

    def _check_common_errors(self, code: str) -> List[str]:
        """
        Check for common Mermaid syntax errors.

        Args:
            code: Mermaid code

        Returns:
            List of error messages
        """
        errors = []

        # Check for tabs (Mermaid prefers spaces)
        if "\t" in code:
            errors.append("Warning: Code contains tabs. Mermaid prefers spaces for indentation.")

        # Check for excessively long lines (readability)
        for i, line in enumerate(code.split("\n"), 1):
            if len(line) > 200:
                errors.append(
                    f"Line {i}: Very long line ({len(line)} chars). "
                    "Consider breaking into multiple lines."
                )

        return errors

    def validate_diagram_type(self, diagram_type: str) -> bool:
        """
        Check if diagram type is valid.

        Args:
            diagram_type: Diagram type string

        Returns:
            True if valid, False otherwise
        """
        return diagram_type in self.valid_diagram_types
