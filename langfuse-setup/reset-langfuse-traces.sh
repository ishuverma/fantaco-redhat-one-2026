#!/bin/bash
# Reset/clear all traces from Langfuse
# Usage: ./reset-langfuse-traces.sh [namespace]
# Default namespace: langfuse
#
# WARNING: This will DELETE ALL traces, observations, and scores from Langfuse!

set -e

NAMESPACE="${1:-langfuse}"

echo "============================================================"
echo "WARNING: This will DELETE ALL traces from Langfuse!"
echo "Namespace: $NAMESPACE"
echo "============================================================"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

# Get ClickHouse password
echo "Getting ClickHouse credentials..."
CH_PASSWORD=$(oc get secret langfuse-clickhouse-auth -n "$NAMESPACE" -o jsonpath='{.data.password}' | base64 -d)

if [ -z "$CH_PASSWORD" ]; then
    echo "Error: Could not retrieve ClickHouse password"
    exit 1
fi

echo "Clearing ClickHouse tables..."

# Delete from ClickHouse tables
TABLES=("traces" "observations" "scores" "event_log")

for TABLE in "${TABLES[@]}"; do
    echo "  Truncating $TABLE..."
    oc exec -n "$NAMESPACE" langfuse-clickhouse-shard0-0 -- \
        clickhouse-client --password "$CH_PASSWORD" \
        --query "TRUNCATE TABLE IF EXISTS $TABLE ON CLUSTER default" 2>/dev/null || \
    oc exec -n "$NAMESPACE" langfuse-clickhouse-shard0-0 -- \
        clickhouse-client --password "$CH_PASSWORD" \
        --query "ALTER TABLE $TABLE DELETE WHERE 1=1" 2>/dev/null || \
        echo "    Warning: Could not truncate $TABLE (may not exist)"
done

echo "Clearing PostgreSQL tables..."

# Get PostgreSQL password
PG_PASSWORD=$(oc get secret langfuse-postgresql-auth -n "$NAMESPACE" -o jsonpath='{.data.password}' | base64 -d)

if [ -z "$PG_PASSWORD" ]; then
    echo "Warning: Could not retrieve PostgreSQL password, skipping PostgreSQL cleanup"
else
    # Delete from PostgreSQL tables (order matters due to foreign keys)
    PG_TABLES=("scores" "observations" "traces" "trace_sessions")

    for TABLE in "${PG_TABLES[@]}"; do
        echo "  Deleting from $TABLE..."
        oc exec -n "$NAMESPACE" langfuse-postgresql-0 -- \
            psql -U langfuse -d postgres_langfuse -c "DELETE FROM $TABLE;" 2>/dev/null || \
            echo "    Warning: Could not delete from $TABLE (may not exist or have dependencies)"
    done
fi

echo ""
echo "============================================================"
echo "Langfuse traces have been cleared!"
echo "============================================================"
echo ""
echo "Note: You may need to restart the Langfuse pods for changes to take effect:"
echo "  oc rollout restart deployment/langfuse-web -n $NAMESPACE"
echo "  oc rollout restart deployment/langfuse-worker -n $NAMESPACE"
