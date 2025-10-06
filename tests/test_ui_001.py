"""Test Suite for UI-001 Module

Tests all UI components:
- IntelligenceDashboard
- VisualizationPanel
- PlaybookViewer
- SettingsPanel
"""

import pytest
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from modules.ui_001 import (
    IntelligenceDashboard,
    VisualizationPanel,
    PlaybookViewer,
    SettingsPanel,
)


@pytest.fixture
def root():
    """Create Tkinter root window for testing"""
    root = tk.Tk()
    root.withdraw()  # Hide window during tests
    yield root
    root.destroy()


@pytest.fixture
def callback_log():
    """Create callback that logs messages"""
    messages = []

    def callback(msg):
        messages.append(msg)

    callback.messages = messages
    return callback


# IntelligenceDashboard Tests


def test_intelligence_dashboard_init(root, callback_log):
    """Test IntelligenceDashboard initialization"""
    dashboard = IntelligenceDashboard(root, callback=callback_log)
    assert dashboard.container is not None
    assert dashboard.notebook is not None


def test_intelligence_dashboard_tabs(root):
    """Test that all tabs are created"""
    dashboard = IntelligenceDashboard(root)
    assert dashboard.roi_tab is not None
    assert dashboard.learning_tab is not None
    assert dashboard.knowledge_tab is not None
    assert dashboard.progress_tab is not None


def test_intelligence_dashboard_update_data(root, callback_log):
    """Test updating dashboard with data"""
    dashboard = IntelligenceDashboard(root, callback=callback_log)

    test_data = {
        "roi_scores": [
            {
                "title": "Test Item",
                "score": 8.5,
                "time_minutes": 30,
                "readiness": "READY",
                "category": "Tool",
            }
        ],
        "learning_path": [
            {"title": "Step 1", "description": "First step"},
            {"title": "Step 2", "description": "Second step"},
        ],
        "knowledge_base": [{"id": 1, "content": "Test entry"}],
        "progress_items": [
            {"title": "Item 1", "status": "completed"},
            {"title": "Item 2", "status": "in_progress"},
        ],
    }

    dashboard.update_data(test_data)
    assert dashboard.data == test_data


def test_intelligence_dashboard_roi_filtering(root):
    """Test ROI filtering functionality"""
    dashboard = IntelligenceDashboard(root)

    test_data = {
        "roi_scores": [
            {"title": "High ROI", "score": 8.0, "time_minutes": 20, "readiness": "READY"},
            {"title": "Medium ROI", "score": 5.0, "time_minutes": 40, "readiness": "READY"},
            {"title": "Low ROI", "score": 2.0, "time_minutes": 60, "readiness": "NEEDS_SETUP"},
        ]
    }

    dashboard.update_data(test_data)

    # Test different filters
    dashboard.roi_filter_var.set("high")
    dashboard._refresh_roi()

    dashboard.roi_filter_var.set("medium")
    dashboard._refresh_roi()

    dashboard.roi_filter_var.set("low")
    dashboard._refresh_roi()


# VisualizationPanel Tests


def test_visualization_panel_init(root, callback_log):
    """Test VisualizationPanel initialization"""
    panel = VisualizationPanel(root, callback=callback_log)
    assert panel.container is not None
    assert panel.diagram_combo is not None
    assert panel.code_text is not None


def test_visualization_panel_load_diagrams(root, callback_log):
    """Test loading diagrams"""
    panel = VisualizationPanel(root, callback=callback_log)

    test_diagrams = {
        "timeline": {
            "type": "timeline",
            "mermaid": "graph TD\nA-->B",
            "complexity": "simple",
            "generated_at": "2025-10-06",
        },
        "architecture": {
            "type": "architecture",
            "mermaid": "graph LR\nFrontend-->Backend",
            "complexity": "detailed",
            "generated_at": "2025-10-06",
        },
    }

    panel.load_diagrams(test_diagrams)
    assert panel.diagrams == test_diagrams
    assert len(panel.diagram_combo["values"]) == 2


