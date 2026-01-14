#!/bin/bash

# Fix Langflow probe timeouts for OpenShift deployments
# Langflow takes a long time to start up and the default probe settings are too aggressive

NAMESPACE="${1:-langflow}"

echo "Patching langflow-service StatefulSet in namespace: $NAMESPACE"

oc patch statefulset langflow-service -n "$NAMESPACE" --type='json' -p='[
  {"op": "replace", "path": "/spec/template/spec/containers/0/livenessProbe/initialDelaySeconds", "value": 300},
  {"op": "replace", "path": "/spec/template/spec/containers/0/livenessProbe/failureThreshold", "value": 20},
  {"op": "replace", "path": "/spec/template/spec/containers/0/livenessProbe/periodSeconds", "value": 30},
  {"op": "replace", "path": "/spec/template/spec/containers/0/livenessProbe/timeoutSeconds", "value": 15},
  {"op": "replace", "path": "/spec/template/spec/containers/0/readinessProbe/initialDelaySeconds", "value": 120},
  {"op": "replace", "path": "/spec/template/spec/containers/0/readinessProbe/failureThreshold", "value": 20},
  {"op": "replace", "path": "/spec/template/spec/containers/0/readinessProbe/periodSeconds", "value": 30},
  {"op": "replace", "path": "/spec/template/spec/containers/0/readinessProbe/timeoutSeconds", "value": 15}
]'

if [ $? -eq 0 ]; then
  echo "Patch applied successfully."
  echo ""
  echo "Restarting pod to apply new settings..."
  oc delete pod langflow-service-0 -n "$NAMESPACE" --ignore-not-found=true
  echo ""
  echo "Monitor the pod status with:"
  echo "  oc get pods -n $NAMESPACE -w"
  echo ""
  echo "Probe settings applied:"
  echo "  Liveness:  300s initial delay, 20 failures × 30s = ~15 min before restart"
  echo "  Readiness: 120s initial delay, 20 failures × 30s = ~12 min before unready"
else
  echo "Failed to apply patch. Make sure:"
  echo "  - You are logged into the OpenShift cluster"
  echo "  - The langflow-service StatefulSet exists in namespace $NAMESPACE"
  exit 1
fi
