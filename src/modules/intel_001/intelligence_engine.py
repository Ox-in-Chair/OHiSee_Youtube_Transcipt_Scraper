"""
Intelligence Engine - Unified orchestration API for INTEL-001

Coordinates readiness analysis, ROI scoring, and learning path generation
to provide comprehensive implementation intelligence.
"""

from typing import Dict, List
from .roi_scorer import ROIScorer, ROIMetrics
from .readiness_analyzer import ReadinessAnalyzer, ReadinessScore
from .learning_path_generator import LearningPathGenerator


class IntelligenceEngine:
    """
    Main orchestration engine for INTEL-001 module

    Provides unified API for:
    - Readiness scoring
    - ROI calculation
    - Learning path generation
    - Quick wins identification
    - Comprehensive intelligence reports
    """

    def __init__(self, callback=None):
        """
        Initialize intelligence engine

        Args:
            callback: Optional logging function
        """
        self.callback = callback
        self.readiness_analyzer = ReadinessAnalyzer(callback=callback)
        self.roi_scorer = ROIScorer(callback=callback)
        self.learning_path_generator = LearningPathGenerator(callback=callback)

    def analyze_items(
        self, items: List[Dict], include_learning_path: bool = True
    ) -> Dict:
        """
        Complete intelligence analysis for all items

        Args:
            items: List of notable items from CORE-001
            include_learning_path: Whether to generate learning path

        Returns:
            Complete intelligence report with all analyses
        """
        self._log("Starting intelligence analysis...")

        # Step 1: Readiness analysis
        self._log(f"Analyzing readiness for {len(items)} items...")
        readiness_scores = self.readiness_analyzer.batch_analyze(items)

        # Step 2: ROI calculation
        self._log(f"Calculating ROI for {len(items)} items...")
        roi_scores = self.roi_scorer.batch_calculate(items, readiness_scores)

        # Step 3: Learning path generation (optional)
        learning_path = None
        if include_learning_path:
            self._log("Generating learning path...")
            learning_path = self.learning_path_generator.generate_path(
                items, readiness_scores, roi_scores
            )

        # Step 4: Generate prioritization
        self._log("Generating prioritization recommendations...")
        prioritization = self._generate_prioritization(
            items, readiness_scores, roi_scores
        )

        # Step 5: Generate summary statistics
        stats = self._generate_statistics(items, readiness_scores, roi_scores)

        self._log("Intelligence analysis complete!")

        return {
            "readiness_scores": readiness_scores,
            "roi_scores": roi_scores,
            "learning_path": learning_path,
            "prioritization": prioritization,
            "statistics": stats,
        }

    def generate_report(self, items: List[Dict], analysis_result: Dict) -> str:
        """
        Generate markdown intelligence report

        Args:
            items: List of notable items
            analysis_result: Result from analyze_items()

        Returns:
            Markdown report string
        """
        sections = []

        # Header
        sections.append("# Intelligence Report")
        sections.append("")
        sections.append("## Executive Summary")
        sections.append("")

        # Statistics
        stats = analysis_result["statistics"]
        sections.append(f"**Total Items**: {stats['total_items']}")
        sections.append(
            f"**Ready to Implement**: {stats['ready_count']} ({stats['ready_percentage']:.1f}%)"
        )
        sections.append(f"**High Priority**: {stats['high_priority_count']}")
        sections.append(f"**Total Implementation Time**: {stats['total_hours']}h")
        sections.append(
            f"**Potential Annual Savings**: {stats['total_annual_savings']}h"
        )
        sections.append("")

        # Quick Wins
        if analysis_result.get("learning_path"):
            quick_wins = analysis_result["learning_path"].quick_wins
            if quick_wins:
                sections.append("## Quick Wins")
                sections.append("")
                sections.append(
                    "High ROI, low complexity items for immediate implementation:"
                )
                sections.append("")
                for i, win in enumerate(quick_wins[:5], 1):
                    sections.append(f"{i}. **{win['title']}**")
                    sections.append(f"   - ROI Score: {win['roi_score']:.1f}x")
                    sections.append(f"   - Complexity: {win['complexity']:.2f}")
                    sections.append(f"   - Time: {win['implementation_time']}min")
                    sections.append("")

        # Prioritization
        prioritization = analysis_result["prioritization"]
        sections.append("## Prioritization Dashboard")
        sections.append("")

        for priority in ["HIGH", "MEDIUM", "LOW"]:
            priority_items = prioritization.get(priority, [])
            if priority_items:
                sections.append(
                    f"### {priority} Priority ({len(priority_items)} items)"
                )
                sections.append("")
                for item_data in priority_items[:10]:  # Top 10 per category
                    sections.append(f"- **{item_data['title']}**")
                    sections.append(f"  - Status: {item_data['status']}")
                    sections.append(f"  - ROI: {item_data['roi_score']:.1f}x")
                    sections.append(f"  - Complexity: {item_data['complexity']:.2f}")
                    sections.append("")

        # Learning Path
        if analysis_result.get("learning_path"):
            path = analysis_result["learning_path"]
            sections.append("## Learning Path")
            sections.append("")
            sections.append(f"**Total Duration**: {path.total_hours} hours")
            sections.append(f"**Number of Phases**: {len(path.phases)}")
            sections.append("")

            for phase in path.phases:
                sections.append(f"### Phase {phase.phase_number}: {phase.title}")
                sections.append(f"**Goal**: {phase.goal}")
                sections.append(f"**Duration**: {phase.estimated_hours}h")
                prereqs = ', '.join(phase.prerequisites) if phase.prerequisites else 'None'
                sections.append(f"**Prerequisites**: {prereqs}")
                sections.append(f"**Success Criteria**: {phase.success_criteria}")
                sections.append("")
                sections.append("**Items**:")
                for item in phase.items[:5]:  # First 5 items
                    sections.append(
                        f"- {item['title']} ({item['status']}, {item['setup_time']}min)"
                    )
                if len(phase.items) > 5:
                    sections.append(f"- ... and {len(phase.items) - 5} more items")
                sections.append("")

            # Dependency diagram
            sections.append("## Dependency Roadmap")
            sections.append("")
            sections.append("```mermaid")
            sections.append(path.mermaid_diagram)
            sections.append("```")
            sections.append("")

        return "\n".join(sections)

    def _generate_prioritization(
        self,
        items: List[Dict],
        readiness_scores: Dict[str, ReadinessScore],
        roi_scores: Dict[str, ROIMetrics],
    ) -> Dict[str, List[Dict]]:
        """
        Generate prioritization by priority level

        Args:
            items: List of items
            readiness_scores: Readiness scores
            roi_scores: ROI scores

        Returns:
            Dict of priority level -> list of items
        """
        prioritization = {"HIGH": [], "MEDIUM": [], "LOW": []}

        item_map = {item.get("id"): item for item in items}

        for item_id, roi in roi_scores.items():
            item = item_map.get(item_id)
            if not item:
                continue

            readiness = readiness_scores.get(item_id)

            prioritization[roi.recommendation].append(
                {
                    "id": item_id,
                    "title": item.get("title"),
                    "status": readiness.status if readiness else "UNKNOWN",
                    "complexity": readiness.complexity if readiness else 0.5,
                    "roi_score": roi.roi_score,
                    "breakeven_weeks": roi.breakeven_period,
                    "implementation_hours": roi.implementation_time,
                }
            )

        # Sort each priority group by ROI score
        for priority in prioritization:
            prioritization[priority].sort(key=lambda x: x["roi_score"], reverse=True)

        return prioritization

    def _generate_statistics(
        self,
        items: List[Dict],
        readiness_scores: Dict[str, ReadinessScore],
        roi_scores: Dict[str, ROIMetrics],
    ) -> Dict:
        """
        Generate summary statistics

        Args:
            items: List of items
            readiness_scores: Readiness scores
            roi_scores: ROI scores

        Returns:
            Statistics dict
        """
        total_items = len(items)

        # Readiness stats
        ready_count = sum(1 for r in readiness_scores.values() if r.status == "READY")

        # ROI stats
        high_priority_count = sum(
            1 for r in roi_scores.values() if r.recommendation == "HIGH"
        )

        # Time stats
        total_hours = sum(r.implementation_time for r in roi_scores.values())
        total_annual_savings = sum(r.annual_time_savings for r in roi_scores.values())

        # Average complexity
        avg_complexity = (
            sum(r.complexity for r in readiness_scores.values()) / len(readiness_scores)
            if readiness_scores
            else 0
        )

        return {
            "total_items": total_items,
            "ready_count": ready_count,
            "ready_percentage": (ready_count / total_items * 100) if total_items else 0,
            "high_priority_count": high_priority_count,
            "total_hours": total_hours,
            "total_annual_savings": total_annual_savings,
            "average_complexity": avg_complexity,
        }

    def _log(self, message: str):
        """Log message via callback"""
        if self.callback:
            self.callback(message)
