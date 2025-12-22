# main.py
import os
import uuid
import logging
from typing import TypedDict, Annotated, Sequence
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langfuse.langchain import CallbackHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

class Settings(BaseSettings):
    """Application settings from environment variables."""

    # LLM Configuration
    API_KEY: str
    INFERENCE_MODEL: str
    BASE_URL: str 

    # Langfuse Configuration
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_SECRET_KEY: str
    LANGFUSE_BASE_URL: str

    # Application Configuration
    PORT: int = 8002

    class Config:
        env_file = ".env"


settings = Settings()

# Set Langfuse environment variables for v3.x compatibility
os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_HOST"] = settings.LANGFUSE_BASE_URL


# ============================================================================
# LangGraph Agent State
# ============================================================================

class AgentState(TypedDict):
    """Simple agent state - just messages and metadata."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: str
    session_id: str


# ============================================================================
# Agent Node
# ============================================================================

def agent_node(state: AgentState) -> AgentState:
    """
    Main agent node - calls LLM with Langfuse tracing.
    This is where the magic happens for observability!
    """

    # Create Langfuse callback handler for this conversation
    # In Langfuse 3.x, credentials are read from environment variables
    # session_id and user_id are set via metadata
    langfuse_handler = CallbackHandler()

    # Initialize LLM with Langfuse callbacks
    llm = ChatOpenAI(
        model=settings.INFERENCE_MODEL,
        temperature=0.7,
        api_key=settings.API_KEY,
        base_url=settings.BASE_URL,
        callbacks=[langfuse_handler]
    )

    # Call the LLM (this will be traced in Langfuse)
    # Pass session_id and user_id as metadata
    response = llm.invoke(
        state["messages"],
        config={
            "callbacks": [langfuse_handler],
            "metadata": {
                "session_id": state["session_id"],
                "user_id": state["user_id"],
            }
        }
    )

    return {"messages": [response]}


# ============================================================================
# Create Agent Graph
# ============================================================================

def create_agent_graph():
    """Create a simple LangGraph workflow."""

    # Initialize the graph
    workflow = StateGraph(AgentState)

    # Add single node (keep it simple for teaching)
    workflow.add_node("agent", agent_node)

    # Set entry point and end
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", END)

    # Compile the graph
    return workflow.compile()


# ============================================================================
# FastAPI Application
# ============================================================================

# Global agent graph instance
agent_graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agent graph on startup."""
    global agent_graph

    # Log configuration at startup
    logger.info("=" * 60)
    logger.info("🚀 Starting LangGraph + Langfuse Demo")
    logger.info("=" * 60)
    logger.info(f"BASE_URL: {settings.BASE_URL}")
    logger.info(f"INFERENCE_MODEL: {settings.INFERENCE_MODEL}")
    logger.info(f"LANGFUSE_BASE_URL: {settings.LANGFUSE_BASE_URL}")
    logger.info(f"PORT: {settings.PORT}")
    logger.info("=" * 60)

    agent_graph = create_agent_graph()
    logger.info("✅ Agent graph initialized")
    yield
    logger.info("🛑 Shutting down")


app = FastAPI(
    title="LangGraph + Langfuse Demo",
    description="Simple demo for teaching Langfuse tracing",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# API Models
# ============================================================================

class ChatRequest(BaseModel):
    """Chat request from frontend."""
    message: str
    session_id: str | None = None
    user_id: str | None = None


class ChatResponse(BaseModel):
    """Chat response to frontend."""
    message: str
    session_id: str
    user_id: str


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Simple chat endpoint.
    Sends message to agent and returns response.
    All interactions are traced in Langfuse!
    """

    try:
        # Generate IDs if not provided
        session_id = request.session_id or str(uuid.uuid4())
        user_id = request.user_id or "anonymous"

        # Log chat invocation
        logger.info("=" * 60)
        logger.info("💬 Chat invocation")
        logger.info(f"Session ID: {session_id}")
        logger.info(f"User ID: {user_id}")
        logger.info(f"Message: {request.message[:100]}...")  # Log first 100 chars
        logger.info("=" * 60)

        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=request.message)],
            "session_id": session_id,
            "user_id": user_id,
        }

        # Run the agent (this creates the Langfuse trace)
        logger.info("🤖 Invoking agent...")
        result = agent_graph.invoke(initial_state)

        # Extract AI response
        ai_message = result["messages"][-1]
        logger.info(f"✅ Agent response received (length: {len(ai_message.content)} chars)")
        logger.info(f"Response preview: {ai_message.content[:100]}...")

        return ChatResponse(
            message=ai_message.content,
            session_id=session_id,
            user_id=user_id
        )

    except Exception as e:
        logger.error(f"❌ Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print(f"""
    🚀 Starting server on http://localhost:{settings.PORT}
    📊 Langfuse: {settings.LANGFUSE_BASE_URL}
    🤖 Model: {settings.INFERENCE_MODEL}
    """)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True,
    )
