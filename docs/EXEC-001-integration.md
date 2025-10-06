# EXEC-001 Integration Guide

## Playbook & Execution Engine

**Version**: 1.0.0
**Status**: Production Ready
**Last Updated**: 2025-10-06

---

## Overview

This guide shows how to integrate EXEC-001 (Playbook & Execution Engine) with CORE-001 and downstream modules.

**EXEC-001 Purpose**: Transform passive insights into actionable artifacts

**Input**: CORE-001 notable items (structured insights)
**Output**: Playbooks, prompts, commands, checklists (execution-ready)

---

## Quick Start

### 1. Basic Integration with CORE-001

```python
from src.modules.core_001 import CoreEngine
from src.modules.exec_001 import ExecutionEngine

# Step 1: Generate CORE-001 summary
core = CoreEngine(api_key="sk-...")
summary = core.enhance_summary(transcript, metadata, mode="developer")

# Step 2: Generate execution artifacts
exec_engine = ExecutionEngine()
artifacts = exec_engine.generate_all(
    insights=summary["notable_items"]
)

# Step 3: Access results
print(f"Playbooks: {len(artifacts['playbooks'])}")
print(f"Prompts: {sum(len(v) for v in artifacts['prompts'].values())}")
print(f"Commands: {sum(len(v) for v in artifacts['cli_commands'].values())}")
print(f"Checklists: {len(artifacts['checklists'])}")
```

### 2. Export Artifacts to Files

```python
import os

# Create output directories
os.makedirs("output/playbooks", exist_ok=True)
os.makedirs("output/checklists", exist_ok=True)

# Export playbooks
for pb_id, playbook in artifacts["playbooks"].items():
    md = exec_engine.export_playbook(playbook)
    with open(f"output/playbooks/{pb_id}.md", "w", encoding="utf-8") as f:
        f.write(md)

# Export checklists
for idx, checklist in enumerate(artifacts["checklists"]):
    format_type = checklist["format"]
    ext = "md" if format_type == "markdown" else format_type
    filename = f"output/checklists/checklist_{idx}.{ext}"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(checklist["formatted_output"])

print("✅ All artifacts exported successfully")
```

---

## Integration Patterns

### Pattern 1: Complete Pipeline (CORE → EXEC → Output)

**Use Case**: Process video transcript to executable guides

```python
def process_video_to_playbooks(transcript, metadata, api_key):
    """Complete pipeline from transcript to playbooks."""

    # Step 1: CORE-001 - Extract insights
    core = CoreEngine(api_key=api_key)
    summary = core.enhance_summary(transcript, metadata, mode="developer")

    # Step 2: EXEC-001 - Generate artifacts
    exec_engine = ExecutionEngine()
    artifacts = exec_engine.generate_all(
        insights=summary["notable_items"],
        context={
            "user_skill_level": "intermediate",
            "output_formats": ["markdown", "html"]
        }
    )

    # Step 3: Export results
    output_dir = f"output/{metadata['title']}"
    os.makedirs(output_dir, exist_ok=True)

    # Export playbooks
    for pb_id, playbook in artifacts["playbooks"].items():
        md = exec_engine.export_playbook(playbook)
        with open(f"{output_dir}/{pb_id}.md", "w") as f:
            f.write(md)

    # Export interactive checklist
    for checklist in artifacts["checklists"]:
        if checklist["format"] == "html":
            with open(f"{output_dir}/checklist.html", "w") as f:
                f.write(checklist["formatted_output"])

    return artifacts


# Usage
artifacts = process_video_to_playbooks(
    transcript=my_transcript,
    metadata={"title": "Claude Setup Tutorial", "channel": "AI Dev"},
    api_key="sk-..."
)
```

### Pattern 2: Selective Artifact Generation

**Use Case**: Generate only specific artifact types

