Llama Stack provides a comprehensive evaluation framework with three main APIs:
- /datasetio + /datasets: Interface with datasets and data loaders
- /scoring + /scoring_functions: Evaluate outputs with scoring functions
- /eval + /benchmarks: Generate outputs and perform scoring

## Evaluation Workflow Steps

### Dataset Providers
- Backend systems that provide access to datasets (e.g., Hugging Face, local files)
- List available providers: `python 1_list_dataset_providers.py`
- Providers implement the `datasetio` API for loading and accessing evaluation data

### Benchmark Providers
- Backend systems that provide evaluation and benchmarking capabilities
- List available providers: `python 1_list_eval_benchmark_providers.py`
- Providers implement the `eval` and `benchmarks` APIs

### Datasets
- Collections of test cases used for evaluation
- Register datasets from CSV files: `python 2_register_basic_subset_of_evals.py`
- List registered datasets: `python 3_list_datasets.py`
- Unregister datasets: `python 2_unregister_subset_of_evals.py`
- Each dataset contains prompts and expected outputs for testing

### Scoring Functions
- Methods to evaluate model outputs (e.g., accuracy, BLEU, exact match)
- List available functions: `python 4_list_scoring_functions.py`
- Functions are provided by scoring providers and can include custom metrics

### Benchmarks
- Complete evaluation configurations combining datasets and scoring functions
- Register benchmarks: `python 5_register_benchmark.py`
- List registered benchmarks: `python 4_list_benchmarks.py`
- Unregister benchmarks: `python 5_unregister_benchmark.py`
- Benchmarks define how to evaluate a model on a specific dataset

### Jobs
- Execution instances that run evaluations on benchmarks
- Execute eval job: `python 7_execute_eval.py`
- Review job results: `python 8_review_eval_job.py`
- Jobs generate model outputs and apply scoring functions to measure performance
- Additional: LLM-as-judge evaluation: `python 9_llm_as_judge.py`

