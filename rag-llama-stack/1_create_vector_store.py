import os
import requests
import logging
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from llama_stack_client import LlamaStackClient
from llama_stack_client import APIConnectionError, APIStatusError
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    force=True
)
logger = logging.getLogger(__name__)

# Suppress httpx and llama_stack_client INFO logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("llama_stack_client").setLevel(logging.WARNING)

# Load environment variables
load_dotenv()

# Get configuration from environment
LLAMA_STACK_BASE_URL = os.getenv("LLAMA_STACK_BASE_URL", "http://localhost:8321")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
EMBEDDING_DIMENSION = os.getenv("EMBEDDING_DIMENSION")

# Validate required environment variables
if not EMBEDDING_MODEL:
    logger.error("EMBEDDING_MODEL not set in .env file")
    sys.exit(1)

if not EMBEDDING_DIMENSION:
    logger.error("EMBEDDING_DIMENSION not set in .env file")
    sys.exit(1)

try:
    EMBEDDING_DIMENSION = int(EMBEDDING_DIMENSION)
except ValueError:
    logger.error(f"EMBEDDING_DIMENSION must be a number, got: {EMBEDDING_DIMENSION}")
    sys.exit(1)

logger.info(f"LLAMA_STACK_BASE_URL: {LLAMA_STACK_BASE_URL}")
logger.info(f"EMBEDDING_MODEL: {EMBEDDING_MODEL}")
logger.info(f"EMBEDDING_DIMENSION: {EMBEDDING_DIMENSION}")
logger.info("-" * 80)

# Initialize client
try:
    logger.info("Initializing Llama Stack client...")
    client = LlamaStackClient(base_url=LLAMA_STACK_BASE_URL)
    logger.info("Client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize client: {e}")
    logger.error("Make sure Llama Stack server is running")
    sys.exit(1)

# Define multiple files to process
# Can be URLs or local file paths
FILES_TO_PROCESS = [
    {
        "source": "https://raw.githubusercontent.com/burrsutter/fantaco-redhat-one-2026/refs/heads/main/rag-llama-stack/source_docs/FantaCoFabulousHRBenefits_clean.txt",
        "name": "hr-benefits-clean.txt",
        "type": "url"
    },
    # Add more files here:
    # {
    #     "source": "https://example.com/another-doc.txt",
    #     "name": "another-doc.txt",
    #     "type": "url"
    # },
    # {
    #     "source": "/path/to/local/file.txt",
    #     "name": "local-file.txt",
    #     "type": "local"
    # },
]

# Create vector store with embedding model configuration and hybrid search
try:
    logger.info("Creating vector store...")
    vs = client.vector_stores.create(
        name="hr-benefits-hybrid-multi",
        extra_body={
            "embedding_model": EMBEDDING_MODEL,
            "embedding_dimension": EMBEDDING_DIMENSION,
            "search_mode": "hybrid",
            "bm25_weight": 0.5,
            "semantic_weight": 0.5,
        }
    )
    logger.info(f"✓ Vector store created: {vs.id}")
except APIConnectionError as e:
    logger.error(f"Cannot connect to Llama Stack server at {LLAMA_STACK_BASE_URL}")
    logger.error("Please ensure the server is running and accessible")
    sys.exit(1)
except APIStatusError as e:
    logger.error(f"API error creating vector store: {e.status_code} - {e.message}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Unexpected error creating vector store: {e}")
    sys.exit(1)

# Process each file
uploaded_files = []
failed_files = []

logger.info("-" * 80)
logger.info(f"Processing {len(FILES_TO_PROCESS)} file(s)...")
logger.info("-" * 80)

