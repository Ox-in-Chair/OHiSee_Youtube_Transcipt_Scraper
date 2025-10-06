"""
VISUAL-001: Diagram Generation Engine
Main entry point for visualization layer.

Generates Mermaid diagrams from CORE-001 synthesis outputs:
- Timeline diagrams (technology evolution)
- Architecture diagrams (system components)
- Comparison matrices (tool comparisons)
- Flowcharts (decision trees)
"""

from typing import Dict
from .timeline_generator import TimelineGenerator
from .architecture_generator import ArchitectureGenerator
from .comparison_generator import ComparisonGenerator
from .flowchart_generator import FlowchartGenerator
from .validator import MermaidValidator


class VisualEngine:
    """
    Main Visual-001 engine for diagram generation.

    Integrates all diagram generators and provides
    unified interface for downstream modules.
    """

    def __init__(self, callback=None):
        """
        Initialize visual engine.

        Args:
            callback: Optional logging callback function
        """
        self.timeline_gen = TimelineGenerator()
        self.architecture_gen = ArchitectureGenerator()
        self.comparison_gen = ComparisonGenerator()
        self.flowchart_gen = FlowchartGenerator()
        self.validator = MermaidValidator()
        self.callback = callback or self._default_callback

    def generate_all(self, synthesis: Dict, config: Dict) -> Dict:
        """
        Generate all requested diagrams from CORE-001 synthesis.

        Args:
            synthesis: CORE-001 synthesis output with keys:
                - chronological_timeline: list[dict]
                - cross_video_patterns: list[dict]
                - tool_mentions: dict
            config: Configuration dict with keys:
                - diagram_types: list[str] (diagrams to generate)
                - complexity: str ("simple"|"detailed"|"comprehensive")
                - validate: bool (run validation, default True)

        Returns:
            Dict matching VISUAL-001 output contract:
                - diagrams: dict (timeline, architecture, comparison, flowchart)
                - markdown_embeds: dict (ready-to-embed MD snippets)
                - validation: dict (all_valid, errors)

        Example config:
            {
                "diagram_types": ["timeline", "architecture", "comparison"],
                "complexity": "detailed",
                "validate": True
            }
        """
        self._log("Starting diagram generation...")

        diagram_types = config.get("diagram_types", [])
        complexity = config.get("complexity", "detailed")
        validate = config.get("validate", True)

        diagrams = {}
        markdown_embeds = {}
        all_errors = []

        # Generate timeline diagram
        if "timeline" in diagram_types:
            self._log("Generating timeline diagram...")
            timeline_result = self._generate_timeline(synthesis, complexity)
            diagrams["timeline"] = timeline_result

            if validate:
                is_valid, errors = self.validator.validate_mermaid_syntax(
                    timeline_result["mermaid_code"]
                )
                if not is_valid:
                    all_errors.extend([f"Timeline: {e}" for e in errors])

            markdown_embeds["timeline"] = self._create_markdown_embed(timeline_result, "Timeline")

        # Generate architecture diagram
        if "architecture" in diagram_types:
            self._log("Generating architecture diagram...")
            architecture_result = self._generate_architecture(synthesis, complexity)
            diagrams["architecture"] = architecture_result

            if validate:
                is_valid, errors = self.validator.validate_mermaid_syntax(
                    architecture_result["mermaid_code"]
                )
                if not is_valid:
                    all_errors.extend([f"Architecture: {e}" for e in errors])

            markdown_embeds["architecture"] = self._create_markdown_embed(
                architecture_result, "Architecture"
            )

        # Generate comparison diagram
        if "comparison" in diagram_types:
            self._log("Generating comparison diagram...")
            comparison_result = self._generate_comparison(synthesis, complexity)
            diagrams["comparison"] = comparison_result

            if validate:
                is_valid, errors = self.validator.validate_mermaid_syntax(
                    comparison_result["mermaid_code"]
                )
                if not is_valid:
                    all_errors.extend([f"Comparison: {e}" for e in errors])

            markdown_embeds["comparison"] = self._create_markdown_embed(
                comparison_result, "Comparison"
            )

        # Generate flowchart diagram
        if "flowchart" in diagram_types:
            self._log("Generating flowchart diagram...")
            flowchart_result = self._generate_flowchart(synthesis, complexity)
            diagrams["flowchart"] = flowchart_result

            if validate:
                is_valid, errors = self.validator.validate_mermaid_syntax(
                    flowchart_result["mermaid_code"]
                )
                if not is_valid:
                    all_errors.extend([f"Flowchart: {e}" for e in errors])

            markdown_embeds["flowchart"] = self._create_markdown_embed(
                flowchart_result, "Flowchart"
            )

        self._log(f"Generated {len(diagrams)} diagrams")

        return {
            "diagrams": diagrams,
            "markdown_embeds": markdown_embeds,
            "validation": {"all_valid": len(all_errors) == 0, "errors": all_errors},
        }

    def _generate_timeline(self, synthesis: Dict, complexity: str) -> Dict:
        """Generate timeline diagram from synthesis."""
        events = synthesis.get("chronological_timeline", [])
        return self.timeline_gen.generate(events, complexity)

    def _generate_architecture(self, synthesis: Dict, complexity: str) -> Dict:
        """Generate architecture diagram from synthesis."""
        # Extract components and relationships from patterns
        patterns = synthesis.get("cross_video_patterns", [])

        # Build component list from tool mentions
        tool_mentions = synthesis.get("tool_mentions", {})
        components = list(tool_mentions.keys())[:20]  # Limit to 20 components

        # Infer relationships from patterns
        relationships = []
        for pattern in patterns[:10]:  # Limit to 10 relationships
            videos = pattern.get("videos", [])
            if len(videos) >= 2:
                # Create relationships between tools mentioned together
                for i in range(len(videos) - 1):
                    relationships.append(
                        {
                            "from": videos[i],
                            "to": videos[i + 1],
                            "label": pattern.get("pattern", "")[:20],  # Truncate label
                        }
                    )

        # Determine style based on complexity
        style = "layered" if complexity == "simple" else "flow"

        return self.architecture_gen.generate(components, relationships, style)

    def _generate_comparison(self, synthesis: Dict, complexity: str) -> Dict:
        """Generate comparison diagram from synthesis."""
        tool_mentions = synthesis.get("tool_mentions", {})

        # Get top tools by mention count
        sorted_tools = sorted(
            tool_mentions.items(), key=lambda x: x[1].get("count", 0), reverse=True
        )[
            :5
        ]  # Top 5 tools

        tools = [tool for tool, _ in sorted_tools]

        # Define attributes to compare
        attributes = ["Mention Count", "Contexts", "Popularity"]

        # Build comparison data
        data = {}
        for tool, tool_data in sorted_tools:
            data[tool] = {
                "Mention Count": tool_data.get("count", 0),
                "Contexts": len(tool_data.get("contexts", [])),
                "Popularity": tool_data.get("count", 0) > 3,
            }

        return self.comparison_gen.generate(tools, attributes, data)

    def _generate_flowchart(self, synthesis: Dict, complexity: str) -> Dict:
        """Generate flowchart diagram from synthesis."""
        # Build decision tree from consensus points and contradictions
        consensus = synthesis.get("consensus_points", [])
        contradictions = synthesis.get("contradictions", [])

        # Simple decision tree: Start → Check consensus → Actions
        decision_tree = {
            "type": "start",
            "text": "Start Research Process",
            "next": {
                "type": "decision",
                "text": f"Found {len(consensus)} consensus points?",
                "branches": [
                    {
                        "condition": "Yes",
                        "next": {
                            "type": "action",
                            "text": f"Apply {len(consensus)} best practices",
                            "next": {
                                "type": "decision",
                                "text": f"Any contradictions ({len(contradictions)})?",
                                "branches": [
                                    {
                                        "condition": "Yes",
                                        "next": {
                                            "type": "action",
                                            "text": "Investigate contradictions",
                                            "next": {"type": "end", "text": "Complete"},
                                        },
                                    },
                                    {
                                        "condition": "No",
                                        "next": {"type": "end", "text": "Complete"},
                                    },
                                ],
                            },
                        },
                    },
                    {
                        "condition": "No",
                        "next": {
                            "type": "action",
                            "text": "Gather more research",
                            "next": {"type": "end", "text": "Incomplete"},
                        },
                    },
                ],
            },
        }

        return self.flowchart_gen.generate(decision_tree)

    def _create_markdown_embed(self, diagram_result: Dict, diagram_type: str) -> str:
        """
        Create ready-to-embed Markdown snippet.

        Args:
            diagram_result: Diagram generation result
            diagram_type: Type of diagram

        Returns:
            Markdown string with Mermaid code block
        """
        title = diagram_result.get("title", f"{diagram_type} Diagram")
        description = diagram_result.get("description", "")
        mermaid_code = diagram_result.get("mermaid_code", "")

        markdown = f"## {title}\n\n"
        if description:
            markdown += f"{description}\n\n"

        markdown += "```mermaid\n"
        markdown += mermaid_code
        markdown += "\n```\n"

        return markdown

    def _log(self, message: str):
        """Log message via callback."""
        if self.callback:
            self.callback(message)

    def _default_callback(self, message: str):
        """Default callback (no-op)."""
        pass


# Export main classes
__all__ = [
    "VisualEngine",
    "TimelineGenerator",
    "ArchitectureGenerator",
    "ComparisonGenerator",
    "FlowchartGenerator",
    "MermaidValidator",
]
