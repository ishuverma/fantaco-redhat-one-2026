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


# Load environment variables from .env file
load_dotenv()

base_url = os.getenv("LLAMA_STACK_BASE_URL")
if not base_url:
    logger.error("LLAMA_STACK_BASE_URL environment variable is not set")
    sys.exit(1)

# 1. Connect
client = LlamaStackClient(base_url=base_url)

# 2. Data
eval_rows = [
    {
        "input_query": "What is 2 + 2?",
        "generated_answer": "4",
        "expected_answer": "4",
    },
]

# 3. Score
result = client.scoring.score(
    input_rows=eval_rows,
    scoring_functions={"basic::subset_of": None}
)

# Pretty print the results
for func_name, scoring_result in result.results.items():
    print(f"\n=== {func_name} ===")

    # Aggregated results
    agg = scoring_result.aggregated_results
    if agg:
        print(f"Accuracy: {agg['accuracy']['accuracy']:.1%}")
        print(f"Correct: {int(agg['accuracy']['num_correct'])} / {agg['accuracy']['num_total']}")

    # Individual scores
    print("\nRow scores:")
    for i, row in enumerate(scoring_result.score_rows):
        score = row['score']
        status = "✓" if score == 1.0 else "✗"
        print(f"  Row {i+1}: {status} (score: {score})")