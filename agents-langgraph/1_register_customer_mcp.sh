echo "LLAMA_STACK_BASE_URL: ${LLAMA_STACK_BASE_URL}"
echo "LLAMA_STACK_API_KEY: ${LLAMA_STACK_API_KEY}"
echo "CUSTOMER_MCP_SERVER_URL: ${CUSTOMER_MCP_SERVER_URL}"

curl -w "\nHTTP Status: %{http_code}\n" -X POST "${LLAMA_STACK_BASE_URL}/v1/toolgroups" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${LLAMA_STACK_API_KEY}" \
  -d '{
    "toolgroup_id": "customer_mcp",
    "provider_id": "model-context-protocol",
    "mcp_endpoint": { "uri": "'"${CUSTOMER_MCP_SERVER_URL}"'" }
  }'