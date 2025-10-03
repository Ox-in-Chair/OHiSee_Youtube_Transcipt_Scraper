"""AI-Powered Search Query Optimizer using OpenAI GPT-4"""
from openai import OpenAI
from prompts import GODLY_SEARCH_PROMPT


def optimize_search_query(user_input, api_key=None):
    """
    Convert natural language to optimized YouTube search with advanced operators

    Args:
        user_input: User's description
        api_key: OpenAI API key

    Returns:
        Optimized query with operators ("quotes", OR, -)
        Falls back to original if optimization fails
    """
    if not api_key or not user_input:
        return user_input

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4",  # Premium model for 100% accuracy
            messages=[
                {"role": "system", "content": GODLY_SEARCH_PROMPT},
                {"role": "user", "content": user_input}
            ],
            max_tokens=60,  # Allow longer, more precise queries
            temperature=0.2  # More deterministic, less creative
        )

        optimized = response.choices[0].message.content.strip()

        # Remove outer quotes if AI wrapped entire response
        if optimized.startswith('"') and optimized.endswith('"') and optimized.count('"') == 2:
            optimized = optimized[1:-1]

        return optimized if optimized else user_input

    except Exception as e:
        print(f"Optimization failed: {e}")
        return user_input
