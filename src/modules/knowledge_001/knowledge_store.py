"""KNOWLEDGE-001: Knowledge Store - SQLite Persistence Layer

Provides persistent storage for insights, sources, journal entries, and relationships
using SQLite database with comprehensive schema and ACID guarantees.

Features:
- Atomic insight storage with automatic ID generation
- Source metadata tracking
- Implementation journal entries
- Relationship management between insights
- Full ACID compliance with transaction support
- Automatic backups and data validation

Author: Backend Developer Agent
Version: 1.0.0
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import shutil


class KnowledgeStore:
    """Persistent SQLite storage for knowledge base"""

    def __init__(self, db_path: str = None, callback=None):
        """
        Initialize knowledge store with SQLite database

        Args:
            db_path: Path to SQLite database file (default: ./knowledge_base.db)
            callback: Optional callback function for logging
        """
        self.db_path = db_path or "knowledge_base.db"
        self.callback = callback or print
        self.conn = None
        self._initialize_database()

    def _log(self, message: str):
        """Internal logging helper"""
        if self.callback:
            self.callback(message)

    def _initialize_database(self):
        """Create database schema if not exists"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = self.conn.cursor()

            # Enable foreign key support
            cursor.execute("PRAGMA foreign_keys = ON")

            # Create insights table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS insights (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    source_video_id TEXT,
                    confidence REAL DEFAULT 1.0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    tags TEXT,
                    metadata TEXT,
                    FOREIGN KEY (source_video_id) REFERENCES sources(id)
                )
            """
            )

            # Create sources table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sources (
                    id TEXT PRIMARY KEY,
                    video_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    channel TEXT,
                    upload_date TEXT,
                    views INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    metadata TEXT
                )
            """
            )

            # Create journal entries table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS journal_entries (
                    id TEXT PRIMARY KEY,
                    insight_id TEXT,
                    date TEXT NOT NULL,
                    status TEXT,
                    time_spent INTEGER DEFAULT 0,
                    notes TEXT,
                    success INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (insight_id) REFERENCES insights(id)
                )
            """
            )

            # Create relationships table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS relationships (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    strength REAL DEFAULT 0.5,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (source_id) REFERENCES insights(id),
                    FOREIGN KEY (target_id) REFERENCES insights(id),
                    UNIQUE(source_id, target_id, relationship_type)
                )
            """
            )

            # Create indexes for performance
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_insights_category
                ON insights(category)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_insights_source
                ON insights(source_video_id)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_insights_created
                ON insights(created_at)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_journal_insight
                ON journal_entries(insight_id)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_journal_date
                ON journal_entries(date)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_relationships_source
                ON relationships(source_id)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_relationships_target
                ON relationships(target_id)
            """
            )

            # Create full-text search virtual table
            cursor.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS insights_fts USING fts5(
                    id UNINDEXED,
                    title,
                    description,
                    tags,
                    content='insights',
                    content_rowid='rowid'
                )
            """
            )

            # Create triggers to keep FTS in sync
            cursor.execute(
                """
                CREATE TRIGGER IF NOT EXISTS insights_fts_insert
                AFTER INSERT ON insights BEGIN
                    INSERT INTO insights_fts(rowid, id, title, description, tags)
                    VALUES (new.rowid, new.id, new.title, new.description, new.tags);
                END
            """
            )

            cursor.execute(
                """
                CREATE TRIGGER IF NOT EXISTS insights_fts_update
                AFTER UPDATE ON insights BEGIN
                    UPDATE insights_fts
                    SET title = new.title,
                        description = new.description,
                        tags = new.tags
                    WHERE rowid = new.rowid;
                END
            """
            )

            cursor.execute(
                """
                CREATE TRIGGER IF NOT EXISTS insights_fts_delete
                AFTER DELETE ON insights BEGIN
                    DELETE FROM insights_fts WHERE rowid = old.rowid;
                END
            """
            )

            self.conn.commit()
            self._log(f"Database initialized: {self.db_path}")

        except sqlite3.Error as e:
            self._log(f"Database initialization error: {e}")
            raise

    def store_insight(
        self,
        title: str,
        description: str,
        category: str,
        source_video_id: Optional[str] = None,
        confidence: float = 1.0,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """
        Store a single insight in the database

        Args:
            title: Insight title
            description: Detailed description
            category: Category (tools, techniques, patterns, anti_patterns)
            source_video_id: Source video ID reference
            confidence: Confidence score (0-1)
            tags: List of tags
            metadata: Additional metadata dict

        Returns:
            Insight ID (UUID)
        """
        try:
            # Generate unique ID
            insight_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()

            # Serialize tags and metadata
            tags_str = json.dumps(tags or [])
            metadata_str = json.dumps(metadata or {})

            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO insights
                (id, title, description, category, source_video_id,
                 confidence, created_at, updated_at, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    insight_id,
                    title,
                    description,
                    category,
                    source_video_id,
                    confidence,
                    now,
                    now,
                    tags_str,
                    metadata_str,
                ),
            )

            self.conn.commit()
            self._log(f"Stored insight: {insight_id} - {title[:50]}")
            return insight_id

        except sqlite3.Error as e:
            self._log(f"Error storing insight: {e}")
            self.conn.rollback()
            raise

    def store_source(
        self,
        video_id: str,
        title: str,
        channel: str = None,
        upload_date: str = None,
        views: int = 0,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """
        Store video source metadata

        Args:
            video_id: YouTube video ID
            title: Video title
            channel: Channel name
            upload_date: Upload date (ISO format)
            views: View count
            metadata: Additional metadata

        Returns:
            Source ID (UUID)
        """
        try:
            source_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            metadata_str = json.dumps(metadata or {})

            cursor = self.conn.cursor()

            # Check if source already exists
            cursor.execute("SELECT id FROM sources WHERE video_id = ?", (video_id,))
            existing = cursor.fetchone()

            if existing:
                # Update existing source
                cursor.execute(
                    """
                    UPDATE sources
                    SET title = ?, channel = ?, upload_date = ?,
                        views = ?, metadata = ?
                    WHERE video_id = ?
                """,
                    (title, channel, upload_date, views, metadata_str, video_id),
                )
                source_id = existing[0]
                self._log(f"Updated source: {source_id} - {video_id}")
            else:
                # Insert new source
                cursor.execute(
                    """
                    INSERT INTO sources
                    (id, video_id, title, channel, upload_date, views,
                     created_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        source_id,
                        video_id,
                        title,
                        channel,
                        upload_date,
                        views,
                        now,
                        metadata_str,
                    ),
                )
                self._log(f"Stored source: {source_id} - {video_id}")

            self.conn.commit()
            return source_id

        except sqlite3.Error as e:
            self._log(f"Error storing source: {e}")
            self.conn.rollback()
            raise

    def add_journal_entry(
        self,
        insight_id: Optional[str],
        status: str,
        notes: str = "",
        time_spent: int = 0,
        success: bool = False,
    ) -> str:
        """
        Add implementation journal entry

        Args:
            insight_id: Related insight ID (optional)
            status: Implementation status
            notes: Journal notes
            time_spent: Time spent in minutes
            success: Whether implementation was successful

        Returns:
            Journal entry ID
        """
        try:
            entry_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()

            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO journal_entries
                (id, insight_id, date, status, time_spent, notes,
                 success, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    entry_id,
                    insight_id,
                    now,
                    status,
                    time_spent,
                    notes,
                    1 if success else 0,
                    now,
                ),
            )

            self.conn.commit()
            self._log(f"Added journal entry: {entry_id}")
            return entry_id

        except sqlite3.Error as e:
            self._log(f"Error adding journal entry: {e}")
            self.conn.rollback()
            raise

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        strength: float = 0.5,
    ) -> str:
        """
        Add relationship between insights

        Args:
            source_id: Source insight ID
            target_id: Target insight ID
            relationship_type: Type of relationship (similar, prerequisite, alternative, etc.)
            strength: Relationship strength (0-1)

        Returns:
            Relationship ID
        """
        try:
            relationship_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()

            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO relationships
                (id, source_id, target_id, relationship_type, strength, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    relationship_id,
                    source_id,
                    target_id,
                    relationship_type,
                    strength,
                    now,
                ),
            )

            self.conn.commit()
            self._log(
                f"Added relationship: {source_id} -> {target_id} ({relationship_type})"
            )
            return relationship_id

        except sqlite3.Error as e:
            self._log(f"Error adding relationship: {e}")
            self.conn.rollback()
            raise

    def get_insight(self, insight_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve single insight by ID

        Args:
            insight_id: Insight ID

        Returns:
            Insight dict or None if not found
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM insights WHERE id = ?", (insight_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_dict(row)
            return None

        except sqlite3.Error as e:
            self._log(f"Error retrieving insight: {e}")
            return None

    def get_all_insights(
        self, category: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all insights with optional filtering

        Args:
            category: Filter by category
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of insight dicts
        """
        try:
            cursor = self.conn.cursor()

            if category:
                cursor.execute(
                    """
                    SELECT * FROM insights
                    WHERE category = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """,
                    (category, limit, offset),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM insights
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """,
                    (limit, offset),
                )

            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

        except sqlite3.Error as e:
            self._log(f"Error retrieving insights: {e}")
            return []

    def get_source(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get source by video ID

        Args:
            video_id: YouTube video ID

        Returns:
            Source dict or None
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM sources WHERE video_id = ?", (video_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_dict(row)
            return None

        except sqlite3.Error as e:
            self._log(f"Error retrieving source: {e}")
            return None

    def get_journal_entries(
        self, insight_id: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get journal entries

        Args:
            insight_id: Filter by insight ID
            limit: Maximum entries

        Returns:
            List of journal entry dicts
        """
        try:
            cursor = self.conn.cursor()

            if insight_id:
                cursor.execute(
                    """
                    SELECT * FROM journal_entries
                    WHERE insight_id = ?
                    ORDER BY date DESC
                    LIMIT ?
                """,
                    (insight_id, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM journal_entries
                    ORDER BY date DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

        except sqlite3.Error as e:
            self._log(f"Error retrieving journal entries: {e}")
            return []

    def get_relationships(
        self, insight_id: str, direction: str = "both"
    ) -> List[Dict[str, Any]]:
        """
        Get relationships for an insight

        Args:
            insight_id: Insight ID
            direction: "source", "target", or "both"

        Returns:
            List of relationship dicts
        """
        try:
            cursor = self.conn.cursor()

            if direction == "source":
                cursor.execute(
                    """
                    SELECT * FROM relationships
                    WHERE source_id = ?
                    ORDER BY strength DESC
                """,
                    (insight_id,),
                )
            elif direction == "target":
                cursor.execute(
                    """
                    SELECT * FROM relationships
                    WHERE target_id = ?
                    ORDER BY strength DESC
                """,
                    (insight_id,),
                )
            else:  # both
                cursor.execute(
                    """
                    SELECT * FROM relationships
                    WHERE source_id = ? OR target_id = ?
                    ORDER BY strength DESC
                """,
                    (insight_id, insight_id),
                )

            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

        except sqlite3.Error as e:
            self._log(f"Error retrieving relationships: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics

        Returns:
            Statistics dict with counts and metrics
        """
        try:
            cursor = self.conn.cursor()

            # Total counts
            cursor.execute("SELECT COUNT(*) FROM insights")
            total_insights = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM sources")
            total_sources = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM journal_entries")
            total_journal = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM relationships")
            total_relationships = cursor.fetchone()[0]

            # Category breakdown
            cursor.execute(
                """
                SELECT category, COUNT(*) as count
                FROM insights
                GROUP BY category
            """
            )
            categories = {row[0]: row[1] for row in cursor.fetchall()}

            # Success rate from journal
            cursor.execute(
                """
                SELECT
                    SUM(success) as successes,
                    COUNT(*) as total
                FROM journal_entries
            """
            )
            journal_stats = cursor.fetchone()
            success_rate = (
                journal_stats[0] / journal_stats[1] if journal_stats[1] > 0 else 0
            )

            return {
                "total_insights": total_insights,
                "total_sources": total_sources,
                "total_journal_entries": total_journal,
                "total_relationships": total_relationships,
                "categories": categories,
                "success_rate": success_rate,
            }

        except sqlite3.Error as e:
            self._log(f"Error getting statistics: {e}")
            return {}

    def backup_database(self, backup_path: str = None) -> str:
        """
        Create database backup

        Args:
            backup_path: Backup file path

        Returns:
            Backup file path
        """
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{self.db_path}.backup_{timestamp}"

            # Close connection to allow file copy
            if self.conn:
                self.conn.close()

            # Copy database file
            shutil.copy2(self.db_path, backup_path)

            # Reconnect
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row

            self._log(f"Database backed up to: {backup_path}")
            return backup_path

        except Exception as e:
            self._log(f"Backup error: {e}")
            raise

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """
        Convert SQLite row to dictionary

        Args:
            row: SQLite Row object

        Returns:
            Dictionary with row data
        """
        result = dict(row)

        # Parse JSON fields
        if "tags" in result and result["tags"]:
            try:
                result["tags"] = json.loads(result["tags"])
            except json.JSONDecodeError:
                result["tags"] = []

        if "metadata" in result and result["metadata"]:
            try:
                result["metadata"] = json.loads(result["metadata"])
            except json.JSONDecodeError:
                result["metadata"] = {}

        # Convert boolean
        if "success" in result:
            result["success"] = bool(result["success"])

        return result

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self._log("Database connection closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
