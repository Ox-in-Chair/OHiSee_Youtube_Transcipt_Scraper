"""
Learning Path Generator - Create dependency-ordered learning paths

Analyzes item dependencies and generates phased implementation paths
with quick wins identification and prerequisite ordering.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class LearningPhase:
    """Single phase in learning path"""

    phase_number: int
    title: str
    goal: str
    items: List[Dict]  # Item IDs with metadata
    estimated_hours: int
    prerequisites: List[str]  # Previous phase IDs
    success_criteria: str


@dataclass
class LearningPath:
    """Complete learning path with phases"""

    phases: List[LearningPhase]
    total_hours: int
    quick_wins: List[Dict]  # High ROI, low complexity items
    foundational: List[Dict]  # Required for later items
    advanced: List[Dict]  # Requires earlier phases
    dependency_graph: Dict[str, List[str]]  # Item ID -> dependencies
    mermaid_diagram: str  # Mermaid flowchart


class LearningPathGenerator:
    """
    Generate phased learning paths with dependency ordering
    """

    def __init__(self, callback=None):
        """
        Initialize learning path generator

        Args:
            callback: Optional logging function
        """
        self.callback = callback

    def generate_path(
        self,
        items: List[Dict],
        readiness_scores: Optional[Dict[str, Dict]] = None,
        roi_scores: Optional[Dict[str, Dict]] = None,
    ) -> LearningPath:
        """
        Generate phased learning path

        Args:
            items: List of notable items from CORE-001
            readiness_scores: Optional readiness scores by item ID
            roi_scores: Optional ROI scores by item ID

        Returns:
            LearningPath with complete phased structure
        """
        # Build dependency graph
        dep_graph = self._build_dependency_graph(items)

        # Topologically sort items
        sorted_items = self._topological_sort(items, dep_graph)

        # Identify quick wins
        quick_wins = self._identify_quick_wins(items, readiness_scores, roi_scores)

        # Identify foundational items
        foundational = self._identify_foundational(items, dep_graph)

        # Cluster into phases
        phases = self._cluster_into_phases(sorted_items, readiness_scores, dep_graph)

        # Identify advanced items
        advanced = self._identify_advanced(items, phases, readiness_scores)

        # Calculate total time
        total_hours = sum(phase.estimated_hours for phase in phases)

        # Generate Mermaid diagram
        mermaid = self._generate_mermaid_diagram(phases, dep_graph)

        return LearningPath(
            phases=phases,
            total_hours=total_hours,
            quick_wins=quick_wins,
            foundational=foundational,
            advanced=advanced,
            dependency_graph=dep_graph,
            mermaid_diagram=mermaid,
        )

    def _build_dependency_graph(self, items: List[Dict]) -> Dict[str, List[str]]:
        """
        Build dependency graph from items

        Args:
            items: List of notable items

        Returns:
            Dict mapping item ID to list of dependency IDs
        """
        graph = defaultdict(list)
        item_titles = {item.get("id"): item.get("title", "") for item in items}

        for item in items:
            item_id = item.get("id", "")
            dependencies = []

            # Check explicit prerequisites
            if "prerequisites" in item:
                for prereq in item["prerequisites"]:
                    # Try to match prerequisite to another item title
                    dep_id = self._match_prerequisite_to_item(prereq, item_titles)
                    if dep_id and dep_id != item_id:
                        dependencies.append(dep_id)

            # Extract implicit dependencies from description
            text = f"{item.get('description', '')} {' '.join(item.get('implementation_steps', []))}"
            implicit_deps = self._extract_implicit_dependencies(
                text, item_titles, item_id
            )
            dependencies.extend(implicit_deps)

            # Remove duplicates
            graph[item_id] = list(set(dependencies))

        return dict(graph)

    def _match_prerequisite_to_item(
        self, prerequisite: str, item_titles: Dict[str, str]
    ) -> Optional[str]:
        """
        Match a prerequisite string to an item ID

        Args:
            prerequisite: Prerequisite description
            item_titles: Dict of item ID -> title

        Returns:
            Matching item ID or None
        """
        prereq_lower = prerequisite.lower()

        # Try exact title match
        for item_id, title in item_titles.items():
            if title.lower() in prereq_lower or prereq_lower in title.lower():
                return item_id

        # Try keyword match (extract key terms)
        prereq_keywords = re.findall(r"\b[a-z]{4,}\b", prereq_lower)
        for item_id, title in item_titles.items():
            title_lower = title.lower()
            # If 2+ keywords match, consider it a dependency
            matches = sum(1 for kw in prereq_keywords if kw in title_lower)
            if matches >= 2:
                return item_id

        return None

    def _extract_implicit_dependencies(
        self, text: str, item_titles: Dict[str, str], current_item_id: str
    ) -> List[str]:
        """
        Extract implicit dependencies from text

        Args:
            text: Item description and steps
            item_titles: Dict of item ID -> title
            current_item_id: Current item ID to exclude

        Returns:
            List of dependency item IDs
        """
        dependencies = []
        text_lower = text.lower()

        # Dependency signal phrases
        dependency_patterns = [
            r"requires?\s+([^.]+)",
            r"after\s+(?:setting up|installing|configuring)\s+([^.]+)",
            r"first\s+(?:set up|install|configure)\s+([^.]+)",
            r"depends on\s+([^.]+)",
        ]

        for pattern in dependency_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                mentioned = match.group(1)
                # Try to match to item title
                dep_id = self._match_prerequisite_to_item(mentioned, item_titles)
                if dep_id and dep_id != current_item_id:
                    dependencies.append(dep_id)

        return list(set(dependencies))

    def _topological_sort(
        self, items: List[Dict], dep_graph: Dict[str, List[str]]
    ) -> List[Dict]:
        """
        Sort items by dependency order (topological sort)

        Args:
            items: List of notable items
            dep_graph: Dependency graph

        Returns:
            Sorted list of items
        """
        # Build reverse lookup
        item_map = {item.get("id"): item for item in items}

        # Calculate in-degrees (how many items depend on me)
        in_degree = defaultdict(int)
        for item in items:
            item_id = item.get("id")
            # Initialize all items with 0 in-degree
            in_degree[item_id] = 0

        # For each item, count how many dependencies it has
        for item_id, dependencies in dep_graph.items():
            in_degree[item_id] = len(dependencies)

        # Initialize queue with items that have no dependencies
        queue = [item.get("id") for item in items if in_degree[item.get("id")] == 0]

        sorted_ids = []
        while queue:
            # Sort queue by item title for consistent ordering
            queue.sort(key=lambda x: item_map.get(x, {}).get("title", ""))

            current_id = queue.pop(0)
            sorted_ids.append(current_id)

            # Reduce in-degree for items that depend on current
            for item_id, dependencies in dep_graph.items():
                if current_id in dependencies:
                    in_degree[item_id] -= 1
                    if in_degree[item_id] == 0 and item_id not in sorted_ids:
                        queue.append(item_id)

        # Handle remaining items (circular dependencies or disconnected)
        remaining = [
            item.get("id") for item in items if item.get("id") not in sorted_ids
        ]
        sorted_ids.extend(remaining)

        # Convert IDs back to items
        return [item_map[item_id] for item_id in sorted_ids if item_id in item_map]

    def _identify_quick_wins(
        self,
        items: List[Dict],
        readiness_scores: Optional[Dict],
        roi_scores: Optional[Dict],
    ) -> List[Dict]:
        """
        Identify quick wins (high ROI, low complexity)

        Args:
            items: List of items
            readiness_scores: Optional readiness scores
            roi_scores: Optional ROI scores

        Returns:
            List of quick win items
        """
        quick_wins = []

        for item in items:
            item_id = item.get("id")
            if not item_id:
                continue

            # Get scores
            readiness = readiness_scores.get(item_id) if readiness_scores else None
            roi = roi_scores.get(item_id) if roi_scores else None

            # Criteria for quick win
            is_ready = not readiness or readiness.status == "READY"
            is_simple = not readiness or readiness.complexity < 0.4
            is_high_roi = not roi or roi.recommendation == "HIGH"

            if is_ready and is_simple and is_high_roi:
                quick_wins.append(
                    {
                        "id": item_id,
                        "title": item.get("title"),
                        "roi_score": roi.roi_score if roi else 0,
                        "complexity": readiness.complexity if readiness else 0,
                        "implementation_time": (
                            readiness.setup_time if readiness else 30
                        ),
                    }
                )

        # Sort by ROI score descending
        quick_wins.sort(key=lambda x: x.get("roi_score", 0), reverse=True)

        return quick_wins[:10]  # Top 10 quick wins

    def _identify_foundational(
        self, items: List[Dict], dep_graph: Dict[str, List[str]]
    ) -> List[Dict]:
        """
        Identify foundational items (required by many others)

        Args:
            items: List of items
            dep_graph: Dependency graph

        Returns:
            List of foundational items
        """
        # Count how many items depend on each item
        dependency_count = defaultdict(int)
        for dependencies in dep_graph.values():
            for dep in dependencies:
                dependency_count[dep] += 1

        # Items with 3+ dependents are foundational
        foundational = []
        item_map = {item.get("id"): item for item in items}

        for item_id, count in dependency_count.items():
            if count >= 3 and item_id in item_map:
                foundational.append(
                    {
                        "id": item_id,
                        "title": item_map[item_id].get("title"),
                        "dependent_count": count,
                    }
                )

        # Sort by dependency count descending
        foundational.sort(key=lambda x: x["dependent_count"], reverse=True)

        return foundational

    def _cluster_into_phases(
        self,
        sorted_items: List[Dict],
        readiness_scores: Optional[Dict],
        dep_graph: Dict[str, List[str]],
    ) -> List[LearningPhase]:
        """
        Cluster items into learning phases

        Args:
            sorted_items: Topologically sorted items
            readiness_scores: Optional readiness scores
            dep_graph: Dependency graph

        Returns:
            List of learning phases
        """
        phases = []
        assigned = set()

        phase_num = 1
        remaining = sorted_items.copy()

        while remaining:
            phase_items = []

            for item in remaining[:]:
                item_id = item.get("id")

                # Check if dependencies are satisfied
                deps = dep_graph.get(item_id, [])
                if all(dep in assigned for dep in deps):
                    phase_items.append(item)
                    assigned.add(item_id)
                    remaining.remove(item)

            # If no items added, break circular dependency by adding one item
            if not phase_items and remaining:
                phase_items.append(remaining[0])
                assigned.add(remaining[0].get("id"))
                remaining.pop(0)

            if not phase_items:
                break

            # Create phase
            phase_hours = self._estimate_phase_hours(phase_items, readiness_scores)
            phase = self._create_phase(
                phase_num, phase_items, readiness_scores, phase_hours
            )
            phases.append(phase)
            phase_num += 1

            # Limit to 6 phases for manageability
            if phase_num > 6:
                # Add remaining items to last phase
                if remaining:
                    phases[-1].items.extend(remaining)
                    phases[-1].estimated_hours += self._estimate_phase_hours(
                        remaining, readiness_scores
                    )
                break

        return phases

    def _estimate_phase_hours(
        self, items: List[Dict], readiness_scores: Optional[Dict]
    ) -> int:
        """Estimate total hours for phase items"""
        total_minutes = 0
        for item in items:
            item_id = item.get("id")
            if readiness_scores and item_id in readiness_scores:
                total_minutes += readiness_scores[item_id].setup_time
            else:
                total_minutes += 30  # Default 30 minutes

        return max(1, int(total_minutes / 60))

    def _create_phase(
        self,
        phase_num: int,
        items: List[Dict],
        readiness_scores: Optional[Dict],
        hours: int,
    ) -> LearningPhase:
        """
        Create a learning phase

        Args:
            phase_num: Phase number
            items: Items in this phase
            readiness_scores: Optional readiness scores
            hours: Estimated hours

        Returns:
            LearningPhase object
        """
        # Determine phase characteristics
        if phase_num == 1:
            title = "Foundation"
            goal = "Establish core environment and tooling"
            prerequisites = []
            success_criteria = "Can run basic AI workflows"
        elif phase_num == 2:
            title = "Integration"
            goal = "Connect tools into workflows"
            prerequisites = ["Phase 1"]
            success_criteria = "Can automate common tasks"
        elif phase_num == 3:
            title = "Advanced Workflows"
            goal = "Implement complex automation"
            prerequisites = ["Phase 1", "Phase 2"]
            success_criteria = "Can build custom solutions"
        else:
            title = f"Specialization {phase_num - 2}"
            goal = "Implement specialized techniques"
            prerequisites = [f"Phase {i}" for i in range(1, phase_num)]
            success_criteria = "Master advanced patterns"

        # Format items for phase
        formatted_items = []
        for item in items:
            item_id = item.get("id")
            readiness = (
                readiness_scores.get(item_id) if readiness_scores and item_id else None
            )

            formatted_items.append(
                {
                    "id": item_id,
                    "title": item.get("title"),
                    "status": readiness.status if readiness else "NEEDS_SETUP",
                    "setup_time": (
                        readiness.setup_time if readiness else 30
                    ),  # minutes
                }
            )

        return LearningPhase(
            phase_number=phase_num,
            title=title,
            goal=goal,
            items=formatted_items,
            estimated_hours=hours,
            prerequisites=prerequisites,
            success_criteria=success_criteria,
        )

    def _identify_advanced(
        self,
        items: List[Dict],
        phases: List[LearningPhase],
        readiness_scores: Optional[Dict],
    ) -> List[Dict]:
        """
        Identify advanced items (in later phases or high complexity)

        Args:
            items: All items
            phases: Learning phases
            readiness_scores: Optional readiness scores

        Returns:
            List of advanced items
        """
        advanced = []

        # Items in phase 3+ are advanced
        if len(phases) >= 3:
            for phase in phases[2:]:
                for phase_item in phase.items:
                    item_id = phase_item["id"]
                    # Find full item
                    full_item = next((i for i in items if i.get("id") == item_id), None)
                    if full_item:
                        advanced.append(
                            {
                                "id": item_id,
                                "title": full_item.get("title"),
                                "phase": phase.phase_number,
                            }
                        )

        # Also add items with high complexity
        if readiness_scores:
            for item in items:
                item_id = item.get("id")
                readiness = readiness_scores.get(item_id)
                if readiness and readiness.complexity > 0.7:
                    # Check if not already in advanced
                    if not any(a["id"] == item_id for a in advanced):
                        advanced.append(
                            {
                                "id": item_id,
                                "title": item.get("title"),
                                "reason": "high_complexity",
                            }
                        )

        return advanced

    def _generate_mermaid_diagram(
        self, phases: List[LearningPhase], dep_graph: Dict[str, List[str]]
    ) -> str:
        """
        Generate Mermaid flowchart of learning path

        Args:
            phases: Learning phases
            dep_graph: Dependency graph

        Returns:
            Mermaid diagram string
        """
        lines = ["graph TD"]

        # Add phase nodes
        for phase in phases:
            phase_id = f"P{phase.phase_number}"
            phase_label = f"{phase.title}<br/>({phase.estimated_hours}h)"
            lines.append(f'    {phase_id}["{phase_label}"]')

        # Link phases
        for i in range(len(phases) - 1):
            lines.append(f"    P{i+1} --> P{i+2}")

        # Style phases by difficulty
        for i, phase in enumerate(phases):
            if i == 0:
                lines.append(f"    style P{i+1} fill:#90EE90")  # Green for foundation
            elif i < len(phases) - 1:
                lines.append(
                    f"    style P{i+1} fill:#87CEEB"
                )  # Light blue for intermediate
            else:
                lines.append(f"    style P{i+1} fill:#FFD700")  # Gold for advanced

        return "\n".join(lines)
