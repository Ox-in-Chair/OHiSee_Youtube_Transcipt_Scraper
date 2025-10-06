"""
Integration tests for v2.0 modules with v1.0 core.

Tests the complete workflow:
1. v1.0 scraper extracts transcript
2. CORE-001 generates enhanced summary
3. VISUAL-001 creates diagrams
4. EXEC-001 generates playbooks

Validates that all 3 completed modules integrate correctly.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from modules.core_001 import CoreEngine
from modules.visual_001 import VisualEngine
from modules.exec_001 import ExecutionEngine


class TestModuleIntegration:
    """Test integration between completed v2.0 modules."""

    def setup_method(self):
        """Setup test fixtures."""
        self.callback = Mock()

        # Sample transcript data (simulates v1.0 scraper output)
        self.sample_transcript = """
        In this video, we'll explore workflow automation for manufacturing.
        First, let's discuss the key tools: Python for scripting, Docker for containerization.
        The implementation steps are: 1. Install Python 3.9, 2. Set up virtual environment.
        Common commands include: pip install -r requirements.txt, docker-compose up.
        This approach saves 30% time and reduces errors by 50%.
        """

        self.sample_metadata = {
            "title": "Workflow Automation Guide",
            "channel": "Tech Channel",
            "duration": 600,
            "upload_date": "2024-01-15",
            "views": 10000,
            "url": "https://youtube.com/watch?v=test123"
        }

    @patch('modules.core_001.engine.OpenAI')
    def test_core_to_visual_workflow(self, mock_openai):
        """Test CORE-001 → VISUAL-001 integration."""
        # Mock GPT-4 response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """
## Key Insights
- Python 3.9 required for automation
- Docker containerization improves portability
- 30% time savings reported

## Tools & Technologies
- Python 3.9
- Docker
- pip package manager

## Implementation Steps
1. Install Python 3.9
2. Create virtual environment
3. Install dependencies with pip
4. Configure Docker environment

## Technical Concepts
- Virtual environments isolate dependencies
- Docker containers ensure consistency
- Package managers automate installation

## Performance Metrics
- 30% time reduction
- 50% error reduction
"""
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        # Step 1: Generate enhanced summary with CORE-001
        core_engine = CoreEngine(api_key='test-key-mock', callback=self.callback)
        summary = core_engine.enhance_summary(
            self.sample_transcript,
            self.sample_metadata,
            mode='developer'
        )

        # Verify summary structure
        assert 'insights' in summary
        assert 'tools' in summary
        assert 'steps' in summary
        assert len(summary['insights']) >= 3
        assert len(summary['tools']) >= 2

        # Step 2: Create synthesis from single summary (VISUAL-001 expects synthesis)
        synthesis = {
            'chronological_timeline': [
                {'timestamp': '2024-01-15', 'event': 'Python 3.9', 'description': 'Python 3.9 required'}
            ],
            'cross_video_patterns': [
                {'pattern': 'Docker usage', 'videos': ['Video 1', 'Video 2']}
            ],
            'tool_mentions': {
                'Python': {'count': 3, 'contexts': ['automation', 'scripting']},
                'Docker': {'count': 2, 'contexts': ['containerization']}
            },
            'consensus_points': ['Use virtual environments'],
            'contradictions': []
        }

        # Generate diagrams with VISUAL-001
        visual_engine = VisualEngine(callback=self.callback)
        config = {
            'diagram_types': ['timeline', 'architecture', 'comparison', 'flowchart'],
            'complexity': 'detailed',
            'validate': True
        }
        result = visual_engine.generate_all(synthesis, config)

        # Verify all diagram types generated
        assert 'diagrams' in result
        assert 'timeline' in result['diagrams']
        assert 'architecture' in result['diagrams']
        assert 'comparison' in result['diagrams']
        assert 'flowchart' in result['diagrams']

        # Verify Mermaid syntax validity
        for diagram_type, diagram_data in result['diagrams'].items():
            assert 'mermaid_code' in diagram_data
            assert len(diagram_data['mermaid_code']) > 10

    @patch('modules.core_001.engine.OpenAI')
    def test_core_to_exec_workflow(self, mock_openai):
        """Test CORE-001 → EXEC-001 integration."""
        # Mock GPT-4 response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """
## Key Insights
- Automation reduces manual effort
- Docker ensures reproducibility

## Tools & Technologies
- Python 3.9
- Docker
- pip

