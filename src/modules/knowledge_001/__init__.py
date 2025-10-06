"""KNOWLEDGE-001: Persistent Knowledge Base

Persistent knowledge storage with deduplication, search, and cross-referencing.

This module provides:
- SQLite-backed persistent storage
- Automatic deduplication (90%+ accuracy)
- Full-text search with filtering
- Relationship discovery and management
- Implementation journal tracking
- Export functionality (JSON, Markdown, CSV)

Usage:
    from modules.knowledge_001 import KnowledgeEngine

    # Initialize engine
    engine = KnowledgeEngine(
        db_path="knowledge_base.db",
        deduplication_threshold=0.85
    )

    # Store insights with automatic deduplication
    insight_id = engine.store_insight({
        "title": "Setup Gmail MCP",
        "description": "Configure Gmail MCP server for email access",
        "category": "tools",
        "tags": ["gmail", "mcp", "email"],
        "confidence": 0.95
    })

    # Search knowledge base
    results = engine.search_knowledge(
        query="gmail setup",
        filters={"category": "tools"},
        limit=10
    )

    # Export to file
    engine.export_knowledge(
        format="markdown",
        output_path="knowledge_export.md"
    )

API Version: 1.0.0
Status: Production Ready
Dependencies: None (uses stdlib sqlite3)
"""

from .knowledge_engine import KnowledgeEngine
from .knowledge_store import KnowledgeStore
from .search_engine import SearchEngine
from .cross_reference import CrossReferenceEngine

__version__ = "1.0.0"
__all__ = ["KnowledgeEngine", "KnowledgeStore", "SearchEngine", "CrossReferenceEngine"]
