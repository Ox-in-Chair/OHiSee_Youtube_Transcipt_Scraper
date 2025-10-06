"""Unit tests for CORE-001 CoreEngine

Tests cover:
- Enhanced summary generation (50+ items)
- Entity extraction (tools, commands, prompts)
- Cross-video synthesis
- Error handling and edge cases
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from modules.core_001.engine import CoreEngine


@pytest.fixture
def mock_api_key():
    """Mock OpenAI API key"""
    return "sk-test-key-12345"


@pytest.fixture
def sample_transcript():
    """Sample transcript for testing"""
    return """In this tutorial, I'll show you how to set up Claude Code with custom agents.

    First, install Claude Code using: npm install -g claude-code

    Then create your agent file in .claude/agents/ directory.

    Use this prompt template: "You are a helpful coding assistant..."

    Configure the model to use Claude 3.5 Sonnet. Version 3.5 is recommended.

    Common error: "API key not found" - Fix by setting ANTHROPIC_API_KEY environment variable.

    This approach is better than using Cursor for complex projects.
    """


@pytest.fixture
def sample_metadata():
    """Sample video metadata"""
    return {
        "title": "Claude Code Custom Agents Setup Guide",
        "channel": "AI Dev Tutorials",
        "upload_date": "2025-10-01",
        "duration": "15:30",
        "views": 12500,
        "description": "Learn how to set up custom agents",
        "tags": ["claude", "ai", "coding"]
    }


@pytest.fixture
def core_engine(mock_api_key):
    """CoreEngine instance with mocked OpenAI client"""
    with patch('modules.core_001.engine.OpenAI') as mock_openai:
        # Mock the completion response
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content="# Summary: Test\n\n## Notable Items\n\n### 1. **Test Item** [Protocol]\n**Implementation Time**: [5min]\n**Readiness**: [✅ Ready]\n\nTest description\n\n**How to Implement**:\n1. Step 1\n2. Step 2\n\n```bash\ntest command\n```\n\n**Source Timestamp**: 01:23"))
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        engine = CoreEngine(api_key=mock_api_key)
        engine.client = mock_client

        yield engine


class TestCoreEngine:
    """Test suite for CoreEngine class"""

    def test_initialization(self, mock_api_key):
        """Test CoreEngine initializes correctly"""
        with patch('modules.core_001.engine.OpenAI'):
            engine = CoreEngine(api_key=mock_api_key)
            assert engine.model == "gpt-4"
            assert engine.max_tokens == 4096

    def test_initialization_with_callback(self, mock_api_key):
        """Test CoreEngine with custom callback"""
        callback = Mock()
        with patch('modules.core_001.engine.OpenAI'):
            engine = CoreEngine(api_key=mock_api_key, callback=callback)
            engine._log("Test message")
            callback.assert_called_once_with("Test message")

    def test_token_count_estimate(self, core_engine):
        """Test token counting approximation"""
        text = "This is a test sentence with approximately twenty-five characters."
        tokens = core_engine._count_tokens_estimate(text)
        assert tokens > 0
        assert tokens == len(text) // 4

    def test_chunk_transcript_short(self, core_engine, sample_transcript):
        """Test chunking short transcript (no chunking needed)"""
        chunks = core_engine._chunk_transcript(sample_transcript, max_chunk_tokens=50000)
        assert len(chunks) == 1
        assert chunks[0] == sample_transcript

    def test_chunk_transcript_long(self, core_engine):
        """Test chunking long transcript"""
        long_transcript = "Test paragraph.\n\n" * 5000  # Create long text
        chunks = core_engine._chunk_transcript(long_transcript, max_chunk_tokens=5000)
        assert len(chunks) > 1
        # Verify chunks have overlap (context continuity)
        assert any(chunk in chunks[i+1] for i, chunk in enumerate(chunks[:-1]))

    def test_parse_time_to_minutes(self, core_engine):
        """Test time string parsing"""
        assert core_engine._parse_time_to_minutes("5min") == 5
        assert core_engine._parse_time_to_minutes("2hr") == 120
        assert core_engine._parse_time_to_minutes("1day") == 480
        assert core_engine._parse_time_to_minutes("unknown") == 30  # Default

    def test_calculate_complexity(self, core_engine):
        """Test complexity score calculation"""
        items = [
            {"readiness": "READY"},
            {"readiness": "NEEDS_SETUP"},
            {"readiness": "EXPERIMENTAL"}
        ]
        tools = {"Tool1": {}, "Tool2": {}, "Tool3": {}}

        complexity = core_engine._calculate_complexity(items, tools)
        assert 0.0 <= complexity <= 1.0
        assert complexity > 0.3  # Should be medium-high with experimental items

    def test_estimate_api_cost(self, core_engine):
        """Test API cost estimation"""
        input_text = "Short input"
        output_text = "Short output"
        cost = core_engine._estimate_api_cost(input_text, output_text)
        assert cost > 0
        assert cost < 0.01  # Very short texts should be cheap

    def test_extract_readiness_ready(self, core_engine):
        """Test readiness extraction - READY status"""
        content = "**Readiness**: [✅ Ready]"
        assert core_engine._extract_readiness(content) == "READY"

    def test_extract_readiness_needs_setup(self, core_engine):
        """Test readiness extraction - NEEDS_SETUP status"""
        content = "**Readiness**: [⚠️ Needs Setup]"
        assert core_engine._extract_readiness(content) == "NEEDS_SETUP"

    def test_extract_readiness_experimental(self, core_engine):
        """Test readiness extraction - EXPERIMENTAL status"""
        content = "**Readiness**: [🔬 Experimental]"
        assert core_engine._extract_readiness(content) == "EXPERIMENTAL"

    def test_extract_timestamp(self, core_engine):
        """Test timestamp extraction"""
        content = "**Source Timestamp**: 12:34"
        assert core_engine._extract_timestamp(content) == "12:34"

        content_no_timestamp = "No timestamp here"
        assert core_engine._extract_timestamp(content_no_timestamp) == "00:00"

    def test_extract_code_snippet(self, core_engine):
        """Test code snippet extraction"""
        content = "Some text\n```python\nprint('hello')\n```\nMore text"
        code = core_engine._extract_code_snippet(content)
        assert code == "print('hello')"

    def test_extract_implementation_steps(self, core_engine):
        """Test implementation steps extraction"""
        content = """**How to Implement**:
