#!/usr/bin/env python3
"""
List dataset providers from a Llama Stack server.
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

    # List all available providers
    logger.info("Fetching available providers...")
    providers = client.providers.list()

    if not providers:
        logger.warning("No providers found")
        return

    dataset_providers = [provider for provider in providers if provider.api == "datasetio"]

    if not dataset_providers:
        logger.warning("No dataset providers found (api=datasetio)")
        return

    logger.info(f"Found {len(dataset_providers)} dataset provider(s):\n")

    for provider in dataset_providers:
        print(f"  Provider ID: {provider.provider_id}")
        print(f"    Type: {provider.provider_type}")
        print(f"    API: {provider.api}")
        if provider.health:
            print(f"    Health: {provider.health}")
        print()


if __name__ == "__main__":
    main()
