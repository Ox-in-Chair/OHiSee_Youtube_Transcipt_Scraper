"""
Checklist Creator - EXEC-001 Component

Generates implementation checklists with progress tracking.
Supports multiple output formats (Markdown, JSON, HTML).
"""

import json
from typing import Dict, List, Optional
from datetime import datetime


class ChecklistCreator:
    """Create implementation checklists from steps and playbooks."""

    def __init__(self, callback=None):
        """
        Initialize checklist creator.

        Args:
            callback: Optional logging callback function
        """
        self.callback = callback or (lambda x: None)

    def create_checklist(self, steps: List[Dict], format: str = "markdown",
                        metadata: Optional[Dict] = None) -> Dict:
        """
        Generate implementation checklist.

        Formats:
        - markdown: GitHub-style checkboxes
        - json: Programmatic access with completion tracking
        - html: Interactive web checklist

        Args:
            steps: List of step dictionaries (from playbook or manual)
            format: Output format ("markdown", "json", "html")
            metadata: Optional metadata (title, objective, etc.)

        Returns:
            Checklist dictionary with formatted output
        """
        self.callback(f"Creating {format} checklist with {len(steps)} items")

        # Build checklist items
        items = self._build_checklist_items(steps, metadata)

        # Calculate total time
        total_time = self.estimate_completion_time(steps)

        # Generate formatted output based on format
        if format == "markdown":
            formatted_output = self._to_markdown(items, metadata, total_time)
        elif format == "json":
            formatted_output = self._to_json(items, metadata, total_time)
        elif format == "html":
            formatted_output = self._to_html(items, metadata, total_time)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'markdown', 'json', or 'html'")

        # Build complete checklist dictionary
        checklist = {
            'items': items,
            'total_items': len(items),
            'completed_items': sum(1 for item in items if item.get('completed', False)),
            'estimated_time': total_time,
            'format': format,
            'formatted_output': formatted_output,
            'metadata': metadata or {},
            'generated_at': datetime.now().isoformat()
        }

        return checklist

    def estimate_completion_time(self, steps: List[Dict]) -> str:
        """
        Calculate total time from individual step times.

        Args:
            steps: List of step dictionaries

        Returns:
            Formatted time estimate string
        """
        total_minutes = 0

        for step in steps:
            # Try to extract time from step
            time_str = step.get('time', step.get('estimated_time', ''))

            if time_str:
                minutes = self._parse_time_to_minutes(time_str)
                total_minutes += minutes
            else:
                # Default estimate per step
                total_minutes += 5

        # Add 20% buffer for troubleshooting
        total_minutes = int(total_minutes * 1.2)

        # Format output
        if total_minutes < 60:
            return f"{total_minutes} minutes"
        elif total_minutes < 120:
            return f"{total_minutes // 60} hour {total_minutes % 60} minutes"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            if minutes > 0:
                return f"{hours} hours {minutes} minutes"
            else:
                return f"{hours} hours"

    def create_from_playbook(self, playbook: Dict, format: str = "markdown") -> Dict:
        """
        Create checklist from playbook structure.

        Args:
            playbook: Playbook dictionary (from PlaybookGenerator)
            format: Output format

        Returns:
            Checklist dictionary
        """
        # Extract steps from playbook
        steps = playbook.get('steps', [])

        # Build enhanced metadata
        metadata = {
            'title': playbook.get('title', 'Implementation Checklist'),
            'objective': playbook.get('objective', ''),
            'complexity': playbook.get('complexity', 'Unknown'),
            'readiness': playbook.get('readiness', 'READY'),
            'playbook_id': playbook.get('playbook_id')
        }

        # Add prerequisites as first checklist section
        prerequisites = playbook.get('prerequisites', [])
        if prerequisites:
            prereq_steps = [
                {
                    'section': 'Prerequisites',
                    'action': prereq['description'],
                    'type': 'prerequisite',
                    'command': prereq.get('command'),
                    'mandatory': prereq.get('mandatory', True)
                }
                for prereq in prerequisites
            ]
            steps = prereq_steps + steps

        # Add verification steps at the end
        verification = playbook.get('verification', [])
        if verification:
            verify_steps = [
                {
                    'section': 'Verification',
                    'action': verify['step'],
                    'type': 'verification',
                    'expected': verify.get('expected')
                }
                for verify in verification
            ]
            steps = steps + verify_steps

        return self.create_checklist(steps, format, metadata)

    def update_progress(self, checklist: Dict, completed_indices: List[int]) -> Dict:
        """
        Update checklist with completed items.

        Args:
            checklist: Existing checklist dictionary
            completed_indices: List of item indices that are completed

        Returns:
            Updated checklist dictionary
        """
        items = checklist['items']

        for idx in completed_indices:
            if 0 <= idx < len(items):
                items[idx]['completed'] = True

        # Recalculate completed count
        checklist['completed_items'] = sum(1 for item in items if item.get('completed', False))

        # Update progress percentage
        if checklist['total_items'] > 0:
            checklist['progress_percentage'] = int(
                (checklist['completed_items'] / checklist['total_items']) * 100
            )

        # Regenerate formatted output with new completion status
        format_type = checklist['format']
        metadata = checklist.get('metadata', {})
        total_time = checklist['estimated_time']

        if format_type == "markdown":
            checklist['formatted_output'] = self._to_markdown(items, metadata, total_time)
        elif format_type == "json":
            checklist['formatted_output'] = self._to_json(items, metadata, total_time)
        elif format_type == "html":
            checklist['formatted_output'] = self._to_html(items, metadata, total_time)

        checklist['last_updated'] = datetime.now().isoformat()

        return checklist

    # Helper methods

    def _build_checklist_items(self, steps: List[Dict], metadata: Optional[Dict]) -> List[Dict]:
        """Build structured checklist items from steps."""
        items = []

        for idx, step in enumerate(steps):
            # Handle different step formats
            if isinstance(step, dict):
                action = step.get('action', step.get('description', step.get('step', 'Unknown step')))
                section = step.get('section', 'Implementation')
                item_type = step.get('type', 'step')
                command = step.get('command')
                expected = step.get('expected_output', step.get('expected'))
            else:
                # Handle string steps
                action = str(step)
                section = 'Implementation'
                item_type = 'step'
                command = None
                expected = None

            items.append({
                'index': idx,
                'section': section,
                'action': action,
                'type': item_type,
                'command': command,
                'expected': expected,
                'completed': False
            })

        return items

    def _parse_time_to_minutes(self, time_str: str) -> int:
        """Parse time string to minutes."""
        time_str = time_str.lower().strip()

        # Extract numbers
        numbers = []
        current_num = ''
        for char in time_str:
            if char.isdigit():
                current_num += char
            elif current_num:
                numbers.append(int(current_num))
                current_num = ''
        if current_num:
            numbers.append(int(current_num))

        if not numbers:
            return 5  # Default

        # Parse based on units
        total_minutes = 0

        if 'hour' in time_str or 'hr' in time_str:
            total_minutes += numbers[0] * 60
            if len(numbers) > 1 and ('minute' in time_str or 'min' in time_str):
                total_minutes += numbers[1]
        elif 'minute' in time_str or 'min' in time_str:
            total_minutes += numbers[0]
        elif 'second' in time_str or 'sec' in time_str:
            total_minutes += max(1, numbers[0] // 60)
        else:
            # Assume minutes if no unit
            total_minutes += numbers[0]

        return total_minutes

    def _to_markdown(self, items: List[Dict], metadata: Optional[Dict],
                    total_time: str) -> str:
        """Generate markdown checklist."""
        md = ""

        # Add title and metadata if provided
        if metadata:
            title = metadata.get('title', 'Implementation Checklist')
            md += f"# {title}\n\n"

            if metadata.get('objective'):
                md += f"**Objective**: {metadata['objective']}\n\n"

            md += f"**Estimated Time**: {total_time}\n"

            if metadata.get('complexity'):
                md += f"**Complexity**: {metadata['complexity']}\n"

            if metadata.get('readiness'):
                md += f"**Readiness**: {metadata['readiness']}\n"

            md += "\n"

        # Group items by section
        current_section = None

        for item in items:
            section = item.get('section', 'Tasks')

            # Add section header if changed
            if section != current_section:
                md += f"## {section}\n\n"
                current_section = section

            # Add checkbox
            checkbox = "[x]" if item.get('completed', False) else "[ ]"
            md += f"- {checkbox} {item['action']}\n"

            # Add command if present
            if item.get('command'):
                md += f"  ```bash\n"
                md += f"  {item['command']}\n"
                md += f"  ```\n"

            # Add expected output if present
            if item.get('expected'):
                md += f"  - *Expected*: {item['expected']}\n"

        return md

    def _to_json(self, items: List[Dict], metadata: Optional[Dict],
                total_time: str) -> str:
        """Generate JSON checklist."""
        checklist_data = {
            'metadata': metadata or {},
            'estimated_time': total_time,
            'items': items,
            'summary': {
                'total_items': len(items),
                'completed_items': sum(1 for item in items if item.get('completed', False)),
                'progress_percentage': int(
                    (sum(1 for item in items if item.get('completed', False)) / len(items) * 100)
                    if items else 0
                )
            },
            'generated_at': datetime.now().isoformat()
        }

        return json.dumps(checklist_data, indent=2)

    def _to_html(self, items: List[Dict], metadata: Optional[Dict],
                total_time: str) -> str:
        """Generate interactive HTML checklist."""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Implementation Checklist</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-top: 0;
        }
        .metadata {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 25px;
        }
        .metadata p {
            margin: 5px 0;
            color: #666;
        }
        .section {
            margin-bottom: 30px;
        }
        .section h2 {
            color: #555;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }
        .checklist-item {
            padding: 12px;
            margin: 8px 0;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            background: #fafafa;
            transition: background 0.2s;
        }
        .checklist-item:hover {
            background: #f0f0f0;
        }
        .checklist-item.completed {
            background: #e8f5e9;
            border-color: #4caf50;
        }
        .checklist-item input[type="checkbox"] {
            margin-right: 10px;
            transform: scale(1.2);
        }
        .checklist-item label {
            cursor: pointer;
            flex: 1;
        }
        .command {
            background: #263238;
            color: #aed581;
            padding: 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            margin-top: 8px;
            overflow-x: auto;
        }
        .expected {
            color: #666;
            font-style: italic;
            margin-top: 6px;
            font-size: 14px;
        }
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4caf50, #8bc34a);
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
"""

        # Add metadata
        if metadata:
            title = metadata.get('title', 'Implementation Checklist')
            html += f"        <h1>{title}</h1>\n"

            html += "        <div class='metadata'>\n"
            if metadata.get('objective'):
                html += f"            <p><strong>Objective:</strong> {metadata['objective']}</p>\n"
            html += f"            <p><strong>Estimated Time:</strong> {total_time}</p>\n"
            if metadata.get('complexity'):
                html += f"            <p><strong>Complexity:</strong> {metadata['complexity']}</p>\n"
            if metadata.get('readiness'):
                html += f"            <p><strong>Readiness:</strong> {metadata['readiness']}</p>\n"
            html += "        </div>\n"

        # Add progress bar
        completed_count = sum(1 for item in items if item.get('completed', False))
        total_count = len(items)
        progress_pct = int((completed_count / total_count * 100) if total_count > 0 else 0)

        html += "        <div class='progress-bar'>\n"
        html += f"            <div class='progress-fill' id='progress' style='width: {progress_pct}%'>\n"
        html += f"                {progress_pct}% Complete\n"
        html += "            </div>\n"
        html += "        </div>\n"

        # Group items by section
        current_section = None

        for item in items:
            section = item.get('section', 'Tasks')

            if section != current_section:
                if current_section is not None:
                    html += "        </div>\n"  # Close previous section
                html += f"        <div class='section'>\n"
                html += f"            <h2>{section}</h2>\n"
                current_section = section

            # Add checklist item
            item_id = f"item_{item['index']}"
            completed_class = " completed" if item.get('completed', False) else ""
            checked = " checked" if item.get('completed', False) else ""

            html += f"            <div class='checklist-item{completed_class}' id='{item_id}'>\n"
            html += f"                <input type='checkbox' id='check_{item_id}' onchange='toggleItem(this)'{checked}>\n"
            html += f"                <label for='check_{item_id}'>{item['action']}</label>\n"

            if item.get('command'):
                html += f"                <div class='command'>{item['command']}</div>\n"

            if item.get('expected'):
                html += f"                <div class='expected'>Expected: {item['expected']}</div>\n"

            html += "            </div>\n"

        # Close last section
        if current_section is not None:
            html += "        </div>\n"

        # Add JavaScript for interactivity
        html += """    </div>

    <script>
        function toggleItem(checkbox) {
            const item = checkbox.parentElement;
            if (checkbox.checked) {
                item.classList.add('completed');
            } else {
                item.classList.remove('completed');
            }
            updateProgress();
        }

        function updateProgress() {
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            const completed = Array.from(checkboxes).filter(cb => cb.checked).length;
            const total = checkboxes.length;
            const percentage = Math.round((completed / total) * 100);

            const progressFill = document.getElementById('progress');
            progressFill.style.width = percentage + '%';
            progressFill.textContent = percentage + '% Complete';
        }
    </script>
</body>
</html>
"""

        return html
