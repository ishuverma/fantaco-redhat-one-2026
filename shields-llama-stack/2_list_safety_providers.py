#!/usr/bin/env python3
"""
List all safety providers from a Llama Stack server.
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

    logger.info(f"Connecting to Llama Stack server at: {base_url}")

    # Create the Llama Stack client
    client = LlamaStackClient(base_url=base_url)

    # List all providers and filter for safety
    logger.info("Fetching safety providers...")
    providers = client.providers.list()

    safety_providers = [p for p in providers if p.api == "safety"]

    if not safety_providers:
        logger.warning("No safety providers found")
        return

    logger.info(f"Found {len(safety_providers)} safety provider(s):\n")

    for provider in safety_providers:
        print(f"  Provider ID: {provider.provider_id}")
        print(f"    Type: {provider.provider_type}")
        if hasattr(provider, 'config') and provider.config:
            print(f"    Config: {provider.config}")
        print()

if __name__ == "__main__":
    main()
