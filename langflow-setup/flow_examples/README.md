# Langflow Flow Examples

This directory contains example Langflow flows for the FantaCo workshop.

## Prerequisites

Before creating flows that use custom components, you must first upload the custom components:

1. Open Langflow UI
2. Go to Settings (gear icon) → Custom Components → Upload
3. Upload these files from `../custom_components/`:
   - `vllm_model_component.py` - Basic vLLM model component
   - `vllm_agent_component.py` - vLLM Agent with tool support
   - `mcp_streamable_http_component.py` - MCP server connector

## Available Flows

### Chat_vLLM_Output.json
Basic chat flow: Chat Input → vLLM Model → Chat Output

### simple-agent-template.json
Agent flow with Calculator and URL tools (uses built-in Agent component)

## Creating a Customer MCP Agent Flow

This flow connects: Chat Input → vLLM Agent ← MCP Tools → Chat Output

### Step 1: Get your MCP Server URLs

```bash
export NAMESPACE=agentic-user1
export CUSTOMER_MCP_SERVER_URL=https://$(oc get routes -l app=mcp-customer -n $NAMESPACE -o jsonpath="{range .items[*]}{.status.ingress[0].host}{end}")/mcp
echo $CUSTOMER_MCP_SERVER_URL
```

### Step 2: Create the Flow in Langflow UI

1. **Create new flow** → Click "Blank Flow" → Name it "Customer MCP Agent"

2. **Add Chat Input**
   - From sidebar: Input/Output → Chat Input
   - Drag onto canvas (left side)

3. **Add MCP Streamable HTTP**
   - From sidebar: Custom Components → MCP Streamable HTTP
   - Drag onto canvas (top center)
   - Configure:
     - **MCP Server URL**: `https://mcp-customer-route-agentic-user1.apps.cluster-j9f4d.dynamic.redhatworkshops.io/mcp`
     - **Server Name**: `Customer Service`

4. **Add vLLM Agent**
   - From sidebar: Custom Components → vLLM Agent
   - Drag onto canvas (center)
   - Configure:
     - **vLLM API Base URL**: `https://litellm-prod.apps.maas.redhatworkshops.io/v1`
     - **Model Name**: `qwen3-14b`
     - **API Key**: (your LiteLLM API key from showroom)
     - **System Prompt**: Customize as needed

5. **Add Chat Output**
   - From sidebar: Input/Output → Chat Output
   - Drag onto canvas (right side)

6. **Connect the components**:
   ```
   Chat Input (message) ────────► vLLM Agent (Input)
   MCP Streamable HTTP (Tools) ──► vLLM Agent (Tools)
   vLLM Agent (Response) ────────► Chat Output (Inputs)
   ```

7. **Save** the flow

### Step 3: Test the Flow

1. Click "Playground" button (bottom right)
2. Try queries like:
   - "List all customers"
   - "Get customer with ID 1"
   - "What orders does customer 1 have?"

## Importing/Exporting Flows via API

```bash
# Set environment variables
export LANGFLOW_URL=https://$(oc get routes -l app=langflow-service -o jsonpath="{range .items[*]}{.status.ingress[0].host}{end}")
export LANGFLOW_API_KEY=your-api-key

# List all flows
curl -s --compressed -X GET \
  "${LANGFLOW_URL}/api/v1/flows/?get_all=true" \
  -H "accept: application/json" \
  -H "x-api-key: ${LANGFLOW_API_KEY}" | jq '.[] | {id: .id, name: .name}'

# Export a flow (replace FLOW_ID)
curl -s --compressed -X GET \
  "${LANGFLOW_URL}/api/v1/flows/FLOW_ID" \
  -H "accept: application/json" \
  -H "x-api-key: ${LANGFLOW_API_KEY}" > my-flow.json

# Import a flow
curl -s --compressed -X POST \
  "${LANGFLOW_URL}/api/v1/flows/" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${LANGFLOW_API_KEY}" \
  -d @my-flow.json
```

## Flow Architecture Diagram

```
┌──────────────┐     ┌─────────────────────┐     ┌──────────────┐
│  Chat Input  │────►│     vLLM Agent      │────►│ Chat Output  │
│              │     │                     │     │              │
└──────────────┘     │  - System Prompt    │     └──────────────┘
                     │  - Model: qwen3-14b │
                     │  - Temperature: 0.1 │
┌──────────────────┐ │                     │
│ MCP Streamable   │►│  Tools ────────────►│
│ HTTP             │ │                     │
│                  │ └─────────────────────┘
│ Customer MCP URL │
└──────────────────┘
```