```python
def extract_prompts_only(transcript, metadata, api_key):
    """Extract only prompt templates from video."""

    # Generate insights
    core = CoreEngine(api_key=api_key)
    summary = core.enhance_summary(transcript, metadata, mode="developer")

    # Extract prompts only
    exec_engine = ExecutionEngine()
    prompts = exec_engine.prompt_extractor.extract_from_notable_items(
        summary["notable_items"]
    )

    # Build prompt library
    library = []
    for category, prompt_list in prompts.items():
        for prompt in prompt_list:
            library.append({
                "category": category,
                "template": prompt["template"],
                "variables": [v["name"] for v in prompt["variables"]],
                "use_case": prompt["use_case"]
            })

    return library


def extract_cli_commands_only(transcript, metadata, api_key):
    """Extract only CLI commands from video."""

    core = CoreEngine(api_key=api_key)
    summary = core.enhance_summary(transcript, metadata, mode="developer")

    exec_engine = ExecutionEngine()
    commands = exec_engine.cli_parser.extract_from_notable_items(
        summary["notable_items"]
    )

    # Build command reference
    reference = []
    for platform, cmd_list in commands.items():
        for cmd in cmd_list:
            reference.append({
                "platform": platform,
                "command": cmd["command"],
                "description": cmd["description"],
                "flags": cmd["flags"]
            })

    return reference
```

### Pattern 3: Batch Processing Multiple Videos

**Use Case**: Process entire video collection

```python
def batch_process_videos(video_list, api_key, output_base="output"):
    """Process multiple videos and aggregate artifacts."""

    core = CoreEngine(api_key=api_key)
    exec_engine = ExecutionEngine()

    all_playbooks = {}
    all_prompts = []
    all_commands = []

    for video in video_list:
        print(f"Processing: {video['title']}")

        # Generate insights
        summary = core.enhance_summary(
            video["transcript"],
            video["metadata"],
            mode="developer"
        )

        # Generate artifacts
        artifacts = exec_engine.generate_all(
            insights=summary["notable_items"]
        )

        # Aggregate results
        all_playbooks.update(artifacts["playbooks"])

        for category, prompts in artifacts["prompts"].items():
            all_prompts.extend(prompts)

        for platform, commands in artifacts["cli_commands"].items():
            all_commands.extend(commands)

    # Export aggregated results
    print(f"\n✅ Processed {len(video_list)} videos")
    print(f"   Total playbooks: {len(all_playbooks)}")
    print(f"   Total prompts: {len(all_prompts)}")
    print(f"   Total commands: {len(all_commands)}")

    return {
        "playbooks": all_playbooks,
        "prompts": all_prompts,
        "commands": all_commands
    }
```

---

## Advanced Usage

### Custom Skill-Level Mapping

```python
def generate_adaptive_playbooks(insights, user_experience):
    """Generate playbooks adapted to user experience level."""

    exec_engine = ExecutionEngine()

    # Map experience to playbook style
    style_map = {
        "novice": "comprehensive",      # 20+ steps, max detail
        "beginner": "comprehensive",     # 20+ steps, max detail
        "intermediate": "detailed",      # 10-20 steps, balanced
        "advanced": "detailed",          # 10-20 steps, balanced
        "expert": "quick"                # 5-10 steps, minimal
    }

    style = style_map.get(user_experience, "detailed")

    artifacts = exec_engine.generate_all(
        insights=insights,
        context={
            "user_skill_level": user_experience,
            "output_formats": ["markdown"]
        }
    )

    return artifacts
```

### Platform-Specific Command Export

```python
def export_platform_commands(artifacts, target_platform):
    """Export commands for specific platform only."""

    commands = artifacts["cli_commands"].get(target_platform, [])

    if not commands:
        print(f"⚠️  No commands found for platform: {target_platform}")
        return

    # Generate platform-specific markdown
    md = f"# CLI Commands for {target_platform.title()}\n\n"

    for cmd in commands:
        md += f"## {cmd['purpose']}\n\n"
        md += f"```bash\n{cmd['command']}\n```\n\n"

        if cmd['flags']:
            md += "**Flags**:\n"
            for flag, desc in cmd['flags'].items():
                md += f"- `{flag}`: {desc}\n"
            md += "\n"

    # Save to file
    with open(f"commands_{target_platform}.md", "w") as f:
        f.write(md)

    print(f"✅ Exported {len(commands)} commands for {target_platform}")
```

