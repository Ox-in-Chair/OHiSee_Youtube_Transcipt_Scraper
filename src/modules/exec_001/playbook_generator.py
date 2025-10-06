"""
Playbook Generator - EXEC-001 Component

Generates step-by-step executable playbooks from CORE-001 insights.
Creates comprehensive guides with prerequisites, troubleshooting, and verification.
"""

import re
from typing import Dict, List, Optional
from datetime import datetime


class PlaybookGenerator:
    """Generate executable implementation playbooks from insights."""

    def __init__(self, callback=None):
        """
        Initialize playbook generator.

        Args:
            callback: Optional logging callback function
        """
        self.callback = callback or (lambda x: None)
        self.playbook_counter = 0

    def generate(self, insight: Dict, style: str = "detailed") -> Dict:
        """
        Generate step-by-step executable playbook.

        Args:
            insight: Notable item from CORE-001 summary
            style: "quick" (5-10 steps), "detailed" (10-20 steps),
                   "comprehensive" (20+ steps with alternatives)

        Returns:
            Playbook dictionary with all sections
        """
        self.playbook_counter += 1
        playbook_id = f"playbook_{self.playbook_counter}"

        self.callback(f"Generating {style} playbook: {insight.get('title', 'Untitled')}")

        # Extract prerequisites
        prerequisites = self.extract_prerequisites(insight)

        # Generate implementation steps
        steps = self.generate_steps(insight, style)

        # Create troubleshooting guide
        troubleshooting = self.create_troubleshooting_guide(insight)

        # Generate verification steps
        verification = self.generate_verification_steps(insight)

        # Calculate estimated time
        estimated_time = self._calculate_time(insight, steps)

        # Determine complexity
        complexity = self._determine_complexity(insight)

        # Find related playbooks (placeholder for future cross-referencing)
        related_playbooks = []

        playbook = {
            "playbook_id": playbook_id,
            "title": insight.get("title", "Implementation Guide"),
            "objective": self._extract_objective(insight),
            "prerequisites": prerequisites,
            "estimated_time": estimated_time,
            "complexity": complexity,
            "steps": steps,
            "verification": verification,
            "success_criteria": self._extract_success_criteria(insight),
            "troubleshooting": troubleshooting,
            "related_playbooks": related_playbooks,
            "tags": [insight.get("tag", "General")],
            "readiness": insight.get("readiness", "READY"),
            "source_timestamp": insight.get("source_timestamp", "00:00"),
            "generated_at": datetime.now().isoformat()
        }

        return playbook

    def extract_prerequisites(self, insight: Dict) -> List[Dict]:
        """
        Extract prerequisites from insight.

        Looks for patterns like:
        - "Requires X"
        - "You need Y"
        - "Install Z"
        - "Before starting, ensure..."
        """
        prerequisites = []

        # Check description for prerequisite patterns
        description = insight.get("description", "")
        implementation_steps = insight.get("implementation_steps", [])

        # Common prerequisite indicators
        prereq_patterns = [
            r"(?:requires?|needs?|must have|install|setup)\s+([^\.]+)",
            r"(?:before|prior to|first)\s+(?:starting|beginning|you)\s+(?:must|need|should)\s+([^\.]+)",
            r"(?:ensure|make sure|verify)\s+(?:you have|that)\s+([^\.]+)"
        ]

        # Scan description
        for pattern in prereq_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                prereq_text = match.group(1).strip()
                if prereq_text and len(prereq_text) < 150:  # Reasonable length
                    prerequisites.append({
                        "description": prereq_text,
                        "type": "software" if any(x in prereq_text.lower() for x in
                                                 ["install", "npm", "pip", "download"]) else "knowledge",
                        "command": self._extract_install_command(prereq_text),
                        "mandatory": True
                    })

        # Check for explicit prerequisites in implementation steps
        for step in implementation_steps:
            if any(keyword in step.lower() for keyword in
                  ["install", "setup", "configure", "download"]):
                if len(prerequisites) < 5:  # Limit to reasonable number
                    prerequisites.append({
                        "description": step,
                        "type": "setup",
                        "command": self._extract_command_from_text(step),
                        "mandatory": True
                    })

        # Add default prerequisites based on tags
        tag = insight.get("tag", "")
        if tag == "Command" and not prerequisites:
            prerequisites.append({
                "description": "Terminal or command-line access",
                "type": "environment",
                "command": None,
                "mandatory": True
            })

        return prerequisites[:5]  # Limit to 5 most relevant

    def generate_steps(self, insight: Dict, style: str) -> List[Dict]:
        """
        Generate implementation steps based on style.

        Args:
            insight: Notable item from CORE-001
            style: "quick", "detailed", or "comprehensive"
        """
        steps = []
        implementation_steps = insight.get("implementation_steps", [])
        code_snippet = insight.get("code_snippet")

        if not implementation_steps and not code_snippet:
            # Generate minimal step from description
            steps.append({
                "step_number": 1,
                "action": insight.get("title", "Execute implementation"),
                "command": None,
                "expected_output": "Implementation complete",
                "explanation": insight.get("description", ""),
                "troubleshooting": {}
            })
            return steps

        # Process each implementation step
        for idx, step_text in enumerate(implementation_steps):
            step_number = idx + 1

            # Extract command if present
            command = self._extract_command_from_text(step_text)

            # Generate expected output
            expected_output = self._generate_expected_output(step_text, command)

            # Add explanation for detailed/comprehensive styles
            explanation = ""
            if style in ["detailed", "comprehensive"]:
                explanation = self._generate_step_explanation(step_text)

            # Create troubleshooting for this step
            step_troubleshooting = {}
            if style == "comprehensive":
                step_troubleshooting = self._generate_step_troubleshooting(step_text, command)

            steps.append({
                "step_number": step_number,
                "action": step_text,
                "command": command,
                "expected_output": expected_output,
                "explanation": explanation,
                "troubleshooting": step_troubleshooting
            })

        # Add code snippet as final step if present
        if code_snippet and style in ["detailed", "comprehensive"]:
            steps.append({
                "step_number": len(steps) + 1,
                "action": "Implement the code",
                "command": None,
                "code_block": code_snippet,
                "expected_output": "Code integrated successfully",
                "explanation": "Use the provided code snippet in your implementation",
                "troubleshooting": {}
            })

        return steps

    def create_troubleshooting_guide(self, insight: Dict) -> Dict:
        """
        Create troubleshooting section from common errors mentioned.

        Returns:
            Dictionary with {issue: solution} pairs
        """
        troubleshooting = {}

        description = insight.get("description", "")

        # Look for error/warning patterns
        error_patterns = [
            r"(?:error|warning|issue|problem):\s*([^\.]+)\s*(?:solution|fix|resolve):\s*([^\.]+)",
            r"if\s+(?:you see|get|encounter)\s+([^,]+),\s*(?:then\s+)?([^\.]+)",
            r"common\s+(?:error|issue):\s*([^\.]+?)(?:fix|solution):\s*([^\.]+)"
        ]

        for pattern in error_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                issue = match.group(1).strip()
                solution = match.group(2).strip()
                if issue and solution:
                    troubleshooting[issue] = solution

        # Add generic troubleshooting based on tag
        tag = insight.get("tag", "")
        if tag == "Command" and not troubleshooting:
            troubleshooting["Command not found"] = "Ensure the tool is installed and in your PATH"
            troubleshooting["Permission denied"] = "Run with administrator/sudo privileges"
        elif tag == "Warning" and not troubleshooting:
            troubleshooting["Unexpected behavior"] = description.split(".")[0] if description else "Review the warning carefully"

        return troubleshooting

    def generate_verification_steps(self, insight: Dict) -> List[Dict]:
        """
        Generate verification/testing steps.

        Returns:
            List of verification steps with expected results
        """
        verification_steps = []

        tag = insight.get("tag", "")

        # Generate tag-specific verification
        if tag == "Command":
            verification_steps.append({
                "step": "Run the command with --help or --version flag",
                "expected": "Command executes successfully without errors",
                "type": "functional"
            })
        elif tag == "Tool":
            verification_steps.append({
                "step": "Verify tool installation and version",
                "expected": "Tool is accessible and version matches requirements",
                "type": "installation"
            })
        elif tag == "Pattern" or tag == "Protocol":
            verification_steps.append({
                "step": "Test the implementation with sample data",
                "expected": "Pattern executes as described in documentation",
                "type": "integration"
            })

        # Always add final verification
        verification_steps.append({
            "step": "Review implementation against success criteria",
            "expected": "All success criteria met",
            "type": "final"
        })

        return verification_steps

    def to_markdown(self, playbook: Dict) -> str:
        """
        Convert playbook to markdown format.

        Args:
            playbook: Playbook dictionary

        Returns:
            Formatted markdown string
        """
        md = f"# Playbook: {playbook['title']}\n\n"
        md += f"**ID**: `{playbook['playbook_id']}`\n"
        md += f"**Generated**: {playbook['generated_at']}\n\n"

        md += "## Objective\n\n"
        md += f"{playbook['objective']}\n\n"

        md += "## Overview\n\n"
        md += f"- **Estimated Time**: {playbook['estimated_time']}\n"
        md += f"- **Complexity**: {playbook['complexity']}\n"
        md += f"- **Readiness**: {playbook['readiness']}\n"
        md += f"- **Source Timestamp**: {playbook['source_timestamp']}\n\n"

        # Prerequisites
        if playbook['prerequisites']:
            md += "## Prerequisites\n\n"
            for prereq in playbook['prerequisites']:
                checkbox = "[ ]"
                md += f"- {checkbox} {prereq['description']}"
                if prereq.get('command'):
                    md += f"\n  - Install: `{prereq['command']}`"
                md += "\n"
            md += "\n"

        # Implementation Steps
        md += "## Step-by-Step Implementation\n\n"
        for step in playbook['steps']:
            md += f"### Step {step['step_number']}: {step['action']}\n\n"

            if step.get('explanation'):
                md += f"{step['explanation']}\n\n"

            if step.get('command'):
                md += "```bash\n"
                md += f"{step['command']}\n"
                md += "```\n\n"

            if step.get('code_block'):
                md += "```\n"
                md += f"{step['code_block']}\n"
                md += "```\n\n"

            if step.get('expected_output'):
                md += f"**Expected Output**: {step['expected_output']}\n\n"

            if step.get('troubleshooting'):
                md += "**Troubleshooting**:\n"
                for issue, solution in step['troubleshooting'].items():
                    md += f"- **{issue}**: {solution}\n"
                md += "\n"

        # Verification
        if playbook['verification']:
            md += "## Verification\n\n"
            for verify in playbook['verification']:
                md += f"- [ ] **{verify['step']}**\n"
                md += f"  - Expected: {verify['expected']}\n"
            md += "\n"

        # Success Criteria
        if playbook['success_criteria']:
            md += "## Success Criteria\n\n"
            for criterion in playbook['success_criteria']:
                md += f"- [ ] {criterion}\n"
            md += "\n"

        # Troubleshooting Guide
        if playbook['troubleshooting']:
            md += "## Troubleshooting\n\n"
            md += "| Issue | Solution |\n"
            md += "|-------|----------|\n"
            for issue, solution in playbook['troubleshooting'].items():
                md += f"| {issue} | {solution} |\n"
            md += "\n"

        return md

    # Helper methods

    def _extract_objective(self, insight: Dict) -> str:
        """Extract clear objective statement."""
        title = insight.get("title", "")
        description = insight.get("description", "")

        # Try to extract first sentence from description
        if description:
            first_sentence = description.split(".")[0] + "."
            return first_sentence

        return f"Implement {title}"

    def _extract_success_criteria(self, insight: Dict) -> List[str]:
        """Extract success criteria from insight."""
        criteria = []

        # Use implementation steps as success criteria
        implementation_steps = insight.get("implementation_steps", [])
        if implementation_steps:
            criteria = [f"Completed: {step}" for step in implementation_steps[:3]]

        # Always add final criterion
        criteria.append(f"Implementation matches description and requirements")

        return criteria

    def _calculate_time(self, insight: Dict, steps: List[Dict]) -> str:
        """Calculate estimated implementation time."""
        # Use insight's implementation_time if available
        if insight.get("implementation_time"):
            return insight["implementation_time"]

        # Otherwise estimate from steps
        num_steps = len(steps)
        if num_steps <= 3:
            return "15-30 minutes"
        elif num_steps <= 5:
            return "30-60 minutes"
        elif num_steps <= 10:
            return "1-2 hours"
        else:
            return "2-4 hours"

    def _determine_complexity(self, insight: Dict) -> str:
        """Determine complexity level."""
        readiness = insight.get("readiness", "READY")
        implementation_steps = insight.get("implementation_steps", [])

        if readiness == "EXPERIMENTAL":
            return "Advanced"
        elif readiness == "NEEDS_SETUP":
            return "Intermediate"
        elif len(implementation_steps) > 5:
            return "Intermediate"
        else:
            return "Beginner"

    def _extract_install_command(self, text: str) -> Optional[str]:
        """Extract installation command from text."""
        # Common package manager patterns
        install_patterns = [
            r"(npm install[^\n]+)",
            r"(pip install[^\n]+)",
            r"(apt-get install[^\n]+)",
            r"(brew install[^\n]+)",
            r"(cargo install[^\n]+)"
        ]

        for pattern in install_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_command_from_text(self, text: str) -> Optional[str]:
        """Extract command from step text."""
        # Look for common command indicators
        if "`" in text:
            # Extract from backticks
            match = re.search(r"`([^`]+)`", text)
            if match:
                return match.group(1).strip()

        # Look for command prefixes
        command_prefixes = ["run:", "execute:", "type:", "enter:"]
        for prefix in command_prefixes:
            if prefix in text.lower():
                parts = text.lower().split(prefix, 1)
                if len(parts) > 1:
                    return parts[1].strip().split("\n")[0].strip()

        return None

    def _generate_expected_output(self, step_text: str, command: Optional[str]) -> str:
        """Generate expected output for a step."""
        if not command:
            return "Step completed successfully"

        # Command-specific expectations
        if "install" in command.lower():
            return "Package installed successfully"
        elif "test" in command.lower():
            return "All tests passing"
        elif "build" in command.lower():
            return "Build completed without errors"
        elif "run" in command.lower() or "start" in command.lower():
            return "Application running without errors"
        else:
            return "Command executed successfully"

    def _generate_step_explanation(self, step_text: str) -> str:
        """Generate explanation for a step (detailed mode)."""
        # Extract explanation from step text if available
        if ":" in step_text:
            parts = step_text.split(":", 1)
            if len(parts) > 1:
                return parts[1].strip()

        return ""

    def _generate_step_troubleshooting(self, step_text: str, command: Optional[str]) -> Dict:
        """Generate step-specific troubleshooting (comprehensive mode)."""
        troubleshooting = {}

        if command:
            if "npm" in command.lower():
                troubleshooting["EACCES permission error"] = "Run with sudo or fix npm permissions"
                troubleshooting["Module not found"] = "Ensure package.json exists and dependencies are correct"
            elif "pip" in command.lower():
                troubleshooting["Permission denied"] = "Use --user flag or virtual environment"
                troubleshooting["Package not found"] = "Check package name spelling and PyPI availability"
            elif "git" in command.lower():
                troubleshooting["Authentication failed"] = "Configure SSH keys or use personal access token"
                troubleshooting["Repository not found"] = "Verify repository URL and access permissions"

        return troubleshooting
