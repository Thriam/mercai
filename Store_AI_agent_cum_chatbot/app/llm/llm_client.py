import requests
import json
from typing import Optional
from app.config.settings import settings
from app.config.logging_config import logger

class LLMClient:
    """OpenRouter LLM client for generating responses."""

    def __init__(self):
        """Initialize LLM client."""
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_MODEL

    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate response from LLM.

        Args:
            prompt: The prompt to send to LLM
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"LLM generation error: {str(e)}")
            raise

    @staticmethod
    def parse_json_response(response: str) -> dict:
        """
        Parse JSON from LLM response, stripping markdown if needed.

        Args:
            response: Raw LLM response

        Returns:
            Parsed JSON dictionary
        """
        # Remove markdown code blocks if present
        if '```json' in response:
            response = response.split('```json')[1].split('```')[0]
        elif '```' in response:
            response = response.split('```')[1].split('```')[0]

        return json.loads(response.strip())
