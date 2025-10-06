"""KNOWLEDGE-001: Cross-Reference Engine - Relationship Management

Automatically discovers and maintains relationships between insights using
content similarity, co-occurrence patterns, and explicit linkages.

Features:
- Automatic relationship discovery via text similarity
- Deduplication using semantic similarity
- Co-occurrence pattern detection
- Relationship strength scoring
- Transitive relationship inference
- Relationship type classification

Author: Backend Developer Agent
Version: 1.0.0
"""

import re
import json
from typing import Dict, List, Any, Tuple, Set
from collections import Counter
from datetime import datetime


class CrossReferenceEngine:
    """Discovers and manages relationships between insights"""

    # Relationship types
    RELATIONSHIP_TYPES = {
        "similar": "Content is similar",
        "prerequisite": "Required before this insight",
        "alternative": "Alternative approach to same problem",
        "complement": "Works well together",
        "supersedes": "Newer version of this insight",
        "duplicate": "Exact or near duplicate",
        "related": "General relationship",
    }

    def __init__(self, knowledge_store, search_engine, callback=None):
        """
        Initialize cross-reference engine

        Args:
            knowledge_store: KnowledgeStore instance
            search_engine: SearchEngine instance
            callback: Optional callback for logging
        """
        self.store = knowledge_store
        self.search = search_engine
        self.callback = callback or print

    def _log(self, message: str):
        """Internal logging helper"""
        if self.callback:
            self.callback(message)

    def find_duplicates(
        self, insight: Dict[str, Any], threshold: float = 0.85
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find potential duplicate insights

        Args:
            insight: Insight to check for duplicates
            threshold: Similarity threshold (0-1)

        Returns:
            List of (duplicate_insight, similarity_score) tuples
        """
        try:
            # Extract text content
            text = f"{insight['title']} {insight.get('description', '')}"

            # Search for similar insights
            search_results = self.search.search(
                query=text, filters={"category": insight.get("category")}, limit=20
            )

            duplicates = []

            for result in search_results["results"]:
                # Skip self
                if result["id"] == insight.get("id"):
                    continue

                # Calculate similarity
                similarity = self._calculate_similarity(insight, result)

                if similarity >= threshold:
                    duplicates.append((result, similarity))

            # Sort by similarity (highest first)
            duplicates.sort(key=lambda x: x[1], reverse=True)

            self._log(
                f"Found {len(duplicates)} duplicates for '{insight['title'][:50]}'"
            )
            return duplicates

        except Exception as e:
            self._log(f"Duplicate detection error: {e}")
            return []

    def _calculate_similarity(
        self, insight1: Dict[str, Any], insight2: Dict[str, Any]
    ) -> float:
        """
        Calculate similarity score between two insights

        Uses weighted combination of:
        - Title similarity (30%)
        - Description similarity (50%)
        - Tag overlap (20%)

        Args:
            insight1: First insight
            insight2: Second insight

        Returns:
            Similarity score (0-1)
        """
        # Title similarity
        title1 = insight1.get("title", "").lower()
        title2 = insight2.get("title", "").lower()
        title_sim = self._jaccard_similarity(
            self._tokenize(title1), self._tokenize(title2)
        )

        # Description similarity
        desc1 = insight1.get("description", "").lower()
        desc2 = insight2.get("description", "").lower()
        desc_sim = self._jaccard_similarity(
            self._tokenize(desc1), self._tokenize(desc2)
        )

        # Tag overlap
        tags1 = set(insight1.get("tags", []))
        tags2 = set(insight2.get("tags", []))
        tag_sim = self._jaccard_similarity(tags1, tags2)

        # Weighted combination
        similarity = 0.3 * title_sim + 0.5 * desc_sim + 0.2 * tag_sim

        return similarity

    def _tokenize(self, text: str) -> Set[str]:
        """
        Tokenize text into words

        Args:
            text: Input text

        Returns:
            Set of tokens
        """
        # Remove punctuation and split
        tokens = re.findall(r"\w+", text.lower())
        # Remove common stop words
        stop_words = {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "by",
            "for",
            "from",
            "in",
            "is",
            "it",
            "of",
            "on",
            "or",
            "that",
            "the",
            "to",
            "was",
            "with",
        }
        return set(t for t in tokens if t not in stop_words and len(t) > 2)

    def _jaccard_similarity(self, set1: Set, set2: Set) -> float:
        """
        Calculate Jaccard similarity between two sets

        Args:
            set1: First set
            set2: Second set

        Returns:
            Jaccard similarity (0-1)
        """
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def merge_duplicates(self, primary_id: str, duplicate_ids: List[str]) -> bool:
        """
        Merge duplicate insights into primary

        Args:
            primary_id: ID of primary insight to keep
            duplicate_ids: List of duplicate IDs to merge

        Returns:
            Success boolean
        """
        try:
            primary = self.store.get_insight(primary_id)
            if not primary:
                self._log(f"Primary insight not found: {primary_id}")
                return False

            for dup_id in duplicate_ids:
                duplicate = self.store.get_insight(dup_id)
                if not duplicate:
                    continue

                # Add duplicate relationship
                self.store.add_relationship(
                    source_id=dup_id,
                    target_id=primary_id,
                    relationship_type="duplicate",
                    strength=1.0,
                )

                # Merge tags
                primary_tags = set(primary.get("tags", []))
                dup_tags = set(duplicate.get("tags", []))
                merged_tags = list(primary_tags | dup_tags)

                # Update primary with merged tags
                cursor = self.store.conn.cursor()
                cursor.execute(
                    """
                    UPDATE insights
                    SET tags = ?,
                        confidence = MAX(confidence, ?),
                        updated_at = ?
                    WHERE id = ?
                """,
                    (
                        json.dumps(merged_tags),
                        duplicate.get("confidence", 1.0),
                        datetime.utcnow().isoformat(),
                        primary_id,
                    ),
                )

                # Transfer journal entries
                cursor.execute(
                    """
                    UPDATE journal_entries
                    SET insight_id = ?
                    WHERE insight_id = ?
                """,
                    (primary_id, dup_id),
                )

                # Transfer relationships
                cursor.execute(
                    """
                    UPDATE relationships
                    SET source_id = ?
                    WHERE source_id = ?
                """,
                    (primary_id, dup_id),
                )

                cursor.execute(
                    """
                    UPDATE relationships
                    SET target_id = ?
                    WHERE target_id = ?
                """,
                    (primary_id, dup_id),
                )

                self.store.conn.commit()

                self._log(f"Merged duplicate {dup_id} into {primary_id}")

            return True

        except Exception as e:
            self._log(f"Merge error: {e}")
            self.store.conn.rollback()
            return False

    def discover_relationships(
        self, insight_id: str, max_relationships: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Automatically discover relationships for an insight

        Args:
            insight_id: Insight ID to find relationships for
            max_relationships: Maximum relationships to create

        Returns:
            List of created relationships
        """
        try:
            insight = self.store.get_insight(insight_id)
            if not insight:
                return []

            created_relationships = []

            # Find similar insights
            similar = self.search.search_similar(insight_id, limit=10)

            for similar_insight in similar[:max_relationships]:
                # Calculate relationship strength
                strength = similar_insight.get("relevance_score", 0.5)

                # Determine relationship type
                rel_type = self._classify_relationship(insight, similar_insight)

                # Create relationship
                rel_id = self.store.add_relationship(
                    source_id=insight_id,
                    target_id=similar_insight["id"],
                    relationship_type=rel_type,
                    strength=strength,
                )

                created_relationships.append(
                    {
                        "id": rel_id,
                        "target_id": similar_insight["id"],
                        "type": rel_type,
                        "strength": strength,
                    }
                )

            self._log(
                f"Discovered {len(created_relationships)} relationships "
                f"for {insight_id}"
            )
            return created_relationships

        except Exception as e:
            self._log(f"Relationship discovery error: {e}")
            return []

    def _classify_relationship(
        self, insight1: Dict[str, Any], insight2: Dict[str, Any]
    ) -> str:
        """
        Classify relationship type between insights

        Args:
            insight1: First insight
            insight2: Second insight

        Returns:
            Relationship type string
        """
        # Check for prerequisite keywords
        prereq_keywords = {
            "prerequisite",
            "requires",
            "depends on",
            "need to",
            "must first",
            "before",
        }
        desc2_lower = insight2.get("description", "").lower()

        if any(kw in desc2_lower for kw in prereq_keywords):
            return "prerequisite"

        # Check for alternative keywords
        alt_keywords = {
            "alternative",
            "instead",
            "alternatively",
            "option",
            "another way",
        }
        if any(kw in desc2_lower for kw in alt_keywords):
            return "alternative"

        # Check for complement keywords
        comp_keywords = {
            "complement",
            "works with",
            "pairs with",
            "enhances",
            "combines with",
        }
        if any(kw in desc2_lower for kw in comp_keywords):
            return "complement"

        # Check for supersedes (date-based)
        date1 = insight1.get("created_at", "")
        date2 = insight2.get("created_at", "")
        if date2 > date1:
            similarity = self._calculate_similarity(insight1, insight2)
            if similarity > 0.7:
                return "supersedes"

        # Default to similar
        return "similar"

    def find_co_occurring_insights(
        self, video_id: str, min_occurrences: int = 2
    ) -> List[Tuple[str, str, int]]:
        """
        Find insights that frequently appear together in videos

        Args:
            video_id: Source video ID to analyze
            min_occurrences: Minimum co-occurrences required

        Returns:
            List of (insight1_id, insight2_id, count) tuples
        """
        try:
            cursor = self.store.conn.cursor()

            # Get all insights from same sources
            cursor.execute(
                """
                SELECT i1.id as id1, i2.id as id2, COUNT(*) as count
                FROM insights i1
                JOIN insights i2 ON i1.source_video_id = i2.source_video_id
                WHERE i1.id < i2.id
                GROUP BY i1.id, i2.id
                HAVING count >= ?
                ORDER BY count DESC
            """,
                (min_occurrences,),
            )

            results = cursor.fetchall()

            co_occurrences = [(row[0], row[1], row[2]) for row in results]

            self._log(f"Found {len(co_occurrences)} co-occurring insight pairs")
            return co_occurrences

        except Exception as e:
            self._log(f"Co-occurrence detection error: {e}")
            return []

    def build_relationship_graph(
        self, root_id: str, max_depth: int = 2
    ) -> Dict[str, Any]:
        """
        Build relationship graph starting from root insight

        Args:
            root_id: Root insight ID
            max_depth: Maximum traversal depth

        Returns:
            Graph dict with nodes and edges
        """
        try:
            visited = set()
            graph = {"nodes": [], "edges": []}

            def traverse(insight_id: str, depth: int):
                if depth > max_depth or insight_id in visited:
                    return

                visited.add(insight_id)

                # Add node
                insight = self.store.get_insight(insight_id)
                if insight:
                    graph["nodes"].append(
                        {
                            "id": insight_id,
                            "title": insight["title"],
                            "category": insight.get("category"),
                            "depth": depth,
                        }
                    )

                # Get relationships
                relationships = self.store.get_relationships(
                    insight_id, direction="both"
                )

                for rel in relationships:
                    # Add edge
                    graph["edges"].append(
                        {
                            "source": rel["source_id"],
                            "target": rel["target_id"],
                            "type": rel["relationship_type"],
                            "strength": rel["strength"],
                        }
                    )

                    # Traverse connected insights
                    next_id = (
                        rel["target_id"]
                        if rel["source_id"] == insight_id
                        else rel["source_id"]
                    )
                    traverse(next_id, depth + 1)

            traverse(root_id, 0)

            self._log(
                f"Built graph: {len(graph['nodes'])} nodes, "
                f"{len(graph['edges'])} edges"
            )
            return graph

        except Exception as e:
            self._log(f"Graph building error: {e}")
            return {"nodes": [], "edges": []}

    def suggest_tags(self, insight: Dict[str, Any], limit: int = 5) -> List[str]:
        """
        Suggest tags based on similar insights

        Args:
            insight: Insight to suggest tags for
            limit: Maximum tag suggestions

        Returns:
            List of suggested tags
        """
        try:
            # Find similar insights
            similar = self.search.search_similar(insight.get("id", ""), limit=10)

            # Collect tags from similar insights
            tag_counter = Counter()

            for similar_insight in similar:
                tags = similar_insight.get("tags", [])
                tag_counter.update(tags)

            # Remove tags already present
            existing_tags = set(insight.get("tags", []))
            suggested = [
                tag
                for tag, count in tag_counter.most_common(limit * 2)
                if tag not in existing_tags
            ][:limit]

            self._log(f"Suggested {len(suggested)} tags")
            return suggested

        except Exception as e:
            self._log(f"Tag suggestion error: {e}")
            return []

    def validate_relationships(self) -> Dict[str, Any]:
        """
        Validate all relationships in knowledge base

        Returns:
            Validation report with issues found
        """
        try:
            cursor = self.store.conn.cursor()

            report = {"total_relationships": 0, "valid": 0, "invalid": 0, "issues": []}

            # Get all relationships
            cursor.execute("SELECT * FROM relationships")
            relationships = cursor.fetchall()

            report["total_relationships"] = len(relationships)

            for rel in relationships:
                rel_dict = self.store._row_to_dict(rel)

                # Check if both insights exist
                source = self.store.get_insight(rel_dict["source_id"])
                target = self.store.get_insight(rel_dict["target_id"])

                if not source:
                    report["invalid"] += 1
                    report["issues"].append(
                        {
                            "type": "missing_source",
                            "relationship_id": rel_dict["id"],
                            "source_id": rel_dict["source_id"],
                        }
                    )
                elif not target:
                    report["invalid"] += 1
                    report["issues"].append(
                        {
                            "type": "missing_target",
                            "relationship_id": rel_dict["id"],
                            "target_id": rel_dict["target_id"],
                        }
                    )
                else:
                    report["valid"] += 1

            self._log(
                f"Validation complete: {report['valid']} valid, "
                f"{report['invalid']} invalid"
            )
            return report

        except Exception as e:
            self._log(f"Validation error: {e}")
            return {"error": str(e)}
