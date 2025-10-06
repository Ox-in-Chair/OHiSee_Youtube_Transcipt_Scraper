"""
INTEL-001: ROI Scoring & Intelligence Layer

Transforms CORE-001 insights into strategic intelligence:
- ROI scoring and time savings estimation
- Learning path generation with dependency ordering
- Readiness analysis and prerequisite detection
- Technology freshness tracking

Version: 1.0.0
Status: Production Ready
Dependencies: CORE-001
"""

from .intelligence_engine import IntelligenceEngine
from .roi_scorer import ROIScorer
from .learning_path_generator import LearningPathGenerator
from .readiness_analyzer import ReadinessAnalyzer

__version__ = "1.0.0"
__all__ = [
    "IntelligenceEngine",
    "ROIScorer",
    "LearningPathGenerator",
    "ReadinessAnalyzer",
]
