"""YouTube Search Filters"""


def build_filter_string(filters):
    if not filters:
        return ""
    parts = []
    if (ud := filters.get("upload_date", "any")) != "any" and ud in [
        "hour",
        "today",
        "week",
        "month",
        "year",
    ]:
        parts.append(f"date:{ud}")
    if (sb := filters.get("sort_by", "relevance")) != "relevance" and sb in [
        "date",
        "views",
        "rating",
    ]:
        parts.append(f"sortby:{sb}")
    return ",".join(parts) if parts else ""


def build_query_filters(duration=None, features=None, upload_days=None):
    parts = []
    if duration == "short":
        parts.append(", short")
    elif duration == "long":
        parts.append(", long")
    if features:
        parts.extend([f", {f}" for f in features if f in ["cc", "hd", "4k", "live"]])
    if upload_days and upload_days != "any":
        parts.append(
            ", this week"
            if upload_days <= 7
            else (
                ", this month" if upload_days <= 31 else ", this year" if upload_days <= 365 else ""
            )
        )
    return "".join(parts)


def sanitize_query(query):
    """Preserve search operators for YouTube (quotes, OR, -)"""
    return query  # yt-dlp handles operators correctly


UPLOAD_DATE_OPTIONS = {
    "Any time": "any",
    "Last 7 days": 7,
    "Last 30 days": 30,
    "Last 90 days": 90,
    "Last 6 months": 180,
    "Last year": 365,
}
SORT_BY_OPTIONS = {
    "Relevance": "relevance",
    "Upload date": "date",
    "View count": "views",
    "Rating": "rating",
}
DURATION_OPTIONS = {
    "Any duration": None,
    "Short (< 4 min)": "short",
    "Medium (4-20 min)": None,
    "Long (> 20 min)": "long",
}
FEATURE_OPTIONS = ["Subtitles/CC", "HD", "4K", "Live"]
