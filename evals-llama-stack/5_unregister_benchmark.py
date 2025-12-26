#!/usr/bin/env python3
"""
Unregister a benchmark from a Llama Stack server.
"""

import logging
import os
import sys

from dotenv import load_dotenv
from llama_stack_client import LlamaStackClient, NoneType
from llama_stack_client._models import FinalRequestOptions

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

    benchmark_id = os.getenv("LLAMA_STACK_BENCHMARK_ID", "my-basic-quality-benchmark")

    logger.info(f"Connecting to Llama Stack server at: {base_url}")
    logger.info(f"Unregistering benchmark: {benchmark_id}")

    # Create the Llama Stack client
    client = LlamaStackClient(base_url=base_url)

    opts = FinalRequestOptions.construct(
        method="delete",
        url=f"/v1alpha/eval/benchmarks/{benchmark_id}",
        headers={"Accept": "*/*"},
    )

    try:
        client.request(NoneType, opts)
    except Exception as exc:
        logger.error(f"Failed to unregister benchmark: {exc}")
        sys.exit(1)

    logger.info("Benchmark unregistered successfully")


if __name__ == "__main__":
    main()
