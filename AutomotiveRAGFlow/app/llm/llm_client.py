import json
import requests


class LLMClient:
    # Original Ollama init:
    # def __init__(self, base_url: str, model_name: str):
    #     self.base_url = base_url.rstrip("/")
    #     self.model_name = model_name
    def __init__(self, base_url: str, model_name: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.api_key = api_key

    # Original Ollama generate:
    # def generate(self, prompt: str) -> str:
    #     response = requests.post(
    #         f"{self.base_url}/api/generate",
    #         json={
    #             "model": self.model_name,
    #             "prompt": prompt,
    #             "stream": False,
    #         },
    #         timeout=180,
    #     )
    #     response.raise_for_status()
    #     data = response.json()
    #     return data.get("response", "")
    def generate(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://blackbox.ai",
            "X-Title": "AutomotiveRAGFlow",
            "Content-Type": "application/json",
        }
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json={
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    @staticmethod
    def parse_json_response(raw_text: str) -> dict:
        raw_text = raw_text.strip()

        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text.replace("```", "").strip()

        return json.loads(raw_text)