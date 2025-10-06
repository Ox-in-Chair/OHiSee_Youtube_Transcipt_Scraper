"""
Readiness Analyzer - Score implementation readiness and complexity

Analyzes prerequisites, complexity, and setup requirements to determine
how ready each item is for immediate implementation.
"""

import re
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ReadinessScore:
    """Readiness analysis results"""

    status: str  # "READY" | "NEEDS_SETUP" | "EXPERIMENTAL"
    complexity: float  # 0-1 (0=trivial, 1=expert)
    setup_time: int  # minutes to set up
    prerequisites: List[str]  # What's needed first
    confidence: float  # 0-1 (how sure we are)
    blockers: List[str]  # What prevents implementation
    reasoning: str  # Why this status


class ReadinessAnalyzer:
    """
    Analyze implementation readiness and complexity
    """

    # Status keywords
    READY_KEYWORDS = [
        "simple",
        "basic",
        "easy",
        "straightforward",
        "copy-paste",
        "ready to use",
    ]

    NEEDS_SETUP_KEYWORDS = [
        "requires",
        "needs",
        "first you",
        "install",
        "configure",
        "api key",
        "setup",
        "prerequisite",
    ]

    EXPERIMENTAL_KEYWORDS = [
        "experimental",
        "beta",
        "unstable",
        "alpha",
        "testing",
        "might not work",
        "still working on",
        "not stable",
    ]

    def __init__(self, callback=None):
        """
        Initialize readiness analyzer

        Args:
            callback: Optional logging function
        """
        self.callback = callback

    def analyze(self, item: Dict) -> ReadinessScore:
        """
        Analyze item readiness

        Args:
            item: Notable item from CORE-001

        Returns:
            ReadinessScore with complete analysis
        """
        # Extract text for analysis
        text = self._extract_text(item)

        # Detect status
        status = self._detect_status(item, text)

        # Calculate complexity
        complexity = self._calculate_complexity(item, text)

        # Extract prerequisites
        prerequisites = self._extract_prerequisites(item, text)

        # Identify blockers
        blockers = self._identify_blockers(item, text, prerequisites)

        # Estimate setup time
        setup_time = self._estimate_setup_time(status, complexity, prerequisites)

        # Calculate confidence
        confidence = self._calculate_confidence(item, text)

        # Generate reasoning
        reasoning = self._generate_reasoning(
            status, complexity, prerequisites, blockers
        )

        return ReadinessScore(
            status=status,
            complexity=complexity,
            setup_time=setup_time,
            prerequisites=prerequisites,
            confidence=confidence,
            blockers=blockers,
            reasoning=reasoning,
        )

    def _extract_text(self, item: Dict) -> str:
        """Extract all text from item for analysis"""
        parts = [
            item.get("title", ""),
            item.get("description", ""),
            item.get("tag", ""),
        ]

        # Add implementation steps if available
        if "implementation_steps" in item:
            parts.extend(item["implementation_steps"])

        return " ".join(parts).lower()

    def _detect_status(self, item: Dict, text: str) -> str:
        """
        Detect readiness status

        Args:
            item: Notable item dict
            text: Combined text for analysis

        Returns:
            Status: "READY" | "NEEDS_SETUP" | "EXPERIMENTAL"
        """
        # Check for explicit readiness marker
        if "readiness" in item:
            readiness = item["readiness"].upper()
            if "READY" in readiness:
                return "READY"
            elif "NEEDS_SETUP" in readiness or "SETUP" in readiness:
                return "NEEDS_SETUP"
            elif "EXPERIMENTAL" in readiness:
                return "EXPERIMENTAL"

        # Check for experimental keywords (highest priority)
        if any(kw in text for kw in self.EXPERIMENTAL_KEYWORDS):
            return "EXPERIMENTAL"

        # Check for setup requirements
        if any(kw in text for kw in self.NEEDS_SETUP_KEYWORDS):
            return "NEEDS_SETUP"

        # Check version number
        version_match = re.search(r"v?(\d+)\.(\d+)", text)
        if version_match:
            major = int(version_match.group(1))
            if major == 0:
                return "EXPERIMENTAL"

        # Check for code snippet
        if "code_snippet" in item and item["code_snippet"]:
            # Has copy-paste ready code
            if not any(kw in text for kw in self.NEEDS_SETUP_KEYWORDS):
                return "READY"

        # Default based on keywords
        if any(kw in text for kw in self.READY_KEYWORDS):
            return "READY"

        # Default to NEEDS_SETUP if unclear
        return "NEEDS_SETUP"

    def _calculate_complexity(self, item: Dict, text: str) -> float:
        """
        Calculate complexity score 0-1

        Args:
            item: Notable item dict
            text: Combined text

        Returns:
            Complexity score (0=beginner, 1=expert)
        """
        score = 0.0

        # Factor 1: Implementation steps count
        steps = item.get("implementation_steps", [])
        step_count = len(steps)
        if step_count == 0:
            score += 0.1  # No steps = somewhat complex
        elif step_count <= 3:
            score += 0.0  # Simple
        elif step_count <= 7:
            score += 0.2  # Moderate
        else:
            score += 0.4  # Complex

        # Factor 2: Code length
        code = item.get("code_snippet", "")
        if code:
            lines = code.count("\n") + 1
            if lines > 50:
                score += 0.3
            elif lines > 20:
                score += 0.2
            elif lines > 5:
                score += 0.1

        # Factor 3: Technical jargon
        advanced_terms = [
            "architecture",
            "microservice",
            "distributed",
            "async",
            "concurrent",
            "optimization",
            "performance",
            "scalability",
        ]
        jargon_count = sum(1 for term in advanced_terms if term in text)
        score += min(0.2, jargon_count * 0.05)

        # Factor 4: Multiple tools interaction
        tool_keywords = ["api", "database", "server", "client", "integration"]
        tool_count = sum(1 for kw in tool_keywords if kw in text)
        if tool_count >= 3:
            score += 0.2
        elif tool_count >= 2:
            score += 0.1

        # Factor 5: Error handling mentions
        if "error" in text or "exception" in text or "try-catch" in text:
            score += 0.1

        # Factor 6: Complexity markers
        if "advanced" in text or "expert" in text:
            score += 0.2
        elif "intermediate" in text:
            score += 0.1
        elif "beginner" in text or "simple" in text:
            score -= 0.1

        # Clamp to 0-1 range
        return max(0.0, min(1.0, score))

    def _extract_prerequisites(self, item: Dict, text: str) -> List[str]:
        """
        Extract prerequisites from item

        Args:
            item: Notable item dict
            text: Combined text

        Returns:
            List of prerequisite strings
        """
        prerequisites = []

        # Check explicit prerequisites
        if "prerequisites" in item:
            prerequisites.extend(item["prerequisites"])

        # Extract from text patterns
        prereq_patterns = [
            r"requires?\s+([^.]+?)(?:\.|$)",
            r"needs?\s+([^.]+?)(?:\.|$)",
            r"first\s+(?:you\s+)?(?:need|must)\s+([^.]+?)(?:\.|$)",
            r"prerequisite[s]?:\s*([^.]+?)(?:\.|$)",
            r"install\s+([^.]+?)(?:\.|$)",
        ]

        for pattern in prereq_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                prereq = match.group(1).strip()
                if len(prereq) < 100:  # Sanity check
                    prerequisites.append(prereq)

        # Extract tool names
        tool_pattern = r"(?:install|setup|configure)\s+([a-z0-9-]+)"
        tool_matches = re.finditer(tool_pattern, text)
        for match in tool_matches:
            tool = match.group(1).strip()
            prerequisites.append(f"Install {tool}")

        # Remove duplicates while preserving order
        seen = set()
        unique_prerequisites = []
        for prereq in prerequisites:
            if prereq.lower() not in seen:
                seen.add(prereq.lower())
                unique_prerequisites.append(prereq)

        return unique_prerequisites[:10]  # Limit to 10 most important

    def _identify_blockers(
        self, item: Dict, text: str, prerequisites: List[str]
    ) -> List[str]:
        """
        Identify blockers preventing implementation

        Args:
            item: Notable item dict
            text: Combined text
            prerequisites: Extracted prerequisites

        Returns:
            List of blocker strings
        """
        blockers = []

        # API key requirements
        if "api key" in text or "api_key" in text:
            if "needs" in text or "requires" in text:
                blockers.append("API key required")

        # Paid services
        if "paid" in text or "subscription" in text or "premium" in text:
            blockers.append("Paid service/subscription required")

        # External dependencies
        if len(prerequisites) > 5:
            blockers.append(f"{len(prerequisites)} prerequisites to set up")

        # Platform-specific
        if "windows only" in text or "mac only" in text or "linux only" in text:
            blockers.append("Platform-specific implementation")

        # Experimental/beta
        if "experimental" in text or "beta" in text:
            blockers.append("Experimental/beta software")

        # Complex setup
        if "complex setup" in text or "difficult to" in text:
            blockers.append("Complex configuration required")

        # Version compatibility
        version_warnings = re.findall(
            r"(?:only works with|requires)\s+version\s+([0-9.]+)", text
        )
        if version_warnings:
            blockers.append(f"Specific version required: {version_warnings[0]}")

        return blockers

    def _estimate_setup_time(
        self, status: str, complexity: float, prerequisites: List[str]
    ) -> int:
        """
        Estimate setup time in minutes

        Args:
            status: Readiness status
            complexity: Complexity score
            prerequisites: List of prerequisites

        Returns:
            Setup time in minutes
        """
        # Base time by status
        if status == "READY":
            base_time = 5
        elif status == "NEEDS_SETUP":
            base_time = 30
        else:  # EXPERIMENTAL
            base_time = 60

        # Add time for complexity
        complexity_time = int(complexity * 120)  # 0-120 minutes

        # Add time for prerequisites (10 min each)
        prereq_time = len(prerequisites) * 10

        total_time = base_time + complexity_time + prereq_time

        # Round to nearest 5 minutes
        return max(5, int(total_time / 5) * 5)

    def _calculate_confidence(self, item: Dict, text: str) -> float:
        """
        Calculate confidence in readiness assessment

        Args:
            item: Notable item dict
            text: Combined text

        Returns:
            Confidence score 0-1
        """
        confidence = 0.5  # Start at medium confidence

        # Increase confidence if we have code
        if item.get("code_snippet"):
            confidence += 0.2

        # Increase confidence if we have implementation steps
        if item.get("implementation_steps"):
            confidence += 0.2

        # Increase confidence if explicit readiness marked
        if "readiness" in item:
            confidence += 0.1

        # Decrease confidence if vague
        vague_keywords = ["maybe", "might", "could", "possibly", "probably"]
        if any(kw in text for kw in vague_keywords):
            confidence -= 0.1

        # Increase confidence if explicit instructions
        explicit_keywords = ["exactly", "specifically", "must", "required"]
        if any(kw in text for kw in explicit_keywords):
            confidence += 0.1

        return max(0.0, min(1.0, confidence))

    def _generate_reasoning(
        self,
        status: str,
        complexity: float,
        prerequisites: List[str],
        blockers: List[str],
    ) -> str:
        """
        Generate human-readable reasoning

        Args:
            status: Readiness status
            complexity: Complexity score
            prerequisites: List of prerequisites
            blockers: List of blockers

        Returns:
            Reasoning string
        """
        parts = []

        # Status explanation
        if status == "READY":
            parts.append("Ready for immediate implementation.")
        elif status == "NEEDS_SETUP":
            parts.append("Requires setup before implementation.")
        else:
            parts.append("Experimental - proceed with caution.")

        # Complexity
        if complexity < 0.3:
            parts.append("Low complexity (beginner-friendly).")
        elif complexity < 0.6:
            parts.append("Moderate complexity (some experience needed).")
        else:
            parts.append("High complexity (advanced implementation).")

        # Prerequisites
        if prerequisites:
            parts.append(f"{len(prerequisites)} prerequisite(s) required.")

        # Blockers
        if blockers:
            parts.append(f"Blockers: {', '.join(blockers)}.")

        return " ".join(parts)

    def batch_analyze(self, items: List[Dict]) -> Dict[str, ReadinessScore]:
        """
        Analyze multiple items

        Args:
            items: List of notable items

        Returns:
            Dict mapping item ID to ReadinessScore
        """
        results = {}
        for item in items:
            item_id = item.get("id", f"item_{len(results) + 1}")

            try:
                score = self.analyze(item)
                results[item_id] = score
                if self.callback:
                    self.callback(
                        f"Readiness analyzed for {item_id}: "
                        f"{score.status} (complexity: {score.complexity:.2f})"
                    )
            except Exception as e:
                if self.callback:
                    self.callback(f"Error analyzing {item_id}: {e}")
                continue

        return results
