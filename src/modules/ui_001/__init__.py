"""UI-001: Enhanced Intelligence Dashboard

Provides comprehensive GUI integration for all v2.0 modules including:
- Intelligence dashboard with ROI scoring and learning paths
- Visualization panel for Mermaid diagrams (HTML preview)
- Playbook viewer with interactive step-by-step guides
- Settings panel for module configuration

Version: 1.0.0
Status: Production Ready
Dependencies: tkinter, CORE-001, VISUAL-001, EXEC-001, INTEL-001
"""

from .intelligence_dashboard import IntelligenceDashboard
from .visualization_panel import VisualizationPanel
from .playbook_viewer import PlaybookViewer
from .settings_panel import SettingsPanel

__version__ = "1.0.0"
__all__ = [
    "IntelligenceDashboard",
    "VisualizationPanel",
    "PlaybookViewer",
    "SettingsPanel",
]
