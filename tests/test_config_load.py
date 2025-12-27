
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
from mcp_client.main import main, run_chat_loop, cli_entry 

@patch("mcp_client.main.run_chat_loop")
def test_config_loading(mock_loop):
    print("Verifying Config Loading...")
    
    # Path to test config
    config_path = os.path.join(os.getcwd(), "tests", "test_config.toml")
    
    # Run cli_entry
    # We invoke it via Typer's CliRunner on the function itself, wrapping it in a Typer app temporarily
    # or just use typer.testing.CliRunner to invoke the function if we treat it as command.
    
    from typer.testing import CliRunner
    import typer
    runner = CliRunner()
    
    # Since cli_entry is just a function now, we need to wrap it in an app to test with CliRunner
    app = typer.Typer()
    app.command()(cli_entry)
    
    result = runner.invoke(app, ["--config", config_path])

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
