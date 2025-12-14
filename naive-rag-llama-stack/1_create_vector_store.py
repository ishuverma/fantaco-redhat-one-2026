import os
import requests
from dotenv import load_dotenv
from llama_stack_client import LlamaStackClient

# Load environment variables
load_dotenv()

# Get configuration from environment
LLAMA_STACK_BASE_URL = os.getenv("LLAMA_STACK_BASE_URL", "http://localhost:8321")

# Initialize client
client = LlamaStackClient(base_url=LLAMA_STACK_BASE_URL)

# Create vector store with embedding model configuration
# Note: Embedding model must be specified for proper file indexing
vs = client.vector_stores.create(
    name="my-documents",
    extra_body={
        "embedding_model": "sentence-transformers/nomic-ai/nomic-embed-text-v1.5",
        "embedding_dimension": 768,
    }
)
print(f"Vector store created: {vs.id}")

  # Upload a file
url = "https://raw.githubusercontent.com/burrsutter/sample-pdfs/main/FantaCo/HR/FantaCo-Fabulous-HR-Benefits.pdf"
response = requests.get(url)
uploaded_file = client.files.create(
   file=response.content,
   purpose="assistants"
)

  # Attach file to vector store
client.vector_stores.files.create(
    vector_store_id=vs.id,
    file_id=uploaded_file.id
)

print(f"File {uploaded_file.id} added to vector store")