def test_visualization_panel_diagram_selection(root, callback_log):
    """Test diagram selection"""
    panel = VisualizationPanel(root, callback=callback_log)

    test_diagrams = {
        "timeline": {
            "type": "timeline",
            "mermaid": "graph TD\nA-->B",
            "complexity": "simple",
        }
    }

    panel.load_diagrams(test_diagrams)
    panel.diagram_var.set("Timeline")
    panel._on_diagram_selected()

    assert panel.current_diagram is not None


def test_visualization_panel_html_generation(root):
    """Test HTML generation for diagrams"""
    panel = VisualizationPanel(root)

    mermaid_code = "graph TD\nA-->B"
    html = panel._generate_html(mermaid_code)

    assert "mermaid" in html
    assert mermaid_code in html
    assert "<!DOCTYPE html>" in html


# PlaybookViewer Tests


def test_playbook_viewer_init(root, callback_log):
    """Test PlaybookViewer initialization"""
    viewer = PlaybookViewer(root, callback=callback_log)
    assert viewer.container is not None
    assert viewer.playbook_combo is not None
    assert viewer.step_title is not None


def test_playbook_viewer_load_playbooks(root, callback_log):
    """Test loading playbooks"""
    viewer = PlaybookViewer(root, callback=callback_log)

    test_playbooks = [
        {
            "title": "Test Playbook 1",
            "description": "Test description",
            "steps": [
                {
                    "title": "Step 1",
                    "description": "First step",
                    "instructions": ["Do this", "Do that"],
                    "code": "print('hello')",
                },
                {
                    "title": "Step 2",
                    "description": "Second step",
                    "instructions": ["Next action"],
                },
            ],
        }
    ]

    viewer.load_playbooks(test_playbooks)
    assert viewer.playbooks == test_playbooks
    assert len(viewer.playbook_combo["values"]) == 1


def test_playbook_viewer_navigation(root, callback_log):
    """Test step navigation"""
    viewer = PlaybookViewer(root, callback=callback_log)

    test_playbooks = [
        {
            "title": "Navigation Test",
            "steps": [
                {"title": "Step 1", "description": "First"},
                {"title": "Step 2", "description": "Second"},
                {"title": "Step 3", "description": "Third"},
            ],
        }
    ]

    viewer.load_playbooks(test_playbooks)
    viewer.current_playbook = test_playbooks[0]
    viewer.current_step = 0

    # Test next
    viewer._next_step()
    assert viewer.current_step == 1

    # Test previous
    viewer._previous_step()
    assert viewer.current_step == 0


def test_playbook_viewer_markdown_generation(root):
    """Test markdown playbook generation"""
    viewer = PlaybookViewer(root)

    viewer.current_playbook = {
        "title": "Test Playbook",
        "description": "Test",
        "steps": [
            {
                "title": "Step 1",
                "description": "First",
                "instructions": ["Action 1"],
                "code": "test code",
            }
        ],
    }

    markdown = viewer._generate_playbook_markdown()
    assert "# Test Playbook" in markdown
    assert "## Step 1" in markdown
    assert "test code" in markdown


# SettingsPanel Tests


def test_settings_panel_init(root, callback_log):
    """Test SettingsPanel initialization"""
    panel = SettingsPanel(root, callback=callback_log)
    assert panel.container is not None
    assert panel.notebook is not None
    assert panel.settings is not None


def test_settings_panel_tabs(root):
    """Test that all settings tabs are created"""
    panel = SettingsPanel(root)
    assert panel.core_tab is not None
    assert panel.intel_tab is not None
    assert panel.visual_tab is not None
    assert panel.exec_tab is not None
    assert panel.knowledge_tab is not None
    assert panel.api_tab is not None