for idx, file_config in enumerate(FILES_TO_PROCESS, 1):
    source = file_config["source"]
    name = file_config["name"]
    file_type = file_config["type"]

    logger.info(f"\n[{idx}/{len(FILES_TO_PROCESS)}] Processing: {name}")

    try:
        # Load file content based on type
        if file_type == "url":
            logger.info(f"  Downloading from URL...")
            response = requests.get(source, timeout=30)
            response.raise_for_status()
            text_content = response.text
        elif file_type == "local":
            logger.info(f"  Reading local file...")
            file_path = Path(source)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {source}")
            text_content = file_path.read_text(encoding='utf-8')
        else:
            raise ValueError(f"Unknown file type: {file_type}")

        if not text_content or len(text_content) < 100:
            raise ValueError("File appears to be empty or too small")

        logger.info(f"  ✓ Loaded {len(text_content)} characters")

        # Upload to Llama Stack
        logger.info("  Uploading to Llama Stack...")
        text_buffer = BytesIO(text_content.encode('utf-8'))
        text_buffer.name = name

        uploaded_file = client.files.create(
            file=text_buffer,
            purpose="assistants"
        )
        logger.info(f"  ✓ File uploaded: {uploaded_file.id}")

        # Attach to vector store
        logger.info("  Attaching to vector store...")
        client.vector_stores.files.create(
            vector_store_id=vs.id,
            file_id=uploaded_file.id,
            chunking_strategy={
                "type": "static",
                "static": {
                    "max_chunk_size_tokens": 100,
                    "chunk_overlap_tokens": 10
                }
            }
        )
        logger.info(f"  ✓ File attached to vector store")

        uploaded_files.append({
            "name": name,
            "file_id": uploaded_file.id,
            "source": source
        })

    except requests.exceptions.Timeout:
        logger.error(f"  ✗ Download timed out for {name}")
        failed_files.append({"name": name, "error": "Timeout"})
    except requests.exceptions.ConnectionError:
        logger.error(f"  ✗ Connection error for {name}")
        failed_files.append({"name": name, "error": "Connection error"})
    except requests.exceptions.HTTPError as e:
        logger.error(f"  ✗ HTTP error {e.response.status_code} for {name}")
        failed_files.append({"name": name, "error": f"HTTP {e.response.status_code}"})
    except FileNotFoundError as e:
        logger.error(f"  ✗ {e}")
        failed_files.append({"name": name, "error": "File not found"})
    except APIConnectionError as e:
        logger.error(f"  ✗ Lost connection to Llama Stack server")
        failed_files.append({"name": name, "error": "API connection error"})
    except APIStatusError as e:
        logger.error(f"  ✗ API error: {e.status_code} - {e.message}")
        failed_files.append({"name": name, "error": f"API error {e.status_code}"})
    except Exception as e:
        logger.error(f"  ✗ Unexpected error: {e}")
        failed_files.append({"name": name, "error": str(e)})

# Summary
logger.info("\n" + "=" * 80)
logger.info("PROCESSING SUMMARY")
logger.info("=" * 80)
logger.info(f"Successfully uploaded: {len(uploaded_files)}/{len(FILES_TO_PROCESS)} file(s)")

if uploaded_files:
    logger.info("\nSuccessful uploads:")
    for f in uploaded_files:
        logger.info(f"  ✓ {f['name']} (ID: {f['file_id']})")

if failed_files:
    logger.info(f"\nFailed uploads: {len(failed_files)}")
    for f in failed_files:
        logger.info(f"  ✗ {f['name']}: {f['error']}")

# Check file processing status
if uploaded_files:
    logger.info("\n" + "-" * 80)
    logger.info("Checking file processing status...")
    logger.info("Waiting 10 seconds for processing to complete...")
    time.sleep(10)

    try:
        files = client.vector_stores.files.list(vector_store_id=vs.id)
        file_list = list(files)

        if not file_list:
            logger.warning("No files found in vector store")
        else:
            logger.info(f"\nFound {len(file_list)} file(s) in vector store:")
            completed_count = 0
            failed_count = 0
            in_progress_count = 0

            for f in file_list:
                logger.info(f"\n  File ID: {f.id}")
                logger.info(f"  Status: {f.status}")

                if f.status == "completed":
                    logger.info("  ✓ Processing completed")
                    completed_count += 1
                elif f.status == "failed":
                    logger.error("  ✗ Processing failed")
                    if hasattr(f, 'last_error') and f.last_error:
                        logger.error(f"  Error: {f.last_error}")
                    failed_count += 1
                elif f.status == "in_progress":
                    logger.warning("  ⏳ Still processing")
                    in_progress_count += 1

            logger.info("\n" + "-" * 80)
            logger.info(f"Status Summary:")
            logger.info(f"  Completed: {completed_count}")
            logger.info(f"  Failed: {failed_count}")
            logger.info(f"  In Progress: {in_progress_count}")

            if completed_count > 0:
                logger.info("\n✓ Vector store is ready for querying")
                logger.info(f"Vector store ID: {vs.id}")

            if failed_count > 0:
                logger.error("\nSome files failed to process. Check:")
                logger.error("1. Embedding model is available: " + EMBEDDING_MODEL)
                logger.error(f"2. Embedding dimension matches: {EMBEDDING_DIMENSION}")
                logger.error("3. Server logs for detailed errors")

            if in_progress_count > 0:
                logger.info("\nSome files are still processing.")
                logger.info("Run 2_list_available_vector_stores.py later to check status")

    except APIConnectionError as e:
        logger.error("Lost connection to Llama Stack server while checking status")
        logger.warning("Files may still be processing - check later")
    except Exception as e:
        logger.error(f"Error checking file status: {e}")
        logger.warning("Files may still be processing - check manually")

logger.info("=" * 80)
