"""
Gemini client wrapper used by PawPal+.

Handles:
- Configuring the Gemini client from the GEMINI_API_KEY environment variable
- Supplies specific prompt to receive alternative time recommendations.

"""

import os
from google import genai

# Central place to update the model name if needed.
# You can swap this for a different Gemini model in the future.
GEMINI_MODEL_NAME = "gemini-flash-lite-latest"


class GeminiClient:
    """
    Simple wrapper around the Gemini model.

    Usage:
        client = GeminiClient()
        answer = client.naive_answer_over_full_docs(query, all_text)
        # or
        answer = client.answer_from_snippets(query, snippets)
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Missing GEMINI_API_KEY environment variable. "
                "Set it in your shell or .env file to enable LLM features."
            )
        self.client = genai.Client(api_key=api_key)
    
    def get_client_recommendation(self, prompt: str) -> str:
        """Get Gemini recommendation for scheduling conflict."""
        response = self.client.models.generate_content(
                    model=GEMINI_MODEL_NAME,
                    contents=prompt
                )
        return response.text