def test_settings_panel_default_values(root):
    """Test default settings values"""
    panel = SettingsPanel(root)

    assert panel.settings["core"]["mode"] == "developer"
    assert panel.settings["core"]["depth"] == 50
    assert panel.settings["intel"]["learning_goal"] == "comprehensive"
    assert panel.settings["visual"]["complexity"] == "detailed"


def test_settings_panel_save_settings(root, callback_log):
    """Test saving settings"""
    panel = SettingsPanel(root, callback=callback_log)

    # Change some settings
    panel.core_mode_var.set("quick")
    panel.core_depth_var.set(25)
    panel.intel_goal_var.set("quick")

    # Save
    panel._save_settings()

    # Verify saved
    assert panel.settings["core"]["mode"] == "quick"
    assert panel.settings["core"]["depth"] == 25
    assert panel.settings["intel"]["learning_goal"] == "quick"
    assert "Settings saved successfully" in callback_log.messages


def test_settings_panel_reset_defaults(root):
    """Test resetting to defaults"""
    panel = SettingsPanel(root)

    # Change settings
    panel.settings["core"]["mode"] = "research"
    panel.settings["core"]["depth"] = 100

    # Reset
    panel.settings = panel._load_default_settings()

    assert panel.settings["core"]["mode"] == "developer"
    assert panel.settings["core"]["depth"] == 50


def test_settings_panel_get_settings(root):
    """Test getting current settings"""
    panel = SettingsPanel(root)

    settings = panel.get_settings()
    assert isinstance(settings, dict)
    assert "core" in settings
    assert "intel" in settings
    assert "visual" in settings


# Integration Tests


def test_all_components_pack(root):
    """Test that all components can be packed"""
    dashboard = IntelligenceDashboard(root)
    dashboard.pack()

    panel = VisualizationPanel(root)
    panel.pack()

    viewer = PlaybookViewer(root)
    viewer.pack()

    settings = SettingsPanel(root)
    settings.pack()


def test_all_components_grid(root):
    """Test that all components can be gridded"""
    dashboard = IntelligenceDashboard(root)
    dashboard.grid(row=0, column=0)

    panel = VisualizationPanel(root)
    panel.grid(row=0, column=1)

    viewer = PlaybookViewer(root)
    viewer.grid(row=1, column=0)

    settings = SettingsPanel(root)
    settings.grid(row=1, column=1)


def test_callback_functionality(root, callback_log):
    """Test callback logging across all components"""
    dashboard = IntelligenceDashboard(root, callback=callback_log)
    panel = VisualizationPanel(root, callback=callback_log)
    viewer = PlaybookViewer(root, callback=callback_log)
    settings = SettingsPanel(root, callback=callback_log)

    # Trigger some callbacks
    dashboard.callback("Test dashboard message")
    panel.callback("Test panel message")
    viewer.callback("Test viewer message")
    settings.callback("Test settings message")

    assert len(callback_log.messages) == 4
    assert "Test dashboard message" in callback_log.messages


# Performance Tests


def test_large_roi_dataset(root):
    """Test dashboard with large ROI dataset"""
    dashboard = IntelligenceDashboard(root)

    # Create 100 ROI items
    large_data = {
        "roi_scores": [
            {
                "title": f"Item {i}",
                "score": i % 10,
                "time_minutes": i * 5,
                "readiness": "READY",
                "category": "Tool",
            }
            for i in range(100)
        ]
    }

    dashboard.update_data(large_data)
    dashboard._refresh_roi()


def test_multiple_playbooks(root):
    """Test viewer with multiple playbooks"""
    viewer = PlaybookViewer(root)

    # Create 10 playbooks with 10 steps each
    playbooks = [
        {
            "title": f"Playbook {i}",
            "steps": [
                {"title": f"Step {j}", "description": f"Description {j}"}
                for j in range(10)
            ],
        }
        for i in range(10)
    ]

    viewer.load_playbooks(playbooks)
    assert len(viewer.playbooks) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
