"""
Workflow Orchestrator - INTEGRATE-001 Core Component

Coordinates execution of all v2.0 intelligence modules with:
- Dependency-aware execution ordering
- Error handling and recovery
- Progress tracking
- Performance monitoring
"""

from typing import Dict, List, Optional, Callable
from datetime import datetime
import traceback


class WorkflowOrchestrator:
    """
    Orchestrates execution of all v2.0 modules in correct dependency order.

    Execution Order:
    1. CORE-001: Extract enhanced summary from video transcript
    2. VISUAL-001: Generate diagrams from summary/synthesis
    3. EXEC-001: Create playbooks and execution artifacts
    4. INTEL-001: Calculate ROI and generate learning paths
    5. KNOWLEDGE-001: Store insights in persistent knowledge base
    6. UI-001: Render results in enhanced dashboard
    """

    def __init__(self, callback: Optional[Callable] = None):
        """
        Initialize workflow orchestrator.

        Args:
            callback: Optional logging callback function
        """
        self.callback = callback or (lambda x: None)
        self.execution_log = []

    def execute_workflow(
        self,
        workflow_type: str,
        video_data: Dict,
        config: Dict
    ) -> Dict:
        """
        Execute complete v2.0 workflow from video to intelligence.

        Args:
            workflow_type: "quick" | "standard" | "comprehensive"
            video_data: Video transcript and metadata
            config: Configuration for all modules

        Returns:
            Complete workflow results with all module outputs
        """
        self.callback("=" * 70)
        self.callback(f"INTEGRATE-001: Starting {workflow_type.upper()} workflow")
        self.callback("=" * 70)

        start_time = datetime.now()
        results = {
            "workflow_id": f"workflow_{start_time.strftime('%Y%m%d_%H%M%S')}",
            "workflow_type": workflow_type,
            "status": "running",
            "completed_modules": [],
            "failed_modules": [],
            "module_outputs": {},
            "errors": [],
            "metadata": {
                "start_time": start_time.isoformat(),
                "video_title": video_data.get("title", "Unknown"),
                "video_url": video_data.get("url", ""),
            }
        }

        try:
            # Phase 1: CORE-001 - Enhanced Summary
            core_result = self._execute_core_001(video_data, workflow_type, config)
            if core_result["success"]:
                results["module_outputs"]["CORE-001"] = core_result
                results["completed_modules"].append("CORE-001")
                self.callback("✓ CORE-001 complete")
            else:
                results["failed_modules"].append({"module": "CORE-001", "error": core_result.get("error")})
                results["status"] = "failed"
                return self._finalize_results(results, start_time)

            # Phase 2: VISUAL-001 - Diagram Generation (optional, non-blocking)
            if config.get("enable_diagrams", True):
                visual_result = self._execute_visual_001(core_result, workflow_type, config)
                if visual_result["success"]:
                    results["module_outputs"]["VISUAL-001"] = visual_result
                    results["completed_modules"].append("VISUAL-001")
                    self.callback("✓ VISUAL-001 complete")
                else:
                    results["failed_modules"].append({"module": "VISUAL-001", "error": visual_result.get("error")})
                    self.callback("⚠ VISUAL-001 failed (non-critical, continuing)")

            # Phase 3: EXEC-001 - Playbook Generation
            if config.get("enable_playbooks", True):
                exec_result = self._execute_exec_001(core_result, workflow_type, config)
                if exec_result["success"]:
                    results["module_outputs"]["EXEC-001"] = exec_result
                    results["completed_modules"].append("EXEC-001")
                    self.callback("✓ EXEC-001 complete")
                else:
                    results["failed_modules"].append({"module": "EXEC-001", "error": exec_result.get("error")})
                    self.callback("⚠ EXEC-001 failed (non-critical, continuing)")

            # Phase 4: INTEL-001 - ROI & Intelligence
            if config.get("enable_intelligence", True):
                intel_result = self._execute_intel_001(core_result, workflow_type, config)
                if intel_result["success"]:
                    results["module_outputs"]["INTEL-001"] = intel_result
                    results["completed_modules"].append("INTEL-001")
                    self.callback("✓ INTEL-001 complete")
                else:
                    results["failed_modules"].append({"module": "INTEL-001", "error": intel_result.get("error")})
                    self.callback("⚠ INTEL-001 failed (non-critical, continuing)")

            # Phase 5: KNOWLEDGE-001 - Persistent Storage (optional)
            if config.get("enable_knowledge_base", False):
                knowledge_result = self._execute_knowledge_001(core_result, intel_result, config)
                if knowledge_result["success"]:
                    results["module_outputs"]["KNOWLEDGE-001"] = knowledge_result
                    results["completed_modules"].append("KNOWLEDGE-001")
                    self.callback("✓ KNOWLEDGE-001 complete")
                else:
                    results["failed_modules"].append({"module": "KNOWLEDGE-001", "error": knowledge_result.get("error")})
                    self.callback("⚠ KNOWLEDGE-001 failed (non-critical, continuing)")

            # Determine final status
            if len(results["failed_modules"]) == 0:
                results["status"] = "complete"
            elif len(results["completed_modules"]) > 0:
                results["status"] = "partial"
            else:
                results["status"] = "failed"

        except Exception as e:
            results["status"] = "failed"
            results["errors"].append({
                "type": "WorkflowError",
                "message": str(e),
                "traceback": traceback.format_exc()
            })
            self.callback(f"✗ Workflow failed: {e}")

        return self._finalize_results(results, start_time)

    def _execute_core_001(self, video_data: Dict, workflow_type: str, config: Dict) -> Dict:
        """Execute CORE-001 enhanced summary generation."""
        self.callback("[1/5] Executing CORE-001 (Enhanced Summary)...")

        try:
            from modules.core_001 import CoreEngine

            api_key = config.get("openai_api_key")
            if not api_key:
                return {"success": False, "error": "Missing OpenAI API key"}

            # Map workflow types to CORE-001 modes
            mode_map = {
                "quick": "quick",
                "standard": "developer",
                "comprehensive": "research"
            }
            mode = mode_map.get(workflow_type, "developer")

            engine = CoreEngine(api_key=api_key, callback=self.callback)

            summary = engine.enhance_summary(
                transcript=video_data.get("transcript", ""),
                metadata=video_data,
                mode=mode
            )

            return {
                "success": True,
                "summary": summary,
                "mode": mode,
                "insights_count": len(summary.get("insights", []))
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def _execute_visual_001(self, core_result: Dict, workflow_type: str, config: Dict) -> Dict:
        """Execute VISUAL-001 diagram generation."""
        self.callback("[2/5] Executing VISUAL-001 (Diagram Generation)...")

        try:
            from modules.visual_001 import VisualEngine

            # Create synthesis from single summary for visualization
            summary = core_result["summary"]

            # Build synthesis structure expected by VISUAL-001
            synthesis = {
                "chronological_timeline": self._extract_timeline(summary),
                "cross_video_patterns": [],
                "tool_mentions": self._extract_tool_mentions(summary),
                "key_concepts": summary.get("insights", [])[:10],
                "consensus_points": [],
                "contradictions": []
            }

            engine = VisualEngine(callback=self.callback)

            # Configure diagram generation based on workflow type
            diagram_config = {
                "diagram_types": ["timeline", "architecture", "comparison", "flowchart"],
                "complexity": "simple" if workflow_type == "quick" else "detailed",
                "validate": True
            }

            diagrams = engine.generate_all(synthesis, diagram_config)

            return {
                "success": True,
                "diagrams": diagrams,
                "diagram_count": len(diagrams.get("diagrams", {}))
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def _execute_exec_001(self, core_result: Dict, workflow_type: str, config: Dict) -> Dict:
        """Execute EXEC-001 playbook generation."""
        self.callback("[3/5] Executing EXEC-001 (Playbook Generation)...")

        try:
            from modules.exec_001 import ExecutionEngine

            summary = core_result["summary"]
            insights = summary.get("insights", [])

            engine = ExecutionEngine(callback=self.callback)

            # Build context for execution engine
            context = {
                "user_skill_level": config.get("skill_level", "intermediate"),
                "available_tools": config.get("installed_tools", []),
                "output_formats": ["markdown"]
            }

            execution_output = engine.generate_all(insights, context=context)

            return {
                "success": True,
                "playbook": execution_output.get("playbook", {}),
                "prompts": execution_output.get("prompts", {}),
                "commands": execution_output.get("commands", {}),
                "checklists": execution_output.get("checklists", {})
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def _execute_intel_001(self, core_result: Dict, workflow_type: str, config: Dict) -> Dict:
        """Execute INTEL-001 ROI and intelligence analysis."""
        self.callback("[4/5] Executing INTEL-001 (ROI & Intelligence)...")

        try:
            from modules.intel_001 import IntelligenceEngine

            summary = core_result["summary"]
            insights = summary.get("insights", [])

            # Convert insights to items for INTEL-001
            items = [
                {
                    "title": insight.get("insight", ""),
                    "description": insight.get("context", ""),
                    "category": insight.get("category", "General"),
                    "actionability": insight.get("actionability", "medium")
                }
                for insight in insights
            ]

            engine = IntelligenceEngine(callback=self.callback)

            intelligence = engine.analyze_items(
                items=items,
                generate_learning_path=workflow_type == "comprehensive"
            )

            return {
                "success": True,
                "roi_analysis": intelligence.get("roi_analysis", {}),
                "readiness_analysis": intelligence.get("readiness_analysis", {}),
                "learning_path": intelligence.get("learning_path"),
                "prioritization": intelligence.get("prioritization", {}),
                "quick_wins": intelligence.get("quick_wins", [])
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def _execute_knowledge_001(
        self,
        core_result: Dict,
        intel_result: Dict,
        config: Dict
    ) -> Dict:
        """Execute KNOWLEDGE-001 persistent storage."""
        self.callback("[5/5] Executing KNOWLEDGE-001 (Knowledge Base)...")

        try:
            from modules.knowledge_001 import KnowledgeEngine

            summary = core_result["summary"]
            insights = summary.get("insights", [])

            engine = KnowledgeEngine(
                db_path=config.get("knowledge_db_path", "knowledge.db"),
                callback=self.callback
            )

            # Store insights in knowledge base
            stored_count = 0
            for insight in insights:
                result = engine.store_insight(
                    content=insight.get("insight", ""),
                    metadata={
                        "category": insight.get("category", ""),
                        "timestamp": insight.get("timestamp", ""),
                        "confidence": insight.get("confidence", 0.5),
                        "actionability": insight.get("actionability", "medium"),
                        "roi_score": intel_result.get("roi_analysis", {}).get("score", 0) if intel_result.get("success") else 0
                    }
                )
                if result.get("stored"):
                    stored_count += 1

            return {
                "success": True,
                "stored_count": stored_count,
                "duplicates_skipped": len(insights) - stored_count
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def _extract_timeline(self, summary: Dict) -> List[Dict]:
        """Extract timeline events from summary for VISUAL-001."""
        insights = summary.get("insights", [])
        timeline = []

        for insight in insights:
            if insight.get("timestamp"):
                timeline.append({
                    "timestamp": insight["timestamp"],
                    "event": insight.get("category", "Event"),
                    "description": insight.get("insight", "")[:50]
                })

        return timeline

    def _extract_tool_mentions(self, summary: Dict) -> Dict:
        """Extract tool mentions from summary for VISUAL-001."""
        tools = summary.get("tools", [])
        tool_mentions = {}

        for tool in tools:
            tool_name = tool if isinstance(tool, str) else tool.get("name", "Unknown")
            tool_mentions[tool_name] = {
                "count": 1,
                "contexts": ["video content"]
            }

        return tool_mentions

    def _finalize_results(self, results: Dict, start_time: datetime) -> Dict:
        """Add final metadata to results."""
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        results["metadata"]["end_time"] = end_time.isoformat()
        results["metadata"]["execution_time_seconds"] = execution_time
        results["metadata"]["modules_completed"] = len(results["completed_modules"])
        results["metadata"]["modules_failed"] = len(results["failed_modules"])

        self.callback("=" * 70)
        self.callback(f"Workflow {results['status'].upper()}")
        self.callback(f"Completed modules: {', '.join(results['completed_modules'])}")
        if results["failed_modules"]:
            self.callback(f"Failed modules: {', '.join([m['module'] for m in results['failed_modules']])}")
        self.callback(f"Execution time: {execution_time:.2f}s")
        self.callback("=" * 70)

        return results
