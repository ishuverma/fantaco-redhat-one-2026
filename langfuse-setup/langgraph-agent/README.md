# LangGraph + Langfuse Demo

A simple teaching demo showing how to integrate LangGraph agents with Langfuse observability.

## Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key (or vLLM endpoint)
- Langfuse account and API keys
- Any modern web browser

### 1. Setup and Run

```bash
cd backend

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your credentials:
# - API_KEY (your OpenAI or vLLM API key)
# - LANGFUSE_PUBLIC_KEY
# - LANGFUSE_SECRET_KEY
# - LANGFUSE_BASE_URL (default: https://cloud.langfuse.com)

# Run the server
python 6-langgraph-langfuse-fastapi-chatbot.py
```

The server will start on `http://localhost:8002` and serve both the API and web UI.


#### Test Backend

```bash
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "who does Thomas Hardy work for?",
    "user_id": "test-user",
    "session_id": "test-session-123"
}'
```

#### Test Standalone FastAPI Server (6-langgraph-langfuse-fastapi-chatbot.py)

The backend also includes a standalone FastAPI server that integrates with MCP servers:

**Start the server:**
```bash
cd backend
python 6-langgraph-langfuse-fastapi-chatbot.py
```

**Health Check:**
```bash
curl -s http://localhost:8002/health | python -m json.tool
```

**Root Endpoint (API Info):**
```bash
curl -s http://localhost:8002/ | python -m json.tool
```

**Chat Endpoint - Simple Query:**
```bash
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Who is Thomas Hardy?", "session_id": "test-session-123", "user_id": "test-user"}'
```

**Chat Endpoint - Complex Query with Orders:**
```bash
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What are the orders for Thomas Hardy?\", \"session_id\": \"session-456\", \"user_id\": \"admin\"}"
```

**Chat Endpoint - Search by Company:**
```bash
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find orders for Lonesome Pine Restaurant", "session_id": "demo-session"}'
```

**Expected Response Format:**
```json
{
  "reply": "Thomas Hardy is a Sales Representative at Around the Horn...",
  "tool_result": null,
  "trace_id": "019b4ccc-fa59-7fa2-a56e-854d0fafbfda"
}
```

The `trace_id` can be used to view the full trace in Langfuse at:
```
http://localhost:3000/trace/{trace_id}
```

### 2. Access the Application

Once the backend is running, open your browser and go to:

```
http://localhost:8002
```

The chat interface will load automatically!

**That's it!** The backend serves both the API and the web interface. No separate frontend server needed.

### 3. Test the Application

1. Open `http://localhost:8002` in your browser
2. Send a message like "Who is Thomas Hardy?"
3. Check your Langfuse dashboard to see the trace!
4. Click on the trace ID in Langfuse to view detailed execution

## What You'll See in Langfuse

When you send messages, Langfuse will capture:

- **Traces**: Complete conversation flows with session ID and user ID
- **Spans**: Individual LLM calls with input/output messages
- **Metrics**: Token usage, latency, and costs

## Project Structure

```
.
├── backend/
│   ├── 6-langgraph-langfuse-fastapi.py   # FastAPI app serving API + web UI
│   ├── requirements.txt     # Python dependencies
│   └── .env.example        # Environment variables template
├── frontend/
│   └── index.html          # Single-file vanilla JS chat interface
├── SPEC.md                  # Full technical specification
└── README.md               # This file
```

## Architecture

The application is now a **single Python process**:
- FastAPI backend handles chat requests via `/chat` endpoint
- Frontend HTML is served from root `/`
- Both run on `http://localhost:8002`
- No separate frontend server needed
- No Node.js or npm dependencies

**Alternative:** You can still run the frontend standalone if needed:
```bash
cd frontend
python3 -m http.server 3002  # Opens on http://localhost:3002
```

## Chat Interface

![Chat UI](images/chat-ui-1.png)

![Langfuse Trace 1](images/langfuse-trace-1.png)

[Video Demo](https://youtu.be/VFldGFVgUvk)


## Learning Resources

- [SPEC.md](./SPEC.md) - Complete technical specification
- [LangGraph Docs](https://python.langchain.com/docs/langgraph)
- [Langfuse Docs](https://langfuse.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

## Next Steps

1. Add a simple tool (e.g., current time lookup)
2. Implement conversation memory
3. Explore different prompt engineering techniques
4. Analyze traces in Langfuse dashboard
