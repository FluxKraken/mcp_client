
import sys
import os
import asyncio
from unittest.mock import AsyncMock, patch
from contextlib import asynccontextmanager

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

# Mock mcp module before importing src
from unittest.mock import MagicMock
sys.modules["mcp"] = MagicMock()
sys.modules["mcp.types"] = MagicMock()
sys.modules["mcp.client"] = MagicMock()
sys.modules["mcp.client.sse"] = MagicMock()
sys.modules["mcp.client.stdio"] = MagicMock()
sys.modules["mcp.client.session"] = MagicMock()

# Now import main
from mcp_client.main import main, run_chat_loop

@patch("mcp_client.main.run_chat_loop")
def test_config_loading(mock_loop):
    print("Verifying Config Loading...")
    
    # Path to test config
    config_path = os.path.join(os.getcwd(), "tests", "test_config.toml")
    
    # Run main with --config
    # We catch SystemExit because Typer exits
    try:
        from typer.testing import CliRunner
        from mcp_client.main import app
        runner = CliRunner()
        result = runner.invoke(app, ["--config", config_path])
    except SystemExit:
        pass

    # Verify run_chat_loop was called with values from config
    mock_loop.assert_called_with(
        "ollama",      # provider from config
        "llama2",      # model from config
        "http://localhost:9000/sse", # mcp_url from config
        None,           # api_key
        "http://custom-ollama:11434/v1" # base_url (mapped from api_endpoint)
    )
    print("Config Verification Successful!")

if __name__ == "__main__":
    test_config_loading()
