import os
import logging
import sys
from dotenv import load_dotenv
from llama_stack_client import LlamaStackClient
from llama_stack_client import APIConnectionError

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

logger.info("=" * 80)
logger.info("Available Embedding Models on Llama Stack Server")
logger.info("=" * 80)
logger.info(f"Server: {LLAMA_STACK_BASE_URL}")
logger.info("-" * 80)

# Initialize client
try:
    client = LlamaStackClient(base_url=LLAMA_STACK_BASE_URL)
except Exception as e:
    logger.error(f"Failed to initialize client: {e}")
    sys.exit(1)

# List all models
try:
    logger.info("\nFetching available models...")
    models = client.models.list()

    model_list = list(models)

    if not model_list:
        logger.warning("No models found on the server")
        logger.info("\nYou need to register models using client.models.register()")
        sys.exit(0)

    # Filter for embedding models only
    embedding_models = []
    for model in model_list:
        model_type = getattr(model, 'model_type', 'unknown')
        if model_type == 'embedding':
            embedding_models.append(model)

    # Display Embedding Models
    if embedding_models:
        logger.info(f"\nFound {len(embedding_models)} embedding model(s):\n")
        for i, model in enumerate(embedding_models, 1):
            logger.info(f"{i}. {model.identifier}")
            if hasattr(model, 'provider_id'):
                logger.info(f"   Provider: {model.provider_id}")
            if hasattr(model, 'provider_resource_id'):
                logger.info(f"   Resource ID: {model.provider_resource_id}")
            if hasattr(model, 'metadata'):
                embedding_dim = model.metadata.get('embedding_dimension', 'unknown')
                logger.info(f"   Dimension: {embedding_dim}")
                if model.metadata.get('default_configured'):
                    logger.info(f"   ⭐ Default configured")
            logger.info("")
    else:
        logger.warning("\n⚠ No embedding models found!")
        logger.info("You need an embedding model for vector stores.")
        logger.info("Run: python 0_register_embedding_model.py")

    logger.info("=" * 80)

except APIConnectionError as e:
    logger.error(f"Cannot connect to server at {LLAMA_STACK_BASE_URL}")
    logger.error("Make sure the server is running")
    sys.exit(1)
except Exception as e:
    logger.error(f"Error listing models: {e}")
    sys.exit(1)
