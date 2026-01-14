"""
MCP Streamable HTTP Component for Langflow

This component connects to MCP servers using the Streamable HTTP transport protocol.
Streamable HTTP uses standard HTTP POST but returns SSE-formatted responses.
Sessions are managed via the mcp-session-id header.

Place this file in your Langflow custom components folder or upload it via the UI.
"""

import httpx
import json
from typing import Any

from langflow.custom import Component
from langflow.io import MessageTextInput, Output, SecretStrInput, StrInput
from langflow.schema import Data
from langflow.schema.message import Message
from langchain_core.tools import StructuredTool


class MCPStreamableHTTPComponent(Component):
    display_name = "MCP Streamable HTTP"
    description = "Connects to an MCP server using Streamable HTTP transport and exposes its tools."
    icon = "globe"
    name = "MCPStreamableHTTP"

    # Session ID storage
    _session_id: str | None = None

    inputs = [
        StrInput(
            name="server_url",
            display_name="MCP Server URL",
            info="The URL of your MCP server (e.g., https://mcp-customer.apps.cluster.com/mcp)",
            required=True,
        ),
        StrInput(
            name="server_name",
            display_name="Server Name",
            info="A friendly name for this MCP server (e.g., 'Customer Service', 'Finance')",
            value="MCP Server",
            required=True,
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key (optional)",
            info="API key for authentication if required by the MCP server",
            required=False,
        ),
        MessageTextInput(
            name="input_value",
            display_name="Input",
            info="Input message to process with MCP tools",
            required=False,
        ),
    ]

    outputs = [
        Output(display_name="Tools", name="tools", method="get_tools", types=["Tool"]),
        Output(display_name="Tool List", name="tool_list", method="list_tools"),
    ]

    def _get_headers(self, include_session: bool = False) -> dict:
        """Build headers for MCP requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Cache-Control": "no-cache",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if include_session and self._session_id:
            headers["mcp-session-id"] = self._session_id
        return headers

    def _parse_sse_response(self, text: str) -> dict:
        """Parse SSE-formatted response and extract JSON data."""
        # SSE format:
        # event: message
        # data: {"jsonrpc": "2.0", ...}
        lines = text.strip().split('\n')
        for line in lines:
            if line.startswith('data: '):
                json_str = line[6:]  # Remove 'data: ' prefix
                return json.loads(json_str)
        # If no SSE format, try parsing as plain JSON
        return json.loads(text)

    def _initialize_session(self) -> dict:
        """Initialize the MCP session and store the session ID."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "langflow-mcp-client",
                    "version": "1.0.0"
                }
            }
        }

        with httpx.Client(timeout=30.0, verify=False) as client:
            # Step 1: Send initialize request
            response = client.post(
                self.server_url,
                json=payload,
                headers=self._get_headers(include_session=False),
            )
            response.raise_for_status()

            # Extract and store session ID from response headers
            self._session_id = response.headers.get("mcp-session-id")

            # Step 2: Send initialized notification (required by MCP protocol)
            notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            client.post(
                self.server_url,
                json=notification,
                headers=self._get_headers(include_session=True),
            )

            return self._parse_sse_response(response.text)

    def _make_request(self, method: str, params: dict | None = None) -> dict:
        """Make a JSON-RPC request to the MCP server with session ID."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
        }
        if params:
            payload["params"] = params

        with httpx.Client(timeout=30.0, verify=False) as client:
            response = client.post(
                self.server_url,
                json=payload,
                headers=self._get_headers(include_session=True),
            )
            response.raise_for_status()
            return self._parse_sse_response(response.text)

    def _list_tools_from_server(self) -> list[dict]:
        """Fetch the list of available tools from the MCP server."""
        try:
            # Initialize session first (this sets self._session_id)
            self._initialize_session()

            # Then list tools using the session ID
            result = self._make_request("tools/list")
            if "result" in result and "tools" in result["result"]:
                return result["result"]["tools"]
            return []
        except Exception as e:
            self.log(f"Error listing tools: {e}")
            return []

    def _call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Call a specific tool on the MCP server."""
        try:
            # Ensure we have a session
            if not self._session_id:
                self._initialize_session()

            result = self._make_request(
                "tools/call",
                {
                    "name": tool_name,
                    "arguments": arguments
                }
            )
            if "result" in result:
                content = result["result"].get("content", [])
                # Extract text from content blocks
                texts = []
                for item in content:
                    if item.get("type") == "text":
                        texts.append(item.get("text", ""))
                return "\n".join(texts) if texts else str(result["result"])
            elif "error" in result:
                return f"Error: {result['error'].get('message', 'Unknown error')}"
            return str(result)
        except Exception as e:
            return f"Error calling tool {tool_name}: {e}"

    def _create_langchain_tool(self, tool_info: dict) -> StructuredTool:
        """Create a LangChain tool from MCP tool info."""
        tool_name = tool_info["name"]
        description = tool_info.get("description", f"Tool: {tool_name}")
        input_schema = tool_info.get("inputSchema", {"type": "object", "properties": {}})

        # Capture self for closure
        component = self

        def tool_func(**kwargs) -> str:
            return component._call_tool(tool_name, kwargs)

        return StructuredTool.from_function(
            func=tool_func,
            name=tool_name,
            description=description,
            args_schema=None,  # Could parse inputSchema to create Pydantic model
        )

    def get_tools(self) -> list:
        """Get tools as LangChain tools for use with agents."""
        mcp_tools = self._list_tools_from_server()
        langchain_tools = []

        for tool_info in mcp_tools:
            try:
                lc_tool = self._create_langchain_tool(tool_info)
                langchain_tools.append(lc_tool)
            except Exception as e:
                self.log(f"Error creating tool {tool_info.get('name')}: {e}")

        return langchain_tools

    def list_tools(self) -> Data:
        """List available tools from the MCP server."""
        tools = self._list_tools_from_server()
        tool_names = [t.get("name", "unknown") for t in tools]

        return Data(
            data={
                "server_name": self.server_name,
                "server_url": self.server_url,
                "tools": tools,
                "tool_names": tool_names,
            }
        )