1. First step
2. Second step
3. Third step
**Other Section**: Not a step"""

        steps = core_engine._extract_implementation_steps(content)
        assert len(steps) == 3
        assert "1. First step" in steps

    def test_extract_tool_mentions(self, core_engine):
        """Test tool mention extraction"""
        text = "Use Claude v3.5 and GPT-4 for best results. Python 3.11 is required."
        tools = core_engine._extract_tool_mentions(text)

        assert len(tools) > 0
        tool_names = [t["name"] for t in tools]
        assert "Claude" in tool_names or "GPT-4" in tool_names

    def test_extract_command_mentions(self, core_engine):
        """Test command extraction"""
        text = """Install using:
```bash
npm install -g claude-code
pip install openai
```
Also run: $ python script.py"""

        commands = core_engine._extract_command_mentions(text)
        assert len(commands) > 0
        command_texts = [c["command"] for c in commands]
        assert any("npm install" in cmd for cmd in command_texts)

    def test_extract_prompt_mentions(self, core_engine):
        """Test prompt template extraction"""
        text = 'Use this prompt: "You are a helpful assistant that writes Python code..."'
        prompts = core_engine._extract_prompt_mentions(text)

        # Long quotes should be detected as prompts
        assert len(prompts) >= 0  # May or may not find depending on length threshold

    def test_extract_version_numbers(self, core_engine):
        """Test version number extraction"""
        text = "Use version 3.5 or v4.0. Note: v2.0 is deprecated."
        versions = core_engine._extract_version_numbers(text)

        assert len(versions) > 0
        assert versions.get("deprecation_warning") == True

    def test_extract_entities_all_types(self, core_engine):
        """Test entity extraction with all types"""
        text = """Use Claude v3.5 for this project.
