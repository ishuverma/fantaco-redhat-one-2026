#!/bin/bash
# Converts keys.txt to environment variables
# Usage: source ./convert-keys-txt-env-vars.sh
#
# Reads keys.txt and exports:
#   LANGFUSE_SECRET_KEY
#   LANGFUSE_PUBLIC_KEY
#   LANGFUSE_HOST

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEYS_FILE="${SCRIPT_DIR}/keys.txt"

if [ ! -f "$KEYS_FILE" ]; then
    echo "Error: keys.txt not found at $KEYS_FILE"
    return 1 2>/dev/null || exit 1
fi

# Extract values from keys.txt (handles format: KEY = "value")
LANGFUSE_SECRET_KEY=$(grep 'LANGFUSE_SECRET_KEY' "$KEYS_FILE" | sed 's/.*= *"//' | sed 's/"$//')
LANGFUSE_PUBLIC_KEY=$(grep 'LANGFUSE_PUBLIC_KEY' "$KEYS_FILE" | sed 's/.*= *"//' | sed 's/"$//')
LANGFUSE_HOST=$(grep 'LANGFUSE_BASE_URL' "$KEYS_FILE" | sed 's/.*= *"//' | sed 's/"$//')

# Validate
if [ -z "$LANGFUSE_SECRET_KEY" ]; then
    echo "Error: Could not extract LANGFUSE_SECRET_KEY from keys.txt"
    return 1 2>/dev/null || exit 1
fi

if [ -z "$LANGFUSE_PUBLIC_KEY" ]; then
    echo "Error: Could not extract LANGFUSE_PUBLIC_KEY from keys.txt"
    return 1 2>/dev/null || exit 1
fi

if [ -z "$LANGFUSE_HOST" ]; then
    echo "Error: Could not extract LANGFUSE_HOST from keys.txt"
    return 1 2>/dev/null || exit 1
fi

export LANGFUSE_SECRET_KEY
export LANGFUSE_PUBLIC_KEY
export LANGFUSE_HOST

echo "LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}"
echo "LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}"
echo "LANGFUSE_HOST=${LANGFUSE_HOST}"