### Interactive Checklist with Progress Tracking

```python
def create_interactive_checklist(playbook):
    """Create HTML checklist with live progress tracking."""

    exec_engine = ExecutionEngine()
    checklist = exec_engine.checklist_creator.create_from_playbook(
        playbook, format="html"
    )

    # Save interactive HTML
    html_file = f"checklist_{playbook['playbook_id']}.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(checklist["formatted_output"])

    print(f"✅ Interactive checklist created: {html_file}")
    print(f"   Open in browser to track progress")

    return html_file
```

---

## Integration with Downstream Modules

### KNOWLEDGE-001 Integration (Future)

```python
# EXEC-001 provides structured artifacts for knowledge base storage

def store_in_knowledge_base(artifacts, knowledge_engine):
    """Store execution artifacts in knowledge base."""

    # Store playbooks with searchable metadata
    for pb_id, playbook in artifacts["playbooks"].items():
        knowledge_engine.store_document(
            doc_id=pb_id,
            doc_type="playbook",
            content=playbook,
            metadata={
                "title": playbook["title"],
                "complexity": playbook["complexity"],
                "tags": playbook["tags"]
            }
        )

    # Index prompts by category and variables
    for category, prompts in artifacts["prompts"].items():
        for prompt in prompts:
            knowledge_engine.index_prompt(
                template=prompt["template"],
                category=category,
                variables=[v["name"] for v in prompt["variables"]]
            )

    # Index commands by platform and tool
    for platform, commands in artifacts["cli_commands"].items():
        for cmd in commands:
            knowledge_engine.index_command(
                command=cmd["command"],
                platform=platform,
                tool=cmd["command"].split()[0],
                description=cmd["description"]
            )
```

### UI-001 Integration (Future)

```python
# EXEC-001 provides render-ready data for UI components

def render_playbook_ui(playbook, ui_renderer):
    """Render playbook in web UI."""

    # Render title and metadata
    ui_renderer.render_header(
        title=playbook["title"],
        metadata={
            "Time": playbook["estimated_time"],
            "Complexity": playbook["complexity"],
            "Readiness": playbook["readiness"]
        }
    )

    # Render prerequisites as checklist
    ui_renderer.render_checklist(
        title="Prerequisites",
        items=[p["description"] for p in playbook["prerequisites"]]
    )

    # Render steps with code blocks
    for step in playbook["steps"]:
        ui_renderer.render_step(
            number=step["step_number"],
            action=step["action"],
            code=step.get("command") or step.get("code_block"),
            expected=step.get("expected_output")
        )

    # Render troubleshooting as collapsible section
    ui_renderer.render_troubleshooting(
        issues=playbook["troubleshooting"]
    )
```

---

## Error Handling

### Validation Best Practices

```python
def safe_artifact_generation(insights):
    """Generate artifacts with comprehensive error handling."""

    exec_engine = ExecutionEngine()

    try:
        # Generate artifacts
        artifacts = exec_engine.generate_all(insights)

        # Validate output contract
        validation = exec_engine.validate_output_contract(artifacts)

        if not validation["valid"]:
            print("❌ Validation errors:")
            for error in validation["errors"]:
                print(f"   - {error}")
            return None

        if validation["warnings"]:
            print("⚠️  Warnings:")
            for warning in validation["warnings"]:
                print(f"   - {warning}")

        return artifacts

    except Exception as e:
        print(f"❌ Error generating artifacts: {e}")
        return None
```

### Handling Empty Results

