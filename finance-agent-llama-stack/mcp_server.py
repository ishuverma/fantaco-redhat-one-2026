#!/usr/bin/env python3
"""
MCP Server wrapping Llama Stack Finance Agent

This MCP server exposes the Llama Stack finance agent as an MCP tool.
It uses FastMCP with SSE transport to provide a finance_agent tool that
accepts prompts and returns responses from the underlying agent.

Architecture:
┌─────────────────────────────────────────────┐
│         MCP Client                          │
│         (Connects via SSE)                  │
└────────┬────────────────────────────────────┘
         │
         │ finance_agent(prompt)
         ▼
┌─────────────────────────────────────────────┐
│         FastMCP Server (This File)          │
│         - SSE Transport                     │
│         - Tool: finance_agent               │
└────────┬────────────────────────────────────┘
         │
         │ Uses Llama Stack SDK
         ▼
┌─────────────────────────────────────────────┐
│         Llama Stack Agent                   │
│         (lls_finance_agent.py)              │
│         - Calls Finance MCP Server          │
└─────────────────────────────────────────────┘
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from llama_stack_client import LlamaStackClient
from mcp.server.fastmcp import FastMCP

# Load environment variables
env_path = find_dotenv(usecwd=True)
if env_path:
    load_dotenv(env_path)

# Initialize FastMCP server with SSE transport
mcp = FastMCP("Finance Agent MCP Server")

# Global Llama Stack client
llama_client = None


def get_llama_client():
    """Get or create Llama Stack client."""
    global llama_client
    if llama_client is None:
        LLAMA_STACK_BASE_URL = os.getenv("LLAMA_STACK_BASE_URL", "http://localhost:8321")
        llama_client = LlamaStackClient(base_url=LLAMA_STACK_BASE_URL)
    return llama_client


@mcp.tool()
def finance_agent(prompt: str) -> str:
    """
    Execute the finance agent with the given prompt.

    This tool wraps the Llama Stack finance agent, which uses MCP tools
    from the finance microservice to answer questions about orders, invoices,
    and financial transactions.

    Args:
        prompt: The question or instruction for the finance agent

    Returns:
        The agent's response as a string

    Examples:
        - "Get order history for customer TRADH"
        - "Show me all invoices for customer LONEP"
        - "Find orders with amount greater than 1000"
        - "List all pending invoices"
    """
    try:
        client = get_llama_client()

        INFERENCE_MODEL = os.getenv("INFERENCE_MODEL", "ollama/llama3.2:3b")
        MCP_FINANCE_SERVER_URL = os.getenv("MCP_FINANCE_SERVER_URL")

        if not MCP_FINANCE_SERVER_URL:
            return "Error: MCP_FINANCE_SERVER_URL not configured in environment"

        # Use Llama Stack's Responses API with MCP tools
        agent_responses = client.responses.create(
            model=INFERENCE_MODEL,
            input=prompt,
            tools=[
                {
                    "type": "mcp",
                    "server_url": MCP_FINANCE_SERVER_URL,
                    "server_label": "FINANCE",
                }
            ],
        )

        # Return the final text response
        return agent_responses.output_text

    except Exception as e:
        return f"Error executing finance agent: {str(e)}"


@mcp.tool()
def finance_agent_detailed(prompt: str) -> str:
    """
    Execute the finance agent with detailed execution trace.

    This tool provides the same functionality as finance_agent but includes
    detailed information about tool discovery, tool calls, and execution steps.

    Args:
        prompt: The question or instruction for the finance agent

    Returns:
        A detailed JSON string containing the execution trace and final response
    """
    try:
        client = get_llama_client()

        INFERENCE_MODEL = os.getenv("INFERENCE_MODEL", "ollama/llama3.2:3b")
        MCP_FINANCE_SERVER_URL = os.getenv("MCP_FINANCE_SERVER_URL")

        if not MCP_FINANCE_SERVER_URL:
            return json.dumps({"error": "MCP_FINANCE_SERVER_URL not configured"})

        # Use Llama Stack's Responses API with MCP tools
        agent_responses = client.responses.create(
            model=INFERENCE_MODEL,
            input=prompt,
            tools=[
                {
                    "type": "mcp",
                    "server_url": MCP_FINANCE_SERVER_URL,
                    "server_label": "FINANCE",
                }
            ],
        )

        # Build detailed trace
        trace = []
        for i, output in enumerate(agent_responses.output):
            trace_item = {
                "step": i + 1,
                "type": output.type
            }

            if output.type == "mcp_list_tools":
                trace_item["server"] = output.server_label
                trace_item["tools"] = [t.name for t in output.tools]

            elif output.type == "mcp_call":
                trace_item["tool_name"] = output.name
                trace_item["arguments"] = output.arguments
                if output.error:
                    trace_item["error"] = output.error

            elif output.type == "message":
                trace_item["role"] = output.role
                if hasattr(output.content[0], 'text'):
                    trace_item["content"] = output.content[0].text

            trace.append(trace_item)

        result = {
            "trace": trace,
            "final_response": agent_responses.output_text
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error executing finance agent: {str(e)}"})


if __name__ == "__main__":
    # Run the MCP server with SSE transport
    # The server will be available at http://localhost:8000/sse by default
    mcp.run(transport="sse")
