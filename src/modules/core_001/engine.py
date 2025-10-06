"""CORE-001 Enhanced Summary & Synthesis Engine

This module implements the foundation layer for AI Research Intelligence System.
Provides enhanced summary generation (50+ insights per video) and cross-video synthesis.
"""

import re
import time
from typing import Dict, List, Optional
from datetime import datetime

from openai import OpenAI

from .prompts import get_enhanced_summary_prompt, get_synthesis_prompt


class CoreEngine:
    """Enhanced summary and synthesis engine for YouTube transcript analysis"""

    def __init__(self, api_key: str, callback=None):
        """
        Initialize Core Engine

        Args:
            api_key: OpenAI API key for GPT-4 access
            callback: Optional callback function for logging (receives string messages)
        """
        self.client = OpenAI(api_key=api_key)
        self.callback = callback
        self.model = "gpt-4"
        self.max_tokens = 4096  # GPT-4 supports up to 8192, but 4096 is safer for costs

    def _log(self, message: str):
        """Internal logging method"""
        if self.callback:
            self.callback(message)
        else:
            print(message)

    def _count_tokens_estimate(self, text: str) -> int:
        """
        Estimate token count (rough approximation: 1 token ≈ 4 characters)

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        return len(text) // 4

    def _chunk_transcript(self, transcript: str, max_chunk_tokens: int = 12000) -> List[str]:
        """
        Split long transcripts into chunks that fit within GPT-4 context window

        Args:
            transcript: Full transcript text
            max_chunk_tokens: Maximum tokens per chunk (default: 12000 for GPT-4 16K context)

        Returns:
            List of transcript chunks with overlap for context continuity
        """
        estimated_tokens = self._count_tokens_estimate(transcript)

        if estimated_tokens <= max_chunk_tokens:
            return [transcript]

        # Split into paragraphs for better chunking
        paragraphs = transcript.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._count_tokens_estimate(para)

            if current_tokens + para_tokens > max_chunk_tokens and current_chunk:
                # Save current chunk and start new one
                chunks.append("\n\n".join(current_chunk))
                # Keep last 2 paragraphs for overlap/context
                current_chunk = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk
                current_tokens = sum(self._count_tokens_estimate(p) for p in current_chunk)

            current_chunk.append(para)
            current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        self._log(f"Split transcript into {len(chunks)} chunks for processing")
        return chunks

    def enhance_summary(
        self,
        transcript: str,
        metadata: Dict,
        mode: str = "developer"
    ) -> Dict:
        """
        Generate enhanced summary with 50+ actionable insights

        Args:
            transcript: Video transcript text
            metadata: Video metadata dictionary (title, channel, views, etc.)
            mode: Analysis depth ("quick" | "developer" | "research")

        Returns:
            Enhanced summary dictionary with:
                - notable_items: List of extracted insights (50+ in developer mode)
                - key_insights: Strategic synthesis paragraph
                - extracted_prompts: List of prompt templates found
                - extracted_commands: List of CLI commands found
                - tool_mentions: Dictionary of tools with context
                - complexity_score: 0-1 difficulty rating
                - implementation_time: Estimated minutes to implement
                - prerequisites: List of required tools/knowledge
        """
        start_time = time.time()
        self._log(f"Generating {mode} mode summary for: {metadata.get('title', 'Unknown')}")

        # Validate mode
        valid_modes = ["quick", "developer", "research"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of: {valid_modes}")

        # Check if chunking needed
        chunks = self._chunk_transcript(transcript)

        if len(chunks) == 1:
            # Single chunk - process normally
            summary_content = self._process_single_chunk(transcript, metadata, mode)
        else:
            # Multiple chunks - process and merge
            self._log(f"Processing {len(chunks)} chunks...")
            chunk_summaries = []

            for i, chunk in enumerate(chunks, 1):
                self._log(f"  Processing chunk {i}/{len(chunks)}...")
                chunk_summary = self._process_single_chunk(chunk, metadata, mode)
                chunk_summaries.append(chunk_summary)

            # Merge chunk summaries
            summary_content = self._merge_chunk_summaries(chunk_summaries, metadata)

        # Extract structured data from markdown summary
        parsed_summary = self._parse_summary_content(summary_content, metadata)

        # Calculate metrics
        processing_time = time.time() - start_time
        estimated_cost = self._estimate_api_cost(transcript, summary_content)

        self._log(f"✓ Summary generated in {processing_time:.1f}s (est. cost: ${estimated_cost:.3f})")
        self._log(f"  Extracted {len(parsed_summary['notable_items'])} notable items")

        parsed_summary["processing_time_seconds"] = processing_time
        parsed_summary["estimated_cost_usd"] = estimated_cost

        return parsed_summary

    def _process_single_chunk(self, transcript: str, metadata: Dict, mode: str) -> str:
        """
        Process a single transcript chunk with GPT-4

        Args:
            transcript: Transcript text (single chunk)
            metadata: Video metadata
            mode: Analysis mode

        Returns:
            Markdown summary content from GPT-4
        """
        prompt = get_enhanced_summary_prompt(transcript, metadata, mode)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a technical research analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3  # Lower temperature for more focused extraction
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            self._log(f"⚠ GPT-4 API error: {str(e)}")
            raise

    def _merge_chunk_summaries(self, chunk_summaries: List[str], metadata: Dict) -> str:
        """
        Merge multiple chunk summaries into comprehensive summary

        Args:
            chunk_summaries: List of markdown summaries from chunks
            metadata: Video metadata

        Returns:
            Merged comprehensive summary
        """
        # Combine all chunk summaries
        combined_text = "\n\n---\n\n".join([
            f"CHUNK {i+1}:\n{summary}"
            for i, summary in enumerate(chunk_summaries)
        ])

        # Use GPT-4 to deduplicate and merge
        merge_prompt = f"""You are merging multiple partial summaries of the same video into ONE comprehensive summary.

