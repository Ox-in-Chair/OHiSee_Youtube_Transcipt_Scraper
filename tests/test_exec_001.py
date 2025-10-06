"""
Unit Tests for EXEC-001 Execution Engine

Tests all components:
- PlaybookGenerator
- PromptExtractor
- CLIParser
- ChecklistCreator
- ExecutionEngine
"""

import pytest
import json
from src.modules.exec_001 import (
    ExecutionEngine,
    PlaybookGenerator,
    PromptExtractor,
    CLIParser,
    ChecklistCreator
)


# Test Fixtures

@pytest.fixture
def sample_insight():
    """Sample CORE-001 notable item."""
    return {
        "id": "item_1",
        "title": "Setup Claude Code Agent",
        "tag": "Command",
        "description": "Install and configure Claude Code with custom agent. Requires Node.js installed. Run npm install -g claude-code to install globally.",
        "implementation_steps": [
            "Install Node.js from nodejs.org",
            "Run: npm install -g claude-code",
            "Create agent file in .claude/agents/",
            "Configure API key in settings"
        ],
        "code_snippet": "// Example agent config\n{\n  \"name\": \"custom-agent\",\n  \"model\": \"claude-3\"\n}",
        "source_timestamp": "12:34",
        "readiness": "READY",
        "implementation_time": "30min"
    }


@pytest.fixture
def sample_prompt_content():
    """Sample content with prompts."""
    return '''
    Use this prompt: "You are a helpful coding assistant. Your task is to help with {task}."

    Here's another prompt: ```
    Act as a technical expert.
    Analyze the {input} and provide {format} output.
    ```

    For few-shot learning, use this prompt:
    "Example 1: Input: code, Output: review
     Example 2: Input: docs, Output: summary"
    '''


@pytest.fixture
def sample_cli_content():
    """Sample content with CLI commands."""
    return '''
    First, install dependencies:
    ```bash
    npm install -g claude-code
    pip install openai
    ```

    Then run: `git clone https://github.com/user/repo.git`

    Finally execute: docker build -t myapp --no-cache .
    '''


@pytest.fixture
def sample_playbook_steps():
    """Sample steps for checklist."""
    return [
        {"action": "Install Node.js", "time": "10min", "command": "npm install"},
        {"action": "Configure settings", "time": "5min"},
        {"action": "Test installation", "time": "5min", "expected_output": "Version displayed"}
    ]


# PlaybookGenerator Tests

class TestPlaybookGenerator:
    """Test PlaybookGenerator component."""

    def test_init(self):
        """Test initialization."""
        gen = PlaybookGenerator()
        assert gen.playbook_counter == 0

    def test_generate_playbook(self, sample_insight):
        """Test basic playbook generation."""
        gen = PlaybookGenerator()
        playbook = gen.generate(sample_insight, style="detailed")

        assert playbook is not None
        assert "playbook_id" in playbook
        assert playbook["title"] == sample_insight["title"]
        assert len(playbook["steps"]) > 0
        assert "prerequisites" in playbook
        assert "verification" in playbook

    def test_extract_prerequisites(self, sample_insight):
        """Test prerequisite extraction."""
        gen = PlaybookGenerator()
        prereqs = gen.extract_prerequisites(sample_insight)

        assert len(prereqs) > 0
        # Should detect "Requires Node.js"
        assert any("node" in p["description"].lower() for p in prereqs)

    def test_generate_steps_detailed(self, sample_insight):
        """Test step generation in detailed mode."""
        gen = PlaybookGenerator()
        steps = gen.generate_steps(sample_insight, "detailed")

        assert len(steps) == len(sample_insight["implementation_steps"]) + 1  # +1 for code snippet
        assert all("step_number" in step for step in steps)
        assert all("action" in step for step in steps)

    def test_troubleshooting_guide(self, sample_insight):
        """Test troubleshooting guide creation."""
        gen = PlaybookGenerator()
        troubleshooting = gen.create_troubleshooting_guide(sample_insight)

        assert isinstance(troubleshooting, dict)
        # Should have default troubleshooting for Command tag
        assert len(troubleshooting) > 0

    def test_to_markdown(self, sample_insight):
        """Test markdown export."""
        gen = PlaybookGenerator()
        playbook = gen.generate(sample_insight)
        md = gen.to_markdown(playbook)

        assert isinstance(md, str)
        assert "# Playbook:" in md
        assert "## Prerequisites" in md
        assert "## Step-by-Step Implementation" in md
        assert "## Verification" in md

    def test_playbook_styles(self, sample_insight):
        """Test different playbook styles."""
        gen = PlaybookGenerator()

        quick = gen.generate(sample_insight, "quick")
        detailed = gen.generate(sample_insight, "detailed")
        comprehensive = gen.generate(sample_insight, "comprehensive")

        # All should be valid
        assert all(pb["title"] for pb in [quick, detailed, comprehensive])


# PromptExtractor Tests

