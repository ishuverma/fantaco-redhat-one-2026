# Implementation Plan: Llama Stack Client for Customer Search

## Overview
Create a Python script that uses the Llama Stack Client to invoke the `search_customers` tool from the registered customer MCP server to find a customer by email address.

## Objective
Search for customer with email `thomashardy@example.com` using the Llama Stack Client's agent execution capabilities.

## Architecture

### Components
1. **Llama Stack Client** - Main client for interacting with Llama Stack API
2. **Customer MCP Toolgroup** - Already registered as `customer_mcp`
3. **Agent Execution** - Use Llama Stack's agent turn execution to invoke tools
4. **Search Tool** - `search_customers` tool with email parameter

## Implementation Steps

### 1. Setup and Configuration
- Import `Client` from `llama_stack_client`
- Import `logging` module
- Load environment variables (LLAMA_STACK_BASE_URL, API_KEY, INFERENCE_MODEL)
- Configure logging with INFO level and timestamp format
- Create logger instance
- Initialize Llama Stack client
- Log initialization details (base URL, model)

### 2. Agent Configuration
Create an agent that can use the customer MCP toolgroup:
- **Agent ID**: `customer_search_agent`
- **Model**: Load from environment variable `INFERENCE_MODEL` (currently set to `ollama/llama3.2:3b`)
- **Tool Groups**: `["customer_mcp"]` - reference the registered toolgroup
- **Instructions**: System prompt to search for customers by email
- **Logging**: Log agent creation with agent ID and model name

### 3. Session Management
- Create an agent session for the search operation
- Session ID: `customer_search_session` (or generate unique ID)
- **Logging**: Log session creation with agent ID and session ID

### 4. Tool Invocation via Agent Turn
Execute an agent turn with the search request:
- **Input Message**: "Find customer with email thomashardy@example.com"
- **Streaming**: Enable to see tool calls in real-time
- **Tool Execution**: Llama Stack will automatically invoke search_customers tool
- **Logging**:
  - Log search request being sent
  - Log each streaming event as it arrives
  - Log tool calls detected
  - Log tool execution parameters

### 5. Response Processing
- Parse agent turn response
- Extract tool call results
- **Logging**:
  - Log raw tool results
  - Log formatted customer information (if found)
  - Log "No customer found" message (if applicable)
  - Log any errors or exceptions during processing

## API Endpoints to Use

### Logging Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

### Agent Creation
```python
INFERENCE_MODEL = os.getenv("INFERENCE_MODEL")

logger.info("Creating agent with ID: customer_search_agent")
logger.info("Using model: %s", INFERENCE_MODEL)

client.agents.create(
    agent_id="customer_search_agent",
    model=INFERENCE_MODEL,
    toolgroups=["customer_mcp"],
    instructions="You are a customer search assistant. Use the search_customers tool to find customers."
)

logger.info("Agent created successfully")
```

### Session Creation
```python
logger.info("Creating session: customer_search_session")

client.agents.sessions.create(
    agent_id="customer_search_agent",
    session_id="customer_search_session"
)

logger.info("Session created successfully")
```

### Agent Turn Execution
```python
logger.info("=" * 50)
logger.info("Searching for customer with email: thomashardy@example.com")
logger.info("=" * 50)

response = client.agents.turns.create(
    agent_id="customer_search_agent",
    session_id="customer_search_session",
    messages=[{
        "role": "user",
        "content": "Find customer with email thomashardy@example.com"
    }],
    stream=True
)

# Process streaming response
for event in response:
    logger.info("Event type: %s", event.event.type)

    # Log tool calls
    if hasattr(event.event, 'tool_calls'):
        for tool_call in event.event.tool_calls:
            logger.info("Tool called: %s", tool_call.tool_name)
            logger.info("Tool arguments: %s", tool_call.arguments)

    # Log tool responses
    if hasattr(event.event, 'tool_responses'):
        for tool_response in event.event.tool_responses:
            logger.info("Tool response: %s", tool_response.content)
```

## Expected Flow

1. **Initialize**: Create Llama Stack client connection (log connection details)
2. **Register Agent**: Create agent with customer_mcp toolgroup access (log agent creation)
3. **Create Session**: Initialize conversation session (log session ID)
4. **Submit Query**: Send natural language request to find customer (log search parameters)
5. **Stream Events**: Process streaming response events (log each event type)
6. **Tool Invocation**: Llama Stack routes to search_customers tool with appropriate parameters (log tool call and arguments)
7. **Get Results**: Receive customer data from MCP server (log tool response)
8. **Display**: Log formatted customer information with visual separators

## Error Handling

All errors should be caught and logged with appropriate context:

- **Connection Errors**: Handle Llama Stack API unavailability (log error with base URL)
- **Tool Execution Errors**: Catch and log tool invocation failures (log tool name and error details)
- **No Results**: Handle case where email doesn't match any customer (log "no customer found")
- **Invalid Responses**: Validate tool response format (log validation errors)
- **General Exceptions**: Wrap main execution in try-except block (log stack trace)

## Output Format

Log the following information with clear visual separators (using `=` and `-` characters):

**Initialization Phase:**
- Llama Stack base URL
- Inference model being used

**Agent Setup:**
- Agent ID being created
- Model configuration
- Toolgroups being registered

**Execution Phase:**
- Section header with separators: `==========================================`
- Search parameters (email being searched)
- Each streaming event type
- Tool calls detected (tool name and arguments)
- Tool responses (raw content)

**Results:**
- Customer details if found (formatted with labels):
  - Customer ID
  - Company name
  - Contact name
  - Contact email
  - Phone number
  - Address
- "No customer found" message if email doesn't match
- Section footer with separators

**Error Cases:**
- Clear error messages with context
- Stack traces for debugging

## Advantages of Llama Stack Client Approach

1. **Integrated Workflow**: No direct MCP protocol handling needed
2. **Natural Language Interface**: Can use conversational queries
3. **Multi-step Reasoning**: Agent can handle complex multi-tool scenarios
4. **Error Recovery**: Built-in retry and error handling
5. **Consistent API**: Same client for all Llama Stack operations

## Dependencies

- `llama-stack-client` - Already installed and used in scripts 1-3
- `python-dotenv` - For environment configuration
- `logging` - For execution tracking

## Notes

- The customer MCP server must already be registered (done in script 1)
- The Llama Stack server must have access to an LLM model for agent execution
- This approach uses agentic execution rather than direct tool calling
- The agent will automatically format the tool call based on natural language input
