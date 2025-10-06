"""
Output Assembler - INTEGRATE-001 Component

Merges outputs from all v2.0 modules into unified deliverables:
- Complete markdown reports
- Structured JSON data
- HTML dashboards
"""

from typing import Dict, List
from datetime import datetime
import json


class OutputAssembler:
    """
    Assembles outputs from all modules into cohesive deliverables.

    Creates:
    - Unified markdown report with all insights, diagrams, playbooks
    - Structured JSON for programmatic access
    - HTML dashboard for browser viewing
    """

    def __init__(self, callback=None):
        """Initialize output assembler."""
        self.callback = callback or (lambda x: None)

    def assemble_complete_report(self, workflow_results: Dict) -> Dict:
        """
        Assemble complete intelligence report from all module outputs.

        Args:
            workflow_results: Complete workflow execution results

        Returns:
            Dict with assembled outputs in multiple formats
        """
        self.callback("Assembling complete intelligence report...")

        assembled = {
            "markdown": self._generate_markdown_report(workflow_results),
            "json": self._generate_json_export(workflow_results),
            "html": self._generate_html_dashboard(workflow_results),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "workflow_id": workflow_results.get("workflow_id"),
                "workflow_type": workflow_results.get("workflow_type"),
                "modules_included": workflow_results.get("completed_modules", [])
            }
        }

        self.callback(f"✓ Report assembled ({len(assembled['markdown'])} chars)")
        return assembled

    def _generate_markdown_report(self, results: Dict) -> str:
        """Generate comprehensive markdown report."""
        md = []

        # Header
        md.append(f"# YouTube Video Intelligence Report\n")
        md.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        md.append(f"**Workflow**: {results.get('workflow_type', 'standard').upper()}\n")
        md.append(f"**Video**: {results.get('metadata', {}).get('video_title', 'Unknown')}\n")
        md.append(f"**URL**: {results.get('metadata', {}).get('video_url', '')}\n")
        md.append("\n---\n\n")

        # Executive Summary
        md.append("## Executive Summary\n\n")
        md.append(self._create_executive_summary(results))
        md.append("\n")

        # CORE-001 Insights
        if "CORE-001" in results.get("module_outputs", {}):
            md.append("## Key Insights (CORE-001)\n\n")
            md.append(self._format_core_insights(results["module_outputs"]["CORE-001"]))
            md.append("\n")

        # INTEL-001 ROI Analysis
        if "INTEL-001" in results.get("module_outputs", {}):
            md.append("## ROI & Intelligence Analysis (INTEL-001)\n\n")
            md.append(self._format_intel_analysis(results["module_outputs"]["INTEL-001"]))
            md.append("\n")

        # VISUAL-001 Diagrams
        if "VISUAL-001" in results.get("module_outputs", {}):
            md.append("## Visual Diagrams (VISUAL-001)\n\n")
            md.append(self._format_diagrams(results["module_outputs"]["VISUAL-001"]))
            md.append("\n")

        # EXEC-001 Playbook
        if "EXEC-001" in results.get("module_outputs", {}):
            md.append("## Implementation Playbook (EXEC-001)\n\n")
            md.append(self._format_playbook(results["module_outputs"]["EXEC-001"]))
            md.append("\n")

        # KNOWLEDGE-001 Storage
        if "KNOWLEDGE-001" in results.get("module_outputs", {}):
            md.append("## Knowledge Base (KNOWLEDGE-001)\n\n")
            md.append(self._format_knowledge_stats(results["module_outputs"]["KNOWLEDGE-001"]))
            md.append("\n")

        # Workflow Metadata
        md.append("---\n\n")
        md.append("## Workflow Metadata\n\n")
        md.append(self._format_workflow_metadata(results))

        return "".join(md)

    def _create_executive_summary(self, results: Dict) -> str:
        """Create executive summary section."""
        summary = []

        # Quick stats
        modules_completed = len(results.get("completed_modules", []))
        modules_failed = len(results.get("failed_modules", []))

        summary.append(f"**Status**: {results.get('status', 'unknown').upper()}\n")
        summary.append(f"**Modules Completed**: {modules_completed}/6\n")

        if modules_failed > 0:
            summary.append(f"**Modules Failed**: {modules_failed}\n")

        # Insights count
        if "CORE-001" in results.get("module_outputs", {}):
            insights_count = results["module_outputs"]["CORE-001"].get("insights_count", 0)
            summary.append(f"**Insights Extracted**: {insights_count}\n")

        # ROI highlights
        if "INTEL-001" in results.get("module_outputs", {}):
            quick_wins = results["module_outputs"]["INTEL-001"].get("quick_wins", [])
            if quick_wins:
                summary.append(f"**Quick Wins Identified**: {len(quick_wins)}\n")

        return "".join(summary)

    def _format_core_insights(self, core_output: Dict) -> str:
        """Format CORE-001 insights."""
        summary = core_output.get("summary", {})
        insights = summary.get("insights", [])

        md = []
        for i, insight in enumerate(insights[:20], 1):  # Top 20 insights
            category = insight.get("category", "General")
            content = insight.get("insight", "")
            timestamp = insight.get("timestamp", "")
            confidence = insight.get("confidence", 0.5)

            md.append(f"### {i}. {category}\n\n")
            md.append(f"**Insight**: {content}\n\n")
            if timestamp:
                md.append(f"**Timestamp**: {timestamp}\n\n")
            md.append(f"**Confidence**: {confidence:.0%}\n\n")

        if len(insights) > 20:
            md.append(f"\n*... and {len(insights) - 20} more insights*\n")

        return "".join(md)

    def _format_intel_analysis(self, intel_output: Dict) -> str:
        """Format INTEL-001 analysis."""
        md = []

        # Quick wins
        quick_wins = intel_output.get("quick_wins", [])
        if quick_wins:
            md.append("### 🎯 Quick Wins\n\n")
            for win in quick_wins[:5]:
                title = win.get("title", "Unknown")
                roi_score = win.get("roi_score", 0)
                md.append(f"- **{title}** (ROI: {roi_score:.1f}x)\n")
            md.append("\n")

        # Prioritization
        prioritization = intel_output.get("prioritization", {})
        if prioritization:
            md.append("### Priority Breakdown\n\n")
            for priority, items in prioritization.items():
                md.append(f"**{priority}**: {len(items)} items\n")
            md.append("\n")

        # Learning path
        learning_path = intel_output.get("learning_path")
        if learning_path:
            phases = learning_path.get("phases", [])
            md.append(f"### Learning Path\n\n")
            md.append(f"**Total Phases**: {len(phases)}\n")
            md.append(f"**Estimated Hours**: {learning_path.get('total_hours', 0)}\n\n")

        return "".join(md)

    def _format_diagrams(self, visual_output: Dict) -> str:
        """Format VISUAL-001 diagrams."""
        diagrams = visual_output.get("diagrams", {})
        md = []

        for diagram_type, diagram_data in diagrams.items():
            if isinstance(diagram_data, dict) and "mermaid_code" in diagram_data:
                title = diagram_data.get("title", diagram_type.title())
                md.append(f"### {title}\n\n")
                md.append("```mermaid\n")
                md.append(diagram_data["mermaid_code"])
                md.append("\n```\n\n")

        return "".join(md)

    def _format_playbook(self, exec_output: Dict) -> str:
        """Format EXEC-001 playbook."""
        playbook = exec_output.get("playbook", {})
        md = []

        steps = playbook.get("steps", [])
        if steps:
            md.append("### Implementation Steps\n\n")
            for i, step in enumerate(steps, 1):
                title = step.get("title", f"Step {i}")
                description = step.get("description", "")
                md.append(f"{i}. **{title}**\n")
                if description:
                    md.append(f"   {description}\n")
                md.append("\n")

        # Commands
        commands = exec_output.get("commands", {})
        if commands and commands.get("commands"):
            md.append("### Commands\n\n")
            md.append("```bash\n")
            for cmd in commands["commands"][:10]:
                md.append(f"{cmd.get('command', '')}\n")
            md.append("```\n\n")

        return "".join(md)

    def _format_knowledge_stats(self, knowledge_output: Dict) -> str:
        """Format KNOWLEDGE-001 statistics."""
        md = []

        stored = knowledge_output.get("stored_count", 0)
        duplicates = knowledge_output.get("duplicates_skipped", 0)

        md.append(f"**Insights Stored**: {stored}\n")
        md.append(f"**Duplicates Skipped**: {duplicates}\n")

        return "".join(md)

    def _format_workflow_metadata(self, results: Dict) -> str:
        """Format workflow execution metadata."""
        metadata = results.get("metadata", {})
        md = []

        md.append(f"- **Workflow ID**: {results.get('workflow_id', 'N/A')}\n")
        md.append(f"- **Execution Time**: {metadata.get('execution_time_seconds', 0):.2f}s\n")
        md.append(f"- **Start Time**: {metadata.get('start_time', 'N/A')}\n")
        md.append(f"- **End Time**: {metadata.get('end_time', 'N/A')}\n")
        md.append(f"- **Completed Modules**: {', '.join(results.get('completed_modules', []))}\n")

        if results.get("failed_modules"):
            failed = [m["module"] for m in results["failed_modules"]]
            md.append(f"- **Failed Modules**: {', '.join(failed)}\n")

        return "".join(md)

    def _generate_json_export(self, results: Dict) -> str:
        """Generate JSON export of all results."""
        return json.dumps(results, indent=2, default=str)

    def _generate_html_dashboard(self, results: Dict) -> str:
        """Generate HTML dashboard."""
        html = []

        html.append("<!DOCTYPE html>\n")
        html.append("<html>\n<head>\n")
        html.append("<title>YouTube Intelligence Report</title>\n")
        html.append("<style>\n")
        html.append(self._get_html_styles())
        html.append("</style>\n")
        html.append("</head>\n<body>\n")

        html.append("<div class='container'>\n")
        html.append(f"<h1>YouTube Intelligence Report</h1>\n")
        html.append(f"<p class='subtitle'>{results.get('metadata', {}).get('video_title', 'Unknown Video')}</p>\n")

        # Executive summary
        html.append("<div class='section'>\n")
        html.append("<h2>Executive Summary</h2>\n")
        html.append(f"<p>Status: <strong>{results.get('status', 'unknown').upper()}</strong></p>\n")
        html.append(f"<p>Modules: {len(results.get('completed_modules', []))}/6 completed</p>\n")
        html.append("</div>\n")

        # Module outputs
        for module in results.get("completed_modules", []):
            html.append(f"<div class='section'>\n")
            html.append(f"<h2>{module}</h2>\n")
            html.append(f"<p>✓ Module completed successfully</p>\n")
            html.append("</div>\n")

        html.append("</div>\n")
        html.append("</body>\n</html>\n")

        return "".join(html)

    def _get_html_styles(self) -> str:
        """Get CSS styles for HTML dashboard."""
        return """
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }
        .subtitle { color: #666; font-size: 1.1em; margin-top: -10px; }
        .section { margin: 30px 0; padding: 20px; background: #f9f9f9; border-left: 4px solid #4CAF50; border-radius: 4px; }
        h2 { color: #4CAF50; margin-top: 0; }
        """
