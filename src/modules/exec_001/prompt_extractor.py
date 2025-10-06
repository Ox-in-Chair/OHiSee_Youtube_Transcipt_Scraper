"""
Prompt Extractor - EXEC-001 Component

Extracts prompt templates verbatim from transcripts and code.
Identifies variables, categorizes by use case, and creates reusable templates.
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class PromptExtractor:
    """Extract and categorize prompt templates from content."""

    def __init__(self, callback=None):
        """
        Initialize prompt extractor.

        Args:
            callback: Optional logging callback function
        """
        self.callback = callback or (lambda x: None)
        self.prompt_counter = 0

    def extract_prompts(self, content: str, categorize: bool = True,
                       source_info: Optional[Dict] = None) -> List[Dict]:
        """
        Extract prompt templates from transcript or text content.

        Detection patterns:
        - "Use this prompt:", "Here's the prompt:"
        - Text in quotes after "prompt"
        - Multi-line prompts in code blocks
        - Prompts in backticks

        Args:
            content: Text content to scan
            categorize: Whether to categorize prompts automatically
            source_info: Optional source metadata (video title, timestamp)

        Returns:
            List of prompt dictionaries
        """
        self.callback(f"Extracting prompts from content ({len(content)} chars)")

        prompts = []

        # Pattern 1: Explicit prompt indicators with quotes
        explicit_patterns = [
            r'(?:use this prompt|here\'?s the prompt|prompt is|the prompt):\s*["\']([^"\']+)["\']',
            r'(?:use this prompt|here\'?s the prompt|prompt is|the prompt):\s*"""([^"]+)"""',
            r'(?:use this prompt|here\'?s the prompt|prompt is|the prompt):\s*```([^`]+)```'
        ]

        for pattern in explicit_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                prompt_text = match.group(1).strip()
                if self._is_valid_prompt(prompt_text):
                    prompt_dict = self._create_prompt_dict(
                        prompt_text, categorize, source_info
                    )
                    prompts.append(prompt_dict)

        # Pattern 2: Code blocks that look like prompts
        code_block_pattern = r'```(?:prompt|text)?\n((?:.*\n)*?)```'
        code_blocks = re.finditer(code_block_pattern, content, re.MULTILINE)
        for match in code_blocks:
            block_content = match.group(1).strip()
            # Check if it looks like a prompt (starts with common prompt phrases)
            if self._looks_like_prompt(block_content):
                prompt_dict = self._create_prompt_dict(
                    block_content, categorize, source_info
                )
                prompts.append(prompt_dict)

        # Pattern 3: Multi-line quoted sections that look like prompts
        multiline_quote_pattern = r'["\']([^"\']{100,})["\']'
        quote_matches = re.finditer(multiline_quote_pattern, content, re.DOTALL)
        for match in quote_matches:
            quoted_text = match.group(1).strip()
            if self._looks_like_prompt(quoted_text):
                prompt_dict = self._create_prompt_dict(
                    quoted_text, categorize, source_info
                )
                prompts.append(prompt_dict)

        # Pattern 4: Inline backtick prompts
        backtick_pattern = r'`([^`]{50,})`'
        backtick_matches = re.finditer(backtick_pattern, content)
        for match in backtick_matches:
            backtick_text = match.group(1).strip()
            if self._looks_like_prompt(backtick_text):
                prompt_dict = self._create_prompt_dict(
                    backtick_text, categorize, source_info
                )
                prompts.append(prompt_dict)

        # Deduplicate prompts
        prompts = self._deduplicate_prompts(prompts)

        self.callback(f"Extracted {len(prompts)} unique prompts")

        return prompts

    def identify_variables(self, prompt: str) -> List[Dict]:
        """
        Detect variables/placeholders in prompt template.

        Supported formats:
        - {variable_name}
        - [variable_name]
        - <variable_name>
        - {{variable_name}}
        - ${variable_name}

        Args:
            prompt: Prompt template text

        Returns:
            List of variable dictionaries with name, format, example
        """
        variables = []
        seen_vars = set()

        # Different variable formats
        variable_patterns = [
            (r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', 'curly'),  # {var}
            (r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}', 'double_curly'),  # {{var}}
            (r'\[([a-zA-Z_][a-zA-Z0-9_\s]*)\]', 'square'),  # [var]
            (r'<([a-zA-Z_][a-zA-Z0-9_\s]*)>', 'angle'),  # <var>
            (r'\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}', 'dollar'),  # ${var}
        ]

        for pattern, var_format in variable_patterns:
            matches = re.finditer(pattern, prompt)
            for match in matches:
                var_name = match.group(1).strip()

                # Skip if already found
                if var_name in seen_vars:
                    continue

                seen_vars.add(var_name)

                # Try to infer variable purpose from name
                var_type, description = self._infer_variable_purpose(var_name)

                # Generate example value
                example = self._generate_example_value(var_name, var_type)

                variables.append({
                    'name': var_name,
                    'format': var_format,
                    'type': var_type,
                    'description': description,
                    'example': example,
                    'required': True  # Assume all variables are required
                })

        return variables

    def categorize_prompt(self, prompt: str) -> str:
        """
        Determine prompt category based on content patterns.

        Categories:
        - "system": Role/persona definitions (starts with "You are...")
        - "user": Task instructions (imperative language)
        - "few-shot": Contains examples/demonstrations
        - "chain-of-thought": Step-by-step reasoning
        - "general": Default category

        Args:
            prompt: Prompt text

        Returns:
            Category string
        """
        prompt_lower = prompt.lower()

        # System prompts
        system_indicators = [
            "you are a",
            "you are an",
            "act as",
            "your role is",
            "as a"
        ]
        if any(prompt_lower.startswith(ind) for ind in system_indicators):
            return "system"

        # Few-shot prompts (contain examples)
        # Check for multiple examples (case-insensitive)
        example_count = prompt_lower.count("example")
        if example_count >= 2:
            # Additional check: look for numbered examples or example patterns
            if any(pattern in prompt_lower for pattern in ["example 1", "example:", "for example"]):
                return "few-shot"

        # Chain-of-thought prompts
        cot_indicators = [
            "step by step",
            "let's think",
            "first,",
            "then,",
            "finally,"
        ]
        cot_count = sum(1 for ind in cot_indicators if ind in prompt_lower)
        if cot_count >= 2:
            return "chain-of-thought"

        # User prompts (task-oriented)
        user_indicators = [
            "write",
            "create",
            "generate",
            "analyze",
            "explain",
            "summarize"
        ]
        if any(prompt_lower.startswith(ind) for ind in user_indicators):
            return "user"

        return "general"

    def extract_from_notable_items(self, notable_items: List[Dict]) -> Dict:
        """
        Extract prompts from CORE-001 notable items.

        Args:
            notable_items: List of notable items from CORE-001 summary

        Returns:
            Categorized prompts dictionary
        """
        categorized_prompts = {
            "system": [],
            "user": [],
            "few-shot": [],
            "chain-of-thought": [],
            "general": []
        }

        for item in notable_items:
            # Check if item contains prompt-related content
            if item.get("tag") == "Protocol" or "prompt" in item.get("title", "").lower():
                # Extract from description
                prompts = self.extract_prompts(
                    item.get("description", ""),
                    categorize=True,
                    source_info={
                        "title": item.get("title"),
                        "timestamp": item.get("source_timestamp"),
                        "item_id": item.get("id")
                    }
                )

                for prompt in prompts:
                    category = prompt["category"]
                    categorized_prompts[category].append(prompt)

            # Check code snippets
            code_snippet = item.get("code_snippet")
            if code_snippet:
                prompts = self.extract_prompts(
                    code_snippet,
                    categorize=True,
                    source_info={
                        "title": item.get("title"),
                        "timestamp": item.get("source_timestamp"),
                        "item_id": item.get("id")
                    }
                )

                for prompt in prompts:
                    category = prompt["category"]
                    categorized_prompts[category].append(prompt)

        return categorized_prompts

    def to_markdown(self, prompt: Dict) -> str:
        """
        Convert prompt to markdown format.

        Args:
            prompt: Prompt dictionary

        Returns:
            Formatted markdown string
        """
        md = f"# Prompt: {prompt['title']}\n\n"
        md += f"**ID**: `{prompt['prompt_id']}`\n"
        md += f"**Category**: {prompt['category'].replace('_', ' ').title()}\n"
        md += f"**Use Case**: {prompt['use_case']}\n\n"

        if prompt.get('source_video'):
            md += f"**Source**: {prompt['source_video']}"
            if prompt.get('timestamp'):
                md += f" (@ {prompt['timestamp']})"
            md += "\n\n"

        md += "## Template\n\n"
        md += "```\n"
        md += prompt['template']
        md += "\n```\n\n"

        if prompt['variables']:
            md += "## Variables\n\n"
            for var in prompt['variables']:
                md += f"- `{{{var['name']}}}`: {var['description']}\n"
                md += f"  - Type: {var['type']}\n"
                md += f"  - Example: {var['example']}\n"
            md += "\n"

        if prompt.get('example'):
            md += "## Example Usage\n\n"
            md += "**Filled Template**:\n"
            md += "```\n"
            md += prompt['example']
            md += "\n```\n\n"

        md += f"**Generated**: {prompt['generated_at']}\n"

        return md

    # Helper methods

    def _is_valid_prompt(self, text: str) -> bool:
        """Check if extracted text is a valid prompt."""
        # Must be at least 20 characters
        if len(text) < 20:
            return False

        # Must not be too long (likely not a single prompt)
        if len(text) > 2000:
            return False

        # Should contain some instructional language
        instructional_words = [
            'you', 'are', 'write', 'create', 'analyze', 'explain',
            'generate', 'summarize', 'act', 'role', 'task', 'help'
        ]

        text_lower = text.lower()
        word_count = sum(1 for word in instructional_words if word in text_lower)

        return word_count >= 2

    def _looks_like_prompt(self, text: str) -> bool:
        """Check if text looks like a prompt (heuristic)."""
        # Common prompt starters
        prompt_starters = [
            'you are',
            'act as',
            'write',
            'create',
            'generate',
            'analyze',
            'explain',
            'summarize',
            'your task',
            'your role'
        ]

        text_lower = text.lower().strip()

        # Check if starts with common prompt phrases
        if any(text_lower.startswith(starter) for starter in prompt_starters):
            return True

        # Check if contains prompt-like instructions
        if len(text) > 50 and any(starter in text_lower for starter in prompt_starters):
            return True

        return False

    def _create_prompt_dict(self, prompt_text: str, categorize: bool,
                           source_info: Optional[Dict]) -> Dict:
        """Create structured prompt dictionary."""
        self.prompt_counter += 1
        prompt_id = f"prompt_{self.prompt_counter}"

        # Categorize if requested
        category = self.categorize_prompt(prompt_text) if categorize else "general"

        # Identify variables
        variables = self.identify_variables(prompt_text)

        # Generate title from first few words
        title = self._generate_title(prompt_text)

        # Infer use case
        use_case = self._infer_use_case(prompt_text, category)

        # Generate example if variables exist
        example = self._generate_example(prompt_text, variables) if variables else None

        prompt_dict = {
            'prompt_id': prompt_id,
            'title': title,
            'template': prompt_text,
            'category': category,
            'variables': variables,
            'use_case': use_case,
            'example': example,
            'generated_at': datetime.now().isoformat()
        }

        # Add source information if available
        if source_info:
            prompt_dict['source_video'] = source_info.get('title', 'Unknown')
            prompt_dict['timestamp'] = source_info.get('timestamp', '00:00')
            prompt_dict['source_item_id'] = source_info.get('item_id')

        return prompt_dict

    def _generate_title(self, prompt_text: str) -> str:
        """Generate concise title from prompt."""
        # Take first 5-7 words
        words = prompt_text.split()[:7]
        title = ' '.join(words)

        if len(title) > 60:
            title = title[:60] + "..."

        return title

    def _infer_use_case(self, prompt_text: str, category: str) -> str:
        """Infer use case from prompt content and category."""
        prompt_lower = prompt_text.lower()

        # Category-specific use cases
        if category == "system":
            if "code" in prompt_lower or "programming" in prompt_lower:
                return "Coding assistant role definition"
            elif "write" in prompt_lower or "writer" in prompt_lower:
                return "Writing assistant role definition"
            else:
                return "AI assistant role definition"

        elif category == "user":
            if "summarize" in prompt_lower:
                return "Content summarization task"
            elif "analyze" in prompt_lower:
                return "Data/text analysis task"
            elif "write" in prompt_lower or "create" in prompt_lower:
                return "Content generation task"
            else:
                return "General task instruction"

        elif category == "few-shot":
            return "Few-shot learning examples"

        elif category == "chain-of-thought":
            return "Step-by-step reasoning guidance"

        return "General purpose prompt"

    def _infer_variable_purpose(self, var_name: str) -> Tuple[str, str]:
        """Infer variable type and description from name."""
        var_lower = var_name.lower()

        # Common variable patterns
        if 'topic' in var_lower or 'subject' in var_lower:
            return 'string', 'Topic or subject matter'
        elif 'task' in var_lower:
            return 'string', 'Task description'
        elif 'context' in var_lower or 'background' in var_lower:
            return 'string', 'Background context information'
        elif 'input' in var_lower or 'data' in var_lower:
            return 'string', 'Input data or text'
        elif 'format' in var_lower:
            return 'string', 'Output format specification'
        elif 'count' in var_lower or 'number' in var_lower or 'num' in var_lower:
            return 'integer', 'Numeric value'
        elif 'list' in var_lower or 'items' in var_lower:
            return 'array', 'List of items'
        elif 'url' in var_lower or 'link' in var_lower:
            return 'url', 'Web URL or link'
        else:
            return 'string', f'{var_name.replace("_", " ").title()}'

    def _generate_example_value(self, var_name: str, var_type: str) -> str:
        """Generate example value for variable."""
        var_lower = var_name.lower()

        # Type-specific examples
        if var_type == 'integer':
            return '5'
        elif var_type == 'array':
            return '["item1", "item2", "item3"]'
        elif var_type == 'url':
            return 'https://example.com'

        # Name-specific examples
        if 'topic' in var_lower:
            return 'artificial intelligence'
        elif 'task' in var_lower:
            return 'summarize this article'
        elif 'name' in var_lower:
            return 'John Smith'
        elif 'language' in var_lower:
            return 'Python'
        elif 'format' in var_lower:
            return 'markdown'
        else:
            return f'example_{var_name}'

    def _generate_example(self, template: str, variables: List[Dict]) -> str:
        """Generate filled example from template and variables."""
        example = template

        for var in variables:
            # Create placeholder pattern based on format
            if var['format'] == 'curly':
                placeholder = '{' + var['name'] + '}'
            elif var['format'] == 'double_curly':
                placeholder = '{{' + var['name'] + '}}'
            elif var['format'] == 'square':
                placeholder = '[' + var['name'] + ']'
            elif var['format'] == 'angle':
                placeholder = '<' + var['name'] + '>'
            elif var['format'] == 'dollar':
                placeholder = '${' + var['name'] + '}'
            else:
                placeholder = var['name']

            # Replace with example value
            example = example.replace(placeholder, var['example'])

        return example

    def _deduplicate_prompts(self, prompts: List[Dict]) -> List[Dict]:
        """Remove duplicate prompts based on template similarity."""
        unique_prompts = []
        seen_templates = set()

        for prompt in prompts:
            template_normalized = prompt['template'].strip().lower()

            # Skip if we've seen very similar template
            if template_normalized not in seen_templates:
                unique_prompts.append(prompt)
                seen_templates.add(template_normalized)

        return unique_prompts
