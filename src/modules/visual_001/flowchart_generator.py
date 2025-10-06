"""
VISUAL-001: Flowchart Generator
Generates Mermaid flowchart diagrams for decision trees and workflows.
"""

from typing import List, Dict, Optional


class FlowchartGenerator:
    """
    Generate Mermaid flowchart diagrams from decision trees.

    Supports:
    - Decision nodes (diamonds)
    - Action nodes (rectangles)
    - Terminal nodes (rounded rectangles)
    - Conditional branches (Yes/No paths)
    """

    def __init__(self):
        """Initialize flowchart generator."""
        self.node_counter = 0
        self.node_map = {}
        self.node_shapes = {
            "start": ("(", ")"),  # Rounded rectangle
            "end": ("(", ")"),  # Rounded rectangle
            "decision": ("{", "}"),  # Diamond
            "action": ("[", "]"),  # Rectangle
            "process": ("[", "]"),  # Rectangle
        }

    def generate(self, decision_tree: Dict) -> Dict:
        """
        Generate Mermaid flowchart from decision tree.

        Args:
            decision_tree: Nested dict representing workflow:
                {
                    "type": "start"|"end"|"decision"|"action",
                    "text": str (node label),
                    "next": dict | list[dict] (child nodes),
                    "branches": list[dict] (for decision nodes)
                        [
                            {"condition": "Yes", "next": {...}},
                            {"condition": "No", "next": {...}}
                        ]
                }

        Returns:
            Dict with:
                - mermaid_code: str (Mermaid syntax)
                - decision_points: list[str] (decision node texts)
                - paths: list[dict] (all possible paths)

        Example decision_tree:
            {
                "type": "start",
                "text": "Start",
                "next": {
                    "type": "decision",
                    "text": "Has API key?",
                    "branches": [
                        {
                            "condition": "Yes",
                            "next": {"type": "action", "text": "Process request", "next": {...}}
                        },
                        {
                            "condition": "No",
                            "next": {"type": "end", "text": "Show error"}
                        }
                    ]
                }
            }
        """
        if not decision_tree:
            return {
                "mermaid_code": "graph TD\n    A[No Flowchart Data]",
                "decision_points": [],
                "paths": [],
            }

        # Reset node counter
        self.node_counter = 0
        self.node_map = {}

        # Parse decision tree into nodes and edges
        nodes, edges = self.parse_decision_tree(decision_tree)

        # Build Mermaid code
        mermaid_code = self._build_mermaid_flowchart(nodes, edges)

        # Extract decision points
        decision_points = [node["text"] for node in nodes if node["type"] == "decision"]

        # Extract all paths
        paths = self._extract_paths(decision_tree)

        return {"mermaid_code": mermaid_code, "decision_points": decision_points, "paths": paths}

    def parse_decision_tree(self, tree: Dict, parent_id: Optional[str] = None) -> tuple:
        """
        Convert decision tree to nodes and edges.

        Args:
            tree: Decision tree dict
            parent_id: Parent node ID (for recursion)

        Returns:
            Tuple of (nodes, edges)
                nodes: list[dict] with keys (id, type, text)
                edges: list[dict] with keys (from, to, label)
        """
        nodes = []
        edges = []

        if not tree:
            return nodes, edges

        # Create current node
        node_type = tree.get("type", "action")
        node_text = tree.get("text", "")
        node_id = self._get_next_node_id()

        nodes.append({"id": node_id, "type": node_type, "text": node_text})

        # Store in node map
        self.node_map[node_id] = tree

        # Connect to parent if exists
        if parent_id:
            edges.append({"from": parent_id, "to": node_id, "label": ""})

        # Process children
        if "branches" in tree:
            # Decision node with multiple branches
            for branch in tree["branches"]:
                condition = branch.get("condition", "")
                next_node = branch.get("next")

                if next_node:
                    child_nodes, child_edges = self.parse_decision_tree(next_node, node_id)
                    nodes.extend(child_nodes)

                    # Update first edge with condition label
                    if child_edges:
                        child_edges[0]["label"] = condition

                    edges.extend(child_edges)

        elif "next" in tree:
            # Single next node
            next_node = tree["next"]
            if next_node:
                child_nodes, child_edges = self.parse_decision_tree(next_node, node_id)
                nodes.extend(child_nodes)
                edges.extend(child_edges)

        return nodes, edges

    def format_decision_node(self, node: Dict) -> str:
        """
        Format node for Mermaid syntax.

        Args:
            node: Node dict with keys (id, type, text)

        Returns:
            Mermaid node definition string

        Examples:
            - Decision: A{Question?}
            - Action: B[Do something]
            - Start/End: C(Start)
        """
        node_id = node["id"]
        node_type = node["type"]
        node_text = node["text"]

        # Get shape brackets
        open_bracket, close_bracket = self.node_shapes.get(
            node_type, ("[", "]")  # Default to rectangle
        )

        # Escape special characters
        escaped_text = node_text.replace('"', '\\"')

        return f"{node_id}{open_bracket}{escaped_text}{close_bracket}"

    def _get_next_node_id(self) -> str:
        """Get next available node ID (A, B, C, ...)."""
        if self.node_counter < 26:
            node_id = chr(ord("A") + self.node_counter)
        else:
            # After Z, use A1, A2, ...
            overflow = self.node_counter - 26
            node_id = f"A{overflow + 1}"

        self.node_counter += 1
        return node_id

    def _build_mermaid_flowchart(self, nodes: List[Dict], edges: List[Dict]) -> str:
        """
        Build Mermaid flowchart syntax.

        Args:
            nodes: List of node dicts
            edges: List of edge dicts

        Returns:
            Mermaid flowchart code
        """
        lines = ["graph TD"]

        # Add node definitions
        for node in nodes:
            node_def = self.format_decision_node(node)
            lines.append(f"    {node_def}")

        # Add edges
        for edge in edges:
            from_id = edge["from"]
            to_id = edge["to"]
            label = edge.get("label", "")

            if label:
                # Escape label
                label = label.replace('"', '\\"')
                lines.append(f"    {from_id} -->|{label}| {to_id}")
            else:
                lines.append(f"    {from_id} --> {to_id}")

        return "\n".join(lines)

    def _extract_paths(self, tree: Dict, current_path: Optional[List] = None) -> List[Dict]:
        """
        Extract all possible paths through the flowchart.

        Args:
            tree: Decision tree
            current_path: Current path being built (for recursion)

        Returns:
            List of path dicts with keys:
                - steps: list[str] (step descriptions)
                - decisions: list[str] (decision choices)
                - outcome: str (final step)
        """
        if current_path is None:
            current_path = []

        paths = []

        if not tree:
            return paths

        # Add current step to path
        step_text = tree.get("text", "")
        current_path = current_path + [step_text]

        # Check if end node
        if tree.get("type") == "end":
            paths.append(
                {
                    "steps": current_path,
                    "decisions": [s for s in current_path if "?" in s],
                    "outcome": step_text,
                }
            )
            return paths

        # Process branches
        if "branches" in tree:
            for branch in tree["branches"]:
                condition = branch.get("condition", "")
                next_node = branch.get("next")

                if next_node:
                    # Add condition to path
                    branch_path = current_path + [f"→ {condition}"]
                    sub_paths = self._extract_paths(next_node, branch_path)
                    paths.extend(sub_paths)

        # Process single next node
        elif "next" in tree:
            next_node = tree["next"]
            if next_node:
                sub_paths = self._extract_paths(next_node, current_path)
                paths.extend(sub_paths)

        return paths
