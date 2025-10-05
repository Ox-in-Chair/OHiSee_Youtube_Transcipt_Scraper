"""AI-Powered Search Query Optimizer using OpenAI GPT-4"""

from openai import OpenAI
from utils.prompts import GODLY_SEARCH_PROMPT


def optimize_search_query(user_input, api_key=None, duration=None, features=None, upload_days=None):
    """
    Optimize user search query using GPT-4 for YouTube-friendly keywords.

    Args:
        user_input: Natural language search query from user
        api_key: OpenAI API key (optional)
        duration: Video duration filter (optional)
        features: Video features filter (optional)
        upload_days: Upload date filter in days (optional)

    Returns:
        Optimized query string with filter suffixes
    """
    if not user_input:
        return user_input
    from utils.filters import build_query_filters

    filter_suffix = build_query_filters(duration, features, upload_days)
    if not api_key:
        return user_input + filter_suffix
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": GODLY_SEARCH_PROMPT},
                {"role": "user", "content": user_input},
            ],
            max_tokens=80,
            temperature=0.3,
        )
        optimized = response.choices[0].message.content.strip()
        if optimized.startswith('"') and optimized.endswith('"') and optimized.count('"') == 2:
            optimized = optimized[1:-1]
        return (optimized + filter_suffix) if optimized else (user_input + filter_suffix)
    except Exception as e:
        print(f"Optimization failed: {e}")
        return user_input + filter_suffix


def get_synonym_expansion(query, api_key):
    """
    Ask GPT-4 to suggest broader synonym variations when search returns few results.

    Used by Tier 4 fallback strategy when all other search attempts fail.

    Args:
        query: Original search query that returned insufficient results
        api_key: OpenAI API key (required)

    Returns:
        Broader query string with synonyms, or None if expansion fails

    Example:
        Input:  "BRCGS manufacturing workflow"
        Output: "food safety quality management standards"
    """
    if not query or not api_key:
        return None

    prompt = f"""The YouTube search query "{query}" returned very few or zero results.

Suggest ONE broader variation using common synonyms that might find relevant videos.

Rules:
- Keep it 6-10 words maximum
- Use YouTube-friendly everyday terms
- Preserve core intent but broaden scope
- Replace technical jargon with common alternatives
- Output ONLY the new query, nothing else

New query:"""

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=30,
            temperature=0.3,
        )

        broader_query = response.choices[0].message.content.strip()

        # Strip quotes if present
        if broader_query.startswith('"') and broader_query.endswith('"'):
            broader_query = broader_query[1:-1]

        # Return None if same as input (no expansion occurred)
        return broader_query if broader_query != query else None

    except Exception:
        return None
