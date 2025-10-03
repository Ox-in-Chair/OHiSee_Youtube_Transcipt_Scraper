"""YouTube Search Filters"""
def build_filter_string(filters):
    """Build yt-dlp filter string from filter dict"""
    if not filters:
        return ""
    parts = []
    upload_date = filters.get('upload_date', 'any')
    if upload_date != 'any' and upload_date in ['hour', 'today', 'week', 'month', 'year']:
        parts.append(f"date:{upload_date}")
    sort_by = filters.get('sort_by', 'relevance')
    if sort_by != 'relevance' and sort_by in ['date', 'views', 'rating']:
        parts.append(f"sortby:{sort_by}")
    return ','.join(parts) if parts else ""

def sanitize_query(query):
    """Preserve search operators for YouTube (quotes, OR, -)"""
    return query  # yt-dlp handles operators correctly

UPLOAD_DATE_OPTIONS = {'Any time': 'any', 'Last 7 days': 7, 'Last 30 days': 30,
                        'Last 90 days': 90, 'Last 6 months': 180, 'Last year': 365}
SORT_BY_OPTIONS = {'Relevance': 'relevance', 'Upload date': 'date',
                   'View count': 'views', 'Rating': 'rating'}
