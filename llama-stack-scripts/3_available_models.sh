echo $LLAMA_STACK_BASE_URL
curl -sS -L $LLAMA_STACK_BASE_URL/v1/models -H "Content-Type: application/json" | jq -r '.data[].identifier'