"""
VISUAL-001: Architecture Generator
Generates Mermaid architecture diagrams for system component visualization.
"""

from typing import List, Dict


class ArchitectureGenerator:
    """
    Generate Mermaid architecture diagrams from component relationships.

    Supports three diagram styles:
    - layered: Horizontal layers (UI → Core → Data)
    - hub: Central hub with spokes
    - flow: Directional workflow
    """

    def __init__(self):
        """Initialize architecture generator."""
        self.supported_styles = ["layered", "hub", "flow"]
        self.layer_keywords = {
            "ui": ["ui", "interface", "frontend", "view", "display", "gui", "dashboard"],
            "logic": ["core", "engine", "service", "logic", "business", "processor", "controller"],
            "data": ["data", "database", "storage", "cache", "repository", "persistence"],
        }
        self.color_scheme = {
            "ui": "#90EE90",  # Light green
            "logic": "#87CEEB",  # Sky blue
            "data": "#FFB6C1",  # Light pink
            "default": "#D3D3D3",  # Light gray
        }

    def generate(
        self, components: List[str], relationships: List[Dict], style: str = "layered"
    ) -> Dict:
        """
        Generate Mermaid architecture diagram.

        Args:
            components: List of component names
            relationships: List of relationship dicts with keys:
                - from: str (source component)
                - to: str (target component)
                - label: str (optional relationship label)
            style: str ("layered"|"hub"|"flow")

        Returns:
            Dict with:
                - mermaid_code: str (Mermaid syntax)
                - components: list[str] (component names)
                - relationships: list[dict] (relationships)
                - layers: list[str] (detected layers)

        Raises:
            ValueError: If style is invalid
        """
        if style not in self.supported_styles:
            raise ValueError(
                f"Invalid style '{style}'. " f"Must be one of: {self.supported_styles}"
            )

        if not components:
            return {
                "mermaid_code": "graph TD\n    A[No Components]",
                "components": [],
                "relationships": [],
                "layers": [],
            }

        # Detect layers
        layers = self.detect_layers(components)

        # Build component ID mapping
        component_ids = {comp: self._sanitize_id(comp) for comp in components}

        # Generate Mermaid code
        mermaid_code = self._build_mermaid_architecture(
            components, relationships, component_ids, layers, style
        )

        # Apply styling
        mermaid_code = self.apply_styling(mermaid_code, layers, component_ids)

        return {
            "mermaid_code": mermaid_code,
            "components": components,
            "relationships": relationships,
            "layers": list(layers.keys()),
        }

    def detect_layers(self, components: List[str]) -> Dict[str, List[str]]:
        """
        Detect UI, Logic, Data layers from component names.

        Args:
            components: List of component names

        Returns:
            Dict mapping layer names to component lists
        """
        layers = {"ui": [], "logic": [], "data": []}

        for component in components:
            component_lower = component.lower()
            layer_found = False

            # Check each layer's keywords
            for layer, keywords in self.layer_keywords.items():
                if any(keyword in component_lower for keyword in keywords):
                    layers[layer].append(component)
                    layer_found = True
                    break

            # Default to logic layer if no match
            if not layer_found:
                layers["logic"].append(component)

        # Remove empty layers
        return {k: v for k, v in layers.items() if v}

    def apply_styling(
        self, mermaid: str, layers: Dict[str, List[str]], component_ids: Dict[str, str]
    ) -> str:
        """
        Add colors/styles based on component layers.

        Args:
            mermaid: Base Mermaid code
            layers: Dict mapping layers to components
            component_ids: Dict mapping component names to IDs

        Returns:
            Mermaid code with styling
        """
        style_lines = []

        # Add styling for each component based on layer
        for layer, components in layers.items():
            color = self.color_scheme.get(layer, self.color_scheme["default"])

            for component in components:
                component_id = component_ids.get(component, "")
                if component_id:
                    style_lines.append(f"    style {component_id} fill:{color}")

        # Append style lines to Mermaid code
        if style_lines:
            mermaid += "\n" + "\n".join(style_lines)

        return mermaid

    def _sanitize_id(self, text: str) -> str:
        """
        Convert component name to valid Mermaid ID.

        Args:
            text: Component name

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
            sanitized = "C_" + sanitized

        return sanitized or "Component"

    def _build_mermaid_architecture(
        self,
        components: List[str],
        relationships: List[Dict],
        component_ids: Dict[str, str],
        layers: Dict[str, List[str]],
        style: str,
    ) -> str:
        """
        Build Mermaid architecture syntax.

        Args:
            components: Component names
            relationships: Relationship dicts
            component_ids: Component ID mapping
            layers: Layer groupings
            style: Diagram style

        Returns:
            Mermaid architecture code
        """
        lines = []

        # Graph direction based on style
        if style == "layered":
            lines.append("graph LR")  # Left to right
        elif style == "hub":
            lines.append("graph TD")  # Top to down
        else:  # flow
            lines.append("graph TD")

        # Add component definitions
        for component in components:
            comp_id = component_ids[component]
            # Use square brackets for standard nodes
            lines.append(f"    {comp_id}[{component}]")

        # Add relationships
        for rel in relationships:
            from_comp = rel.get("from", "")
            to_comp = rel.get("to", "")
            label = rel.get("label", "")

            from_id = component_ids.get(from_comp)
            to_id = component_ids.get(to_comp)

            if from_id and to_id:
                if label:
                    # Escape special characters in label
                    label = label.replace('"', '\\"')
                    lines.append(f"    {from_id} -->|{label}| {to_id}")
                else:
                    lines.append(f"    {from_id} --> {to_id}")

        # For hub style, ensure central component connects to all
        if style == "hub" and layers:
            # Find logic layer components (most likely to be central)
            logic_components = layers.get("logic", [])
            if logic_components:
                # Use first logic component as hub
                hub = logic_components[0]
                hub_id = component_ids[hub]

                # Ensure hub connects to all others
                for comp in components:
                    if comp != hub:
                        comp_id = component_ids[comp]
                        # Check if relationship already exists
                        existing = any(
                            (r.get("from") == hub and r.get("to") == comp)
                            or (r.get("from") == comp and r.get("to") == hub)
                            for r in relationships
                        )
                        if not existing:
                            lines.append(f"    {hub_id} --> {comp_id}")

        return "\n".join(lines)

    def _get_importance_scores(
        self, components: List[str], relationships: List[Dict]
    ) -> Dict[str, int]:
        """
        Calculate importance score for each component.

        Importance = number of connections (in + out)

        Args:
            components: Component names
            relationships: Relationship dicts

        Returns:
            Dict mapping component names to importance scores
        """
        scores = {comp: 0 for comp in components}

        for rel in relationships:
            from_comp = rel.get("from", "")
            to_comp = rel.get("to", "")

            if from_comp in scores:
                scores[from_comp] += 1
            if to_comp in scores:
                scores[to_comp] += 1

        return scores
