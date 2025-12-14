import os
import requests
from dotenv import load_dotenv
from llama_stack_client import LlamaStackClient
from io import BytesIO

# Load environment variables
load_dotenv()

# Get configuration from environment
LLAMA_STACK_BASE_URL = os.getenv("LLAMA_STACK_BASE_URL", "http://localhost:8321")

# Initialize client
client = LlamaStackClient(base_url=LLAMA_STACK_BASE_URL)

# Create vector store with embedding model configuration
# Note: Embedding model must be specified for proper file indexing
vs = client.vector_stores.create(
    name="my-documents-text",
    extra_body={
        "embedding_model": "sentence-transformers/nomic-ai/nomic-embed-text-v1.5",
        "embedding_dimension": 768,
    }
)
print(f"Vector store created: {vs.id}")

# Upload a text/HTML file (easier to process than PDF)
url = "https://www.paulgraham.com/greatwork.html"
response = requests.get(url)
file_buffer = BytesIO(response.content)
file_buffer.name = "greatwork.html"

uploaded_file = client.files.create(
    file=file_buffer,
    purpose="assistants"
)

# Attach file to vector store
client.vector_stores.files.create(
    vector_store_id=vs.id,
    file_id=uploaded_file.id
)

print(f"File {uploaded_file.id} added to vector store")

# Check file status
import time
time.sleep(2)  # Wait a bit for processing
files = client.vector_stores.files.list(vector_store_id=vs.id)
for f in files:
    print(f"File status: {f.status}")