```python
def handle_empty_insights(artifacts):
    """Handle cases where insights produce no actionable artifacts."""

    stats = exec_engine.get_summary_stats(artifacts)

    if stats["playbooks"]["total"] == 0:
        print("ℹ️  No actionable playbooks generated")
        print("   Insights may not contain implementation steps")

    if stats["prompts"]["total"] == 0:
        print("ℹ️  No prompts extracted")
        print("   Content may not contain prompt templates")

    if stats["commands"]["total"] == 0:
        print("ℹ️  No CLI commands found")
        print("   Content may not contain executable commands")
```

---

## Performance Optimization

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_playbook_generation(insights, max_workers=4):
    """Generate playbooks in parallel for better performance."""

    exec_engine = ExecutionEngine()

    def generate_single(insight):
        return exec_engine.generate_playbook(insight, style="detailed")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        playbooks = list(executor.map(generate_single, insights))

    return {f"playbook_{i}": pb for i, pb in enumerate(playbooks)}
```

### Caching Strategy

```python
import hashlib
import json

def cached_artifact_generation(insights, cache_dir="cache"):
    """Cache artifacts to avoid regeneration."""

    os.makedirs(cache_dir, exist_ok=True)

    # Create cache key from insights
    insights_str = json.dumps(insights, sort_keys=True)
    cache_key = hashlib.md5(insights_str.encode()).hexdigest()
    cache_file = f"{cache_dir}/{cache_key}.json"

    # Check cache
    if os.path.exists(cache_file):
        print("✅ Loading from cache")
        with open(cache_file, "r") as f:
            return json.load(f)

    # Generate and cache
    print("🔄 Generating artifacts...")
    exec_engine = ExecutionEngine()
    artifacts = exec_engine.generate_all(insights)

    with open(cache_file, "w") as f:
        json.dump(artifacts, f, indent=2)

    return artifacts
```

---

## Testing Integration

```python
def test_integration_with_core():
    """Test CORE-001 → EXEC-001 integration."""

    from src.modules.core_001 import CoreEngine
    from src.modules.exec_001 import ExecutionEngine

    # Sample data
    transcript = "Install Node.js. Run: npm install -g package"
    metadata = {"title": "Test", "channel": "Test"}

    # CORE-001
    core = CoreEngine(api_key="sk-test")
    summary = core.enhance_summary(transcript, metadata, mode="quick")

    # EXEC-001
    exec_engine = ExecutionEngine()
    artifacts = exec_engine.generate_all(summary["notable_items"])

    # Assertions
    assert artifacts is not None
    assert "playbooks" in artifacts
    assert "prompts" in artifacts
    assert "cli_commands" in artifacts
    assert "checklists" in artifacts

    print("✅ Integration test passed")
```

---

## Troubleshooting

### Common Integration Issues

**Issue**: No playbooks generated

- **Cause**: Insights lack implementation_steps
- **Solution**: Ensure CORE-001 mode is "developer" or "research"

**Issue**: Prompts not extracted

- **Cause**: Content doesn't match prompt patterns
- **Solution**: Check if prompts use standard delimiters (quotes, backticks)

**Issue**: Commands not parsed

- **Cause**: Commands not in code blocks or backticks
- **Solution**: Use proper markdown formatting for code

**Issue**: Checklist HTML not rendering

- **Cause**: JavaScript disabled or file not opened in browser
- **Solution**: Open .html file in modern browser with JS enabled

---

## Best Practices

1. **Always validate output** before using artifacts
2. **Export to files** for persistence and sharing
3. **Use appropriate skill level** for target audience
4. **Cache results** for repeated processing
5. **Handle empty results** gracefully
6. **Test integration** with sample data first

---

## Version Compatibility

| EXEC-001 | CORE-001 | Status |
|----------|----------|--------|
| 1.0.0 | 1.0.0 | ✅ Compatible |

---

**Last Updated**: 2025-10-06
**Status**: Production Ready
**Next Steps**: Integrate with KNOWLEDGE-001 and UI-001 when available
