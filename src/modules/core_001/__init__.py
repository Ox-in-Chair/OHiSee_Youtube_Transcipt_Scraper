"""CORE-001: Enhanced Summary & Synthesis Engine

Foundation module for YouTube Transcript Scraper v2.0 Intelligence System.

This module provides:
- Enhanced summary generation (50+ insights per video)
- Cross-video synthesis with pattern detection
- Entity extraction (tools, commands, prompts, versions)
- Structured API contracts for downstream modules

Usage:
    from modules.core_001 import CoreEngine

    engine = CoreEngine(api_key="sk-...")
    summary = engine.enhance_summary(transcript, metadata, mode="developer")
    synthesis = engine.synthesize_videos([summary1, summary2, summary3])

API Version: 1.0.0
Status: Production Ready
Dependencies: openai>=1.0.0
"""

from .engine import CoreEngine
from .prompts import (
    get_enhanced_summary_prompt,
    get_synthesis_prompt,
    ENHANCED_SUMMARY_PROMPT_TEMPLATE,
    SYNTHESIS_PROMPT_TEMPLATE
)

__version__ = "1.0.0"
__all__ = [
    "CoreEngine",
    "get_enhanced_summary_prompt",
    "get_synthesis_prompt",
    "ENHANCED_SUMMARY_PROMPT_TEMPLATE",
    "SYNTHESIS_PROMPT_TEMPLATE"
]
