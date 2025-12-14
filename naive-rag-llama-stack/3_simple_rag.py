import os
from dotenv import load_dotenv
from llama_stack_client import LlamaStackClient, Agent, AgentEventLogger

# Load environment variables
load_dotenv()

# Get configuration from environment
LLAMA_STACK_BASE_URL = os.getenv("LLAMA_STACK_BASE_URL", "http://localhost:8321")
INFERENCE_MODEL = os.getenv("INFERENCE_MODEL", "vllm/qwen3-14b-gaudi")

# Initialize client
client = LlamaStackClient(base_url=LLAMA_STACK_BASE_URL)

# Get the vector store (assuming it's named "my-documents")
vector_stores = client.vector_stores.list()
vector_store = None
for vs in vector_stores:
    if vs.name == "my-documents":
        vector_store = vs
        break

if not vector_store:
    print("Error: Vector store 'my-documents' not found. Please run 1_create_vector_store.py first.")
    exit(1)

print(f"Using vector store: {vector_store.id}")
print(f"Using model: {INFERENCE_MODEL}")
print("-" * 80)

# Define the query
query = "what do I receive when I retire?"

print(f"Query: {query}\n")
print("Agent Response:")
print("-" * 80)

# Create agent with file_search tool for RAG
agent = Agent(
    client,
    model=INFERENCE_MODEL,
    instructions="You are a helpful assistant that answers questions based on the provided documents.",
    tools=[
        {
            "type": "file_search",
            "vector_store_ids": [vector_store.id],
        }
    ],
)

# Create a session and ask the question
session_id = agent.create_session("retirement-benefits-query")
response = agent.create_turn(
    messages=[{"role": "user", "content": query}],
    session_id=session_id,
    stream=True,
)

# Stream the response
for log in AgentEventLogger().log(response):
    print(log, end="")
