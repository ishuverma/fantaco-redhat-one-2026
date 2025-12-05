#!/usr/bin/env python3
"""
Test suite for the Customer Agent MCP Server

This test file demonstrates how to interact with the MCP server
using both direct function calls and via the MCP protocol.
"""

import os
import json
import asyncio
import pytest
from dotenv import load_dotenv, find_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
env_path = find_dotenv(usecwd=True)
if env_path:
    load_dotenv(env_path)


# --- Direct Function Tests ---
def test_customer_agent_import():
    """Test that we can import the MCP server module."""
    try:
        import mcp_server
        assert hasattr(mcp_server, 'customer_agent')
        assert hasattr(mcp_server, 'customer_agent_detailed')
        print("✅ MCP server module imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import mcp_server: {e}")


def test_customer_agent_direct():
    """Test calling the customer_agent function directly."""
    from mcp_server import customer_agent

    prompt = "Search customer with name Anabela Domingues"
    result = customer_agent(prompt)

    print(f"\n📝 Prompt: {prompt}")
    print(f"📤 Response: {result}")

    assert isinstance(result, str)
    assert len(result) > 0
    assert "Error" not in result or "not configured" in result
    print("✅ Direct customer_agent call successful")


def test_customer_agent_detailed_direct():
    """Test calling the customer_agent_detailed function directly."""
    from mcp_server import customer_agent_detailed

    prompt = "Give me list of customers"
    result = customer_agent_detailed(prompt)

    print(f"\n📝 Prompt: {prompt}")
    print(f"📤 Response: {result[:500]}...")  # Truncate for display

    assert isinstance(result, str)
    assert len(result) > 0

    # Try to parse as JSON
    try:
        data = json.loads(result)
        assert "trace" in data or "error" in data
        if "trace" in data:
            assert "final_response" in data
        print("✅ Direct customer_agent_detailed call successful")
    except json.JSONDecodeError:
        pytest.fail("Response is not valid JSON")


# --- MCP Protocol Tests ---
@pytest.mark.asyncio
async def test_mcp_server_list_tools():
    """Test listing tools via MCP protocol."""
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env=os.environ.copy()
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()

            print(f"\n🔧 Available tools: {[tool.name for tool in tools.tools]}")

            assert len(tools.tools) >= 2
            tool_names = [tool.name for tool in tools.tools]
            assert "customer_agent" in tool_names
            assert "customer_agent_detailed" in tool_names

            print("✅ MCP server tools listed successfully")


@pytest.mark.asyncio
async def test_mcp_server_call_customer_agent():
    """Test calling customer_agent via MCP protocol."""
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env=os.environ.copy()
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Call the customer_agent tool
            prompt = "Search customer with email test@example.com"
            result = await session.call_tool(
                "customer_agent",
                arguments={"prompt": prompt}
            )

            print(f"\n📝 Prompt: {prompt}")
            print(f"📤 Response: {result.content}")

            assert result is not None
            assert len(result.content) > 0

            print("✅ MCP customer_agent tool call successful")


@pytest.mark.asyncio
async def test_mcp_server_call_customer_agent_detailed():
    """Test calling customer_agent_detailed via MCP protocol."""
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env=os.environ.copy()
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Call the customer_agent_detailed tool
            prompt = "Find all customers from Fantaco company"
            result = await session.call_tool(
                "customer_agent_detailed",
                arguments={"prompt": prompt}
            )

            print(f"\n📝 Prompt: {prompt}")
            print(f"📤 Response: {result.content[0].text[:500]}...")

            assert result is not None
            assert len(result.content) > 0

            # Parse the JSON response
            response_text = result.content[0].text
            data = json.loads(response_text)

            assert "trace" in data or "error" in data

            print("✅ MCP customer_agent_detailed tool call successful")


# --- Manual Test Runner ---
def run_direct_tests():
    """Run direct function tests without pytest."""
    print("\n" + "=" * 80)
    print("Running Direct Function Tests")
    print("=" * 80)

    try:
        test_customer_agent_import()
        test_customer_agent_direct()
        test_customer_agent_detailed_direct()
        print("\n✅ All direct tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


async def run_mcp_tests():
    """Run MCP protocol tests without pytest."""
    print("\n" + "=" * 80)
    print("Running MCP Protocol Tests")
    print("=" * 80)

    try:
        await test_mcp_server_list_tools()
        await test_mcp_server_call_customer_agent()
        await test_mcp_server_call_customer_agent_detailed()
        print("\n✅ All MCP tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


def main():
    """Main test runner."""
    print("=" * 80)
    print("Customer Agent MCP Server - Test Suite")
    print("=" * 80)

    # Check environment configuration
    required_vars = ["LLAMA_STACK_BASE_URL", "MCP_CUSTOMER_SERVER_URL", "INFERENCE_MODEL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"\n⚠️  Warning: Missing environment variables: {missing_vars}")
        print("Some tests may fail. Please check your .env file.")
    else:
        print("\n✅ All required environment variables are set")

    # Run direct tests
    run_direct_tests()

    # Run MCP protocol tests
    print("\n" + "=" * 80)
    print("Note: MCP protocol tests require the MCP server to be runnable")
    print("Skipping async MCP tests in direct execution mode.")
    print("To run MCP tests, use: pytest test_mcp_server.py")
    print("=" * 80)


if __name__ == "__main__":
    main()
