# VISUAL-001 Integration Guide

**Module**: VISUAL-001 (Diagram Generation Engine)
**Version**: 1.0.0
**Status**: Production Ready

---

## Quick Start Integration

### Basic Setup

```python
from src.modules.visual_001 import VisualEngine

# Initialize engine
visual_engine = VisualEngine()

# Generate diagrams from CORE-001 synthesis
config = {
    "diagram_types": ["timeline", "architecture", "comparison", "flowchart"],
    "complexity": "detailed",
    "validate": True
}

result = visual_engine.generate_all(synthesis, config)
```

---

## Integration with Other Modules

### CORE-001 → VISUAL-001 Data Flow

```python
from src.modules.core_001 import CoreEngine
from src.modules.visual_001 import VisualEngine

# Step 1: Generate synthesis from CORE-001
core_engine = CoreEngine(api_key="sk-...")
summaries = [
    core_engine.enhance_summary(transcript1, metadata1),
    core_engine.enhance_summary(transcript2, metadata2)
]
synthesis = core_engine.synthesize_videos(summaries)

# Step 2: Generate diagrams from synthesis
visual_engine = VisualEngine()
config = {
    "diagram_types": ["timeline", "architecture"],
    "complexity": "detailed",
    "validate": True
}

diagrams = visual_engine.generate_all(synthesis, config)

# Step 3: Access results
timeline_code = diagrams["diagrams"]["timeline"]["mermaid_code"]
timeline_markdown = diagrams["markdown_embeds"]["timeline"]
```

---

## UI-001 Integration

### Embedding Diagrams in GUI

```python
import tkinter as tk
from src.modules.visual_001 import VisualEngine

class DiagramPanel:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.visual_engine = VisualEngine()

    def display_diagrams(self, synthesis):
        config = {
            "diagram_types": ["timeline", "comparison"],
            "complexity": "simple",
            "validate": True
        }

        result = self.visual_engine.generate_all(synthesis, config)

        # Display Mermaid code in text widget
        for diagram_type, data in result["diagrams"].items():
            self.add_diagram_section(
                diagram_type,
                data["title"],
                data["mermaid_code"]
            )

    def add_diagram_section(self, diagram_type, title, mermaid_code):
        # Add to UI (text widget, html viewer, etc.)
        section_label = tk.Label(self.frame, text=title, font=("Arial", 14, "bold"))
        section_label.pack()

        code_text = tk.Text(self.frame, height=15, width=80)
        code_text.insert("1.0", mermaid_code)
        code_text.pack()
```

### Rendering Diagrams in Browser

For rendering Mermaid diagrams in a web view:

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({startOnLoad:true});</script>
</head>
<body>
    <div class="mermaid">
        <!-- Insert mermaid_code here -->
        graph TD
            A[Start] --> B[End]
    </div>
</body>
</html>
```

---

## EXEC-001 Integration

### Adding Diagrams to Playbooks

```python
from src.modules.visual_001 import VisualEngine

def create_playbook_with_diagrams(synthesis, playbook_title):
    visual_engine = VisualEngine()

    # Generate workflow diagram
    config = {
        "diagram_types": ["flowchart"],
        "complexity": "detailed",
        "validate": True
    }

    result = visual_engine.generate_all(synthesis, config)

    # Build playbook
    playbook = f"# {playbook_title}\n\n"
    playbook += "## Workflow Diagram\n\n"
    playbook += result["markdown_embeds"]["flowchart"]
    playbook += "\n\n## Implementation Steps\n\n"
    playbook += "1. Follow the flowchart above\n"
    playbook += "2. ...\n"

    return playbook
```

---

## INTEL-001 Integration

### Adding Diagrams to ROI Analysis

```python
def enhance_roi_with_diagrams(synthesis, roi_data):
    visual_engine = VisualEngine()

    # Generate comparison diagram for tools
    config = {
        "diagram_types": ["comparison"],
        "complexity": "detailed",
        "validate": True
    }

    result = visual_engine.generate_all(synthesis, config)

    # Add to ROI report
    roi_data["visual_comparison"] = result["markdown_embeds"]["comparison"]
    roi_data["winner_tool"] = result["diagrams"]["comparison"]["winner"]

    return roi_data
```

---

## File Export Integration

### Saving Diagrams to Markdown Files

```python
import os
from src.modules.visual_001 import VisualEngine

def export_diagrams_to_files(synthesis, output_dir):
    """Export all diagrams as separate markdown files."""

    os.makedirs(output_dir, exist_ok=True)

    visual_engine = VisualEngine()
    config = {
        "diagram_types": ["timeline", "architecture", "comparison", "flowchart"],
        "complexity": "detailed",
        "validate": True
    }

    result = visual_engine.generate_all(synthesis, config)

    # Export each diagram
    for diagram_type, markdown in result["markdown_embeds"].items():
        file_path = os.path.join(output_dir, f"{diagram_type}_diagram.md")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        print(f"Exported: {file_path}")

    # Export validation report
    if not result["validation"]["all_valid"]:
        error_file = os.path.join(output_dir, "validation_errors.txt")
        with open(error_file, "w") as f:
            f.write("\n".join(result["validation"]["errors"]))

    return output_dir
```

### Saving Raw Mermaid Code

```python
def export_mermaid_files(synthesis, output_dir):
    """Export diagrams as .mmd files for external rendering."""

    os.makedirs(output_dir, exist_ok=True)

    visual_engine = VisualEngine()
    config = {
        "diagram_types": ["timeline", "architecture", "comparison", "flowchart"],
        "complexity": "comprehensive",
        "validate": True
    }

    result = visual_engine.generate_all(synthesis, config)

    for diagram_type, data in result["diagrams"].items():
        file_path = os.path.join(output_dir, f"{diagram_type}.mmd")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(data["mermaid_code"])

        print(f"Exported: {file_path}")
