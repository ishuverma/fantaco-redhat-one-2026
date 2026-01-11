#!/bin/bash
# Creates Langfuse and S3 Routes, configures external S3 endpoints
# Usage: source ./create-langfuse-url.sh
#
# Exports: LANGFUSE_HOST, LANGFUSE_URL

# Get current namespace from oc project
NAMESPACE=$(oc project -q)
if [ -z "$NAMESPACE" ]; then
    echo "Error: Could not determine current namespace" >&2
    echo "Make sure you are logged in and have a project selected" >&2
    exit 1
fi

echo "Using namespace: $NAMESPACE"

# Get the cluster's base domain
BASE_DOMAIN=$(oc get ingresses.config.openshift.io cluster -o jsonpath='{.spec.domain}' 2>/dev/null)

if [ -z "$BASE_DOMAIN" ]; then
    # Fallback: try to get from existing routes in namespace
    BASE_DOMAIN=$(oc get routes -n "$NAMESPACE" -o jsonpath='{.items[0].spec.host}' 2>/dev/null | sed 's/^[^.]*\.//')
fi

if [ -z "$BASE_DOMAIN" ]; then
    echo "Error: Could not determine cluster base domain" >&2
    exit 1
fi

# Construct URLs
ROUTE_HOSTNAME="langfuse-${NAMESPACE}.${BASE_DOMAIN}"
S3_ROUTE_HOSTNAME="langfuse-s3-${NAMESPACE}.${BASE_DOMAIN}"
LANGFUSE_HOST="https://${ROUTE_HOSTNAME}"
LANGFUSE_URL="${LANGFUSE_HOST}"
S3_EXTERNAL_URL="https://${S3_ROUTE_HOSTNAME}"

echo "Creating Langfuse Route..."
echo "Host will be: $LANGFUSE_HOST"

# Create the Langfuse Route (points to langfuse-web Service)
oc apply -n "$NAMESPACE" -f - <<EOF
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: langfuse
spec:
  host: ${ROUTE_HOSTNAME}
  port:
    targetPort: 3000
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
  to:
    kind: Service
    name: langfuse-web
    weight: 100
EOF

echo ""
echo "Creating S3 Route for external downloads..."
echo "Host will be: $S3_EXTERNAL_URL"

# Create the S3 Route (for presigned download URLs to work externally)
oc apply -n "$NAMESPACE" -f - <<EOF
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: langfuse-s3
spec:
  host: ${S3_ROUTE_HOSTNAME}
  port:
    targetPort: minio-api
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
  to:
    kind: Service
    name: langfuse-s3
    weight: 100
EOF

echo ""
echo "Routes created:"
oc get route langfuse langfuse-s3 -n "$NAMESPACE"
echo ""

# Update Langfuse deployments to use external S3 endpoint for presigned URLs
# (only if deployments exist - run this script again after helm install if needed)
if oc get deployment langfuse-web -n "$NAMESPACE" &>/dev/null; then
    echo "Updating Langfuse deployments with external S3 endpoint..."
    oc set env deployment/langfuse-web \
      LANGFUSE_S3_EVENT_UPLOAD_ENDPOINT="$S3_EXTERNAL_URL" \
      LANGFUSE_S3_BATCH_EXPORT_ENDPOINT="$S3_EXTERNAL_URL" \
      LANGFUSE_S3_MEDIA_UPLOAD_ENDPOINT="$S3_EXTERNAL_URL"

    oc set env deployment/langfuse-worker \
      LANGFUSE_S3_EVENT_UPLOAD_ENDPOINT="$S3_EXTERNAL_URL" \
      LANGFUSE_S3_BATCH_EXPORT_ENDPOINT="$S3_EXTERNAL_URL" \
      LANGFUSE_S3_MEDIA_UPLOAD_ENDPOINT="$S3_EXTERNAL_URL"
    echo ""
else
    echo "NOTE: Langfuse deployments not found yet."
    echo "After 'helm install', run this script again to configure S3 external endpoints."
    echo ""
fi

# If sourced, export the variables; if executed, print them
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    # Script is being sourced
    export LANGFUSE_HOST
    export LANGFUSE_URL
    echo "Exported LANGFUSE_HOST=${LANGFUSE_HOST}"
    echo "Exported LANGFUSE_URL=${LANGFUSE_URL}"
else
    # Script is being executed
    echo "LANGFUSE_HOST=${LANGFUSE_HOST}"
    echo "LANGFUSE_URL=${LANGFUSE_URL}"
fi
