"""KNOWLEDGE-001: Knowledge Engine - Unified API Facade

Provides high-level API for knowledge base operations with automatic
deduplication, relationship discovery, and intelligent storage.

This is the main entry point for interacting with the KNOWLEDGE-001 module.

Features:
- Automatic deduplication on insert
- Intelligent relationship discovery
- Comprehensive search capabilities
- Journal tracking for implementations
- Export/import functionality
- Statistics and analytics

Author: Backend Developer Agent
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from .knowledge_store import KnowledgeStore
from .search_engine import SearchEngine
from .cross_reference import CrossReferenceEngine


class KnowledgeEngine:
    """Unified API for knowledge base operations"""

    def __init__(
        self, db_path: str = None, deduplication_threshold: float = 0.85, callback=None
    ):
        """
        Initialize knowledge engine

        Args:
            db_path: Path to SQLite database (default: ./knowledge_base.db)
            deduplication_threshold: Similarity threshold for deduplication (0-1)
            callback: Optional callback for logging
        """
        self.db_path = db_path or "knowledge_base.db"
        self.deduplication_threshold = deduplication_threshold
        self.callback = callback or print

        # Initialize components
        self.store = KnowledgeStore(db_path=self.db_path, callback=callback)
        self.search = SearchEngine(knowledge_store=self.store, callback=callback)
        self.cross_ref = CrossReferenceEngine(
            knowledge_store=self.store, search_engine=self.search, callback=callback
        )

        self._log("Knowledge Engine initialized")

    def _log(self, message: str):
        """Internal logging helper"""
        if self.callback:
            self.callback(message)

    def store_insight(
        self, insight: dict, dedupe: bool = True, discover_relationships: bool = True
    ) -> str:
        """
        Store insight with automatic deduplication and relationship discovery

        Args:
            insight: Insight dict with keys:
                - title: str (required)
                - description: str (required)
                - category: str (required)
                - source_video_id: str (optional)
                - confidence: float (optional, default 1.0)
                - tags: List[str] (optional)
                - metadata: dict (optional)
            dedupe: Enable deduplication
            discover_relationships: Enable relationship discovery

        Returns:
            Insight ID (existing ID if duplicate found, new ID otherwise)
        """
        try:
            # Validate required fields
            if not all(k in insight for k in ["title", "description", "category"]):
                raise ValueError("Insight must have title, description, and category")

            # Check for duplicates if enabled
            if dedupe:
                duplicates = self.cross_ref.find_duplicates(
                    insight, threshold=self.deduplication_threshold
                )

                if duplicates:
                    # Use existing insight
                    existing_insight, similarity = duplicates[0]
                    existing_id = existing_insight["id"]

                    self._log(
                        f"Duplicate found (similarity: {similarity:.2f}), "
                        f"using existing ID: {existing_id}"
                    )

                    # Update confidence if higher
                    new_confidence = insight.get("confidence", 1.0)
                    if new_confidence > existing_insight.get("confidence", 1.0):
                        cursor = self.store.conn.cursor()
                        cursor.execute(
                            """
                            UPDATE insights
                            SET confidence = ?, updated_at = ?
                            WHERE id = ?
                        """,
                            (
                                new_confidence,
                                datetime.utcnow().isoformat(),
                                existing_id,
                            ),
                        )
                        self.store.conn.commit()

                    return existing_id

            # Store new insight
            insight_id = self.store.store_insight(
                title=insight["title"],
                description=insight["description"],
                category=insight["category"],
                source_video_id=insight.get("source_video_id"),
                confidence=insight.get("confidence", 1.0),
                tags=insight.get("tags", []),
                metadata=insight.get("metadata", {}),
            )

            # Discover relationships if enabled
            if discover_relationships:
                self.cross_ref.discover_relationships(insight_id, max_relationships=5)

            self._log(f"Stored insight: {insight_id}")
            return insight_id

        except Exception as e:
            self._log(f"Error storing insight: {e}")
            raise

    def store_batch(
        self,
        insights: List[dict],
        dedupe: bool = True,
        discover_relationships: bool = True,
    ) -> Dict[str, Any]:
        """
        Store multiple insights in batch

        Args:
            insights: List of insight dicts
            dedupe: Enable deduplication
            discover_relationships: Enable relationship discovery

        Returns:
            Dict with:
                - stored: List of new insight IDs
                - duplicates: List of duplicate IDs reused
                - total: Total count
                - statistics: Processing statistics
        """
        try:
            start_time = datetime.now()

            stored = []
            duplicates = []

            for insight in insights:
                # Check if duplicate before storing
                if dedupe:
                    dupes = self.cross_ref.find_duplicates(
                        insight, threshold=self.deduplication_threshold
                    )
                    if dupes:
                        dup_id = dupes[0][0]["id"]
                        duplicates.append(dup_id)
                        continue

                # Store new insight
                insight_id = self.store_insight(
                    insight,
                    dedupe=False,  # Already checked
                    discover_relationships=discover_relationships,
                )
                stored.append(insight_id)

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            result = {
                "stored": stored,
                "duplicates": duplicates,
                "total": len(stored) + len(duplicates),
                "statistics": {
                    "new_insights": len(stored),
                    "duplicates_merged": len(duplicates),
                    "processing_time": processing_time,
                    "deduplication_rate": (
                        len(duplicates) / len(insights) if insights else 0
                    ),
                },
            }

            self._log(
                f"Batch stored: {len(stored)} new, " f"{len(duplicates)} duplicates"
            )
            return result

        except Exception as e:
            self._log(f"Batch storage error: {e}")
            raise

    def search_knowledge(
        self, query: str, filters: dict = None, limit: int = 10, offset: int = 0
    ) -> dict:
        """
        Search across knowledge base

        Args:
            query: Search query string
            filters: Optional filters (see SearchEngine.search)
            limit: Maximum results
            offset: Pagination offset

        Returns:
            Search results dict
        """
        return self.search.search(
            query=query, filters=filters, limit=limit, offset=offset
        )

    def update_journal(self, entry: dict) -> str:
        """
        Update implementation journal

        Args:
            entry: Journal entry dict with keys:
                - insight_id: str (optional)
                - status: str (required)
                - notes: str (optional)
                - time_spent: int (optional, minutes)
                - success: bool (optional)

        Returns:
            Journal entry ID
        """
        return self.store.add_journal_entry(
            insight_id=entry.get("insight_id"),
            status=entry["status"],
            notes=entry.get("notes", ""),
            time_spent=entry.get("time_spent", 0),
            success=entry.get("success", False),
        )

    def export_knowledge(
        self, format: str = "json", filters: dict = None, output_path: str = None
    ) -> str:
        """
        Export knowledge base

        Args:
            format: Export format ("json", "markdown", "csv")
            filters: Optional filters for export
            output_path: Output file path (optional)

        Returns:
            Exported data as string
        """
        try:
            # Get insights based on filters
            if filters:
                insights = self.search.search(query="", filters=filters, limit=10000)[
                    "results"
                ]
            else:
                insights = self.store.get_all_insights(limit=10000)

            # Get statistics
            stats = self.store.get_statistics()

            # Format export
            if format == "json":
                export_data = self._export_json(insights, stats)
            elif format == "markdown":
                export_data = self._export_markdown(insights, stats)
            elif format == "csv":
                export_data = self._export_csv(insights)
            else:
                raise ValueError(f"Unsupported format: {format}")

            # Write to file if path provided
            if output_path:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(export_data)
                self._log(f"Exported to: {output_path}")

            return export_data

        except Exception as e:
            self._log(f"Export error: {e}")
            raise

    def _export_json(self, insights: List[dict], stats: dict) -> str:
        """Export as JSON"""
        export = {
            "metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "total_insights": len(insights),
                "statistics": stats,
            },
            "insights": insights,
        }
        return json.dumps(export, indent=2)

    def _export_markdown(self, insights: List[dict], stats: dict) -> str:
        """Export as Markdown"""
        lines = [
            "# Knowledge Base Export",
            f"**Exported**: {datetime.utcnow().isoformat()}",
            f"**Total Insights**: {len(insights)}",
            "",
            "## Statistics",
            "",
        ]

        for key, value in stats.items():
            if isinstance(value, dict):
                lines.append(f"### {key.replace('_', ' ').title()}")
                for k, v in value.items():
                    lines.append(f"- **{k}**: {v}")
                lines.append("")
            else:
                lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")

        lines.extend(["", "## Insights", ""])

        for insight in insights:
            lines.extend(
                [
                    f"### {insight['title']}",
                    f"**Category**: {insight.get('category', 'N/A')}",
                    f"**Confidence**: {insight.get('confidence', 1.0):.2f}",
                    f"**Created**: {insight.get('created_at', 'N/A')}",
                    "",
                    insight.get("description", ""),
                    "",
                ]
            )

            if insight.get("tags"):
                lines.append(f"**Tags**: {', '.join(insight['tags'])}")
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _export_csv(self, insights: List[dict]) -> str:
        """Export as CSV"""
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "id",
                "title",
                "description",
                "category",
                "confidence",
                "created_at",
                "tags",
            ],
        )

        writer.writeheader()

        for insight in insights:
            row = {
                "id": insight.get("id", ""),
                "title": insight.get("title", ""),
                "description": insight.get("description", ""),
                "category": insight.get("category", ""),
                "confidence": insight.get("confidence", 1.0),
                "created_at": insight.get("created_at", ""),
                "tags": ",".join(insight.get("tags", [])),
            }
            writer.writerow(row)

        return output.getvalue()

    def get_statistics(self) -> dict:
        """
        Get comprehensive knowledge base statistics

        Returns:
            Statistics dict
        """
        base_stats = self.store.get_statistics()

        # Add search-specific statistics
        trending = self.search.get_trending(days=7, limit=5)
        most_mentioned = self.search.get_most_mentioned(limit=5)

        return {
            **base_stats,
            "trending_insights": [
                {"id": i["id"], "title": i["title"]} for i in trending
            ],
            "most_mentioned": [
                {"id": i["id"], "title": i["title"]} for i in most_mentioned
            ],
        }

    def get_insight(self, insight_id: str) -> Optional[dict]:
        """
        Get single insight by ID

        Args:
            insight_id: Insight ID

        Returns:
            Insight dict or None
        """
        return self.store.get_insight(insight_id)

    def get_all_insights(
        self, category: str = None, limit: int = 100, offset: int = 0
    ) -> List[dict]:
        """
        Get all insights with optional filtering

        Args:
            category: Filter by category
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of insights
        """
        return self.store.get_all_insights(
            category=category, limit=limit, offset=offset
        )

    def backup_database(self, backup_path: str = None) -> str:
        """
        Create database backup

        Args:
            backup_path: Backup file path

        Returns:
            Backup file path
        """
        return self.store.backup_database(backup_path)

    def close(self):
        """Close all connections"""
        self.store.close()
        self._log("Knowledge Engine closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
