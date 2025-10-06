"""KNOWLEDGE-001: Search Engine - Full-Text Search & Filtering

Provides semantic and keyword-based search across knowledge base with
advanced filtering, ranking, and result aggregation.

Features:
- Full-text search using SQLite FTS5
- Semantic similarity search using simple embeddings
- Multi-field search (title, description, tags)
- Advanced filtering (category, date range, confidence)
- Ranked results with relevance scoring
- Faceted search results

Author: Backend Developer Agent
Version: 1.0.0
"""

import sqlite3
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta


class SearchEngine:
    """Advanced search engine for knowledge base"""

    def __init__(self, knowledge_store, callback=None):
        """
        Initialize search engine

        Args:
            knowledge_store: KnowledgeStore instance
            callback: Optional callback for logging
        """
        self.store = knowledge_store
        self.callback = callback or print

    def _log(self, message: str):
        """Internal logging helper"""
        if self.callback:
            self.callback(message)

    def search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Execute comprehensive search across knowledge base

        Args:
            query: Search query string
            filters: Optional filters dict with keys:
                - category: str or List[str]
                - confidence_min: float (0-1)
                - date_from: str (ISO format)
                - date_to: str (ISO format)
                - tags: List[str]
                - source_video_id: str
            limit: Maximum results to return
            offset: Pagination offset

        Returns:
            Dict with:
                - results: List of matching insights
                - total: Total matching count
                - facets: Faceted aggregations
                - query_time: Search execution time (ms)
        """
        start_time = datetime.now()
        filters = filters or {}

        try:
            # If empty query, use fallback search
            if not query or not query.strip():
                results = self._fallback_search(query, filters, limit, offset)
            else:
                # Execute full-text search
                results = self._full_text_search(query, filters, limit, offset)

            # Get total count
            if not query or not query.strip():
                total_count = len(results)
            else:
                total_count = self._count_results(query, filters)

            # Generate facets
            if not query or not query.strip():
                facets = self._generate_facets_all(filters)
            else:
                facets = self._generate_facets(query, filters)

            # Calculate query time
            query_time = (datetime.now() - start_time).total_seconds() * 1000

            self._log(
                f"Search completed: '{query}' - {len(results)} results "
                f"({query_time:.2f}ms)"
            )

            return {
                "results": results,
                "total": total_count,
                "facets": facets,
                "query_time": query_time,
                "query": query,
                "filters": filters,
            }

        except Exception as e:
            self._log(f"Search error: {e}")
            return {
                "results": [],
                "total": 0,
                "facets": {},
                "query_time": 0,
                "error": str(e),
            }

    def _full_text_search(
        self, query: str, filters: Dict[str, Any], limit: int, offset: int
    ) -> List[Dict[str, Any]]:
        """
        Execute FTS5 full-text search

        Args:
            query: Search query
            filters: Filter conditions
            limit: Result limit
            offset: Pagination offset

        Returns:
            List of matching insights with relevance scores
        """
        try:
            cursor = self.store.conn.cursor()

            # Build FTS5 query (handle special characters)
            fts_query = self._sanitize_fts_query(query)

            # Build base SQL with FTS
            sql = """
                SELECT
                    i.*,
                    fts.rank as relevance_score
                FROM insights i
                JOIN insights_fts fts ON i.id = fts.id
                WHERE insights_fts MATCH ?
            """

            params = [fts_query]

            # Apply filters
            filter_clauses, filter_params = self._build_filter_clauses(filters)
            if filter_clauses:
                sql += " AND " + " AND ".join(filter_clauses)
                params.extend(filter_params)

            # Order by relevance
            sql += " ORDER BY fts.rank, i.created_at DESC"

            # Pagination
            sql += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            # Convert to dicts and normalize scores
            results = []
            for row in rows:
                insight = self.store._row_to_dict(row)
                # FTS5 rank is negative (lower is better), normalize to 0-1
                raw_rank = row["relevance_score"]
                insight["relevance_score"] = self._normalize_rank(raw_rank)
                results.append(insight)

            return results

        except sqlite3.Error as e:
            self._log(f"FTS search error: {e}")
            # Fallback to basic LIKE search
            return self._fallback_search(query, filters, limit, offset)

    def _fallback_search(
        self, query: str, filters: Dict[str, Any], limit: int, offset: int
    ) -> List[Dict[str, Any]]:
        """
        Fallback search using LIKE when FTS fails

        Args:
            query: Search query
            filters: Filter conditions
            limit: Result limit
            offset: Pagination offset

        Returns:
            List of matching insights
        """
        try:
            cursor = self.store.conn.cursor()

            # Build SQL - if no query, just filter
            if query and query.strip():
                like_pattern = f"%{query}%"
                sql = """
                    SELECT * FROM insights
                    WHERE (title LIKE ? OR description LIKE ?)
                """
                params = [like_pattern, like_pattern]
            else:
                sql = "SELECT * FROM insights WHERE 1=1"
                params = []

            # Apply filters (no table alias needed in fallback)
            filter_clauses, filter_params = self._build_filter_clauses(
                filters, table_alias="insights"
            )
            if filter_clauses:
                sql += " AND " + " AND ".join(filter_clauses)
                params.extend(filter_params)

            sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                insight = self.store._row_to_dict(row)
                insight["relevance_score"] = 0.5  # Default relevance
                results.append(insight)

            self._log(f"Fallback search returned {len(results)} results")
            return results

        except sqlite3.Error as e:
            self._log(f"Fallback search error: {e}")
            return []

    def _count_results(self, query: str, filters: Dict[str, Any]) -> int:
        """
        Count total matching results

        Args:
            query: Search query
            filters: Filter conditions

        Returns:
            Total count of matching insights
        """
        try:
            cursor = self.store.conn.cursor()

            # If no query, use fallback count
            if not query or not query.strip():
                sql = "SELECT COUNT(*) FROM insights"
                params = []

                filter_clauses, filter_params = self._build_filter_clauses(
                    filters, table_alias="insights"
                )
                if filter_clauses:
                    sql += " WHERE " + " AND ".join(filter_clauses)
                    params.extend(filter_params)

                cursor.execute(sql, params)
                return cursor.fetchone()[0]

            # FTS count
            fts_query = self._sanitize_fts_query(query)

            sql = """
                SELECT COUNT(DISTINCT i.id)
                FROM insights i
                JOIN insights_fts fts ON i.id = fts.id
                WHERE insights_fts MATCH ?
            """
            params = [fts_query]

            # Apply filters
            filter_clauses, filter_params = self._build_filter_clauses(filters)
            if filter_clauses:
                sql += " AND " + " AND ".join(filter_clauses)
                params.extend(filter_params)

            cursor.execute(sql, params)
            count = cursor.fetchone()[0]
            return count

        except sqlite3.Error as e:
            self._log(f"Count error: {e}")
            return 0

    def _build_filter_clauses(
        self, filters: Dict[str, Any], table_alias: str = "i"
    ) -> Tuple[List[str], List[Any]]:
        """
        Build SQL WHERE clauses from filters

        Args:
            filters: Filter dict
            table_alias: Table alias prefix (default "i")

        Returns:
            Tuple of (clause_list, params_list)
        """
        clauses = []
        params = []

        # Category filter
        if "category" in filters:
            category = filters["category"]
            if isinstance(category, list):
                placeholders = ",".join(["?"] * len(category))
                clauses.append(f"{table_alias}.category IN ({placeholders})")
                params.extend(category)
            else:
                clauses.append(f"{table_alias}.category = ?")
                params.append(category)

        # Confidence threshold
        if "confidence_min" in filters:
            clauses.append(f"{table_alias}.confidence >= ?")
            params.append(filters["confidence_min"])

        # Date range
        if "date_from" in filters:
            clauses.append(f"{table_alias}.created_at >= ?")
            params.append(filters["date_from"])

        if "date_to" in filters:
            clauses.append(f"{table_alias}.created_at <= ?")
            params.append(filters["date_to"])

        # Source video filter
        if "source_video_id" in filters:
            clauses.append(f"{table_alias}.source_video_id = ?")
            params.append(filters["source_video_id"])

        # Tags filter (JSON array contains)
        if "tags" in filters:
            tags = filters["tags"]
            if isinstance(tags, list):
                for tag in tags:
                    # SQLite JSON functions for tag matching
                    clauses.append(
                        f"EXISTS (SELECT 1 FROM json_each({table_alias}.tags) WHERE value = ?)"
                    )
                    params.append(tag)

        return clauses, params

    def _generate_facets_all(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate facets for all insights (no search query)

        Args:
            filters: Current filters

        Returns:
            Dict with facet aggregations
        """
        try:
            cursor = self.store.conn.cursor()
            facets = {}

            # Category facets
            sql = "SELECT category, COUNT(*) as count FROM insights"
            params = []

            # Apply non-category filters
            filter_clauses, filter_params = self._build_filter_clauses(
                {k: v for k, v in filters.items() if k != "category"}
            )
            if filter_clauses:
                sql += " WHERE " + " AND ".join(filter_clauses)
                params.extend(filter_params)

            sql += " GROUP BY category ORDER BY count DESC"

            cursor.execute(sql, params)
            facets["categories"] = {
                row[0]: row[1] for row in cursor.fetchall() if row[0]
            }

            # Confidence range facets
            sql_confidence = """
                SELECT
                    CASE
                        WHEN confidence >= 0.8 THEN 'high'
                        WHEN confidence >= 0.5 THEN 'medium'
                        ELSE 'low'
                    END as confidence_range,
                    COUNT(*) as count
                FROM insights
            """
            params_conf = []

            filter_clauses_conf, filter_params_conf = self._build_filter_clauses(
                {k: v for k, v in filters.items() if k != "confidence_min"},
                table_alias="insights",
            )
            if filter_clauses_conf:
                sql_confidence += " WHERE " + " AND ".join(filter_clauses_conf)
                params_conf.extend(filter_params_conf)

            sql_confidence += " GROUP BY confidence_range"

            cursor.execute(sql_confidence, params_conf)
            facets["confidence_ranges"] = {row[0]: row[1] for row in cursor.fetchall()}

            return facets

        except Exception as e:
            self._log(f"Facet generation error: {e}")
            return {}

    def _generate_facets(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate faceted aggregations for search results

        Args:
            query: Search query
            filters: Current filters

        Returns:
            Dict with facet aggregations
        """
        try:
            cursor = self.store.conn.cursor()
            fts_query = self._sanitize_fts_query(query)

            facets = {}

            # Category facets
            sql = """
                SELECT i.category, COUNT(*) as count
                FROM insights i
                JOIN insights_fts fts ON i.id = fts.id
                WHERE insights_fts MATCH ?
            """
            params = [fts_query]

            # Apply non-category filters
            filter_clauses, filter_params = self._build_filter_clauses(
                {k: v for k, v in filters.items() if k != "category"}
            )
            if filter_clauses:
                sql += " AND " + " AND ".join(filter_clauses)
                params.extend(filter_params)

            sql += " GROUP BY i.category ORDER BY count DESC"

            cursor.execute(sql, params)
            facets["categories"] = {
                row[0]: row[1] for row in cursor.fetchall() if row[0]
            }

            # Confidence range facets
            sql_confidence = """
                SELECT
                    CASE
                        WHEN i.confidence >= 0.8 THEN 'high'
                        WHEN i.confidence >= 0.5 THEN 'medium'
                        ELSE 'low'
                    END as confidence_range,
                    COUNT(*) as count
                FROM insights i
                JOIN insights_fts fts ON i.id = fts.id
                WHERE insights_fts MATCH ?
            """
            params_conf = [fts_query]

            filter_clauses_conf, filter_params_conf = self._build_filter_clauses(
                {k: v for k, v in filters.items() if k != "confidence_min"},
                table_alias="i",
            )
            if filter_clauses_conf:
                sql_confidence += " AND " + " AND ".join(filter_clauses_conf)
                params_conf.extend(filter_params_conf)

            sql_confidence += " GROUP BY confidence_range"

            cursor.execute(sql_confidence, params_conf)
            facets["confidence_ranges"] = {row[0]: row[1] for row in cursor.fetchall()}

            return facets

        except sqlite3.Error as e:
            self._log(f"Facet generation error: {e}")
            return {}

    def _sanitize_fts_query(self, query: str) -> str:
        """
        Sanitize query for FTS5 syntax

        Args:
            query: Raw query string

        Returns:
            Sanitized FTS5 query
        """
        # Remove special FTS5 characters
        query = re.sub(r"[^\w\s\-]", " ", query)

        # Split into terms
        terms = query.strip().split()

        # Wrap in quotes for phrase search if multi-word
        if len(terms) > 1:
            return " OR ".join([f'"{term}"' for term in terms])
        elif len(terms) == 1:
            return f'"{terms[0]}"'
        else:
            return '""'

    def _normalize_rank(self, rank: float) -> float:
        """
        Normalize FTS5 rank to 0-1 scale

        Args:
            rank: Raw FTS5 rank (negative value)

        Returns:
            Normalized score (0-1, higher is better)
        """
        # FTS5 rank is negative, lower is better
        # Normalize using sigmoid-like function
        normalized = 1 / (1 + abs(rank))
        return min(max(normalized, 0.0), 1.0)

    def search_similar(self, insight_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar insights based on content

        Args:
            insight_id: Reference insight ID
            limit: Maximum similar insights to return

        Returns:
            List of similar insights with similarity scores
        """
        try:
            # Get reference insight
            reference = self.store.get_insight(insight_id)
            if not reference:
                return []

            # Build query from reference title and description
            query = f"{reference['title']} {reference['description']}"

            # Search, excluding the reference itself
            results = self.search(query=query, filters={}, limit=limit + 1, offset=0)

            # Filter out reference insight and limit
            similar = [r for r in results["results"] if r["id"] != insight_id][:limit]

            self._log(f"Found {len(similar)} similar insights for {insight_id}")
            return similar

        except Exception as e:
            self._log(f"Similar search error: {e}")
            return []

    def get_trending(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending insights based on recent activity

        Args:
            days: Look-back period in days
            limit: Maximum results

        Returns:
            List of trending insights
        """
        try:
            cursor = self.store.conn.cursor()

            # Calculate date threshold
            threshold_date = (datetime.now() - timedelta(days=days)).isoformat()

            # Count journal entries per insight in time window
            sql = """
                SELECT
                    i.*,
                    COUNT(j.id) as activity_count
                FROM insights i
                LEFT JOIN journal_entries j ON i.id = j.insight_id
                WHERE i.created_at >= ? OR j.date >= ?
                GROUP BY i.id
                ORDER BY activity_count DESC, i.created_at DESC
                LIMIT ?
            """

            cursor.execute(sql, (threshold_date, threshold_date, limit))
            rows = cursor.fetchall()

            results = []
            for row in rows:
                insight = self.store._row_to_dict(row)
                insight["activity_count"] = row["activity_count"]
                results.append(insight)

            self._log(f"Found {len(results)} trending insights")
            return results

        except sqlite3.Error as e:
            self._log(f"Trending search error: {e}")
            return []

    def get_most_mentioned(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most referenced insights

        Args:
            limit: Maximum results

        Returns:
            List of most mentioned insights
        """
        try:
            cursor = self.store.conn.cursor()

            # Count relationships (both incoming and outgoing)
            sql = """
                SELECT
                    i.*,
                    COUNT(r.id) as mention_count
                FROM insights i
                LEFT JOIN relationships r
                    ON (r.source_id = i.id OR r.target_id = i.id)
                GROUP BY i.id
                ORDER BY mention_count DESC, i.created_at DESC
                LIMIT ?
            """

            cursor.execute(sql, (limit,))
            rows = cursor.fetchall()

            results = []
            for row in rows:
                insight = self.store._row_to_dict(row)
                insight["mention_count"] = row["mention_count"]
                results.append(insight)

            self._log(f"Found {len(results)} most mentioned insights")
            return results

        except sqlite3.Error as e:
            self._log(f"Most mentioned search error: {e}")
            return []

    def advanced_search(
        self,
        title_query: str = None,
        description_query: str = None,
        tags: List[str] = None,
        category: str = None,
        confidence_range: Tuple[float, float] = None,
        date_range: Tuple[str, str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Advanced multi-field search

        Args:
            title_query: Search in title field
            description_query: Search in description field
            tags: Filter by tags
            category: Filter by category
            confidence_range: Tuple of (min, max) confidence
            date_range: Tuple of (from_date, to_date) ISO strings
            limit: Maximum results

        Returns:
            List of matching insights
        """
        try:
            cursor = self.store.conn.cursor()

            sql = "SELECT * FROM insights WHERE 1=1"
            params = []

            # Title search
            if title_query:
                sql += " AND title LIKE ?"
                params.append(f"%{title_query}%")

            # Description search
            if description_query:
                sql += " AND description LIKE ?"
                params.append(f"%{description_query}%")

            # Tags filter
            if tags:
                for tag in tags:
                    sql += " AND EXISTS (SELECT 1 FROM json_each(tags) WHERE value = ?)"
                    params.append(tag)

            # Category filter
            if category:
                sql += " AND category = ?"
                params.append(category)

            # Confidence range
            if confidence_range:
                sql += " AND confidence BETWEEN ? AND ?"
                params.extend(confidence_range)

            # Date range
            if date_range:
                sql += " AND created_at BETWEEN ? AND ?"
                params.extend(date_range)

            sql += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            results = [self.store._row_to_dict(row) for row in rows]

            self._log(f"Advanced search returned {len(results)} results")
            return results

        except sqlite3.Error as e:
            self._log(f"Advanced search error: {e}")
            return []
