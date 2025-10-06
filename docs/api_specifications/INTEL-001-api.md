# INTEL-001 API Specification

## ROI Scoring & Intelligence Layer

**Version**: 1.0.0
**Status**: Production Ready
**Module**: INTEL-001 (Intelligence Layer)
**Dependencies**: CORE-001

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [API Reference](#api-reference)
4. [Usage Examples](#usage-examples)
5. [Integration Guide](#integration-guide)

---

## Overview

INTEL-001 provides strategic intelligence for YouTube Transcript Scraper v2.0, transforming CORE-001 summaries into actionable prioritization and learning paths through:

- **ROI Scoring**: Calculate return on investment for implementations
- **Readiness Analysis**: Assess complexity and prerequisites
- **Learning Path Generation**: Create dependency-ordered implementation phases
- **Quick Wins Identification**: Find high-value, low-complexity items

### Key Features

✅ **Automated Prioritization**: HIGH/MEDIUM/LOW recommendations
✅ **Dependency Detection**: Automatic prerequisite ordering
✅ **Time Estimation**: Implementation time and breakeven period
✅ **Quick Wins**: Identify easy wins for immediate implementation
✅ **Mermaid Diagrams**: Visual learning path roadmaps

---

## Installation

### Prerequisites

- Python 3.8+
- CORE-001 module installed

### Import Module

```python
from modules.intel_001 import IntelligenceEngine
```

---

## API Reference

### Class: `IntelligenceEngine`

Main orchestration engine for complete intelligence analysis.

#### Constructor

```python
IntelligenceEngine(callback=None)
```

**Parameters:**

- `callback` (callable, optional): Logging callback function

**Example:**

```python
engine = IntelligenceEngine()

# With logging
def log_message(msg):
    print(f"[INTEL] {msg}")

engine = IntelligenceEngine(callback=log_message)
```

---

### Method: `analyze_items()`

Complete intelligence analysis for all items.

```python
analyze_items(
    items: List[Dict],
    include_learning_path: bool = True
) -> Dict
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `items` | List[Dict] | Yes | Notable items from CORE-001 |
| `include_learning_path` | bool | No | Generate learning path (default True) |

**Returns:**

```python
{
    "readiness_scores": Dict[str, ReadinessScore],
    "roi_scores": Dict[str, ROIMetrics],
    "learning_path": LearningPath,  # or None
    "prioritization": Dict[str, List[Dict]],  # HIGH/MEDIUM/LOW
    "statistics": Dict  # Summary stats
}
```

**Example:**

```python
items = [...]  # From CORE-001
result = engine.analyze_items(items)

print(f"High priority items: {len(result['prioritization']['HIGH'])}")
print(f"Ready to implement: {result['statistics']['ready_count']}")
```

---

### Method: `generate_report()`

Generate markdown intelligence report.

```python
generate_report(
    items: List[Dict],
    analysis_result: Dict
) -> str
```

**Parameters:**

- `items`: List of notable items
- `analysis_result`: Result from `analyze_items()`

**Returns:**

- Markdown report string with executive summary, quick wins, prioritization dashboard, and learning path

**Example:**

```python
result = engine.analyze_items(items)
report = engine.generate_report(items, result)

# Save to file
with open("intelligence_report.md", "w") as f:
    f.write(report)
```

---

## Data Structures

### ReadinessScore

```python
@dataclass
class ReadinessScore:
    status: str  # "READY" | "NEEDS_SETUP" | "EXPERIMENTAL"
    complexity: float  # 0-1 (0=trivial, 1=expert)
    setup_time: int  # minutes
    prerequisites: List[str]
    confidence: float  # 0-1
    blockers: List[str]
    reasoning: str
```

### ROIMetrics

```python
@dataclass
class ROIMetrics:
    implementation_time: int  # hours
    time_saved_per_use: int  # minutes
    use_frequency: str  # "daily" | "weekly" | "monthly" | "rarely"
    annual_time_savings: int  # hours
    cost: float  # USD
    roi_score: float  # (savings - cost) / implementation_time
    breakeven_period: int  # weeks
    recommendation: str  # "HIGH" | "MEDIUM" | "LOW"
    reasoning: str
```

### LearningPath

```python
@dataclass
class LearningPath:
    phases: List[LearningPhase]
    total_hours: int
    quick_wins: List[Dict]  # High ROI, low complexity
    foundational: List[Dict]  # Required for later items
    advanced: List[Dict]  # Phase 3+ or high complexity
    dependency_graph: Dict[str, List[str]]
    mermaid_diagram: str  # Mermaid flowchart
```

---

## Usage Examples

### Example 1: Basic Intelligence Analysis

```python
from modules.intel_001 import IntelligenceEngine

# Initialize engine
engine = IntelligenceEngine()

# Items from CORE-001
items = [
    {
        "id": "item_1",
        "title": "Setup Claude API",
        "description": "Configure API key. Takes 5 minutes.",
        "implementation_steps": ["Get key", "Add to .env"],
    },
    {
        "id": "item_2",
        "title": "Workflow Automation",
        "description": "Automates daily tasks. Saves 2 hours every time.",
        "implementation_steps": ["Install", "Configure", "Test"],
    }
]

# Analyze
result = engine.analyze_items(items)

# Access results
print(f"Total items: {result['statistics']['total_items']}")
print(f"Ready: {result['statistics']['ready_count']}")
print(f"High priority: {result['statistics']['high_priority_count']}")
```

### Example 2: Prioritization Dashboard

```python
result = engine.analyze_items(items)
prioritization = result["prioritization"]

# High priority items
for item in prioritization["HIGH"]:
    print(f"- {item['title']}")
    print(f"  ROI: {item['roi_score']:.1f}x")
    print(f"  Breakeven: {item['breakeven_weeks']} weeks")
```

### Example 3: Learning Path Generation

```python
result = engine.analyze_items(items)
path = result["learning_path"]

# Print phases
for phase in path.phases:
    print(f"Phase {phase.phase_number}: {phase.title}")
    print(f"  Goal: {phase.goal}")
    print(f"  Duration: {phase.estimated_hours}h")
    print(f"  Items: {len(phase.items)}")

# Get quick wins
print("\nQuick Wins:")
for win in path.quick_wins[:5]:
    print(f"- {win['title']} (ROI: {win['roi_score']:.1f}x)")
```

### Example 4: Complete Report Generation

```python
# Full analysis
result = engine.analyze_items(items)

# Generate markdown report
report = engine.generate_report(items, result)

# Save to file
with open("02_SYNTHESIS/05_INTELLIGENCE_REPORT.md", "w") as f:
    f.write(report)

# Also save prioritization dashboard
dashboard = []
dashboard.append("# Prioritization Dashboard\n")
for priority in ["HIGH", "MEDIUM", "LOW"]:
    items_list = result["prioritization"][priority]
    dashboard.append(f"## {priority} Priority ({len(items_list)} items)\n")
    for item in items_list[:10]:
        dashboard.append(f"- **{item['title']}**\n")
        dashboard.append(f"  - ROI: {item['roi_score']:.1f}x\n")
        dashboard.append(f"  - Status: {item['status']}\n")

with open("02_SYNTHESIS/06_PRIORITIZATION_DASHBOARD.md", "w") as f:
    f.write("\n".join(dashboard))
```

---

## Integration Guide

### For UI-001 Integration

```python
# INTEL-001 provides intelligence for UI display
from modules.intel_001 import IntelligenceEngine
from modules.core_001 import CoreEngine

core = CoreEngine(api_key=api_key)
intel = IntelligenceEngine()

# Generate summaries
summaries = [core.enhance_summary(t, m) for t, m in zip(transcripts, metadata)]

# Get intelligence
items = []
for summary in summaries:
    items.extend(summary["notable_items"])

result = intel.analyze_items(items)

# Pass to UI
ui_data = {
    "quick_wins": result["learning_path"].quick_wins,
    "prioritization": result["prioritization"],
    "stats": result["statistics"],
    "phases": result["learning_path"].phases
}
```

### For EXEC-001 Integration

```python
# INTEL-001 prioritizes items for playbook generation
from modules.intel_001 import IntelligenceEngine
from modules.exec_001 import ExecutionEngine

intel = IntelligenceEngine()
exec_engine = ExecutionEngine()

# Get intelligence
result = intel.analyze_items(items)

# Generate playbooks for high-priority items only
high_priority_items = result["prioritization"]["HIGH"]
for item_data in high_priority_items[:5]:  # Top 5
    item_id = item_data["id"]
    item = next(i for i in items if i["id"] == item_id)
    playbook = exec_engine.generate_playbook([item])
```

---

## Performance Characteristics

### Processing Time

| Items | Analysis Time | Memory |
|-------|---------------|--------|
| 10 | <1s | ~20MB |
| 50 | 1-2s | ~50MB |
| 100 | 2-4s | ~100MB |

### Scaling

- **Single Video**: <1 second intelligence analysis
- **10 Videos**: 2-3 seconds total
- **Learning Path**: +0.5 seconds for 50+ items

---

## Error Handling

```python
try:
    result = engine.analyze_items(items)
except Exception as e:
    print(f"Intelligence analysis failed: {e}")
    # Fallback: basic prioritization without ROI
```

---

## API Versioning

**Current Version**: 1.0.0

### Version History

- **1.0.0** (2025-10-06): Initial production release
  - ROI scoring
  - Readiness analysis
  - Learning path generation
  - Quick wins identification
  - Complete API contracts

---

**Last Updated**: 2025-10-06
**API Version**: 1.0.0
**Status**: ✅ Production Ready
