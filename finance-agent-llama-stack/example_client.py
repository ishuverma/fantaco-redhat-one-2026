#!/usr/bin/env python3
"""
Example MCP Client for Finance Agent MCP Server

This script demonstrates how to connect to the Finance Agent MCP Server
via SSE transport and call the available tools.
"""

import asyncio
import json
from mcp import ClientSession
from mcp.client.sse import sse_client


async def main():
    """Main client function."""
    print("=" * 80)
    print("Finance Agent MCP Server - Example Client")
    print("=" * 80)

    # Connect to the MCP server via SSE
    # By default, FastMCP runs on http://localhost:8000/sse
    server_url = "http://localhost:8000/sse"

    print(f"\n🌐 Connecting to MCP server at: {server_url}")

    async with sse_client(server_url) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            print("✅ Connected to MCP server\n")

            # List available tools
            print("📋 Listing available tools...")
            tools = await session.list_tools()

            for tool in tools.tools:
                print(f"\n  Tool: {tool.name}")
                print(f"  Description: {tool.description}")
                if tool.inputSchema:
                    print(f"  Parameters: {json.dumps(tool.inputSchema.get('properties', {}), indent=4)}")

            # Example 1: Simple order history query
            print("\n" + "=" * 80)
            print("Example 1: Order History Query")
            print("=" * 80)

            prompt1 = "Get order history for customer LONEP"
            print(f"📝 Prompt: {prompt1}")

            result1 = await session.call_tool(
                "finance_agent",
                arguments={"prompt": prompt1}
            )

            print(f"📤 Response:\n{result1.content[0].text}\n")

            # Example 2: Invoice search with detailed trace
            print("=" * 80)
            print("Example 2: Invoice Search (Detailed)")
            print("=" * 80)

            prompt2 = "Show me all invoices for customer LONEP"
            print(f"📝 Prompt: {prompt2}")

            result2 = await session.call_tool(
                "finance_agent_detailed",
                arguments={"prompt": prompt2}
            )

            response_data = json.loads(result2.content[0].text)
            print(f"📤 Execution Trace:")
            for step in response_data.get("trace", []):
                print(f"\n  Step {step['step']}: {step['type']}")
                if "tools" in step:
                    print(f"    Available tools: {step['tools']}")
                if "tool_name" in step:
                    print(f"    Tool called: {step['tool_name']}")
                    print(f"    Arguments: {step['arguments']}")

            print(f"\n📤 Final Response:\n{response_data.get('final_response', 'No response')}\n")

            # Example 3: Custom financial query
            print("=" * 80)
            print("Example 3: Custom Financial Query")
            print("=" * 80)

            prompt3 = "Find orders with amount greater than 1000"
            print(f"📝 Prompt: {prompt3}")

            result3 = await session.call_tool(
                "finance_agent",
                arguments={"prompt": prompt3}
            )

            print(f"📤 Response:\n{result3.content[0].text}\n")

    print("=" * 80)
    print("Example completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
