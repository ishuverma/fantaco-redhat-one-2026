#!/bin/bash

# List all available Langflow components via API
# Usage: ./list-langflow-components.sh [namespace]

NAMESPACE="${1:-langflow}"

# Get the Langflow URL
LANGFLOW_URL="https://$(oc get route langflow-service -n $NAMESPACE -o jsonpath='{.status.ingress[0].host}' 2>/dev/null)"

if [ -z "$LANGFLOW_URL" ] || [ "$LANGFLOW_URL" == "https://" ]; then
    echo "Error: Could not get Langflow URL. Make sure you're logged into OpenShift."
    exit 1
fi

echo "Langflow URL: $LANGFLOW_URL"
echo ""

# Try to get components list
echo "Fetching component types..."
echo ""

# Method 1: Try the types endpoint
RESPONSE=$(curl -sk "$LANGFLOW_URL/api/v1/all" 2>/dev/null)

if echo "$RESPONSE" | grep -q "detail"; then
    echo "API requires authentication. Trying internal method..."
    echo ""

    # Method 2: Query from inside the pod
    echo "=== Component Categories ==="
    oc exec langflow-service-0 -n $NAMESPACE -- python3 -c "
import json
from pathlib import Path

# Find all component directories
components_path = Path('/app/.venv/lib/python3.12/site-packages/lfx/components')
categories = []

for item in sorted(components_path.iterdir()):
    if item.is_dir() and not item.name.startswith('_'):
        # Count .py files (components)
        py_files = list(item.glob('*.py'))
        py_files = [f.stem for f in py_files if not f.stem.startswith('_')]
        if py_files:
            categories.append({'category': item.name, 'components': py_files})

for cat in categories:
    print(f\"\\n📁 {cat['category'].upper()}\")
    for comp in cat['components']:
        print(f\"   - {comp}\")
" 2>/dev/null

else
    # Parse and display the response
    echo "$RESPONSE" | python3 -c "
import sys
import json

try:
    data = json.load(sys.stdin)
    for category, components in data.items():
        if isinstance(components, dict):
            print(f'\\n📁 {category.upper()}')
            for name in components.keys():
                print(f'   - {name}')
except Exception as e:
    print(f'Error parsing response: {e}')
    print('Raw response:')
    print(sys.stdin.read()[:500])
"
fi

echo ""
echo "=== Search for specific components ==="
echo "Looking for: OpenAI, vLLM, MCP, Agent..."
echo ""

oc exec langflow-service-0 -n $NAMESPACE -- python3 -c "
from pathlib import Path
import re

components_path = Path('/app/.venv/lib/python3.12/site-packages/lfx/components')
search_terms = ['openai', 'vllm', 'mcp', 'agent']

print('Found components:')
for term in search_terms:
    matches = list(components_path.rglob(f'*{term}*.py'))
    matches = [m for m in matches if '__pycache__' not in str(m)]
    if matches:
        print(f'\\n  {term.upper()}:')
        for m in matches:
            # Get display_name from file
            try:
                content = m.read_text()
                display_match = re.search(r'display_name\s*=\s*[\"\\']([^\"\\']+)[\"\\']', content)
                if display_match:
                    print(f'    - {display_match.group(1)} ({m.parent.name}/{m.name})')
                else:
                    print(f'    - {m.parent.name}/{m.name}')
            except:
                print(f'    - {m.parent.name}/{m.name}')
" 2>/dev/null

echo ""
echo "Done."
