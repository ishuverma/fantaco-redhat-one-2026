#!/bin/bash

# View opendatahub.io/dashboard label for all agentic-userN namespaces

echo "Namespace                Label: opendatahub.io/dashboard"
echo "-----------------------------------------------------------"

for ns in $(oc get namespaces -o name | grep -E 'agentic-user[0-9]+$' | cut -d'/' -f2 | sort -t'r' -k2 -n); do
    label=$(oc get namespace "$ns" -o jsonpath='{.metadata.labels.opendatahub\.io/dashboard}' 2>/dev/null)
    printf "%-24s %s\n" "$ns" "${label:-<not set>}"
done
