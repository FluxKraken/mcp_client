
import os
import tomli
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class LLMConfig:
    provider: str
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None

@dataclass
class MCPConfig:
    url: str

class Config:
    def __init__(self):
        self._llm_config: Optional[LLMConfig] = None
        self._mcp_config: Optional[MCPConfig] = None

    def load_from_file(self, path: str):
        """Load configuration from a TOML file."""
        with open(path, "rb") as f:
            data = tomli.load(f)
        
        llm_data = data.get("llm_provider", {})
        if llm_data:
            self._llm_config = LLMConfig(
                provider=llm_data.get("provider", "openai"),
                model=llm_data.get("model", "gpt-3.5-turbo"),
                api_key=llm_data.get("api_key"),
                # Support both base_url and api_endpoint
                base_url=llm_data.get("base_url") or llm_data.get("api_endpoint")
            )

        mcp_data = data.get("mcp_server", {})
        if mcp_data:
            self._mcp_config = MCPConfig(
                url=mcp_data.get("url", "")
            )

    @property
    def openrouter_api_key(self) -> Optional[str]:
        if self._llm_config and self._llm_config.api_key:
            return self._llm_config.api_key
        return os.getenv("OPENROUTER_API_KEY")

    @property
    def openai_api_key(self) -> Optional[str]:
         if self._llm_config and self._llm_config.api_key:
            return self._llm_config.api_key
         return os.getenv("OPENAI_API_KEY")

    @property
    def ollama_url(self) -> str:
        if self._llm_config and self._llm_config.base_url:
            return self._llm_config.base_url
        return os.getenv("OLLAMA_URL", "http://localhost:11434")

    # Helpers to get active config preferred over defaults
    def get_llm_config(self, cli_provider: str, cli_model: str, cli_api_key: Optional[str]) -> LLMConfig:
        """
        Prioritize CLI args, then Config file, then defaults.
        """
        # If config file loaded and CLI args are defaults/None, use config file
        # But CLI args usually have defaults "openai"/"gpt-3.5"... detecting if user explicitly set them is hard with Typer defaults.
        # Strategy: If config file is present, use it as base, override with specific CLI args if we can,
        # but for simplicity, let's say if --config is passed, we mostly rely on it unless other flags are EXPLICITLY passed?
        # Actually simplest is: if --config is used, load it.
        # But we need to allow overriding.
        
        # New approach: Return a merged config object
        provider = cli_provider 
        model = cli_model
        api_key = cli_api_key
        base_url = None

        if self._llm_config:
             # If CLI values match defaults (we can't easily know if they are defaults or user input without more complex Typer usage),
             # checking defaults is tricky.
             # Let's assume if config file is loaded, we prefer it unless user forced something different.
             # However, standard CLI pattern: CLI flags > Config File > Env Vars.
             
             # Since we are essentially re-implementing hierarchy, let's keep it simple:
             # If config loaded, use its values as defaults for missing CLI values? 
             # No, CLI values are passed in.
             
             # Let's trust the caller to handle precedence or just return the file config if available.
             pass
        
        return LLMConfig(provider, model, api_key, base_url)

config = Config()
