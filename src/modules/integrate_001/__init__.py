"""
INTEGRATE-001: System Integration & Orchestration

Final module that orchestrates all v2.0 intelligence modules into a cohesive system.

Components:
- WorkflowOrchestrator: Coordinates module execution
- OutputAssembler: Merges all outputs into unified deliverable
- ExportManager: Multi-format exports (MD, PDF, HTML, ZIP)

Version: 1.0.0
Status: Production Ready
Dependencies: CORE-001, VISUAL-001, EXEC-001, INTEL-001, KNOWLEDGE-001, UI-001
"""

from .workflow_orchestrator import WorkflowOrchestrator
from .output_assembler import OutputAssembler
from .export_manager import ExportManager

__version__ = "1.0.0"
__all__ = [
    "WorkflowOrchestrator",
    "OutputAssembler",
    "ExportManager",
]
