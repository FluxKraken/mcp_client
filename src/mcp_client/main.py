
import asyncio
import typer
import json
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from dotenv import load_dotenv

from .client import connect_mcp_sse
from .llm import LLMClient
from .config import config

# app = typer.Typer() # Removed app usage in favor of typer.run for single-command CLI
console = Console()

async def run_chat_loop(
    provider: str,
    model: str,
    mcp_url: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None
):
    console.print(f"[bold green]Connecting to MCP Server at {mcp_url}...[/bold green]")
    
    try:
        async with connect_mcp_sse(mcp_url) as session:
            console.print("[bold green]Connected to MCP Server![/bold green]")
            
            # Fetch available tools
            tools_result = await session.list_tools()
            available_tools = tools_result.tools
            console.print(f"[dim]Loaded {len(available_tools)} tools.[/dim]")
            
            # Convert MCP tools to OpenAI format
            openai_tools = []
            for tool in available_tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })

            llm_client = LLMClient(provider=provider, model=model, api_key=api_key, base_url=base_url)
            messages: List[Dict[str, Any]] = []

            console.print("[bold blue]Chat started! Type 'exit' or 'quit' to end.[/bold blue]")
            
            while True:
                user_input = Prompt.ask("[bold yellow]You[/bold yellow]")
                
                if user_input.lower() in ["exit", "quit"]:
                    break
                
                messages.append({"role": "user", "content": user_input})
                
                # Turn for LLM
                while True:
                    with console.status("[bold green]Thinking...[/bold green]"):
                        response = await llm_client.chat_completion(
                            messages=messages,
                            tools=openai_tools if openai_tools else None
                        )

                    message = response["choices"][0]["message"]
                    messages.append(message)

                    if message.get("tool_calls"):
                        # Handle tool calls
                        for tool_call in message["tool_calls"]:
                            fc = tool_call["function"]
                            t_name = fc["name"]
                            t_args = json.loads(fc["arguments"])
                            
                            console.print(f"[dim]Executing tool {t_name}...[/dim]")
                            
                            try:
                                result = await session.call_tool(t_name, t_args)
                                # MCP returns CallToolResult with content list
                                content_str = ""
                                for content in result.content:
                                    if content.type == "text":
                                        content_str += content.text
                                    elif content.type == "image":
                                        content_str += "[Image]" # Simplify for now
                                    else:
                                        content_str += str(content)

                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call["id"],
                                    "content": content_str
                                })
                            except Exception as e:
                                console.print(f"[bold red]Tool execution failed: {e}[/bold red]")
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call["id"],
                                    "content": f"Error executing tool: {str(e)}"
                                })
                        # Loop back to let LLM process tool results
                        continue
                    else:
                        # Final response
                        content = message.get("content")
                        if content:
                            console.print("[bold green]Assistant[/bold green]:")
                            console.print(Markdown(content))
                        break
                        
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        
        # Handle TaskGroup exceptions (Python 3.11+)
        if hasattr(e, 'exceptions'):
            for i, exc in enumerate(e.exceptions):
                console.print(f"[bold red]Sub-exception {i+1}: {exc}[/bold red]")
                if "Child exited without calling task_status.started()" in str(exc):
                    console.print("[bold yellow]Hint: This usually means the MCP Client could not connect to the SSE endpoint. Check if the URL is correct and reachable.[/bold yellow]")


def cli_entry(
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Path to TOML configuration file"),
    provider: Optional[str] = typer.Option(None, help="LLM Provider: openai, openrouter, ollama"),
    model: Optional[str] = typer.Option(None, help="Model name"),
    mcp_url: Optional[str] = typer.Option(None, help="URL of the MCP Server (SSE)"),
    api_key: Optional[str] = typer.Option(None, envvar="LLM_API_KEY", help="API Key for the provider"),
    api_endpoint: Optional[str] = typer.Option(None, "--api-endpoint", help="Custom API Endpoint (Base URL) for the LLM")
):
    """
    Start the MCP Client Chat.
    """
    # 1. Load config file if provided
    if config_file:
        try:
            config.load_from_file(config_file)
            console.print(f"[dim]Loaded config from {config_file}[/dim]")
        except Exception as e:
            console.print(f"[bold red]Failed to load config file: {e}[/bold red]")
            raise typer.Exit(code=1)

    # 2. Determine final values: CLI > Config File > Defaults
    
    # Helper to resolve value
    def resolve(cli_val, config_obj, config_attr, default):
        if cli_val is not None:
            return cli_val
        if config_obj and getattr(config_obj, config_attr, None):
            return getattr(config_obj, config_attr)
        return default

    final_provider = resolve(provider, config._llm_config, 'provider', "openai")
    final_model = resolve(model, config._llm_config, 'model', "gpt-3.5-turbo")
    final_api_key = resolve(api_key, config._llm_config, 'api_key', None)
    final_base_url = resolve(api_endpoint, config._llm_config, 'base_url', None)
    
    # MCP URL is required eventually
    final_mcp_url = resolve(mcp_url, config._mcp_config, 'url', None)

    if not final_mcp_url:
        console.print("[bold red]Error: MCP Server URL is required via --mcp-url or config file.[/bold red]")
        raise typer.Exit(code=1)

    asyncio.run(run_chat_loop(final_provider, final_model, final_mcp_url, final_api_key, final_base_url))

def main():
    """Entry point for the console script."""
    typer.run(cli_entry)

if __name__ == "__main__":
    main()