```

---

## Obsidian Integration

### Embedding in Obsidian Vault

```python
def export_to_obsidian(synthesis, vault_path):
    """Export diagrams to Obsidian vault with backlinks."""

    visual_engine = VisualEngine()
    config = {
        "diagram_types": ["timeline", "architecture"],
        "complexity": "detailed",
        "validate": True
    }

    result = visual_engine.generate_all(synthesis, config)

    # Create diagrams note
    diagrams_note = os.path.join(vault_path, "Research_Diagrams.md")

    content = "# Research Diagrams\n\n"
    content += "## Timeline\n\n"
    content += result["markdown_embeds"]["timeline"]
    content += "\n\n## Architecture\n\n"
    content += result["markdown_embeds"]["architecture"]
    content += "\n\n---\n\n"
    content += "Back to: [[Research_Index]]"

    with open(diagrams_note, "w", encoding="utf-8") as f:
        f.write(content)

    return diagrams_note
```

---

## Roam Research Integration

### Creating Roam Blocks

```python
def export_to_roam(synthesis):
    """Generate Roam Research-compatible blocks."""

    visual_engine = VisualEngine()
    config = {
        "diagram_types": ["flowchart"],
        "complexity": "simple",
        "validate": True
    }

    result = visual_engine.generate_all(synthesis, config)

    # Roam block format
    roam_blocks = []
    roam_blocks.append("- Research Workflow #diagram")

    # Indent Mermaid code
    mermaid_lines = result["diagrams"]["flowchart"]["mermaid_code"].split("\n")
    for line in mermaid_lines:
        roam_blocks.append(f"    - {line}")

    return "\n".join(roam_blocks)
```

---

## Error Handling Best Practices

### Graceful Degradation

```python
def generate_diagrams_safe(synthesis, config):
    """Generate diagrams with error handling."""

    visual_engine = VisualEngine()

    try:
        result = visual_engine.generate_all(synthesis, config)

        # Check validation
        if not result["validation"]["all_valid"]:
            print(f"Warning: Validation errors found:")
            for error in result["validation"]["errors"]:
                print(f"  - {error}")

        return result

    except KeyError as e:
        print(f"Error: Missing required data in synthesis: {e}")
        return None

    except Exception as e:
        print(f"Error generating diagrams: {e}")
        return None
```

### Retry Logic

```python
def generate_with_retry(synthesis, config, max_retries=3):
    """Generate diagrams with retry logic."""

    visual_engine = VisualEngine()

    for attempt in range(max_retries):
        try:
            result = visual_engine.generate_all(synthesis, config)

            if result["validation"]["all_valid"]:
                return result
            else:
                print(f"Attempt {attempt + 1}: Validation errors, retrying...")

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")

        # Reduce complexity for retry
        if config["complexity"] == "comprehensive":
            config["complexity"] = "detailed"
        elif config["complexity"] == "detailed":
            config["complexity"] = "simple"

    print("Max retries reached. Returning None.")
    return None
```

---

## Performance Optimization

### Selective Generation

Generate only needed diagrams:

```python
# Instead of all diagrams
config = {
    "diagram_types": ["timeline", "architecture", "comparison", "flowchart"],
    ...
}

# Generate only timeline
config = {
    "diagram_types": ["timeline"],
    "complexity": "simple",
    "validate": True
}

result = visual_engine.generate_all(synthesis, config)
# ~1 second vs ~4 seconds
```

### Caching Results

```python
import json
import hashlib

def generate_with_cache(synthesis, config, cache_dir="cache"):
    """Generate diagrams with file-based caching."""

    # Create cache key
    cache_key = hashlib.md5(
        json.dumps(synthesis, sort_keys=True).encode()
    ).hexdigest()

    cache_file = os.path.join(cache_dir, f"{cache_key}.json")

    # Check cache
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            print("Loading from cache...")
            return json.load(f)

    # Generate fresh
    visual_engine = VisualEngine()
    result = visual_engine.generate_all(synthesis, config)

    # Save to cache
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_file, "w") as f:
        json.dump(result, f)

    return result
```

---

## Testing Integration

### Unit Testing

```python
import pytest
from src.modules.visual_001 import VisualEngine

def test_visual_integration():
    """Test VISUAL-001 integration."""

    visual_engine = VisualEngine()

    # Minimal synthesis for testing
    synthesis = {
        "chronological_timeline": [
            {"date": "2025-01-01", "event": "Test", "tool": "Tool", "version": "1.0"}
        ],
        "cross_video_patterns": [],
        "tool_mentions": {},
        "consensus_points": [],
        "contradictions": []
    }

    config = {
        "diagram_types": ["timeline"],
        "complexity": "simple",
        "validate": True
    }

    result = visual_engine.generate_all(synthesis, config)

    assert result is not None
    assert "diagrams" in result
    assert "timeline" in result["diagrams"]
    assert result["validation"]["all_valid"] is True
```

---

## Deployment Considerations

### Requirements File

Add to `requirements.txt` (no additional dependencies needed):

```
# VISUAL-001 has no external dependencies
# Pure Python implementation
```

### Environment Variables

No environment variables required for VISUAL-001.

---

**Last Updated**: 2025-10-06
**Integration Version**: 1.0.0
**Compatible Modules**: CORE-001, UI-001, EXEC-001, INTEL-001
