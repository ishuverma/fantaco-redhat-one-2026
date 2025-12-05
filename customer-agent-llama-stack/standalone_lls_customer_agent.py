#!/usr/bin/env python3
"""
Building Agents with Llama Stack Agentic Capabilities

This script demonstrates building agentic systems using Llama Stack's native
capabilities for tool calling with MCP (Model Context Protocol) integration.

For more information check:
- Llama Stack Responses API docs: https://llamastack.github.io/docs/building_applications/responses_vs_agents#lls-agents-api
- OpenAI Responses API: https://platform.openai.com/docs/api-reference/responses

Architecture:
┌─────────────────────────────────────────────┐
│         Llama Stack SDK                     │
│         (LlamaStackClient)                  │
└────────┬────────────────────────────────────┘
         │
         │ client.responses.create()
         ▼
┌─────────────────┐   ┌──────────────────────┐
│  Llama Stack    │   │  MCP Servers         │
│  Responses API  │   │  (Server-side MCP)   │
│  - vLLM Engine  │──▶│ - Customer Service  │
│  - Inference    │   │                      │
│  - Tool Calling │   │  - Tool Execution    │
└─────────────────┘   └──────────────────────┘

Configuration:
This script uses environment variables from `.env` file in the project root.
Create your own `.env` file based on `.env.example`.
"""

# Core imports
import os
import sys
import json
from pathlib import Path
from datetime import date
from dotenv import load_dotenv, find_dotenv
from llama_stack_client import LlamaStackClient, Agent


# --- Load environment variables ---
def load_environment():
    """Load environment variables and verify configuration."""
    # Automatically detect the nearest .env (walks up from current directory)
    env_path = find_dotenv(usecwd=True)
    if env_path:
        load_dotenv(env_path)
        print(f"📁 Loading environment from: {env_path}")
        print("✅ .env file FOUND and loaded")
    else:
        default_path = Path.cwd() / ".env"
        print(f"📁 No .env found via find_dotenv — checked: {default_path}")
        print("⚠️  .env file NOT FOUND")

    # --- Verify Python interpreter ---
    print(f"\n🐍 Python: {sys.executable}")

    # Detect if running inside a virtual environment
    in_venv = (
        hasattr(sys, "real_prefix") or
        (getattr(sys, "base_prefix", sys.prefix) != sys.prefix) or
        "VIRTUAL_ENV" in os.environ or
        "CONDA_PREFIX" in os.environ
    )

    if in_venv:
        print("✅ Using virtual environment - CORRECT!")
    else:
        print("⚠️  Using global Python - Consider using a virtual environment!")


# --- Helper Functions ---
def pretty_print(obj) -> None:
    """
    Print object as formatted JSON.
    Handles nested objects and lists.
    """
    def recursive_serializer(o):
        if hasattr(o, '__dict__'):
            return o.__dict__
        if isinstance(o, date):
            return o.isoformat()
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

    data_to_serialize = obj.__dict__ if hasattr(obj, "__dict__") else obj
    print(json.dumps(data_to_serialize, indent=2, default=recursive_serializer))


def create_llama_stack_client():
    """Configure Llama Stack Connection."""
    # Get configuration from environment variables
    LLAMA_STACK_BASE_URL = os.getenv("LLAMA_STACK_BASE_URL")
    LLAMA_STACK_OPENAI_ENDPOINT = os.getenv("LLAMA_STACK_OPENAI_ENDPOINT")

    print("\n🌐 Llama Stack Configuration:")
    print(f"   Base URL: {LLAMA_STACK_BASE_URL}")
    print(f"   OpenAI Endpoint: {LLAMA_STACK_OPENAI_ENDPOINT}")

    # Create client using the base URL
    client = LlamaStackClient(base_url=LLAMA_STACK_BASE_URL)
    print("✅ Llama Stack client created\n")

    return client


