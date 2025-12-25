#!/usr/bin/env python3
"""
Register a new shield with a Llama Stack server.
"""

import logging
import os
import sys

from dotenv import load_dotenv
from llama_stack_client import LlamaStackClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    force=True
)
logger = logging.getLogger(__name__)

# Suppress httpx INFO logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("llama_stack_client").setLevel(logging.WARNING)

def main():
    # Load environment variables from .env file
    load_dotenv()

    base_url = os.getenv("LLAMA_STACK_BASE_URL")
    if not base_url:
        logger.error("LLAMA_STACK_BASE_URL environment variable is not set")
        sys.exit(1)

    shield_id = os.getenv("SHIELD_ID")
    if not shield_id:
        logger.error("SHIELD_ID environment variable is not set")
        sys.exit(1)

    shield_model = os.getenv("SHIELD_MODEL")
    if not shield_model:
        logger.error("SHIELD_MODEL environment variable is not set")
        sys.exit(1)

    shield_provider = os.getenv("SHIELD_PROVIDER")
    if not shield_provider:
        logger.error("SHIELD_PROVIDER environment variable is not set")
        sys.exit(1)

    logger.info(f"Connecting to Llama Stack server at: {base_url}")

    # Create the Llama Stack client
    client = LlamaStackClient(base_url=base_url)

    # Register the shield
    logger.info(f"Registering shield '{shield_id}' with model: {shield_model}")

    shield = client.shields.register(
        shield_id=shield_id,
        provider_id=shield_provider,
        provider_shield_id=shield_model,
    )

    logger.info(f"Shield registered successfully: {shield_id}")

if __name__ == "__main__":
    main()