## CLI Commands
- pip install -r requirements.txt
- docker-compose up -d
- python main.py

## Implementation Steps
1. Install Python 3.9
2. Create virtual environment: python -m venv venv
3. Activate environment: source venv/bin/activate (Linux/Mac)
4. Install dependencies: pip install -r requirements.txt

## Prompt Templates
"Generate a Python script that automates the following workflow: [describe workflow]"

## Technical Concepts
- Virtual environments isolate dependencies
- Docker containers provide consistency
"""
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        # Step 1: Generate enhanced summary with CORE-001
        core_engine = CoreEngine(callback=self.callback)
        summary = core_engine.enhance_summary(
            self.sample_transcript,
            self.sample_metadata,
            mode='developer'
        )

        # Step 2: Generate playbook with EXEC-001
        exec_engine = ExecutionEngine(callback=self.callback)
        playbook = exec_engine.generate_playbook(
            summary['insights'],
            detail_level='detailed'
        )

        # Verify playbook structure
        assert 'playbook' in playbook
        assert len(playbook['playbook']) >= 3

        # Step 3: Extract prompts
        prompts = exec_engine.extract_prompts(summary['insights'])
        assert 'prompts' in prompts
        assert len(prompts['prompts']) >= 1

        # Step 4: Parse CLI commands
        commands = exec_engine.parse_cli_commands(summary['insights'])
        assert 'commands' in commands
        assert len(commands['commands']) >= 2

        # Step 5: Generate checklist
        checklist = exec_engine.create_checklist(
            summary['insights'],
            format='markdown'
        )
        assert 'checklist' in checklist
        assert '- [ ]' in checklist['checklist']

    @patch('modules.core_001.engine.OpenAI')
    def test_full_pipeline_integration(self, mock_openai):
        """Test complete v1.0 → CORE-001 → VISUAL-001 → EXEC-001 workflow."""
        # Mock GPT-4 response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """
## Key Insights
- Python automation reduces manual work by 30%
- Docker containerization improves portability
- CI/CD pipelines ensure quality

## Tools & Technologies
- Python 3.9
- Docker 20.10
- GitHub Actions
- pytest

## Implementation Steps
1. Set up Python development environment
2. Configure Docker for containerization
3. Implement automated testing with pytest
4. Deploy with GitHub Actions

## CLI Commands
- python -m venv venv
- pip install -r requirements.txt
- docker build -t app .
- docker run -p 8000:8000 app
- pytest tests/ -v

## Prompt Templates
"Create a Dockerfile for a Python application with the following requirements: [list requirements]"
"Generate pytest test cases for: [describe functionality]"

## Technical Concepts
- Virtual environments isolate project dependencies
- Docker images ensure consistent deployment
- CI/CD automates testing and deployment
- Unit tests validate code correctness

