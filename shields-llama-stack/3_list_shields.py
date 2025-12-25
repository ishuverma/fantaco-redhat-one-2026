#!/usr/bin/env python3
"""
List all available shields from a Llama Stack server.
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

    # List all available shields
    logger.info("Fetching available shields...")
    shields = client.shields.list()

    if not shields:
        logger.warning("No shields found")
        return

    logger.info(f"Found {len(shields)} shield(s):\n")

    for shield in shields:
        print(f"  Shield ID: {shield.identifier}")
        if hasattr(shield, 'provider_id') and shield.provider_id:
            print(f"    Provider: {shield.provider_id}")
        if hasattr(shield, 'provider_shield_id') and shield.provider_shield_id:
            print(f"    Provider Shield ID: {shield.provider_shield_id}")
        if hasattr(shield, 'params') and shield.params:
            print(f"    Params: {shield.params}")
        print()

if __name__ == "__main__":
    main()