# --- Example 1: Agent with Tools Available (No Tool Usage) ---
def basic_query(client):
    """
    Test the agent with a basic question.
    The agent has tools available but determines they're not needed for this query.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Query (No Tool Usage)")
    print("=" * 80)

    INFERENCE_MODEL = os.getenv("INFERENCE_MODEL")
    EXAMPLE_PROMPT = "Give me list of customers of Fantaco company"

    print(f"🤖 Model: {INFERENCE_MODEL}")
    print(f"💬 Prompt: {EXAMPLE_PROMPT}\n")

    # Use Llama Stack's Responses API
    responses = client.responses.create(
        model=INFERENCE_MODEL,
        input=EXAMPLE_PROMPT,
    )

    print("=" * 80)
    print("FINAL RESPONSE:")
    print("=" * 80)
    print(responses.output_text)



# --- Agentic Tool Execution with Customer MCP Server ---
def customer_tool_example(client, prompt = "Search customer with name Anabela Domingues"):
    """
    Test the agent with a customer search query. The agent will:
    1. Discover available MCP tools
    2. Decide which tool to use (search_customers)
    3. Execute the tool call with appropriate arguments
    4. Synthesize the tool results into a natural language response
    """
    print("\n" + "=" * 80)
    print("Agentic Tool Execution - Customer Search")
    print("=" * 80)

    INFERENCE_MODEL = os.getenv("INFERENCE_MODEL")
    MCP_CUSTOMER_SERVER_URL = os.getenv("MCP_CUSTOMER_SERVER_URL")
    EXAMPLE_PROMPT = prompt

    print(f"🤖 Model: {INFERENCE_MODEL}")
    print(f"🌦️  MCP Server: {MCP_CUSTOMER_SERVER_URL}")
    print(f"💬 Prompt: {EXAMPLE_PROMPT}\n")


 #   agent = Agent(
 #       client=client,
 #       model=INFERENCE_MODEL
 #       instructions=EXAMPLE_PROMPT
 #       tools=[
 #           {
 #               "type": "mcp",  # Server-side MCP
 #               "server_url": MCP_CUSTOMER_SERVER_URL,
 #               "server_label": "customer",
 #           }
 #       ],
 #   )

    # Use Llama Stack's Responses API
    agent_responses = client.responses.create(
        model=INFERENCE_MODEL,
        input=EXAMPLE_PROMPT,
        tools=[
            {
                "type": "mcp",  # Server-side MCP
                "server_url": MCP_CUSTOMER_SERVER_URL,
                "server_label": "customer",
            }
        ],
    )

    # Display execution trace
    print("🤖 Agent Execution Trace:")
    print("-" * 80)

    for i, output in enumerate(agent_responses.output):
        print(f"\n[Output {i + 1}] Type: {output.type}")

        if output.type == "mcp_list_tools":
            print(f"  Server: {output.server_label}")
            print(f"  Tools available: {[t.name for t in output.tools]}")

        elif output.type == "mcp_call":
            print(f"  Tool called: {output.name}")
            print(f"  Arguments: {output.arguments}")
            #print(f"  Result: {output.output[:200]}...")  # Truncate long output
            if output.error:
                print(f"  Error: {output.error}")

        elif output.type == "message":
            print(f"  Role: {output.role}")
            if hasattr(output.content[0], 'text'):
                print(f"  Content: {output.content[0].text}")

    print("\n" + "=" * 80)
    print("FINAL RESPONSE:")
    print("=" * 80)
    print(agent_responses.output_text)


# --- Main Execution ---
def main():
    """Main execution function."""
    print("=" * 80)
    print("Llama Stack Agent Responses - Standalone Script")
    print("=" * 80)

    # Load environment and setup
    load_environment()

    # Create Llama Stack client
    client = create_llama_stack_client()

    # Run examples
    # Uncomment the examples you want to run:

    # basic_query(client)
    customer_tool_example(client, "Search customer with name Anabela Domingues")
    print("\n" + "=" * 80)
    print("Script completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
