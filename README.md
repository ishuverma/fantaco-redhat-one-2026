

## Starting the Llama Stack Server


```bash
ollama serve
```

Pull down your needed models

```bash
ollama pull llama3.2:3b
```

```bash
cd llama-stack-scripts
```


```bash
export LLAMA_STACK_MODEL="meta-llama/Llama-3.2-3B-Instruct"
export INFERENCE_MODEL="meta-llama/Llama-3.2-3B-Instruct"
export LLAMA_STACK_PORT=8321
export LLAMA_STACK_SERVER=http://localhost:$LLAMA_STACK_PORT
```

If using MaaS 

```bash
export VLLM_API_TOKEN=blah
# https://maas.apps.prod.rhoai.rh-aiservices-bu.com/admin/applications
export VLLM_URL=https://llama-4-scout-17b-16e-w4a16-maas-apicast-production.apps.prod.rhoai.rh-aiservices-bu.com:443/v1
```

If using Ollama

```bash
export OLLAMA_URL=http://localhost:11434 
```

```bash
python3.13 -m venv .venv
source .venv/bin/activate

uv run python -v
```

Install Deps 

```bash
uv run --with llama-stack llama stack list-deps starter | xargs -L1 uv pip install
```

Run the Llama Stack server attaching itself to ollama

```bash
uv run --with llama-stack llama stack run starter
```

Inspect the server by running the scripts in `llama-stack-scripts`

## Start Customer Backend

Assumes Postgres is up and running with appropriate database pre-created.  See the deeper dive README.MD

```bash
cd fantaco-customer-main
open README.md
```

Run the Customer REST API

```bash
java -jar target/fantaco-customer-main-1.0.0.jar
```

### Quick test of Customer REST API

```bash
curl -sS -L "$CUST_URL/api/customers?companyName=Around" | jq
```

## Start Finance Backend

```bash
cd fantaco-finance-main
open README.md
```

Run the Finance REST API

```bash
java -jar target/fantaco-finance-main-1.0.0.jar
```

### Quick test for Finance REST API

```bash
curl -sS -X POST $FIN_URL/api/finance/orders/history \
  -H "Content-Type: application/json" \
  -d '{
    "customerId": "AROUT",
    "limit": 10
  }' | jq
```

## Customer MCP

```bash
cd fantaco-mcp-servers/customer-mcp
```

```bash
python customer-api-mcp-server.py
```

## Finance MCP

```bash
cd fantaco-mcp-servers/finance-mcp
```

```bash
python finance-api-mcp-server.py
```

Using `mcp-inspector` to test

