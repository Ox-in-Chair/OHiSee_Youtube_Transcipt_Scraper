"""
CLI Command Parser - EXEC-001 Component

Extracts CLI commands with context, parses flags and arguments.
Handles platform-specific commands and generates comprehensive documentation.
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class CLIParser:
    """Parse and document CLI commands from content."""

    def __init__(self, callback=None):
        """
        Initialize CLI parser.

        Args:
            callback: Optional logging callback function
        """
        self.callback = callback or (lambda x: None)
        self.command_counter = 0

        # Common CLI tools and their platforms
        self.tool_platforms = {
            'npm': 'cross-platform',
            'pip': 'cross-platform',
            'python': 'cross-platform',
            'node': 'cross-platform',
            'git': 'cross-platform',
            'docker': 'cross-platform',
            'powershell': 'windows',
            'cmd': 'windows',
            'bash': 'linux/mac',
            'zsh': 'linux/mac',
            'sh': 'linux/mac',
            'apt-get': 'linux',
            'apt': 'linux',
            'yum': 'linux',
            'brew': 'mac',
            'choco': 'windows'
        }

    def parse_commands(self, text: str, platform: str = "auto") -> List[Dict]:
        """
        Extract CLI commands with context.

        Detection patterns:
        - Lines starting with $, >, #
        - Code blocks with bash/sh/powershell
        - Command patterns (npm, git, python, docker)

        Args:
            text: Content to scan for commands
            platform: "auto", "windows", "linux", "mac", "cross-platform"

        Returns:
            List of command dictionaries
        """
        self.callback(f"Parsing CLI commands from content ({len(text)} chars)")

        commands = []

        # Pattern 1: Code blocks with language hints
        code_block_pattern = r'```(bash|sh|shell|powershell|cmd|console|terminal)\n((?:.*\n)*?)```'
        code_blocks = re.finditer(code_block_pattern, text, re.MULTILINE)

        for match in code_blocks:
            lang = match.group(1)
            block_content = match.group(2).strip()

            # Extract individual commands from block
            block_commands = self._extract_commands_from_block(block_content, lang)
            commands.extend(block_commands)

        # Pattern 2: Inline code with command indicators
        inline_patterns = [
            r'(?:run|execute|type|enter):\s*`([^`]+)`',
            r'(?:\$|>|#)\s*([^\n]+)',  # Command prompt indicators
            r'`([a-zA-Z0-9_-]+(?:\s+[a-zA-Z0-9_-]+)*(?:\s+--?[a-zA-Z0-9_-]+)*)`'  # Backtick commands
        ]

        for pattern in inline_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                command_text = match.group(1).strip()

                # Check if it's actually a command
                if self._is_command(command_text):
                    cmd_dict = self._parse_single_command(command_text, platform)
                    if cmd_dict:
                        commands.append(cmd_dict)

        # Pattern 3: Common tool invocations without special markers
        tool_pattern = r'\b(npm|pip|git|docker|python|node|cargo|go|rustc)\s+[a-z]+(?:\s+[^\n]+)?'
        tool_matches = re.finditer(tool_pattern, text)

        for match in tool_matches:
            command_text = match.group(0).strip()
            # Avoid duplicates from previous patterns
            if not any(cmd['command'] == command_text for cmd in commands):
                cmd_dict = self._parse_single_command(command_text, platform)
                if cmd_dict:
                    commands.append(cmd_dict)

        # Deduplicate commands
        commands = self._deduplicate_commands(commands)

        # Apply platform filter if not auto
        if platform != "auto":
            commands = [cmd for cmd in commands if cmd['platform'] == platform or
                       cmd['platform'] == 'cross-platform']

        self.callback(f"Extracted {len(commands)} CLI commands")

        return commands

    def parse_flags(self, command: str) -> Dict[str, str]:
        """
        Parse command flags and return descriptions.

        Extracts:
        - Long flags: --flag-name
        - Short flags: -f
        - Flag values: --flag=value or --flag value

        Args:
            command: Full command string

        Returns:
            Dictionary of {flag: description}
        """
        flags = {}

        # Pattern for long flags
        long_flag_pattern = r'--([a-zA-Z0-9_-]+)(?:=([^\s]+)|(?:\s+([^\s-][^\s]*))?)'
        long_matches = re.finditer(long_flag_pattern, command)

        for match in long_matches:
            flag_name = match.group(1)
            flag_value = match.group(2) or match.group(3)

            # Generate description based on flag name and value
            description = self._generate_flag_description(flag_name, flag_value)
            flags[f'--{flag_name}'] = description

        # Pattern for short flags
        short_flag_pattern = r'\s-([a-zA-Z])(?:\s+([^\s-][^\s]*))?'
        short_matches = re.finditer(short_flag_pattern, command)

        for match in short_matches:
            flag_name = match.group(1)
            flag_value = match.group(2)

            description = self._generate_flag_description(flag_name, flag_value, short=True)
            flags[f'-{flag_name}'] = description

        return flags

    def extract_prerequisites(self, command: str) -> List[str]:
        """
        Detect what must be installed to run command.

        Args:
            command: Command string

        Returns:
            List of prerequisite descriptions
        """
        prerequisites = []

        # Extract base tool
        tool = command.split()[0] if command else ""

        # Tool-specific prerequisites
        tool_prereqs = {
            'npm': ['Node.js and npm package manager'],
            'npx': ['Node.js and npm package manager'],
            'pip': ['Python and pip package manager'],
            'python': ['Python runtime'],
            'node': ['Node.js runtime'],
            'git': ['Git version control system'],
            'docker': ['Docker engine'],
            'cargo': ['Rust toolchain'],
            'go': ['Go programming language'],
            'mvn': ['Apache Maven'],
            'gradle': ['Gradle build tool'],
            'make': ['Make build system'],
            'kubectl': ['Kubernetes command-line tool'],
            'aws': ['AWS CLI'],
            'gcloud': ['Google Cloud SDK'],
            'az': ['Azure CLI']
        }

        if tool in tool_prereqs:
            prerequisites.extend(tool_prereqs[tool])

        # Check for global package installations
        if 'install -g' in command or 'install --global' in command:
            prerequisites.append('Administrator/sudo privileges for global installation')

        # Check for docker-compose
        if 'docker-compose' in command:
            prerequisites.append('Docker Compose')

        # Check for virtual environment commands
        if 'venv' in command or 'virtualenv' in command:
            prerequisites.append('Python virtual environment support')

        return prerequisites

    def extract_from_notable_items(self, notable_items: List[Dict]) -> Dict:
        """
        Extract CLI commands from CORE-001 notable items.

        Args:
            notable_items: List of notable items from CORE-001 summary

        Returns:
            Categorized commands dictionary by platform
        """
        categorized_commands = {
            'windows': [],
            'linux': [],
            'mac': [],
            'cross-platform': []
        }

        for item in notable_items:
            # Focus on Command-tagged items
            if item.get("tag") == "Command":
                # Extract from description
                commands = self.parse_commands(item.get("description", ""))

                for cmd in commands:
                    # Add source information
                    cmd['source_title'] = item.get('title')
                    cmd['source_timestamp'] = item.get('source_timestamp')
                    cmd['source_item_id'] = item.get('id')

                    platform = cmd['platform']
                    categorized_commands[platform].append(cmd)

            # Check code snippets for commands
            code_snippet = item.get("code_snippet")
            if code_snippet:
                commands = self.parse_commands(code_snippet)

                for cmd in commands:
                    cmd['source_title'] = item.get('title')
                    cmd['source_timestamp'] = item.get('source_timestamp')
                    cmd['source_item_id'] = item.get('id')

                    platform = cmd['platform']
                    categorized_commands[platform].append(cmd)

        return categorized_commands

    def to_markdown(self, command_dict: Dict) -> str:
        """
        Convert command dictionary to markdown format.

        Args:
            command_dict: Command dictionary

        Returns:
            Formatted markdown string
        """
        md = f"# Command: {command_dict['purpose']}\n\n"
        md += f"**ID**: `{command_dict['command_id']}`\n"
        md += f"**Platform**: {command_dict['platform'].replace('_', ' ').title()}\n\n"

        if command_dict.get('prerequisites'):
            md += "## Prerequisites\n\n"
            for prereq in command_dict['prerequisites']:
                md += f"- {prereq}\n"
            md += "\n"

        md += "## Command\n\n"
        md += "```bash\n"
        md += command_dict['command']
        md += "\n```\n\n"

        md += f"**Description**: {command_dict['description']}\n\n"

        if command_dict.get('flags'):
            md += "## Flags Explained\n\n"
            for flag, desc in command_dict['flags'].items():
                md += f"- `{flag}`: {desc}\n"
            md += "\n"

        if command_dict.get('example_output'):
            md += "## Expected Output\n\n"
            md += "```\n"
            md += command_dict['example_output']
            md += "\n```\n\n"

        if command_dict.get('common_errors'):
            md += "## Common Errors\n\n"
            for error, solution in command_dict['common_errors'].items():
                md += f"**Error**: `{error}`\n"
                md += f"**Solution**: {solution}\n\n"

        md += f"**Generated**: {command_dict['generated_at']}\n"

        return md

    # Helper methods

    def _extract_commands_from_block(self, block_content: str, lang: str) -> List[Dict]:
        """Extract individual commands from code block."""
        commands = []

        # Split by lines
        lines = block_content.split('\n')

        for line in lines:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Remove command prompt indicators
            line = re.sub(r'^[\$>#]\s*', '', line)

            if self._is_command(line):
                cmd_dict = self._parse_single_command(line, self._detect_platform(lang))
                if cmd_dict:
                    commands.append(cmd_dict)

        return commands

    def _is_command(self, text: str) -> bool:
        """Check if text looks like a CLI command."""
        # Must have at least one word
        if not text or len(text.split()) == 0:
            return False

        # Get first word (the command)
        first_word = text.split()[0]

        # Check if first word is a known command tool
        known_tools = [
            'npm', 'npx', 'pip', 'python', 'python3', 'node', 'git',
            'docker', 'cargo', 'go', 'mvn', 'gradle', 'make', 'cd',
            'ls', 'pwd', 'mkdir', 'rm', 'cp', 'mv', 'cat', 'echo',
            'curl', 'wget', 'kubectl', 'aws', 'gcloud', 'az', 'terraform'
        ]

        if first_word.lower() in known_tools:
            return True

        # Check for executable patterns (./, .bat, .sh, .exe)
        if first_word.startswith('./') or first_word.endswith(('.sh', '.bat', '.exe', '.py')):
            return True

        return False

    def _parse_single_command(self, command_text: str, platform: str = "auto") -> Optional[Dict]:
        """Parse a single command into structured format."""
        self.command_counter += 1
        command_id = f"cmd_{self.command_counter}"

        # Clean command
        command_text = command_text.strip()

        # Detect platform if auto
        if platform == "auto":
            platform = self._detect_platform_from_command(command_text)

        # Parse flags
        flags = self.parse_flags(command_text)

        # Extract prerequisites
        prerequisites = self.extract_prerequisites(command_text)

        # Generate description
        description = self._generate_command_description(command_text)

        # Generate purpose
        purpose = self._generate_purpose(command_text)

        # Generate example output
        example_output = self._generate_example_output(command_text)

        # Generate common errors
        common_errors = self._generate_common_errors(command_text)

        return {
            'command_id': command_id,
            'command': command_text,
            'platform': platform,
            'purpose': purpose,
            'description': description,
            'flags': flags,
            'prerequisites': prerequisites,
            'example_output': example_output,
            'common_errors': common_errors,
            'generated_at': datetime.now().isoformat()
        }

    def _detect_platform(self, lang_hint: str) -> str:
        """Detect platform from language hint."""
        lang_lower = lang_hint.lower()

        if lang_lower in ['powershell', 'cmd']:
            return 'windows'
        elif lang_lower in ['bash', 'sh', 'zsh']:
            return 'linux'  # Could be linux or mac
        else:
            return 'cross-platform'

    def _detect_platform_from_command(self, command: str) -> str:
        """Detect platform from command content."""
        first_word = command.split()[0].lower()

        if first_word in self.tool_platforms:
            return self.tool_platforms[first_word]

        # Check for Windows-specific patterns
        if any(x in command.lower() for x in ['.exe', '.bat', 'powershell', 'cmd']):
            return 'windows'

        # Check for Unix-specific patterns
        if any(x in command.lower() for x in ['.sh', 'sudo', 'chmod', 'chown']):
            return 'linux'

        return 'cross-platform'

    def _generate_flag_description(self, flag_name: str, flag_value: Optional[str],
                                   short: bool = False) -> str:
        """Generate description for a flag."""
        # Common flag meanings
        flag_meanings = {
            'help': 'Display help information',
            'version': 'Show version number',
            'verbose': 'Enable verbose output',
            'v': 'Enable verbose output',
            'quiet': 'Suppress output',
            'q': 'Quiet mode',
            'force': 'Force operation without confirmation',
            'f': 'Force operation',
            'recursive': 'Recursive operation',
            'r': 'Recursive operation',
            'all': 'Apply to all items',
            'a': 'Apply to all',
            'output': f'Output to: {flag_value}' if flag_value else 'Specify output destination',
            'o': f'Output to: {flag_value}' if flag_value else 'Output file',
            'config': f'Use config: {flag_value}' if flag_value else 'Specify configuration file',
            'port': f'Use port: {flag_value}' if flag_value else 'Specify port number',
            'p': f'Port: {flag_value}' if flag_value else 'Port number',
            'save': 'Save to package.json' if 'npm' in str(flag_value) else 'Save changes',
            'save-dev': 'Save as dev dependency',
            'global': 'Install globally',
            'g': 'Global installation',
            'dry-run': 'Simulate without making changes',
            'no-cache': 'Disable caching',
            'watch': 'Watch for changes',
            'w': 'Watch mode'
        }

        flag_key = flag_name.lower().replace('-', '')

        if flag_key in flag_meanings:
            return flag_meanings[flag_key]

        # Generate from flag name
        readable_name = flag_name.replace('-', ' ').replace('_', ' ').title()

        if flag_value:
            return f'{readable_name}: {flag_value}'
        else:
            return f'Enable {readable_name.lower()}'

    def _generate_command_description(self, command: str) -> str:
        """Generate human-readable description of command."""
        parts = command.split()
        if len(parts) == 0:
            return "Execute command"

        tool = parts[0]
        action = parts[1] if len(parts) > 1 else ""

        # Tool-specific descriptions
        if tool == 'npm':
            if action == 'install':
                return f"Install Node.js package: {' '.join(parts[2:]) if len(parts) > 2 else 'dependencies'}"
            elif action == 'run':
                return f"Run npm script: {parts[2] if len(parts) > 2 else 'script'}"
            elif action == 'start':
                return "Start the application"
            elif action == 'test':
                return "Run tests"
            elif action == 'build':
                return "Build the project"

        elif tool == 'pip':
            if action == 'install':
                return f"Install Python package: {' '.join(parts[2:]) if len(parts) > 2 else 'package'}"
            elif action == 'freeze':
                return "List installed packages"

        elif tool == 'git':
            if action == 'clone':
                return f"Clone repository: {parts[2] if len(parts) > 2 else 'repository'}"
            elif action == 'commit':
                return "Commit changes"
            elif action == 'push':
                return "Push commits to remote"
            elif action == 'pull':
                return "Pull changes from remote"

        elif tool == 'docker':
            if action == 'build':
                return "Build Docker image"
            elif action == 'run':
                return "Run Docker container"
            elif action == 'pull':
                return "Pull Docker image"

        return f"Execute: {command}"

    def _generate_purpose(self, command: str) -> str:
        """Generate concise purpose statement."""
        description = self._generate_command_description(command)
        # Shorten to first part before colon if present
        return description.split(':')[0]

    def _generate_example_output(self, command: str) -> str:
        """Generate example output for command."""
        parts = command.split()
        tool = parts[0] if parts else ""

        if tool == 'npm' and 'install' in command:
            return "added 142 packages, and audited 143 packages in 8s\nfound 0 vulnerabilities"
        elif tool == 'pip' and 'install' in command:
            return "Successfully installed package-name-1.0.0"
        elif tool == 'git' and 'clone' in command:
            return "Cloning into 'repository'...\nremote: Enumerating objects: 100, done."
        elif '--version' in command or '-v' in command:
            return f"{tool} version 1.0.0"
        elif '--help' in command or '-h' in command:
            return f"Usage: {tool} [options] [arguments]"

        return "Command executed successfully"

    def _generate_common_errors(self, command: str) -> Dict[str, str]:
        """Generate common errors and solutions."""
        errors = {}
        parts = command.split()
        tool = parts[0] if parts else ""

        if tool == 'npm':
            errors["EACCES permission denied"] = "Run with sudo or fix npm permissions: npm config set prefix ~/.npm-global"
            errors["Cannot find module"] = "Run npm install to install dependencies"

        elif tool == 'pip':
            errors["Permission denied"] = "Use --user flag or create virtual environment"
            errors["No matching distribution found"] = "Check package name and Python version compatibility"

        elif tool == 'git':
            errors["Permission denied (publickey)"] = "Set up SSH keys or use HTTPS with credentials"
            errors["fatal: not a git repository"] = "Initialize repository with: git init"

        elif tool == 'docker':
            errors["Cannot connect to Docker daemon"] = "Ensure Docker service is running"
            errors["Permission denied"] = "Add user to docker group or use sudo"

        # Universal errors
        if not errors:
            errors["Command not found"] = f"Install {tool} and ensure it's in your PATH"

        return errors

    def _deduplicate_commands(self, commands: List[Dict]) -> List[Dict]:
        """Remove duplicate commands."""
        unique_commands = []
        seen_commands = set()

        for cmd in commands:
            command_normalized = cmd['command'].strip().lower()

            if command_normalized not in seen_commands:
                unique_commands.append(cmd)
                seen_commands.add(command_normalized)

        return unique_commands
