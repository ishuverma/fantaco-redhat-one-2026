# Repository Guidelines

This file created due to the use of Codex CLI

## Project Structure & Module Organization
- `fantaco-customer-main/`: Spring Boot Customer API (Java 21, Maven, PostgreSQL).
- `fantaco-finance-main/`: Spring Boot Finance API (Java 21, Maven, PostgreSQL).
- `fantaco-mcp-servers/`: Python MCP servers for customer and finance APIs.
- `simple-agent-langgraph/`, `customer-agent-llama-stack/`, `finance-agent-llama-stack/`, `rag-llama-stack/`, `shields-llama-stack/`, `evals-llama-stack/`: Llama Stack and LangGraph demos/scripts.
- `llama-stack-scripts/`: Helper scripts for Llama Stack server operations.
- `helm/`: Helm charts for deploying apps and agents.
- `langfuse-setup/`: Langfuse + LangGraph demo assets.

## Build, Test, and Development Commands
- Customer API build/run:
  - `mvn clean package` (build JAR)
  - `mvn spring-boot:run` (run locally)
  - `java -jar target/fantaco-customer-main-1.0.0.jar`
- Finance API build/run:
  - `mvn clean package`
  - `mvn spring-boot:run` or `java -jar target/fantaco-finance-main-1.0.0.jar`
- Llama Stack server (from repo root):
  - `python3.12 -m venv .venv && source .venv/bin/activate`
  - `uv run --with llama-stack llama stack run starter`
- MCP servers (examples):
  - `python fantaco-mcp-servers/customer-mcp/customer-api-mcp-server.py`
  - `python fantaco-mcp-servers/finance-mcp/finance-api-mcp-server.py`

## Coding Style & Naming Conventions
- Java: 4-space indentation, `PascalCase` classes, `camelCase` methods/fields, package names like `com.customer` or `com.fantaco.finance`.
- Python: 4-space indentation, `snake_case` functions/variables, `PascalCase` classes.
- YAML/JSON: 2-space indentation; keep keys lowercase with hyphens where possible.
- No enforced formatter in-repo; keep edits minimal and consistent with neighboring files.

## Testing Guidelines
- Java modules use Maven: `mvn test` (runs unit/integration tests when present under `src/test/java`).
- Python demo modules are typically run as scripts; add targeted tests only when adding logic with clear expected behavior.

## Commit & Pull Request Guidelines
- No formal commit convention in history; use short, imperative summaries (e.g., "add finance MCP docs").
- PRs should describe the module(s) affected, include commands run, and note any new configuration or deployment steps.

## Configuration & Secrets
- Local DB settings live in `fantaco-*/src/main/resources/application.properties`.
- Common env vars: `SPRING_DATASOURCE_URL`, `SPRING_DATASOURCE_USERNAME`, `SPRING_DATASOURCE_PASSWORD`.
- Llama Stack state is stored under `~/.llama/` by default; clear with `rm -rf ~/.llama/distributions/starter` when needed.
