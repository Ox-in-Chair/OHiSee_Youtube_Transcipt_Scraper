"""
Execution Engine - EXEC-001 Main Integration

Unified API for generating all execution artifacts from CORE-001 insights.
Coordinates playbook generation, prompt extraction, CLI parsing, and checklist creation.
"""

from typing import Dict, List, Optional
from datetime import datetime

from .playbook_generator import PlaybookGenerator
from .prompt_extractor import PromptExtractor
from .cli_parser import CLIParser
from .checklist_creator import ChecklistCreator


class ExecutionEngine:
    """
    Main engine for EXEC-001 execution artifact generation.

    Transforms CORE-001 insights into actionable artifacts:
    - Playbooks: Step-by-step implementation guides
    - Prompts: Reusable prompt templates
    - Commands: CLI command references
    - Checklists: Progress tracking tools
    """

    def __init__(self, callback=None):
        """
        Initialize execution engine with all sub-components.

        Args:
            callback: Optional logging callback function
        """
        self.callback = callback or (lambda x: None)

        # Initialize all components
        self.playbook_gen = PlaybookGenerator(callback=callback)
        self.prompt_extractor = PromptExtractor(callback=callback)
        self.cli_parser = CLIParser(callback=callback)
        self.checklist_creator = ChecklistCreator(callback=callback)

    def generate_all(self, insights: List[Dict], context: Optional[Dict] = None) -> Dict:
        """
        Main entry point - generates all execution artifacts.

        Args:
            insights: List of notable items from CORE-001 summary
            context: Optional context dictionary with:
                - user_skill_level: "beginner"|"intermediate"|"advanced"
                - available_tools: List of installed tools
                - time_budget: Available time in minutes
                - objectives: List of user objectives
                - output_formats: List of desired formats

        Returns:
            Complete EXEC-001 output contract with all artifacts
        """
        self.callback("=" * 60)
        self.callback("EXEC-001 Execution Engine Started")
        self.callback("=" * 60)

        start_time = datetime.now()

        # Initialize context with defaults
        context = context or {}
        user_skill = context.get('user_skill_level', 'intermediate')
        output_formats = context.get('output_formats', ['markdown'])

        # Determine playbook style based on skill level
        playbook_style = self._determine_playbook_style(user_skill)

        self.callback(f"User Skill Level: {user_skill}")
        self.callback(f"Playbook Style: {playbook_style}")
        self.callback(f"Processing {len(insights)} insights...")

        # Generate playbooks
        self.callback("\n[1/4] Generating Playbooks...")
        playbooks = self._generate_playbooks(insights, playbook_style)

        # Extract prompts
        self.callback("\n[2/4] Extracting Prompts...")
        prompts = self._extract_prompts(insights)

        # Parse CLI commands
        self.callback("\n[3/4] Parsing CLI Commands...")
        cli_commands = self._parse_cli_commands(insights)

        # Create checklists
        self.callback("\n[4/4] Creating Checklists...")
        checklists = self._create_checklists(playbooks, output_formats)

        # Calculate processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        self.callback(f"\nProcessing completed in {processing_time:.2f} seconds")
        self.callback("=" * 60)

        # Build output contract
        output = {
            'playbooks': playbooks,
            'prompts': prompts,
            'cli_commands': cli_commands,
            'checklists': checklists,
            'metadata': {
                'total_insights_processed': len(insights),
                'total_playbooks': len(playbooks),
                'total_prompts': sum(len(prompts[cat]) for cat in prompts),
                'total_commands': sum(len(cli_commands[plat]) for plat in cli_commands),
                'total_checklists': len(checklists),
                'processing_time_seconds': processing_time,
                'user_context': context,
                'generated_at': datetime.now().isoformat()
            }
        }

        return output

    def generate_playbook(self, insight: Dict, style: str = "detailed") -> Dict:
        """
        Generate single playbook from insight.

        Args:
            insight: Notable item from CORE-001
            style: "quick", "detailed", or "comprehensive"

        Returns:
            Playbook dictionary
        """
        return self.playbook_gen.generate(insight, style)

    def extract_prompts(self, content: str, categorize: bool = True) -> List[Dict]:
        """
        Extract prompts from content.

        Args:
            content: Text content to scan
            categorize: Whether to categorize prompts

        Returns:
            List of prompt dictionaries
        """
        return self.prompt_extractor.extract_prompts(content, categorize)

    def parse_commands(self, text: str, platform: str = "auto") -> List[Dict]:
        """
        Parse CLI commands from text.

        Args:
            text: Content to scan
            platform: Target platform filter

        Returns:
            List of command dictionaries
        """
        return self.cli_parser.parse_commands(text, platform)

    def create_checklist(self, steps: List[Dict], format: str = "markdown") -> Dict:
        """
        Create implementation checklist.

        Args:
            steps: List of step dictionaries
            format: Output format

        Returns:
            Checklist dictionary
        """
        return self.checklist_creator.create_checklist(steps, format)

    def export_playbook(self, playbook: Dict, format: str = "markdown") -> str:
        """
        Export playbook to formatted output.

        Args:
            playbook: Playbook dictionary
            format: "markdown" or other formats

        Returns:
            Formatted string
        """
        if format == "markdown":
            return self.playbook_gen.to_markdown(playbook)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def export_prompt(self, prompt: Dict, format: str = "markdown") -> str:
        """
        Export prompt to formatted output.

        Args:
            prompt: Prompt dictionary
            format: "markdown" or other formats

        Returns:
            Formatted string
        """
        if format == "markdown":
            return self.prompt_extractor.to_markdown(prompt)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def export_command(self, command: Dict, format: str = "markdown") -> str:
        """
        Export command to formatted output.

        Args:
            command: Command dictionary
            format: "markdown" or other formats

        Returns:
            Formatted string
        """
        if format == "markdown":
            return self.cli_parser.to_markdown(command)
        else:
            raise ValueError(f"Unsupported format: {format}")

    # Helper methods

    def _determine_playbook_style(self, user_skill: str) -> str:
        """Determine playbook detail level from user skill."""
        if user_skill == "beginner":
            return "comprehensive"
        elif user_skill == "intermediate":
            return "detailed"
        elif user_skill == "advanced":
            return "quick"
        else:
            return "detailed"

    def _generate_playbooks(self, insights: List[Dict], style: str) -> Dict:
        """Generate playbooks from all insights."""
        playbooks = {}

        # Focus on actionable insights
        actionable_tags = ["Command", "Protocol", "Pattern", "Tool"]

        for insight in insights:
            tag = insight.get("tag", "")

            # Generate playbook for actionable items
            if tag in actionable_tags or insight.get("implementation_steps"):
                playbook = self.playbook_gen.generate(insight, style)
                playbooks[playbook['playbook_id']] = playbook
                self.callback(f"  Generated: {playbook['title']}")

        self.callback(f"  Total playbooks generated: {len(playbooks)}")
        return playbooks

    def _extract_prompts(self, insights: List[Dict]) -> Dict:
        """Extract all prompts from insights."""
        # Use prompt extractor's built-in method
        categorized_prompts = self.prompt_extractor.extract_from_notable_items(insights)

        # Count totals
        total_prompts = sum(len(prompts) for prompts in categorized_prompts.values())
        self.callback(f"  Total prompts extracted: {total_prompts}")

        for category, prompts in categorized_prompts.items():
            if prompts:
                self.callback(f"    {category}: {len(prompts)} prompts")

        return categorized_prompts

    def _parse_cli_commands(self, insights: List[Dict]) -> Dict:
        """Parse all CLI commands from insights."""
        # Use CLI parser's built-in method
        categorized_commands = self.cli_parser.extract_from_notable_items(insights)

        # Count totals
        total_commands = sum(len(cmds) for cmds in categorized_commands.values())
        self.callback(f"  Total commands extracted: {total_commands}")

        for platform, commands in categorized_commands.items():
            if commands:
                self.callback(f"    {platform}: {len(commands)} commands")

        return categorized_commands

    def _create_checklists(self, playbooks: Dict, output_formats: List[str]) -> List[Dict]:
        """Create checklists from playbooks."""
        checklists = []

        # Create one checklist per playbook for each requested format
        for playbook_id, playbook in playbooks.items():
            for format_type in output_formats:
                try:
                    checklist = self.checklist_creator.create_from_playbook(
                        playbook, format=format_type
                    )
                    checklist['playbook_id'] = playbook_id
                    checklists.append(checklist)
                except ValueError as e:
                    self.callback(f"  Warning: Skipped unsupported format {format_type}: {e}")

        self.callback(f"  Total checklists created: {len(checklists)}")
        return checklists

    def get_summary_stats(self, output: Dict) -> Dict:
        """
        Get summary statistics from EXEC-001 output.

        Args:
            output: Full EXEC-001 output dictionary

        Returns:
            Summary statistics dictionary
        """
        prompts = output.get('prompts', {})
        commands = output.get('cli_commands', {})

        stats = {
            'playbooks': {
                'total': len(output.get('playbooks', {})),
                'by_complexity': self._count_by_field(
                    output.get('playbooks', {}).values(), 'complexity'
                ),
                'by_readiness': self._count_by_field(
                    output.get('playbooks', {}).values(), 'readiness'
                )
            },
            'prompts': {
                'total': sum(len(prompts[cat]) for cat in prompts),
                'by_category': {cat: len(prompts[cat]) for cat in prompts}
            },
            'commands': {
                'total': sum(len(commands[plat]) for plat in commands),
                'by_platform': {plat: len(commands[plat]) for plat in commands}
            },
            'checklists': {
                'total': len(output.get('checklists', [])),
                'by_format': self._count_by_field(
                    output.get('checklists', []), 'format'
                )
            }
        }

        return stats

    def _count_by_field(self, items, field: str) -> Dict:
        """Count items grouped by field value."""
        counts = {}

        for item in items:
            value = item.get(field, 'Unknown')
            counts[value] = counts.get(value, 0) + 1

        return counts

    def validate_output_contract(self, output: Dict) -> Dict:
        """
        Validate EXEC-001 output against contract specification.

        Args:
            output: Generated output dictionary

        Returns:
            Validation result dictionary with errors/warnings
        """
        errors = []
        warnings = []

        # Check required top-level keys
        required_keys = ['playbooks', 'prompts', 'cli_commands', 'checklists', 'metadata']
        for key in required_keys:
            if key not in output:
                errors.append(f"Missing required key: {key}")

        # Validate playbooks structure
        playbooks = output.get('playbooks', {})
        if not isinstance(playbooks, dict):
            errors.append("playbooks must be a dictionary")
        else:
            for pb_id, pb in playbooks.items():
                required_pb_keys = ['playbook_id', 'title', 'objective', 'steps']
                for key in required_pb_keys:
                    if key not in pb:
                        errors.append(f"Playbook {pb_id} missing key: {key}")

        # Validate prompts structure
        prompts = output.get('prompts', {})
        if not isinstance(prompts, dict):
            errors.append("prompts must be a dictionary")

        # Validate CLI commands structure
        cli_commands = output.get('cli_commands', {})
        if not isinstance(cli_commands, dict):
            errors.append("cli_commands must be a dictionary")

        # Validate checklists structure
        checklists = output.get('checklists', [])
        if not isinstance(checklists, list):
            errors.append("checklists must be a list")

        # Warnings for empty sections
        if len(playbooks) == 0:
            warnings.append("No playbooks generated")
        if sum(len(prompts.get(cat, [])) for cat in prompts) == 0:
            warnings.append("No prompts extracted")
        if sum(len(cli_commands.get(plat, [])) for plat in cli_commands) == 0:
            warnings.append("No CLI commands extracted")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
