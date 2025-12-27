
import httpx
from typing import List, Dict, Any, Optional
from .config import config

class LLMClient:
    def __init__(self, provider: str = "openai", model: str = "gpt-3.5-turbo", api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

        if provider == "ollama":
            self.base_url = self.base_url or f"{config.ollama_url}/v1"
            self.api_key = "ollama" # Ollama doesn't strictly need one but OpenAI client might
        elif provider == "openrouter":
            self.base_url = "https://openrouter.ai/api/v1"
            self.api_key = self.api_key or config.openrouter_api_key
        elif provider == "openai":
            self.api_key = self.api_key or config.openai_api_key

    async def chat_completion(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        if self.provider == "openrouter":
             headers["HTTP-Referer"] = "https://github.com/mcp-client"
             headers["X-Title"] = "MCP Client"

        payload = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=60.0 # Interaction might take time
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error calling LLM: {e}")
                if hasattr(e, 'response') and e.response:
                     print(f"Response body: {e.response.text}")
                raise
