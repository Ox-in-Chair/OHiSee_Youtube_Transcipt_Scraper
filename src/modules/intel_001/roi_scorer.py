"""
ROI Scorer - Calculate return on investment for implementations

Analyzes time savings, costs, and implementation effort to provide
ROI scores and priority recommendations.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ROIMetrics:
    """ROI calculation results"""

    implementation_time: int  # hours to implement
    time_saved_per_use: int  # minutes saved per use
    use_frequency: str  # "daily" | "weekly" | "monthly" | "rarely"
    annual_time_savings: int  # hours saved per year
    cost: float  # $ cost (API, tools, subscriptions)
    roi_score: float  # (savings - cost) / implementation_time
    breakeven_period: int  # weeks until positive ROI
    recommendation: str  # "HIGH" | "MEDIUM" | "LOW"
    reasoning: str  # Why this ROI score


class ROIScorer:
    """
    Calculate ROI for implementation items based on time savings and costs
    """

    # Frequency multipliers (uses per year)
    FREQUENCY_MAP = {
        "daily": 250,  # 5 days/week * 50 weeks
        "weekly": 50,  # 50 working weeks
        "monthly": 12,  # 12 months
        "rarely": 4,  # quarterly
    }

    # Hourly rate for developer time (used for cost calculation)
    HOURLY_RATE = 75  # $75/hour average developer rate

    def __init__(self, callback=None):
        """
        Initialize ROI scorer

        Args:
            callback: Optional logging function
        """
        self.callback = callback

    def calculate_roi(
        self, item: Dict, readiness_score: Optional[Dict] = None
    ) -> ROIMetrics:
        """
        Calculate ROI metrics for an implementation item

        Args:
            item: Notable item from CORE-001 (dict with title, description, etc.)
            readiness_score: Optional readiness analysis from ReadinessAnalyzer

        Returns:
            ROIMetrics with complete ROI analysis
        """
        # Extract implementation time
        impl_time = self._extract_implementation_time(item, readiness_score)

        # Estimate time savings per use
        time_saved = self._estimate_time_savings(item)

        # Detect usage frequency
        frequency = self._detect_frequency(item)

        # Calculate annual savings
        annual_uses = self.FREQUENCY_MAP.get(frequency, 4)
        annual_savings_hours = (time_saved * annual_uses) / 60

        # Estimate costs
        cost = self._estimate_costs(item, impl_time)

        # Calculate ROI score
        roi_score = self._calculate_roi_score(annual_savings_hours, cost, impl_time)

        # Calculate breakeven period
        breakeven_weeks = self._calculate_breakeven(
            impl_time, time_saved, frequency, cost
        )

        # Generate recommendation
        recommendation, reasoning = self._generate_recommendation(
            roi_score, breakeven_weeks, impl_time
        )

        return ROIMetrics(
            implementation_time=impl_time,
            time_saved_per_use=time_saved,
            use_frequency=frequency,
            annual_time_savings=int(annual_savings_hours),
            cost=cost,
            roi_score=roi_score,
            breakeven_period=breakeven_weeks,
            recommendation=recommendation,
            reasoning=reasoning,
        )

    def _extract_implementation_time(
        self, item: Dict, readiness_score: Optional[Dict]
    ) -> int:
        """
        Extract implementation time from item or readiness score

        Args:
            item: Notable item dict
            readiness_score: Optional readiness analysis

        Returns:
            Implementation time in hours
        """
        # Check readiness score first
        if readiness_score and "setup_time" in readiness_score:
            return int(readiness_score["setup_time"] / 60)  # Convert minutes to hours

        # Check item metadata
        if "implementation_time" in item:
            time_str = item["implementation_time"].lower()
            if "min" in time_str:
                minutes = int(re.search(r"\d+", time_str).group())
                return max(1, int(minutes / 60))
            elif "hr" in time_str or "hour" in time_str:
                return int(re.search(r"\d+", time_str).group())
            elif "day" in time_str:
                days = int(re.search(r"\d+", time_str).group())
                return days * 8

        # Check complexity from readiness
        if readiness_score and "complexity" in readiness_score:
            complexity = readiness_score["complexity"]
            if complexity < 0.3:
                return 1  # Beginner: 1 hour
            elif complexity < 0.6:
                return 4  # Intermediate: 4 hours
            else:
                return 8  # Advanced: 8 hours

        # Default estimate based on item length
        description_length = len(item.get("description", ""))
        if description_length < 200:
            return 1
        elif description_length < 500:
            return 2
        else:
            return 4

    def _estimate_time_savings(self, item: Dict) -> int:
        """
        Estimate time saved per use in minutes

        Args:
            item: Notable item dict

        Returns:
            Time saved per use in minutes
        """
        text = f"{item.get('title', '')} {item.get('description', '')}".lower()

        # Look for explicit time mentions
        time_patterns = [
            r"saves?\s+(\d+)\s*(hour|hr)s?",
            r"saves?\s+(\d+)\s*(minute|min)s?",
            r"(\d+)\s*(hour|hr)s?\s+instead\s+of\s+(\d+)",
            r"reduces?\s+from\s+(\d+)\s*(hour|hr)s?",
            r"automate.*?(\d+)\s*(hour|hr)s?",
        ]

        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                value = int(match.group(1))
                unit = match.group(2) if len(match.groups()) > 1 else "min"
                if "hour" in unit or "hr" in unit:
                    return value * 60
                return value

        # Keyword-based estimation
        automation_keywords = [
            "automat",
            "no longer need",
            "instead of manually",
            "eliminates manual",
        ]
        high_impact_keywords = ["workflow", "process", "pipeline", "automation"]
        medium_impact_keywords = ["tool", "command", "script", "helper"]

        has_automation = any(kw in text for kw in automation_keywords)
        has_high_impact = any(kw in text for kw in high_impact_keywords)
        has_medium_impact = any(kw in text for kw in medium_impact_keywords)

        if has_automation:
            if has_high_impact:
                return 120  # 2 hours saved (major workflow automation)
            elif has_medium_impact:
                return 30  # 30 minutes saved (tool automation)
            return 15  # 15 minutes saved (simple automation)

        # Check for complexity indicators
        if has_high_impact:
            return 60  # 1 hour saved
        elif has_medium_impact:
            return 20  # 20 minutes saved
        else:
            return 5  # 5 minutes saved (minor improvement)

    def _detect_frequency(self, item: Dict) -> str:
        """
        Detect usage frequency from item description

        Args:
            item: Notable item dict

        Returns:
            Frequency string: "daily" | "weekly" | "monthly" | "rarely"
        """
        text = f"{item.get('title', '')} {item.get('description', '')}".lower()

        # Daily indicators
        daily_keywords = [
            "every time",
            "whenever you",
            "each time",
            "daily",
            "constantly",
            "always",
            "every project",
        ]
        if any(kw in text for kw in daily_keywords):
            return "daily"

        # Weekly indicators
        weekly_keywords = [
            "weekly",
            "sprint",
            "standup",
            "meeting",
            "report",
            "review",
        ]
        if any(kw in text for kw in weekly_keywords):
            return "weekly"

        # Monthly indicators
        monthly_keywords = ["monthly", "quarterly", "analysis", "summary"]
        if any(kw in text for kw in monthly_keywords):
            return "monthly"

        # Rarely indicators
        rarely_keywords = ["rarely", "occasionally", "sometimes", "when needed"]
        if any(kw in text for kw in rarely_keywords):
            return "rarely"

        # Default based on tag
        tag = item.get("tag", "").lower()
        if tag in ["protocol", "workflow"]:
            return "daily"
        elif tag in ["tool", "command"]:
            return "weekly"
        else:
            return "monthly"

    def _estimate_costs(self, item: Dict, impl_time: int) -> float:
        """
        Estimate implementation and ongoing costs

        Args:
            item: Notable item dict
            impl_time: Implementation time in hours

        Returns:
            Total cost in USD
        """
        text = f"{item.get('title', '')} {item.get('description', '')}".lower()

        # Implementation labor cost
        impl_cost = impl_time * self.HOURLY_RATE

        # API costs
        api_cost = 0
        if "api" in text or "gpt" in text or "claude" in text:
            # Estimate based on usage
            if "heavy" in text or "frequent" in text:
                api_cost = 50  # $50/month
            elif "moderate" in text:
                api_cost = 20  # $20/month
            else:
                api_cost = 5  # $5/month light usage

        # Tool subscription costs
        subscription_cost = 0
        if "paid" in text or "subscription" in text:
            if "enterprise" in text:
                subscription_cost = 100  # $100/month
            else:
                subscription_cost = 20  # $20/month

        # Annual recurring costs
        annual_recurring = (api_cost + subscription_cost) * 12

        # Total first-year cost
        return impl_cost + annual_recurring

    def _calculate_roi_score(
        self, annual_savings_hours: float, cost: float, impl_time: int
    ) -> float:
        """
        Calculate ROI score

        Args:
            annual_savings_hours: Hours saved per year
            cost: Total first-year cost
            impl_time: Implementation time in hours

        Returns:
            ROI score (higher is better)
        """
        # Convert annual savings to dollars
        annual_savings_dollars = annual_savings_hours * self.HOURLY_RATE

        # Net benefit
        net_benefit = annual_savings_dollars - cost

        # ROI = (net benefit) / (implementation time)
        # Avoid division by zero
        if impl_time == 0:
            return 0

        return net_benefit / impl_time

    def _calculate_breakeven(
        self, impl_time: int, time_saved: int, frequency: str, cost: float
    ) -> int:
        """
        Calculate breakeven period in weeks

        Args:
            impl_time: Implementation time in hours
            time_saved: Time saved per use in minutes
            frequency: Usage frequency
            cost: Total cost in USD

        Returns:
            Weeks until breakeven
        """
        # Uses per year
        annual_uses = self.FREQUENCY_MAP.get(frequency, 4)

        # Weekly uses
        weekly_uses = annual_uses / 52

        # Weekly time savings in hours
        weekly_savings_hours = (time_saved * weekly_uses) / 60

        # Weekly savings in dollars
        weekly_savings_dollars = weekly_savings_hours * self.HOURLY_RATE

        # Weeks to recover cost
        if weekly_savings_dollars <= 0:
            return 9999  # Never breaks even

        weeks = int(cost / weekly_savings_dollars)
        return max(1, weeks)

    def _generate_recommendation(
        self, roi_score: float, breakeven_weeks: int, impl_time: int
    ) -> tuple:
        """
        Generate priority recommendation and reasoning

        Args:
            roi_score: ROI score
            breakeven_weeks: Weeks until breakeven
            impl_time: Implementation time in hours

        Returns:
            Tuple of (recommendation, reasoning)
        """
        # High priority criteria
        if roi_score > 3750 and breakeven_weeks < 2:  # 50x ROI @ $75/hr
            return (
                "HIGH",
                f"Exceptional ROI ({roi_score:.0f}x). "
                f"Breaks even in {breakeven_weeks} week(s). "
                "Implement immediately.",
            )
        elif roi_score > 750 and breakeven_weeks < 8:  # 10x ROI
            return (
                "HIGH",
                f"Strong ROI ({roi_score:.0f}x). "
                f"Breaks even in {breakeven_weeks} week(s). "
                "High priority.",
            )

        # Medium priority criteria
        elif roi_score > 150 and breakeven_weeks < 16:  # 2x ROI
            return (
                "MEDIUM",
                f"Positive ROI ({roi_score:.0f}x). "
                f"Breaks even in {breakeven_weeks} week(s). "
                "Schedule for implementation.",
            )

        # Low priority
        else:
            if roi_score < 0:
                return (
                    "LOW",
                    f"Negative ROI ({roi_score:.0f}x). "
                    "Cost exceeds savings. "
                    "Consider only if strategic value.",
                )
            else:
                return (
                    "LOW",
                    f"Low ROI ({roi_score:.0f}x). "
                    f"Long breakeven ({breakeven_weeks} weeks). "
                    "Low priority.",
                )

    def batch_calculate(
        self, items: List[Dict], readiness_scores: Optional[Dict] = None
    ) -> Dict[str, ROIMetrics]:
        """
        Calculate ROI for multiple items

        Args:
            items: List of notable items
            readiness_scores: Optional dict of readiness scores by item ID

        Returns:
            Dict mapping item ID to ROIMetrics
        """
        results = {}
        for item in items:
            item_id = item.get("id", f"item_{len(results) + 1}")
            readiness = None
            if readiness_scores and item_id in readiness_scores:
                readiness = readiness_scores[item_id]

            try:
                roi = self.calculate_roi(item, readiness)
                results[item_id] = roi
                if self.callback:
                    self.callback(
                        f"ROI calculated for {item_id}: "
                        f"{roi.recommendation} priority "
                        f"(ROI: {roi.roi_score:.1f}x)"
                    )
            except Exception as e:
                if self.callback:
                    self.callback(f"Error calculating ROI for {item_id}: {e}")
                continue

        return results
