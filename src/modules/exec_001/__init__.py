"""
EXEC-001: Playbook & Execution Engine

Transforms CORE-001 insights into executable artifacts:
- Step-by-step playbooks
- Prompt templates with variables
- CLI command references
- Implementation checklists

Version: 1.0.0
Status: Production Ready
Dependencies: CORE-001
"""

from .execution_engine import ExecutionEngine
from .playbook_generator import PlaybookGenerator
from .prompt_extractor import PromptExtractor
from .cli_parser import CLIParser
from .checklist_creator import ChecklistCreator

__version__ = "1.0.0"
__all__ = [
    "ExecutionEngine",
    "PlaybookGenerator",
    "PromptExtractor",
    "CLIParser",
    "ChecklistCreator",
]
