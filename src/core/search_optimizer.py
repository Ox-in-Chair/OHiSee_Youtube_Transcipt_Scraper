"""AI-Powered Search Query Optimizer using OpenAI GPT-4"""

from openai import OpenAI
from utils.prompts import GODLY_SEARCH_PROMPT


def optimize_search_query(user_input, api_key=None, duration=None, features=None, upload_days=None):
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
