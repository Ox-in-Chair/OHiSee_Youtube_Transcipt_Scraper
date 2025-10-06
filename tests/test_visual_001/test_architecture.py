"""
Unit tests for ArchitectureGenerator.
"""

import pytest
from src.modules.visual_001.architecture_generator import ArchitectureGenerator


class TestArchitectureGenerator:
    """Test suite for ArchitectureGenerator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = ArchitectureGenerator()
        self.sample_components = [
            "User Interface",
            "Core Engine",
            "Database"
        ]
        self.sample_relationships = [
            {"from": "User Interface", "to": "Core Engine"},
            {"from": "Core Engine", "to": "Database"}
        ]

    def test_generate_layered_architecture(self):
        """Test layered architecture generation."""
        result = self.generator.generate(
            self.sample_components,
            self.sample_relationships,
            style="layered"
        )

        assert result is not None
        assert "mermaid_code" in result
        assert "graph LR" in result["mermaid_code"]
        assert "User_Interface" in result["mermaid_code"]

    def test_generate_hub_architecture(self):
        """Test hub architecture generation."""
        result = self.generator.generate(
            self.sample_components,
            self.sample_relationships,
            style="hub"
        )

        assert result is not None
        assert "graph TD" in result["mermaid_code"]

    def test_generate_flow_architecture(self):
        """Test flow architecture generation."""
        result = self.generator.generate(
            self.sample_components,
            self.sample_relationships,
            style="flow"
        )

        assert result is not None
        assert "graph TD" in result["mermaid_code"]

    def test_empty_components(self):
        """Test architecture with no components."""
        result = self.generator.generate([], [], style="layered")

        assert result["components"] == []
        assert "No Components" in result["mermaid_code"]

    def test_invalid_style(self):
        """Test invalid diagram style."""
        with pytest.raises(ValueError):
            self.generator.generate(
                self.sample_components,
                self.sample_relationships,
                style="invalid"
            )

    def test_detect_layers(self):
        """Test layer detection."""
        components = [
            "User Interface",
            "Dashboard View",
            "Core Engine",
            "Business Logic",
            "Database",
            "Data Storage"
        ]

        layers = self.generator.detect_layers(components)

        assert "ui" in layers
        assert "logic" in layers
        assert "data" in layers
        assert "User Interface" in layers["ui"]
        assert "Core Engine" in layers["logic"]
        assert "Database" in layers["data"]

    def test_apply_styling(self):
        """Test styling application."""
        component_ids = {
            "User Interface": "User_Interface",
            "Core Engine": "Core_Engine"
        }
        layers = {
            "ui": ["User Interface"],
            "logic": ["Core Engine"]
        }

        mermaid = "graph TD\n    User_Interface[User Interface]\n    Core_Engine[Core Engine]"
        styled = self.generator.apply_styling(mermaid, layers, component_ids)

        assert "style User_Interface fill:#90EE90" in styled
        assert "style Core_Engine fill:#87CEEB" in styled

    def test_sanitize_id(self):
        """Test ID sanitization."""
        assert self.generator._sanitize_id("User Interface") == "User_Interface"
        assert self.generator._sanitize_id("Core-Engine") == "Core_Engine"
        assert self.generator._sanitize_id("Data/Storage") == "Data_Storage"
        assert self.generator._sanitize_id("123Start") == "C_123Start"

    def test_relationships_in_output(self):
        """Test that relationships appear in output."""
        result = self.generator.generate(
            self.sample_components,
            self.sample_relationships,
            style="flow"
        )

        code = result["mermaid_code"]
        assert "-->" in code
        assert "User_Interface" in code
        assert "Core_Engine" in code
        assert "Database" in code

    def test_labeled_relationships(self):
        """Test relationships with labels."""
        relationships = [
            {
                "from": "User Interface",
                "to": "Core Engine",
                "label": "sends request"
            }
        ]

        result = self.generator.generate(
            self.sample_components,
            relationships,
            style="flow"
        )

        assert "sends request" in result["mermaid_code"]

    def test_complex_architecture(self):
        """Test complex architecture with many components."""
        components = [
            "Frontend UI", "API Gateway", "Auth Service",
            "User Service", "Data Service", "Cache Layer",
            "Primary DB", "Replica DB", "Queue System"
        ]

        relationships = [
            {"from": "Frontend UI", "to": "API Gateway"},
            {"from": "API Gateway", "to": "Auth Service"},
            {"from": "API Gateway", "to": "User Service"},
            {"from": "User Service", "to": "Data Service"},
            {"from": "Data Service", "to": "Cache Layer"},
            {"from": "Data Service", "to": "Primary DB"},
            {"from": "Primary DB", "to": "Replica DB"}
        ]

        result = self.generator.generate(components, relationships, style="layered")

        assert len(result["components"]) == 9
        assert len(result["relationships"]) == 7
        assert len(result["layers"]) >= 2

    def test_hub_style_connectivity(self):
        """Test hub style creates central connections."""
        result = self.generator.generate(
            self.sample_components,
            self.sample_relationships,
            style="hub"
        )

        code = result["mermaid_code"]
        # Core Engine should be connected to multiple components
        assert code.count("Core_Engine") >= 2
