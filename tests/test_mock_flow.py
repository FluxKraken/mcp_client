
import sys
import os
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from mcp_client.main import run_chat_loop
from mcp.types import CallToolResult, TextContent, Tool

# Mock data
MOCK_TOOL = Tool(
    name="get_weather",
    description="Get weather for a location",
    inputSchema={
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }
)

async def verify():
    print("Verifying MCP Client Logic...")

    # Mock Session context manager and session object
    mock_session = AsyncMock()
    mock_session.list_tools.return_value.tools = [MOCK_TOOL]
    mock_session.call_tool.return_value = CallToolResult(
        content=[TextContent(type="text", text="The weather in NY is Sunny")]
    )

    @asynccontextmanager
    async def mock_connect_sse(url):
        yield mock_session
    
    # Mock LLM Client
    mock_llm_response_tool_call = {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "arguments": '{"location": "NY"}'
                    }
                }]
            }
        }]
    }

    mock_llm_response_final = {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "It is sunny in NY.",
            }
        }]
    }

    with patch("mcp_client.main.connect_mcp_sse", side_effect=mock_connect_sse), \
         patch("mcp_client.main.LLMClient") as MockLLMClass, \
         patch("mcp_client.main.Prompt.ask", side_effect=["What is weather in NY?", "exit"]), \
         patch("mcp_client.main.Console") as MockConsole:
        
        mock_llm_instance = MockLLMClass.return_value
        # First call returns tool call, second call returns final answer
        mock_llm_instance.chat_completion = AsyncMock(side_effect=[
            mock_llm_response_tool_call,
            mock_llm_response_final
        ])

        await run_chat_loop("openai", "gpt-3.5", "http://fake-mcp")

        # Verifications
        print("Checking tool listing...")
        mock_session.list_tools.assert_called_once()
        
        print("Checking LLM call 1 (Tool Request)...")
        # first call should include user message
        call_args_1 = mock_llm_instance.chat_completion.call_args_list[0]
        assert call_args_1.kwargs['messages'][0]['content'] == "What is weather in NY?"
        
        print("Checking Tool Execution...")
        mock_session.call_tool.assert_awaited_with("get_weather", {"location": "NY"})
        
        print("Checking LLM call 2 (Tool Result)...")
        # second call should include tool result
        call_args_2 = mock_llm_instance.chat_completion.call_args_list[1]
        messages_2 = call_args_2.kwargs['messages']
        assert messages_2[-1]['role'] == 'tool'
        assert "Sunny" in messages_2[-1]['content']
        
        print("Verification Successful!")

from contextlib import asynccontextmanager

if __name__ == "__main__":
    asyncio.run(verify())
