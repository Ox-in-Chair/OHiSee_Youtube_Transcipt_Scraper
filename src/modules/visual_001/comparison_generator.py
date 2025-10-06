"""
VISUAL-001: Comparison Generator
Generates Mermaid comparison diagrams for tool/technology comparisons.
"""

from typing import List, Dict, Optional


class ComparisonGenerator:
    """
    Generate tool comparison diagrams using Mermaid.

    Supports two approaches:
    1. Subgraph-based (for complex comparisons)
    2. Table-based (for simple comparisons)
    """

    def __init__(self):
        """Initialize comparison generator."""
        self.status_icons = {
            "supported": "✅",
            "partial": "⚠️",
            "not_supported": "❌",
            "unknown": "❓",
        }

    def generate(
        self, tools: List[str], attributes: List[str], data: Dict[str, Dict[str, any]]
    ) -> Dict:
        """
        Generate tool comparison diagram.

        Args:
            tools: List of tool names to compare
            attributes: List of attributes/features to compare
            data: Nested dict mapping:
                tool_name -> attribute_name -> value (bool, str, or number)

        Returns:
            Dict with:
                - mermaid_code: str (Mermaid syntax)
                - entities: list[str] (tool names)
                - attributes: list[str] (feature names)
                - winner: str | None (tool with highest score)

        Example data structure:
            {
                "Claude Code": {
                    "MCP Support": True,
                    "Agentic Workflows": True,
                    "Price": "Free"
                },
                "Cursor": {
                    "MCP Support": False,
                    "Agentic Workflows": True,
                    "Price": "$20/mo"
                }
            }
        """
        if not tools or not attributes:
            return {
                "mermaid_code": "graph TD\n    A[No Comparison Data]",
                "entities": [],
                "attributes": [],
                "winner": None,
            }

        # Determine approach (subgraph vs table) based on complexity
        use_subgraph = len(attributes) > 3 or len(tools) > 3

        if use_subgraph:
            mermaid_code = self._build_subgraph_comparison(tools, attributes, data)
        else:
            mermaid_code = self._build_table_comparison(tools, attributes, data)

        # Calculate winner
        winner = self.calculate_winner(data)

        return {
            "mermaid_code": mermaid_code,
            "entities": tools,
            "attributes": attributes,
            "winner": winner,
        }

    def calculate_winner(self, scores: Dict[str, Dict[str, any]]) -> Optional[str]:
        """
        Calculate which tool wins based on features.

        Scoring:
        - True/supported: +1 point
        - partial: +0.5 points
        - False/not_supported: 0 points

        Args:
            scores: Nested dict of tool -> attribute -> value

        Returns:
            Tool name with highest score, or None if tie
        """
        tool_scores = {}

        for tool, attributes in scores.items():
            score = 0.0

            for attr, value in attributes.items():
                if isinstance(value, bool):
                    score += 1.0 if value else 0.0
                elif isinstance(value, str):
                    value_lower = value.lower()
                    if value_lower in ["supported", "yes", "true"]:
                        score += 1.0
                    elif value_lower in ["partial", "limited"]:
                        score += 0.5
                elif isinstance(value, (int, float)):
                    # Normalize numeric values (higher is better assumed)
                    score += min(value / 100, 1.0)

            tool_scores[tool] = score

        if not tool_scores:
            return None

        # Find highest score
        max_score = max(tool_scores.values())
        winners = [tool for tool, score in tool_scores.items() if score == max_score]

        # Return winner, or None if tie
        return winners[0] if len(winners) == 1 else None

    def format_feature_status(self, status: any) -> str:
        """
        Convert status to emoji representation.

        Args:
            status: bool, str, or number

        Returns:
            Emoji string
        """
        if isinstance(status, bool):
            return self.status_icons["supported"] if status else self.status_icons["not_supported"]

        elif isinstance(status, str):
            status_lower = status.lower()
            if status_lower in ["supported", "yes", "true"]:
                return self.status_icons["supported"]
            elif status_lower in ["partial", "limited"]:
                return self.status_icons["partial"]
            elif status_lower in ["not supported", "no", "false"]:
                return self.status_icons["not_supported"]
            else:
                # Return original string for non-status values
                return status

        elif isinstance(status, (int, float)):
            # Format numbers nicely
            return str(status)

        else:
            return str(status)

    def _build_subgraph_comparison(
        self, tools: List[str], attributes: List[str], data: Dict[str, Dict[str, any]]
    ) -> str:
        """
        Build subgraph-based comparison diagram.

        Each tool gets its own subgraph containing all attributes.

        Args:
            tools: Tool names
            attributes: Attribute names
            data: Comparison data

        Returns:
            Mermaid code
        """
        lines = ["graph LR"]

        # Create subgraph for each tool
        for tool in tools:
            tool_id = self._sanitize_id(tool)
            tool_data = data.get(tool, {})

            lines.append(f'    subgraph {tool_id}["{tool}"]')

            # Add each attribute as a node
            for i, attr in enumerate(attributes):
                attr_id = f"{tool_id}_attr{i}"
                value = tool_data.get(attr, "Unknown")
                status_icon = self.format_feature_status(value)

                # Create node with attribute and status
                node_text = f"{attr}: {status_icon}"
                lines.append(f'        {attr_id}["{node_text}"]')

            lines.append("    end")

        return "\n".join(lines)

    def _build_table_comparison(
        self, tools: List[str], attributes: List[str], data: Dict[str, Dict[str, any]]
    ) -> str:
        """
        Build table-based comparison diagram.

        Simple node-based layout for small comparisons.

        Args:
            tools: Tool names
            attributes: Attribute names
            data: Comparison data

        Returns:
            Mermaid code
        """
        lines = ["graph TD"]

        # Create header node
        lines.append('    Header["Comparison"]')

        # Create tool nodes
        for tool in tools:
            tool_id = self._sanitize_id(tool)
            tool_data = data.get(tool, {})

            # Build tool summary
            feature_list = []
            for attr in attributes:
                value = tool_data.get(attr, "Unknown")
                status_icon = self.format_feature_status(value)
                feature_list.append(f"{attr}: {status_icon}")

            # Create multi-line node
            features_text = "<br/>".join(feature_list)
            lines.append(f'    {tool_id}["{tool}<br/>{features_text}"]')

            # Connect to header
            lines.append(f"    Header --> {tool_id}")

        return "\n".join(lines)

    def _sanitize_id(self, text: str) -> str:
        """
        Convert text to valid Mermaid ID.

        Args:
            text: Original text

        Returns:
            Sanitized ID (alphanumeric + underscores)
        """
        # Replace spaces and special chars with underscores
        sanitized = "".join(c if c.isalnum() else "_" for c in text)

        # Remove consecutive underscores
        while "__" in sanitized:
            sanitized = sanitized.replace("__", "_")

        # Remove leading/trailing underscores
        sanitized = sanitized.strip("_")

        # Ensure it starts with a letter
        if sanitized and sanitized[0].isdigit():
            sanitized = "T_" + sanitized

        return sanitized or "Tool"
