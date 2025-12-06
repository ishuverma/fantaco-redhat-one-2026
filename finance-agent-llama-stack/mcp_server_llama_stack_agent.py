#!/usr/bin/env python3
"""
MCP Server wrapping Llama Stack Finance Agent

This MCP server exposes the Llama Stack finance agent as an MCP tool.
It uses FastMCP with HTTP transport to provide a finance_agent tool that
accepts prompts and returns responses from the underlying agent.

Architecture:
┌─────────────────────────────────────────────┐
│         MCP Client                          │
│         (Connects via HTTP)                  │
└────────┬────────────────────────────────────┘
         │
         │ finance_agent(prompt)
         ▼
┌─────────────────────────────────────────────┐
│         FastMCP Server (This File)          │
│         - HTTP Transport                     │
│         - Tool: finance_agent               │
└────────┬────────────────────────────────────┘
         │
         │ Uses Llama Stack SDK
         ▼
┌─────────────────────────────────────────────┐
│         Llama Stack Agent                   │
│         - Calls Finance MCP Server          │
└─────────────────────────────────────────────┘
"""

import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from llama_stack_client import LlamaStackClient
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mcp_server_llama_stack.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = find_dotenv(usecwd=True)
if env_path:
    load_dotenv(env_path)
    logger.info(f"Loaded environment from: {env_path}")
else:
    logger.warning("No .env file found")

# Get port configuration
FINANCE_AGENT_PORT = int(os.getenv("FINANCE_AGENT_PORT"))
logger.info(f"FINANCE_AGENT_PORT: {FINANCE_AGENT_PORT}")

# Initialize FastMCP server with port configuration
logger.info("Initializing FastMCP server: Finance Agent MCP Server")
mcp = FastMCP("Finance Agent MCP Server", port=FINANCE_AGENT_PORT)

# Global Llama Stack client
llama_client = None

def get_llama_client():
    """Get or create Llama Stack client."""
    global llama_client
    if llama_client is None:
        LLAMA_STACK_BASE_URL = os.getenv("LLAMA_STACK_BASE_URL")
        logger.info(f"Initializing Llama Stack client with base_url: {LLAMA_STACK_BASE_URL}")
        llama_client = LlamaStackClient(base_url=LLAMA_STACK_BASE_URL)
        logger.info("Llama Stack client initialized successfully")
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
    logger.info(f"finance_agent called with prompt: {prompt}")
    try:
        client = get_llama_client()

        INFERENCE_MODEL = os.getenv("INFERENCE_MODEL", "ollama/llama3.2:3b")
        MCP_FINANCE_SERVER_URL = os.getenv("MCP_FINANCE_SERVER_URL")

        logger.info(f"Using inference model: {INFERENCE_MODEL}")
        logger.info(f"Using MCP finance server URL: {MCP_FINANCE_SERVER_URL}")

        if not MCP_FINANCE_SERVER_URL:
            logger.error("MCP_FINANCE_SERVER_URL not configured in environment")
            return "Error: MCP_FINANCE_SERVER_URL not configured in environment"

        # Use Llama Stack's Responses API with MCP tools
        logger.info("Calling Llama Stack responses.create API")
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
        logger.info(f"Agent response received: {agent_responses.output_text[:100]}...")
        return agent_responses.output_text

    except Exception as e:
        logger.error(f"Error executing finance agent: {str(e)}", exc_info=True)
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
    logger.info(f"finance_agent_detailed called with prompt: {prompt}")
    try:
        client = get_llama_client()

        INFERENCE_MODEL = os.getenv("INFERENCE_MODEL", "ollama/llama3.2:3b")
        MCP_FINANCE_SERVER_URL = os.getenv("MCP_FINANCE_SERVER_URL")

        logger.info(f"Using inference model: {INFERENCE_MODEL}")
        logger.info(f"Using MCP finance server URL: {MCP_FINANCE_SERVER_URL}")

        if not MCP_FINANCE_SERVER_URL:
            logger.error("MCP_FINANCE_SERVER_URL not configured in environment")
            return json.dumps({"error": "MCP_FINANCE_SERVER_URL not configured"})

        # Use Llama Stack's Responses API with MCP tools
        logger.info("Calling Llama Stack responses.create API (detailed mode)")
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
        logger.info("Building detailed execution trace")
        trace = []
        for i, output in enumerate(agent_responses.output):
            trace_item = {
                "step": i + 1,
                "type": output.type
            }

            if output.type == "mcp_list_tools":
                trace_item["server"] = output.server_label
                trace_item["tools"] = [t.name for t in output.tools]
                logger.debug(f"Step {i+1}: MCP list tools from {output.server_label}")

            elif output.type == "mcp_call":
                trace_item["tool_name"] = output.name
                trace_item["arguments"] = output.arguments
                if output.error:
                    trace_item["error"] = output.error
                    logger.warning(f"Step {i+1}: MCP call {output.name} failed: {output.error}")
                else:
                    logger.debug(f"Step {i+1}: MCP call {output.name}")

            elif output.type == "message":
                trace_item["role"] = output.role
                if hasattr(output.content[0], 'text'):
                    trace_item["content"] = output.content[0].text
                logger.debug(f"Step {i+1}: Message from {output.role}")

            trace.append(trace_item)

        result = {
            "trace": trace,
            "final_response": agent_responses.output_text
        }

        logger.info(f"Detailed agent response completed with {len(trace)} steps")
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error executing finance agent (detailed): {str(e)}", exc_info=True)
        return json.dumps({"error": f"Error executing finance agent: {str(e)}"})


if __name__ == "__main__":
    # Run the MCP server with streamable HTTP transport
    # The server will be available for HTTP streaming connections
    logger.info("Starting MCP server with streamable-http transport...")

    # Log all environment variables used by this server
    LLAMA_STACK_BASE_URL = os.getenv("LLAMA_STACK_BASE_URL")
    INFERENCE_MODEL = os.getenv("INFERENCE_MODEL")
    MCP_FINANCE_SERVER_URL = os.getenv("MCP_FINANCE_SERVER_URL")

    logger.info("=" * 60)
    logger.info("Environment Configuration:")
    logger.info(f"  LLAMA_STACK_BASE_URL: {LLAMA_STACK_BASE_URL}")
    logger.info(f"  INFERENCE_MODEL: {INFERENCE_MODEL}")
    logger.info(f"  MCP_FINANCE_SERVER_URL: {MCP_FINANCE_SERVER_URL}")
    logger.info(f"  FINANCE_AGENT_PORT: {FINANCE_AGENT_PORT}")
    logger.info("=" * 60)

    mcp.run(transport="streamable-http")