## Performance Metrics
- 30% time savings with automation
- 95% test coverage target
- <5 minute build time
"""
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        # PHASE 1: v1.0 scraper (simulated - we have transcript)
        transcript = self.sample_transcript
        metadata = self.sample_metadata

        # PHASE 2: CORE-001 enhanced summary
        core_engine = CoreEngine(callback=self.callback)
        summary = core_engine.enhance_summary(
            transcript,
            metadata,
            mode='developer'
        )

        # Validate CORE-001 output
        assert 'insights' in summary
        assert 'tools' in summary
        assert 'steps' in summary
        assert 'metadata' in summary
        assert len(summary['insights']) >= 5

        # PHASE 3: VISUAL-001 diagrams
        visual_engine = VisualEngine(callback=self.callback)
        diagrams = visual_engine.generate_all_diagrams(summary)

        # Validate VISUAL-001 output
        assert len(diagrams) == 4
        for diagram in diagrams.values():
            assert '```mermaid' in diagram
            assert len(diagram) > 50

        # PHASE 4: EXEC-001 playbooks & artifacts
        exec_engine = ExecutionEngine(callback=self.callback)

        playbook = exec_engine.generate_playbook(summary['insights'], 'detailed')
        prompts = exec_engine.extract_prompts(summary['insights'])
        commands = exec_engine.parse_cli_commands(summary['insights'])
        checklist = exec_engine.create_checklist(summary['insights'], 'markdown')

        # Validate EXEC-001 outputs
        assert len(playbook['playbook']) >= 3
        assert len(prompts['prompts']) >= 1
        assert len(commands['commands']) >= 3
        assert '- [ ]' in checklist['checklist']

        # PHASE 5: Verify complete deliverable package
        complete_output = {
            'transcript': transcript,
            'metadata': metadata,
            'summary': summary,
            'diagrams': diagrams,
            'playbook': playbook,
            'prompts': prompts,
            'commands': commands,
            'checklist': checklist
        }

        # Final validation
        assert all(key in complete_output for key in [
            'transcript', 'metadata', 'summary', 'diagrams',
            'playbook', 'prompts', 'commands', 'checklist'
        ])

        # Verify data flows correctly through pipeline
        assert complete_output['summary']['metadata']['title'] == metadata['title']
        assert len(complete_output['diagrams']) == 4
        assert len(complete_output['playbook']['playbook']) >= 3

    def test_error_handling_integration(self):
        """Test error handling across module boundaries."""
        core_engine = CoreEngine(callback=self.callback)
        visual_engine = VisualEngine(callback=self.callback)
        exec_engine = ExecutionEngine(callback=self.callback)

        # Test invalid mode handling (CORE-001)
        with pytest.raises(ValueError, match="Invalid mode"):
            core_engine.enhance_summary("test", {}, mode='invalid')

        # Test empty insights handling (VISUAL-001)
        empty_summary = {'insights': [], 'tools': [], 'steps': []}
        diagrams = visual_engine.generate_all_diagrams(empty_summary)

        # Should generate valid but minimal diagrams
        assert len(diagrams) == 4
        for diagram in diagrams.values():
            assert '```mermaid' in diagram

        # Test empty insights handling (EXEC-001)
        playbook = exec_engine.generate_playbook([], 'detailed')
        assert 'playbook' in playbook
        assert len(playbook['playbook']) >= 0  # Can be empty

    @patch('modules.core_001.engine.OpenAI')
    def test_performance_integration(self, mock_openai):
        """Test performance of complete pipeline."""
        import time

        # Mock fast GPT-4 response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """
## Key Insights
- Test insight 1
- Test insight 2

## Tools & Technologies
- Tool 1
- Tool 2

## Implementation Steps
1. Step 1
2. Step 2
"""
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        core_engine = CoreEngine(callback=self.callback)
        visual_engine = VisualEngine(callback=self.callback)
        exec_engine = ExecutionEngine(callback=self.callback)

        start_time = time.time()

        # Execute complete pipeline
        summary = core_engine.enhance_summary(
            self.sample_transcript,
            self.sample_metadata,
            mode='quick'
        )
        diagrams = visual_engine.generate_all_diagrams(summary)
        playbook = exec_engine.generate_playbook(summary['insights'], 'basic')

        total_time = time.time() - start_time

        # Performance targets (with mocked GPT-4)
        assert total_time < 5.0, f"Pipeline took {total_time:.2f}s (target: <5s)"


class TestModuleCompatibility:
    """Test backward compatibility with v1.0 core."""

    def test_core001_accepts_v1_transcript(self):
        """Verify CORE-001 can process v1.0 scraper output format."""
        callback = Mock()
        core_engine = CoreEngine(callback=callback)

        # v1.0 transcript format (plain text)
        v1_transcript = "This is a sample transcript from v1.0 scraper."
        v1_metadata = {
            "title": "Test Video",
            "channel": "Test Channel",
            "duration": 300,
            "upload_date": "2024-01-01",
            "views": 1000,
            "url": "https://youtube.com/watch?v=test"
        }

        # Should not raise any errors
        # (Will fail on actual OpenAI call, but structure validation passes)
        try:
            core_engine.enhance_summary(v1_transcript, v1_metadata, mode='quick')
        except Exception as e:
            # Expect OpenAI error, not structure error
            assert 'OpenAI' in str(type(e).__name__) or 'API' in str(e)

    def test_modules_handle_missing_fields_gracefully(self):
        """Test graceful degradation with incomplete data."""
        callback = Mock()

        # Minimal summary (missing optional fields)
        minimal_summary = {
            'insights': ['Insight 1', 'Insight 2'],
            'tools': [],
            'steps': []
        }

        visual_engine = VisualEngine(callback=callback)
        exec_engine = ExecutionEngine(callback=callback)

        # Should not crash with minimal data
        diagrams = visual_engine.generate_all_diagrams(minimal_summary)
        assert len(diagrams) == 4

        playbook = exec_engine.generate_playbook(minimal_summary['insights'], 'basic')
        assert 'playbook' in playbook


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