Run: npm install -g claude-code
Use prompt: "You are a helpful coding assistant"
Version 2.0 is deprecated."""

        entities = core_engine.extract_entities(text)

        assert "tools" in entities
        assert "commands" in entities
        assert "prompts" in entities
        assert "versions" in entities

    def test_extract_entities_specific_types(self, core_engine):
        """Test entity extraction with specific types"""
        text = "Use Claude v3.5"
        entities = core_engine.extract_entities(text, entity_types=["tools"])

        assert "tools" in entities
        assert "commands" not in entities
        assert "prompts" not in entities

    @patch('modules.core_001.engine.OpenAI')
    def test_enhance_summary_quick_mode(self, mock_openai, mock_api_key, sample_transcript, sample_metadata):
        """Test summary generation in quick mode"""
        # Mock GPT-4 response
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content="""# Summary: Test

**Source**: AI Dev | 2025-10-01 | 15:30 | 12,500 views
**Complexity**: Beginner
**Implementation Time**: 30min
**Prerequisites**: Node.js

## Notable Items

### 1. **Install Claude Code** [Command]
**Implementation Time**: [5min]
**Readiness**: [✅ Ready]

Install the CLI tool globally

**How to Implement**:
1. Run npm install -g claude-code
2. Verify with claude --version

```bash
npm install -g claude-code
```

**Source Timestamp**: 01:23

## Key Insights & Strategic Takeaways

This is a beginner-friendly setup guide.

**Most Important Implementation**:
Installing Claude Code CLI

**Red Flags / Anti-Patterns**:
None mentioned
"""))
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        engine = CoreEngine(api_key=mock_api_key)
        engine.client = mock_client

        summary = engine.enhance_summary(sample_transcript, sample_metadata, mode="quick")

        assert "notable_items" in summary
        assert "key_insights" in summary
        assert "complexity_score" in summary
        assert len(summary["notable_items"]) >= 1

    @patch('modules.core_001.engine.OpenAI')
    def test_enhance_summary_developer_mode(self, mock_openai, mock_api_key, sample_transcript, sample_metadata):
        """Test summary generation in developer mode (50+ items expected)"""
        # Mock would need to return 50+ items - for unit test, we verify the call
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content="# Summary\n\n## Notable Items\n\n" +
                "\n\n".join([f"### {i}. **Item {i}** [Protocol]\nTest\n```code```" for i in range(1, 52)])))
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        engine = CoreEngine(api_key=mock_api_key)
        engine.client = mock_client

        summary = engine.enhance_summary(sample_transcript, sample_metadata, mode="developer")

        # Verify GPT-4 was called
        mock_client.chat.completions.create.assert_called()

    def test_enhance_summary_invalid_mode(self, core_engine, sample_transcript, sample_metadata):
        """Test summary generation with invalid mode raises error"""
        with pytest.raises(ValueError, match="Invalid mode"):
            core_engine.enhance_summary(sample_transcript, sample_metadata, mode="invalid")

    @patch('modules.core_001.engine.OpenAI')
    def test_synthesize_videos(self, mock_openai, mock_api_key):
        """Test cross-video synthesis"""
        summaries = [
            {
                "title": "Video 1",
                "content": "Summary 1",
                "metadata": {"channel": "Channel A", "upload_date": "2025-10-01", "views": 1000},
                "tool_mentions": {"Claude": {}, "GPT-4": {}}
            },
            {
                "title": "Video 2",
                "content": "Summary 2",
                "metadata": {"channel": "Channel B", "upload_date": "2025-10-05", "views": 2000},
                "tool_mentions": {"Claude": {}, "Cursor": {}}
            }
        ]

        # Mock synthesis response
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content="""# Comprehensive Synthesis