VIDEO: {metadata.get('title', 'Unknown')}

PARTIAL SUMMARIES:
{combined_text}

TASK: Create a single comprehensive summary by:
1. Combining all notable items (remove duplicates)
2. Merging extracted prompts/commands/tools (no duplicates)
3. Synthesizing key insights into coherent narrative
4. Preserving ALL unique information
5. Maintaining the original summary structure

OUTPUT: Complete merged summary in markdown format following the original template structure.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a technical research analyst."},
                    {"role": "user", "content": merge_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            self._log(f"⚠ Merge failed, concatenating summaries: {str(e)}")
            # Fallback: simple concatenation
            return combined_text

    def _parse_summary_content(self, summary_md: str, metadata: Dict) -> Dict:
        """
        Parse markdown summary into structured dictionary

        Args:
            summary_md: Markdown summary content
            metadata: Video metadata

        Returns:
            Structured summary dictionary
        """
        # Extract notable items (### N. **Title** [Tag])
        notable_items = []
        item_pattern = r'###\s+(\d+)\.\s+\*\*(.*?)\*\*\s+\[(.*?)\]'
        matches = re.finditer(item_pattern, summary_md)

        for match in matches:
            item_num = int(match.group(1))
            title = match.group(2).strip()
            tag = match.group(3).strip()

            # Extract section content (everything until next ### or ---)
            start_pos = match.end()
            next_section = re.search(r'(###|---)', summary_md[start_pos:])
            if next_section:
                content = summary_md[start_pos:start_pos + next_section.start()].strip()
            else:
                content = summary_md[start_pos:].strip()

            # Parse item details
            item = {
                "id": f"item_{item_num}",
                "title": title,
                "tag": tag,
                "description": self._extract_description(content),
                "implementation_steps": self._extract_implementation_steps(content),
                "code_snippet": self._extract_code_snippet(content),
                "source_timestamp": self._extract_timestamp(content),
                "readiness": self._extract_readiness(content),
                "implementation_time": self._extract_implementation_time(content)
            }

            notable_items.append(item)

        # Extract prompts
        extracted_prompts = self._extract_prompts_section(summary_md)

        # Extract commands
        extracted_commands = self._extract_commands_section(summary_md)

        # Extract tool mentions
        tool_mentions = self._extract_tools_section(summary_md)

        # Extract key insights
        key_insights = self._extract_key_insights_section(summary_md)

        # Calculate complexity score (based on prerequisites and setup requirements)
        complexity_score = self._calculate_complexity(notable_items, tool_mentions)

        # Estimate implementation time
        implementation_time = self._estimate_total_implementation_time(notable_items)

        # Extract prerequisites
        prerequisites = self._extract_prerequisites(summary_md, tool_mentions)

        return {
            "notable_items": notable_items,
            "key_insights": key_insights,
            "extracted_prompts": extracted_prompts,
            "extracted_commands": extracted_commands,
            "tool_mentions": tool_mentions,
            "complexity_score": complexity_score,
            "implementation_time": implementation_time,
            "prerequisites": prerequisites,
            "raw_markdown": summary_md,
            "metadata": metadata
        }

    def _extract_description(self, content: str) -> str:
        """Extract description paragraph from item content"""
        lines = content.split("\n")
        description_lines = []
        for line in lines:
            if line.strip() and not line.startswith("**") and not line.startswith("```"):
                description_lines.append(line.strip())
                if len(description_lines) >= 3:  # First 3 non-special lines
                    break
        return " ".join(description_lines)

    def _extract_implementation_steps(self, content: str) -> List[str]:
        """Extract implementation steps from 'How to Implement' section"""
        steps = []
        in_impl_section = False

        for line in content.split("\n"):
            if "**How to Implement**" in line:
                in_impl_section = True
                continue
            if in_impl_section:
                if line.startswith("**") and "How to Implement" not in line:
                    break  # End of implementation section
                if re.match(r'^\d+\.', line.strip()):
                    steps.append(line.strip())

        return steps

    def _extract_code_snippet(self, content: str) -> Optional[str]:
        """Extract code snippet from triple-backtick blocks"""
        code_pattern = r'```(?:\w+)?\n(.*?)\n```'
        match = re.search(code_pattern, content, re.DOTALL)
        return match.group(1).strip() if match else None

    def _extract_timestamp(self, content: str) -> str:
        """Extract source timestamp (MM:SS format)"""
        timestamp_pattern = r'\*\*Source Timestamp\*\*:\s*(\d{1,2}:\d{2})'
        match = re.search(timestamp_pattern, content)
        return match.group(1) if match else "00:00"

    def _extract_readiness(self, content: str) -> str:
        """Extract readiness status"""
        if "✅ Ready" in content or "Ready" in content:
            return "READY"
        elif "⚠️ Needs Setup" in content or "Needs Setup" in content:
            return "NEEDS_SETUP"
        elif "🔬 Experimental" in content or "Experimental" in content:
            return "EXPERIMENTAL"
        return "UNKNOWN"

    def _extract_implementation_time(self, content: str) -> str:
        """Extract implementation time estimate"""
        time_pattern = r'\*\*Implementation Time\*\*:\s*\[?([^\]]+)\]?'
        match = re.search(time_pattern, content)
        return match.group(1).strip() if match else "Unknown"

    def _extract_prompts_section(self, summary_md: str) -> List[Dict]:
        """Extract prompt templates from dedicated section"""
        prompts = []
        # Find "Extracted Prompts & Templates" section
        section_start = summary_md.find("## Extracted Prompts")
        if section_start == -1:
            return prompts

        section_end = summary_md.find("\n## ", section_start + 10)
        if section_end == -1:
            section_end = len(summary_md)

        section = summary_md[section_start:section_end]

        # Extract each prompt (### Prompt: {Purpose})
        prompt_pattern = r'###\s+Prompt:\s+(.*?)\n```\n(.*?)\n```'
        matches = re.finditer(prompt_pattern, section, re.DOTALL)

        for match in matches:
            purpose = match.group(1).strip()
            template = match.group(2).strip()
            prompts.append({
                "purpose": purpose,
                "template": template,
                "source": "video_content"
            })

        return prompts

    def _extract_commands_section(self, summary_md: str) -> List[Dict]:
        """Extract CLI commands from dedicated section"""
        commands = []
        section_start = summary_md.find("## Extracted Commands")
        if section_start == -1:
            return commands

        section_end = summary_md.find("\n## ", section_start + 10)
        if section_end == -1:
            section_end = len(summary_md)

        section = summary_md[section_start:section_end]

        # Extract each command (### Command: {Purpose})
        command_pattern = r'###\s+Command:\s+(.*?)\n```(?:bash|sh)?\n(.*?)\n```'
        matches = re.finditer(command_pattern, section, re.DOTALL)

        for match in matches:
            purpose = match.group(1).strip()
            command = match.group(2).strip()
            commands.append({
                "purpose": purpose,
                "command": command,
                "type": "cli"
            })

        return commands

    def _extract_tools_section(self, summary_md: str) -> Dict:
        """Extract tool specifications from dedicated section"""
        tools = {}
        section_start = summary_md.find("## Tool Specifications")
        if section_start == -1:
            return tools

        section_end = summary_md.find("\n## ", section_start + 10)
        if section_end == -1:
            section_end = len(summary_md)

        section = summary_md[section_start:section_end]

        # Extract tool names (### {Tool Name} v{version})
        tool_pattern = r'###\s+(.*?)\s+v([^\n]+)'
        matches = re.finditer(tool_pattern, section)

        for match in matches:
            tool_name = match.group(1).strip()
            version = match.group(2).strip()
            tools[tool_name] = {"version": version}

        return tools

    def _extract_key_insights_section(self, summary_md: str) -> str:
        """Extract key insights strategic synthesis"""
        section_start = summary_md.find("## Key Insights")
        if section_start == -1:
            return "No key insights extracted"

        section_end = summary_md.find("\n## ", section_start + 10)
        if section_end == -1:
            section_end = summary_md.find("\n---", section_start + 10)
        if section_end == -1:
            section_end = len(summary_md)

        return summary_md[section_start:section_end].strip()

    def _calculate_complexity(self, items: List[Dict], tools: Dict) -> float:
        """Calculate 0-1 complexity score based on setup requirements"""
        complexity_indicators = 0
        total_weight = 0

        # Count "Needs Setup" items (medium complexity)
        needs_setup = sum(1 for item in items if item.get("readiness") == "NEEDS_SETUP")
        complexity_indicators += needs_setup * 0.5
        total_weight += len(items)

        # Count "Experimental" items (high complexity)
        experimental = sum(1 for item in items if item.get("readiness") == "EXPERIMENTAL")
        complexity_indicators += experimental * 1.0
        total_weight += len(items)

        # Tool count (more tools = higher complexity)
        tool_complexity = min(len(tools) / 10, 1.0)  # Cap at 10 tools
        complexity_indicators += tool_complexity
        total_weight += 1

        if total_weight == 0:
            return 0.5  # Default medium complexity

        return min(complexity_indicators / total_weight, 1.0)

    def _estimate_total_implementation_time(self, items: List[Dict]) -> int:
        """Estimate total implementation time in minutes"""
        total_minutes = 0

        for item in items:
            time_str = item.get("implementation_time", "30min")
            minutes = self._parse_time_to_minutes(time_str)
            total_minutes += minutes

        return total_minutes

    def _parse_time_to_minutes(self, time_str: str) -> int:
        """Convert time string to minutes (5min, 2hr, 1day)"""
        time_str = time_str.lower().strip()

        if "min" in time_str:
            return int(re.search(r'(\d+)', time_str).group(1))
        elif "hr" in time_str or "hour" in time_str:
            hours = int(re.search(r'(\d+)', time_str).group(1))
            return hours * 60
        elif "day" in time_str:
            days = int(re.search(r'(\d+)', time_str).group(1))
            return days * 480  # 8 hours per day
        else:
            return 30  # Default 30 minutes

    def _extract_prerequisites(self, summary_md: str, tools: Dict) -> List[str]:
        """Extract prerequisites from summary"""
        prereqs = set()

        # Extract from header section
        prereq_pattern = r'\*\*Prerequisites\*\*:\s*\[(.*?)\]'
        match = re.search(prereq_pattern, summary_md)
        if match:
            prereqs.add(match.group(1).strip())

        # Add all tools as prerequisites
        prereqs.update(tools.keys())

        return sorted(list(prereqs))

    def _estimate_api_cost(self, input_text: str, output_text: str) -> float:
        """
        Estimate API cost based on token usage

        GPT-4 pricing (as of 2024):
        - Input: $0.03 per 1K tokens
        - Output: $0.06 per 1K tokens

        Args:
            input_text: Input prompt text
            output_text: Generated output text

        Returns:
            Estimated cost in USD
        """
        input_tokens = self._count_tokens_estimate(input_text)
        output_tokens = self._count_tokens_estimate(output_text)

        input_cost = (input_tokens / 1000) * 0.03
        output_cost = (output_tokens / 1000) * 0.06

        return input_cost + output_cost

    def synthesize_videos(
        self,
        summaries: List[Dict],
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Cross-video synthesis with pattern detection

        Args:
            summaries: List of enhanced summary dictionaries
            context: Optional user context (collection name, goals, etc.)

        Returns:
            Comprehensive synthesis with:
                - executive_summary: High-level synthesis
                - common_themes: Patterns found across videos
                - contradictions: Conflicting advice between sources
                - unique_insights: Video-specific contributions
                - consensus_points: Agreed-upon best practices
                - chronological_timeline: Technology evolution
                - cross_video_patterns: Meta-patterns
        """
        start_time = time.time()
        self._log(f"Synthesizing {len(summaries)} video summaries...")

        # Build metadata
        metadata = self._build_synthesis_metadata(summaries, context)

        # Generate synthesis prompt
        prompt = get_synthesis_prompt(summaries, metadata)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior technical architect."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.4  # Slightly higher for creative synthesis
            )

            synthesis_md = response.choices[0].message.content.strip()

            # Parse synthesis into structured format
            parsed_synthesis = self._parse_synthesis_content(synthesis_md, metadata)

            processing_time = time.time() - start_time
            estimated_cost = self._estimate_api_cost(prompt, synthesis_md)

            self._log(f"✓ Synthesis generated in {processing_time:.1f}s (est. cost: ${estimated_cost:.3f})")

            parsed_synthesis["processing_time_seconds"] = processing_time
            parsed_synthesis["estimated_cost_usd"] = estimated_cost

            return parsed_synthesis

        except Exception as e:
            self._log(f"⚠ Synthesis generation failed: {str(e)}")
            raise

    def _build_synthesis_metadata(self, summaries: List[Dict], context: Optional[Dict]) -> Dict:
        """Build metadata dictionary for synthesis prompt"""
        if not context:
            context = {}

        # Calculate date range
        dates = [s.get("metadata", {}).get("upload_date", "") for s in summaries]
        valid_dates = [d for d in dates if d and d != "Unknown"]
        date_range = f"{min(valid_dates)} to {max(valid_dates)}" if valid_dates else "Unknown"

        # Unique channels
        channels = list(set(
            s.get("metadata", {}).get("channel", "Unknown") for s in summaries
        ))

        # Total views
        total_views = sum(s.get("metadata", {}).get("views", 0) for s in summaries)

        # Dominant tools
        all_tools = {}
        for summary in summaries:
            tools = summary.get("tool_mentions", {})
            for tool, data in tools.items():
                all_tools[tool] = all_tools.get(tool, 0) + 1

        tool_list = ", ".join([t for t, count in sorted(all_tools.items(), key=lambda x: -x[1])[:10]])

        return {
            "n_videos": len(summaries),
            "date_range": date_range,
            "total_views": total_views,
            "unique_channels": ", ".join(channels),
            "dominant_topics": context.get("dominant_topics", "AI Development"),
            "collection_name": context.get("collection_name", "AI Research Collection"),
            "today": datetime.now().strftime("%Y-%m-%d"),
            "total_duration": "Unknown",  # TODO: Calculate from metadata
            "tool_list": tool_list or "Various AI tools"
        }

    def _parse_synthesis_content(self, synthesis_md: str, metadata: Dict) -> Dict:
        """Parse synthesis markdown into structured dictionary"""
        # Extract executive summary
        exec_summary = self._extract_section(synthesis_md, "Executive Summary")

        # Extract common themes
        common_themes = self._extract_themes_section(synthesis_md)

        # Extract contradictions
        contradictions = self._extract_contradictions_section(synthesis_md)

        # Extract unique insights
        unique_insights = self._extract_unique_insights_section(synthesis_md)

        # Extract consensus points
        consensus_points = self._extract_consensus_section(synthesis_md)

        # Extract timeline
        timeline = self._extract_timeline_section(synthesis_md)

        # Extract cross-video patterns
        patterns = self._extract_patterns_section(synthesis_md)

        return {
            "executive_summary": exec_summary,
            "common_themes": common_themes,
            "contradictions": contradictions,
            "unique_insights": unique_insights,
            "consensus_points": consensus_points,
            "chronological_timeline": timeline,
            "cross_video_patterns": patterns,
            "raw_markdown": synthesis_md,
            "metadata": metadata
        }

    def _extract_section(self, markdown: str, section_name: str) -> str:
        """Extract a named section from markdown"""
        pattern = f"## {section_name}(.*?)(?=\n## |\\Z)"
        match = re.search(pattern, markdown, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_themes_section(self, markdown: str) -> List[str]:
        """Extract common themes as list"""
        section = self._extract_section(markdown, "Common Themes")
        # Extract theme names from ### Theme: {name}
        themes = re.findall(r'### Theme:\s+(.*?)(?=\n|\Z)', section)
        return themes

    def _extract_contradictions_section(self, markdown: str) -> List[Dict]:
        """Extract contradictions as structured list"""
        section = self._extract_section(markdown, "Contradictions")
        contradictions = []

        # Extract each contradiction block
        blocks = re.findall(
            r'### Contradiction:\s+(.*?)\n\*\*Conflicting Sources\*\*:(.*?)(?=\n###|\Z)',
            section,
            re.DOTALL
        )

        for topic, content in blocks:
            contradictions.append({
                "topic": topic.strip(),
                "content": content.strip()
            })

        return contradictions

    def _extract_unique_insights_section(self, markdown: str) -> Dict:
        """Extract unique insights by video"""
        section = self._extract_section(markdown, "Unique Insights")
        insights = {}

        # Extract video-specific insights
        blocks = re.findall(
            r'###\s+(.*?)\n\*\*Unique Contribution\*\*:\s+(.*?)(?=\n###|\Z)',
            section,
            re.DOTALL
        )

        for video_title, contribution in blocks:
            insights[video_title.strip()] = contribution.strip()

        return insights

    def _extract_consensus_section(self, markdown: str) -> List[str]:
        """Extract consensus points as list"""
        section = self._extract_section(markdown, "Consensus Points")
        # Extract numbered list items
        points = re.findall(r'\d+\.\s+\*\*(.*?)\*\*:', section)
        return points

    def _extract_timeline_section(self, markdown: str) -> List[Dict]:
        """Extract chronological timeline"""
        section = self._extract_section(markdown, "Chronological Timeline")
        timeline = []

        # Extract period blocks
        blocks = re.findall(
            r'###\s+([\d\-/]+|Current State.*?)\n(.*?)(?=\n###|\Z)',
            section,
            re.DOTALL
        )

        for period, content in blocks:
            timeline.append({
                "period": period.strip(),
                "content": content.strip()
            })

        return timeline

    def _extract_patterns_section(self, markdown: str) -> List[Dict]:
        """Extract cross-video patterns"""
        section = self._extract_section(markdown, "Cross-Video Patterns")
        patterns = []

        # Extract pattern blocks
        blocks = re.findall(
            r'### Pattern:\s+(.*?)\n\*\*Observed Across\*\*:\s+(.*?)(?=\n###|\Z)',
            section,
            re.DOTALL
        )

        for pattern_name, content in blocks:
            patterns.append({
                "name": pattern_name.strip(),
                "content": content.strip()
            })

        return patterns

    def extract_entities(
        self,
        text: str,
        entity_types: Optional[List[str]] = None
    ) -> Dict:
        """
        Extract technical entities (tools, commands, prompts) from text

        Args:
            text: Source text (transcript or summary)
            entity_types: Types to extract (default: all types)
                Options: ["tools", "commands", "prompts", "versions"]

        Returns:
            Dictionary of extracted entities by type
        """
        if entity_types is None:
            entity_types = ["tools", "commands", "prompts", "versions"]

        entities = {}

        if "tools" in entity_types:
            entities["tools"] = self._extract_tool_mentions(text)

        if "commands" in entity_types:
            entities["commands"] = self._extract_command_mentions(text)

        if "prompts" in entity_types:
            entities["prompts"] = self._extract_prompt_mentions(text)

        if "versions" in entity_types:
            entities["versions"] = self._extract_version_numbers(text)

        return entities

    def _extract_tool_mentions(self, text: str) -> List[Dict]:
        """Extract AI tool mentions from text"""
        # Common AI tools pattern
        tool_patterns = [
            r'(Claude|GPT-4|ChatGPT|Cursor|Copilot|Gemini|Llama|Anthropic)\s*(?:v?(\d+(?:\.\d+)?))?',
            r'(VS Code|Visual Studio Code|PyCharm|IntelliJ)',
            r'(Python|JavaScript|TypeScript|Rust|Go)\s*(?:v?(\d+(?:\.\d+)?))?'
        ]

        tools = []
        for pattern in tool_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                tool_name = match.group(1)
                version = match.group(2) if len(match.groups()) > 1 else None
                tools.append({
                    "name": tool_name,
                    "version": version,
                    "context": text[max(0, match.start()-50):match.end()+50]
                })

        return tools

    def _extract_command_mentions(self, text: str) -> List[Dict]:
        """Extract CLI command mentions from text"""
        # Look for code blocks or command-like patterns
        commands = []

        # Code blocks
        code_blocks = re.findall(r'```(?:bash|sh|shell)?\n(.*?)\n```', text, re.DOTALL)
        for block in code_blocks:
            lines = block.strip().split("\n")
            for line in lines:
                if line.strip() and not line.strip().startswith("#"):
                    commands.append({
                        "command": line.strip(),
                        "type": "code_block"
                    })

        # Inline code with $ or >
        inline_commands = re.findall(r'[$>]\s*([^\n]+)', text)
        for cmd in inline_commands:
            commands.append({
                "command": cmd.strip(),
                "type": "inline"
            })

        return commands

    def _extract_prompt_mentions(self, text: str) -> List[Dict]:
        """Extract prompt template mentions from text"""
        prompts = []

        # Look for quoted multi-line text (likely prompts)
        prompt_patterns = [
            r'"([^"]{100,})"',  # Long quoted strings
            r'prompt:\s*["\']([^"\']+)["\']',  # Explicitly labeled prompts
        ]

        for pattern in prompt_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                prompts.append({
                    "template": match.group(1).strip(),
                    "source": "extracted"
                })

        return prompts

    def _extract_version_numbers(self, text: str) -> Dict:
        """Extract version numbers and deprecation warnings"""
        versions = {}

        # Version number patterns
        version_pattern = r'(v|version)\s*(\d+(?:\.\d+)*)'
        matches = re.finditer(version_pattern, text, re.IGNORECASE)

        for match in matches:
            versions[match.group(0)] = {
                "number": match.group(2),
                "context": text[max(0, match.start()-50):match.end()+50]
            }

        # Deprecation warnings
        deprecation_pattern = r'deprecat\w+|obsolete|no longer (support|work)'
        if re.search(deprecation_pattern, text, re.IGNORECASE):
            versions["deprecation_warning"] = True

        return versions
