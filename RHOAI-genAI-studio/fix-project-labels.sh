#!/bin/bash

# Add opendatahub.io/dashboard=true label to all agentic-userN namespaces

echo "Adding opendatahub.io/dashboard=true label to agentic-userN namespaces..."
echo "-----------------------------------------------------------"

for ns in $(oc get namespaces -o name | grep -E 'agentic-user[0-9]+$' | cut -d'/' -f2 | sort -t'r' -k2 -n); do
    echo "Labeling namespace: $ns"
    oc label namespace "$ns" opendatahub.io/dashboard='true' --overwrite
done

echo "-----------------------------------------------------------"
echo "Done."