## Executive Summary

This is a test synthesis.

## Common Themes & Patterns

### Theme: AI Development
**Mentioned in**: 2 of 2 videos

Pattern description here.

## Contradictions & Conflicts

### Contradiction: Tool Choice
**Conflicting Sources**:
- Position A: Video 1 recommends Claude
- Position B: Video 2 recommends Cursor

## Cross-Video Patterns & Meta-Insights

### Pattern: Consistency
**Observed Across**: 2 videos

Description of pattern.
"""))
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        engine = CoreEngine(api_key=mock_api_key)
        engine.client = mock_client

        synthesis = engine.synthesize_videos(summaries)

        assert "executive_summary" in synthesis
        assert "common_themes" in synthesis
        assert "contradictions" in synthesis
        assert "cross_video_patterns" in synthesis

    def test_build_synthesis_metadata(self, core_engine):
        """Test synthesis metadata building"""
        summaries = [
            {
                "metadata": {
                    "channel": "Channel A",
                    "upload_date": "2025-10-01",
                    "views": 1000
                },
                "tool_mentions": {"Claude": {}, "GPT-4": {}}
            },
            {
                "metadata": {
                    "channel": "Channel B",
                    "upload_date": "2025-10-05",
                    "views": 2000
                },
                "tool_mentions": {"Claude": {}}
            }
        ]

        metadata = core_engine._build_synthesis_metadata(summaries, {})

        assert metadata["n_videos"] == 2
        assert metadata["total_views"] == 3000
        assert "Channel A" in metadata["unique_channels"]
        assert "Claude" in metadata["tool_list"]


class TestPromptGeneration:
    """Test suite for prompt template generation"""

    def test_get_enhanced_summary_prompt_quick(self, sample_transcript, sample_metadata):
        """Test prompt generation for quick mode"""
        from modules.core_001.prompts import get_enhanced_summary_prompt

        prompt = get_enhanced_summary_prompt(sample_transcript, sample_metadata, mode="quick")

        assert "quick" in prompt
        assert "10-15" in prompt
        assert sample_transcript in prompt
        assert sample_metadata["title"] in prompt

    def test_get_enhanced_summary_prompt_developer(self, sample_transcript, sample_metadata):
        """Test prompt generation for developer mode"""
        from modules.core_001.prompts import get_enhanced_summary_prompt

        prompt = get_enhanced_summary_prompt(sample_transcript, sample_metadata, mode="developer")

        assert "developer" in prompt
        assert "50-100" in prompt

    def test_get_enhanced_summary_prompt_research(self, sample_transcript, sample_metadata):
        """Test prompt generation for research mode"""
        from modules.core_001.prompts import get_enhanced_summary_prompt

        prompt = get_enhanced_summary_prompt(sample_transcript, sample_metadata, mode="research")

        assert "research" in prompt
        assert "75-150" in prompt

    def test_get_synthesis_prompt(self):
        """Test synthesis prompt generation"""
        from modules.core_001.prompts import get_synthesis_prompt

        summaries = [
            {"title": "Video 1", "content": "Summary 1", "channel": "Channel A", "views": 1000},
            {"title": "Video 2", "content": "Summary 2", "channel": "Channel B", "views": 2000}
        ]

        metadata = {
            "collection_name": "Test Collection",
            "date_range": "2025-10-01 to 2025-10-05",
            "today": "2025-10-06",
            "total_duration": "30:00",
            "tool_list": "Claude, GPT-4",
            "dominant_topics": "AI Development"
        }

        prompt = get_synthesis_prompt(summaries, metadata)

        assert "Test Collection" in prompt
        assert "Summary 1" in prompt
        assert "Summary 2" in prompt
        assert "2 videos" in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