class TestPromptExtractor:
    """Test PromptExtractor component."""

    def test_init(self):
        """Test initialization."""
        extractor = PromptExtractor()
        assert extractor.prompt_counter == 0

    def test_extract_prompts(self, sample_prompt_content):
        """Test prompt extraction."""
        extractor = PromptExtractor()
        prompts = extractor.extract_prompts(sample_prompt_content)

        assert len(prompts) > 0
        assert all("prompt_id" in p for p in prompts)
        assert all("template" in p for p in prompts)
        assert all("category" in p for p in prompts)

    def test_identify_variables(self):
        """Test variable identification."""
        extractor = PromptExtractor()
        prompt = "You are a {role}. Analyze {input} and provide [format] output."

        variables = extractor.identify_variables(prompt)

        assert len(variables) >= 2
        var_names = [v["name"] for v in variables]
        assert "role" in var_names
        assert "input" in var_names or "format" in var_names

    def test_categorize_prompt_system(self):
        """Test system prompt categorization."""
        extractor = PromptExtractor()
        prompt = "You are a helpful coding assistant."

        category = extractor.categorize_prompt(prompt)
        assert category == "system"

    def test_categorize_prompt_user(self):
        """Test user prompt categorization."""
        extractor = PromptExtractor()
        prompt = "Write a function to calculate fibonacci numbers."

        category = extractor.categorize_prompt(prompt)
        assert category == "user"

    def test_categorize_prompt_few_shot(self):
        """Test few-shot prompt categorization."""
        extractor = PromptExtractor()
        prompt = "Example 1: Input A, Output B\nExample 2: Input C, Output D"

        category = extractor.categorize_prompt(prompt)
        assert category == "few-shot"

    def test_to_markdown(self, sample_prompt_content):
        """Test markdown export."""
        extractor = PromptExtractor()
        prompts = extractor.extract_prompts(sample_prompt_content)

        if prompts:
            md = extractor.to_markdown(prompts[0])
            assert isinstance(md, str)
            assert "# Prompt:" in md
            assert "## Template" in md


# CLIParser Tests

class TestCLIParser:
    """Test CLIParser component."""

    def test_init(self):
        """Test initialization."""
        parser = CLIParser()
        assert parser.command_counter == 0
        assert len(parser.tool_platforms) > 0

    def test_parse_commands(self, sample_cli_content):
        """Test command parsing."""
        parser = CLIParser()
        commands = parser.parse_commands(sample_cli_content)

        assert len(commands) > 0
        assert all("command_id" in cmd for cmd in commands)
        assert all("command" in cmd for cmd in commands)
        assert all("platform" in cmd for cmd in commands)

    def test_parse_flags(self):
        """Test flag parsing."""
        parser = CLIParser()
        command = "npm install --save-dev --verbose eslint"

        flags = parser.parse_flags(command)

        assert "--save-dev" in flags
        assert "--verbose" in flags

    def test_extract_prerequisites(self):
        """Test prerequisite extraction."""
        parser = CLIParser()

        npm_cmd = "npm install package"
        npm_prereqs = parser.extract_prerequisites(npm_cmd)
        assert any("node" in p.lower() for p in npm_prereqs)

        pip_cmd = "pip install package"
        pip_prereqs = parser.extract_prerequisites(pip_cmd)
        assert any("python" in p.lower() for p in pip_prereqs)

    def test_detect_platform(self):
        """Test platform detection."""
        parser = CLIParser()

        # Cross-platform tools
        npm_cmd = "npm install"
        npm_parsed = parser._parse_single_command(npm_cmd)
        assert npm_parsed["platform"] == "cross-platform"

        # Windows-specific
        ps_cmd = "powershell -Command Test"
        ps_parsed = parser._parse_single_command(ps_cmd)
        assert ps_parsed["platform"] == "windows"

    def test_to_markdown(self, sample_cli_content):
        """Test markdown export."""
        parser = CLIParser()
        commands = parser.parse_commands(sample_cli_content)

        if commands:
            md = parser.to_markdown(commands[0])
            assert isinstance(md, str)
            assert "# Command:" in md
            assert "## Command" in md


# ChecklistCreator Tests

class TestChecklistCreator:
    """Test ChecklistCreator component."""

    def test_init(self):
        """Test initialization."""
        creator = ChecklistCreator()
        assert creator is not None

    def test_create_checklist_markdown(self, sample_playbook_steps):
        """Test markdown checklist creation."""
        creator = ChecklistCreator()
        checklist = creator.create_checklist(sample_playbook_steps, format="markdown")

        assert checklist is not None
        assert checklist["format"] == "markdown"
        assert checklist["total_items"] == len(sample_playbook_steps)
        assert "[ ]" in checklist["formatted_output"]

    def test_create_checklist_json(self, sample_playbook_steps):
        """Test JSON checklist creation."""
        creator = ChecklistCreator()
        checklist = creator.create_checklist(sample_playbook_steps, format="json")

        assert checklist["format"] == "json"
        # Should be valid JSON
        json_data = json.loads(checklist["formatted_output"])
        assert "items" in json_data

    def test_create_checklist_html(self, sample_playbook_steps):
        """Test HTML checklist creation."""
        creator = ChecklistCreator()
        checklist = creator.create_checklist(sample_playbook_steps, format="html")

        assert checklist["format"] == "html"
        assert "<html>" in checklist["formatted_output"]
        assert 'type="checkbox"' in checklist["formatted_output"]

    def test_estimate_completion_time(self, sample_playbook_steps):
        """Test time estimation."""
        creator = ChecklistCreator()
        time_estimate = creator.estimate_completion_time(sample_playbook_steps)

        assert isinstance(time_estimate, str)
        assert "minute" in time_estimate or "hour" in time_estimate

    def test_update_progress(self, sample_playbook_steps):
        """Test progress tracking."""
        creator = ChecklistCreator()
        checklist = creator.create_checklist(sample_playbook_steps, format="markdown")

        # Mark first item as complete
        updated = creator.update_progress(checklist, [0])

        assert updated["completed_items"] == 1
        assert "[x]" in updated["formatted_output"]

    def test_invalid_format(self, sample_playbook_steps):
        """Test invalid format handling."""
        creator = ChecklistCreator()

        with pytest.raises(ValueError):
            creator.create_checklist(sample_playbook_steps, format="invalid")


