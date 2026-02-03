#!/bin/bash
# List all available Langflow component types
# These are the building blocks that can be used in any flow
# Requires: LANGFLOW_API_URL, LANGFLOW_API_KEY

# Check required environment variables
if [ -z "$LANGFLOW_API_URL" ]; then
    # Try LANGFLOW_URL as fallback
    if [ -z "$LANGFLOW_URL" ]; then
        echo "Error: LANGFLOW_API_URL (or LANGFLOW_URL) is not set"
        echo "Usage: export LANGFLOW_API_URL=https://langflow-api-xxx.apps.example.com"
        exit 1
    fi
    LANGFLOW_API_URL="$LANGFLOW_URL"
fi

if [ -z "$LANGFLOW_API_KEY" ]; then
    echo "Error: LANGFLOW_API_KEY is not set"
    echo "Usage: export LANGFLOW_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    exit 1
fi

echo "========================================"
echo "LANGFLOW AVAILABLE COMPONENTS"
echo "========================================"
echo "API URL: $LANGFLOW_API_URL"
echo "========================================"
echo ""

# Fetch all components
RESPONSE=$(curl -sL --compressed -X GET \
    "$LANGFLOW_API_URL/api/v1/all" \
    -H "accept: application/json" \
    -H "x-api-key: $LANGFLOW_API_KEY")

# Check for API error
if echo "$RESPONSE" | jq -e '.detail' >/dev/null 2>&1; then
    echo "API Error: $(echo "$RESPONSE" | jq -r '.detail')"
    exit 1
fi

# List categories and their components
echo "Components by Category:"
echo "----------------------------------------"

echo "$RESPONSE" | jq -r '
    to_entries |
    sort_by(.key) |
    .[] |
    "\n### \(.key | ascii_upcase)\n" +
    (.value | keys | sort | map("  - " + .) | join("\n"))
'

echo ""
echo "----------------------------------------"
echo "Total categories: $(echo "$RESPONSE" | jq 'keys | length')"
echo "Total components: $(echo "$RESPONSE" | jq '[.[] | keys] | flatten | length')"
echo ""
echo "To see details for a specific component:"
echo "  curl -s -H \"x-api-key: \$LANGFLOW_API_KEY\" \"\$LANGFLOW_API_URL/api/v1/all\" | jq '.{category}.{ComponentName}'"
echo ""
echo "Example:"
echo "  curl -s -H \"x-api-key: \$LANGFLOW_API_KEY\" \"\$LANGFLOW_API_URL/api/v1/all\" | jq '.agents.Agent'"
