# Customer Agent MCP Server

An MCP (Model Context Protocol) server that wraps a Llama Stack customer agent, exposing it as MCP tools via SSE (Server-Sent Events) transport using the FastMCP library.

## Architecture

```
┌─────────────────────────────────────────────┐
│         MCP Client                          │
│         (Connects via SSE)                  │
└────────┬────────────────────────────────────┘
         │
         │ customer_agent(prompt)
         ▼
┌─────────────────────────────────────────────┐
│         FastMCP Server                      │
│         - SSE Transport                     │
│         - Tools: customer_agent             │
│                  customer_agent_detailed    │
└────────┬────────────────────────────────────┘
         │
         │ Uses Llama Stack SDK
         ▼
┌─────────────────────────────────────────────┐
│         Llama Stack Agent                   │
│         - Calls Customer MCP Server         │
│         - Tool Discovery & Execution        │
└─────────────────────────────────────────────┘
```

## Components

### Files

- **mcp_server.py**: The main MCP server implementation using FastMCP
- **lls_customer_agent.py**: The underlying Llama Stack agent implementation
- **test_mcp_server.py**: Comprehensive test suite for the MCP server
- **example_client.py**: Example client demonstrating how to use the MCP server
- **Containerfile.mcp-server**: Container definition for deploying the MCP server
- **requirements.txt**: Python dependencies

### Available Tools

#### 1. `customer_agent`

Execute the customer agent with a given prompt.

**Parameters:**
- `prompt` (string): The question or instruction for the customer agent

**Returns:** String response from the agent

**Examples:**
- "Search customer with name Anabela Domingues"
- "Give me list of customers of Fantaco company"
- "Find customer with email john@example.com"

#### 2. `customer_agent_detailed`

Execute the customer agent with detailed execution trace.

**Parameters:**
- `prompt` (string): The question or instruction for the customer agent

**Returns:** JSON string containing execution trace and final response

## Installation

### Prerequisites

- Python 3.11+
- Access to a Llama Stack instance
- Access to a Customer MCP Server

### Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:

```bash
# Llama Stack Configuration
LLAMA_STACK_BASE_URL=http://localhost:8321
LLAMA_STACK_OPENAI_ENDPOINT=http://localhost:8321/v1
INFERENCE_MODEL=ollama/llama3.2:3b
API_KEY=fake

# MCP Server Configuration
MCP_CUSTOMER_SERVER_URL=https://your-customer-mcp-server.com/mcp
```

## Usage

### Running the MCP Server

Start the MCP server with SSE transport:

```bash
python mcp_server.py
```

By default, the server runs on `http://localhost:8000/sse`

### Using the Example Client

Run the example client to see how to interact with the MCP server:

```bash
python example_client.py
```

### Running Tests

Run the test suite:

```bash
# Run all tests with pytest
pytest test_mcp_server.py -v

# Run only direct function tests
python test_mcp_server.py
```

### Using with MCP Clients

The server can be used with any MCP-compatible client. For example, using the MCP SDK:

```python
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def use_customer_agent():
    async with sse_client("http://localhost:8000/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "customer_agent",
                arguments={"prompt": "Search customer with name John"}
            )

            print(result.content[0].text)

asyncio.run(use_customer_agent())
```

## Container Deployment

### Building the Container

```bash
podman build -f Containerfile.mcp-server -t customer-agent-mcp-server .
```

### Running the Container

```bash
podman run -p 8000:8000 \
  -e LLAMA_STACK_BASE_URL=http://your-llama-stack:8321 \
  -e MCP_CUSTOMER_SERVER_URL=https://your-customer-mcp-server.com/mcp \
  -e INFERENCE_MODEL=ollama/llama3.2:3b \
  customer-agent-mcp-server
```

## Development

### Project Structure

```
llamastack-agent-customer-mcp/
├── mcp_server.py              # Main MCP server
├── lls_customer_agent.py      # Llama Stack agent
├── test_mcp_server.py         # Test suite
├── example_client.py          # Example client
├── requirements.txt           # Dependencies
├── Containerfile.mcp-server   # Container definition
├── .env                       # Environment configuration
└── README.md                  # This file
```

### Adding New Tools

To add new tools to the MCP server, define them in `mcp_server.py`:

```python
@mcp.tool()
def my_custom_tool(param: str) -> str:
    """
    Description of your tool.

    Args:
        param: Description of parameter

    Returns:
        Description of return value
    """
    # Tool implementation
    return "result"
```

## Configuration Options

### FastMCP Server Options

The server can be configured by modifying the `mcp.run()` call in `mcp_server.py`:

```python
mcp.run(
    transport="sse",  # Transport type (sse, stdio)
    port=8000,        # Port number
    host="0.0.0.0"    # Host address
)
```

### Environment Variables

- `LLAMA_STACK_BASE_URL`: URL of the Llama Stack instance
- `LLAMA_STACK_OPENAI_ENDPOINT`: OpenAI-compatible endpoint (optional)
- `INFERENCE_MODEL`: Model identifier for inference
- `MCP_CUSTOMER_SERVER_URL`: URL of the customer MCP server
- `API_KEY`: API key for authentication (if required)

## Troubleshooting

### Common Issues

1. **Connection refused**: Ensure Llama Stack is running and accessible
2. **MCP server not configured**: Check that `MCP_CUSTOMER_SERVER_URL` is set in `.env`
3. **Import errors**: Run `pip install -r requirements.txt` to install dependencies
4. **Port already in use**: Change the port in `mcp.run()` or stop the conflicting service

## License

This project is part of the BYO Agentic Framework.

## References

- [Llama Stack Documentation](https://llamastack.github.io/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Library](https://github.com/jlowin/fastmcp)
