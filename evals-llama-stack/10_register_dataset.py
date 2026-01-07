#!/usr/bin/env python3
"""
Register a dataset with a Llama Stack server.
Supports CLI arguments with fallback to environment variables.
"""

import argparse
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


def parse_args():
    parser = argparse.ArgumentParser(
        description="Register a dataset with a Llama Stack server"
    )
    parser.add_argument(
        "--base-url",
        help="Llama Stack server base URL (default: LLAMA_STACK_BASE_URL env var)"
    )
    parser.add_argument(
        "--dataset-id",
        help="Unique identifier for the dataset"
    )
    parser.add_argument(
        "--dataset-uri",
        help="URI to the dataset file (default: LLAMA_STACK_DATASET_URI env var)"
    )
    parser.add_argument(
        "--provider-id",
        default=None,
        help="Dataset provider ID (default: LLAMA_STACK_DATASET_PROVIDER_ID env var or 'localfs')"
    )
    parser.add_argument(
        "--purpose",
        default="eval/question-answer",
        help="Dataset purpose (default: eval/question-answer)"
    )
    return parser.parse_args()


def main():
    # Load environment variables from .env file
    load_dotenv()

    args = parse_args()

    # Resolve base_url: CLI > env var
    base_url = args.base_url or os.getenv("LLAMA_STACK_BASE_URL")
    if not base_url:
        logger.error("Base URL not provided. Use --base-url or set LLAMA_STACK_BASE_URL")
        sys.exit(1)

    # Resolve dataset_uri: CLI > env var
    dataset_uri = args.dataset_uri or os.getenv("LLAMA_STACK_DATASET_URI")
    if not dataset_uri:
        logger.error("Dataset URI not provided. Use --dataset-uri or set LLAMA_STACK_DATASET_URI")
        sys.exit(1)

    # Resolve dataset_id: CLI > derive from URI
    if args.dataset_id:
        dataset_id = args.dataset_id
    else:
        # Extract dataset ID from URI filename (without extension)
        filename = os.path.basename(dataset_uri)
        dataset_id = os.path.splitext(filename)[0]

    # Resolve provider_id: CLI > env var > default
    provider_id = args.provider_id or os.getenv("LLAMA_STACK_DATASET_PROVIDER_ID", "localfs")

    logger.info(f"Connecting to Llama Stack server at: {base_url}")
    logger.info(f"Registering dataset: {dataset_id}")
    logger.info(f"Dataset URI: {dataset_uri}")
    logger.info(f"Using dataset provider: {provider_id}")
    logger.info(f"Purpose: {args.purpose}")

    # Create the Llama Stack client
    client = LlamaStackClient(base_url=base_url)

    try:
        dataset = client.datasets.register(
            purpose=args.purpose,
            source={
                "type": "uri",
                "uri": dataset_uri,
            },
            dataset_id=dataset_id,
            extra_body={"provider_id": provider_id},
        )
    except Exception as exc:
        logger.error(f"Failed to register dataset: {exc}")
        sys.exit(1)

    if dataset is None:
        logger.warning("No dataset returned from registration")
        return

    identifier = getattr(dataset, "identifier", dataset_id)
    logger.info(f"Registered dataset: {identifier}")


if __name__ == "__main__":
    main()