# ExecutionEngine Tests

class TestExecutionEngine:
    """Test ExecutionEngine integration."""

    def test_init(self):
        """Test initialization."""
        engine = ExecutionEngine()
        assert engine.playbook_gen is not None
        assert engine.prompt_extractor is not None
        assert engine.cli_parser is not None
        assert engine.checklist_creator is not None

    def test_generate_all(self, sample_insight):
        """Test complete artifact generation."""
        engine = ExecutionEngine()

        insights = [sample_insight]
        context = {
            "user_skill_level": "intermediate",
            "output_formats": ["markdown"]
        }

        output = engine.generate_all(insights, context)

        # Validate output contract
        assert "playbooks" in output
        assert "prompts" in output
        assert "cli_commands" in output
        assert "checklists" in output
        assert "metadata" in output

        # Check metadata
        assert output["metadata"]["total_insights_processed"] == 1
        assert "processing_time_seconds" in output["metadata"]

    def test_generate_playbook(self, sample_insight):
        """Test single playbook generation."""
        engine = ExecutionEngine()
        playbook = engine.generate_playbook(sample_insight, style="detailed")

        assert playbook is not None
        assert "playbook_id" in playbook

    def test_extract_prompts(self, sample_prompt_content):
        """Test prompt extraction."""
        engine = ExecutionEngine()
        prompts = engine.extract_prompts(sample_prompt_content)

        assert len(prompts) > 0

    def test_parse_commands(self, sample_cli_content):
        """Test command parsing."""
        engine = ExecutionEngine()
        commands = engine.parse_commands(sample_cli_content)

        assert len(commands) > 0

    def test_create_checklist(self, sample_playbook_steps):
        """Test checklist creation."""
        engine = ExecutionEngine()
        checklist = engine.create_checklist(sample_playbook_steps)

        assert checklist is not None
        assert "items" in checklist

    def test_export_playbook(self, sample_insight):
        """Test playbook export."""
        engine = ExecutionEngine()
        playbook = engine.generate_playbook(sample_insight)
        md = engine.export_playbook(playbook, format="markdown")

        assert isinstance(md, str)
        assert len(md) > 0

    def test_get_summary_stats(self, sample_insight):
        """Test summary statistics."""
        engine = ExecutionEngine()
        output = engine.generate_all([sample_insight])

        stats = engine.get_summary_stats(output)

        assert "playbooks" in stats
        assert "prompts" in stats
        assert "commands" in stats
        assert "checklists" in stats

    def test_validate_output_contract(self, sample_insight):
        """Test output contract validation."""
        engine = ExecutionEngine()
        output = engine.generate_all([sample_insight])

        validation = engine.validate_output_contract(output)

        assert "valid" in validation
        assert "errors" in validation
        assert "warnings" in validation
        assert validation["valid"] is True

    def test_skill_level_mapping(self):
        """Test skill level to playbook style mapping."""
        engine = ExecutionEngine()

        assert engine._determine_playbook_style("beginner") == "comprehensive"
        assert engine._determine_playbook_style("intermediate") == "detailed"
        assert engine._determine_playbook_style("advanced") == "quick"


# Integration Tests

class TestIntegration:
    """Integration tests across components."""

    def test_full_workflow(self, sample_insight):
        """Test complete workflow from insight to all artifacts."""
        engine = ExecutionEngine()

        # Generate everything
        output = engine.generate_all([sample_insight], context={
            "user_skill_level": "intermediate",
            "output_formats": ["markdown", "json"]
        })

        # Verify complete output
        assert len(output["playbooks"]) > 0
        assert len(output["checklists"]) > 0

        # Verify exports work
        for pb_id, playbook in output["playbooks"].items():
            md = engine.export_playbook(playbook)
            assert len(md) > 0

    def test_empty_insights(self):
        """Test handling of empty insights."""
        engine = ExecutionEngine()
        output = engine.generate_all([])

        # Should still produce valid structure
        validation = engine.validate_output_contract(output)
        assert validation["valid"] is True
        assert len(validation["warnings"]) > 0  # Should warn about empty sections


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
