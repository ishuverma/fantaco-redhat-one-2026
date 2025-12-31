#!/usr/bin/env python3
"""
Register a scoring function and benchmark using an LLM as a judge.
"""

import logging
import os
import sys

from dotenv import load_dotenv
from llama_stack_client import LlamaStackClient
from llama_stack_client import BadRequestError

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
    DATASET_ID = "basic-subset-of-evals"
    SCORING_FN_ID = "my-llm-as-judge-scoring-fn"
    BENCHMARK_ID = "my-llm-as-judge-benchmark"
    LLAMA_STACK_BASE_URL = os.getenv("LLAMA_STACK_BASE_URL", "http://localhost:8321")
    JUDGE_MODEL = os.getenv("JUDGE_MODEL")
    CANDIDATE_MODEL = os.getenv("CANDIDATE_MODEL")

    if not JUDGE_MODEL:
        logger.error("JUDGE_MODEL environment variable is not set")
        sys.exit(1)
    if not CANDIDATE_MODEL:
        logger.error("CANDIDATE_MODEL environment variable is not set")
        sys.exit(1)
    if not LLAMA_STACK_BASE_URL:
        logger.error("LLAMA_STACK_BASE_URL environment variable is not set")
        sys.exit(1)


    # Define the judge prompt template
    # Required variables: {input_query}, {expected_answer}, {generated_answer}
    judge_prompt = """Please evaluate the following response for quality and accuracy.

Question: {input_query}
Expected Answer: {expected_answer}
Generated Answer: {generated_answer}

Provide a score from 1-5 and explain your reasoning."""

    logger.info(f"Connecting to Llama Stack server at: {LLAMA_STACK_BASE_URL}")
    logger.info(f"Registering scoring function: {SCORING_FN_ID}")
    logger.info(f"Using judge model: {JUDGE_MODEL}")
    logger.info(f"Using candidate model: {CANDIDATE_MODEL}")

    # Create the Llama Stack client
    client = LlamaStackClient(base_url=LLAMA_STACK_BASE_URL)

    try:
        client.scoring_functions.register(
            scoring_fn_id=SCORING_FN_ID,
            description="LLM-as-judge scoring function for evaluating response quality",
            return_type={"type": "string"},
            provider_id="llm-as-judge",
            provider_scoring_fn_id="llm-as-judge-base",
            params={
                "type": "llm_as_judge",
                "judge_model": JUDGE_MODEL,
                "prompt_template": judge_prompt,
            },
        )
        logger.info(f"Scoring function '{SCORING_FN_ID}' registered successfully")
    except BadRequestError as e:
        if "already exists" in str(e):
            logger.info(f"Scoring function '{SCORING_FN_ID}' already exists, skipping registration")
        else:
            raise

    try:
        client.benchmarks.register(
            benchmark_id=BENCHMARK_ID,
            dataset_id=DATASET_ID,
            scoring_functions=[SCORING_FN_ID],
            provider_id="meta-reference",
        )
        logger.info(f"Benchmark '{BENCHMARK_ID}' registered successfully")
    except BadRequestError as e:
        if "already exists" in str(e):
            logger.info(f"Benchmark '{BENCHMARK_ID}' already exists, skipping registration")
        else:
            raise

    job = client.alpha.eval.run_eval(
        benchmark_id=BENCHMARK_ID,
        benchmark_config={
            "eval_candidate": {
                "type": "model",
                "model": CANDIDATE_MODEL,
                "sampling_params": {
                    "max_tokens": 1024,
                },
            },
            "scoring_params": {},
        },
    )
    logger.info(f"Eval job started: {job.job_id}")
    
    result = client.alpha.eval.jobs.retrieve(job_id=job.job_id, benchmark_id=BENCHMARK_ID)

    # Format and display results
    print("\n" + "=" * 80)
    print("EVALUATION RESULTS")
    print("=" * 80)

    generations = result.generations
    score_rows = result.scores.get(SCORING_FN_ID).score_rows if result.scores else []

    for i, gen in enumerate(generations):
        print(f"\n--- Evaluation {i + 1} ---")
        generated_answer = gen.get("generated_answer", "N/A")
        # Truncate long answers for display
        if len(generated_answer) > 200:
            display_answer = generated_answer[:200] + "..."
        else:
            display_answer = generated_answer
        print(f"Generated Answer: {display_answer}")

        if i < len(score_rows):
            score_row = score_rows[i]
            score = score_row.get("score", "N/A")
            feedback = score_row.get("judge_feedback", "N/A")
            print(f"Score: {score}")
            print(f"Judge Feedback:\n{feedback}")

    print("\n" + "=" * 80)
    print(f"Total evaluations: {len(generations)}")
    print("=" * 80)


if __name__ == "__main__":
    main()