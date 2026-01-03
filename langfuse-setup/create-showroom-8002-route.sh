#!/bin/bash

# Extract namespace and base domain from existing showroom route
SHOWROOM_HOST=$(oc get route showroom -o jsonpath='{.spec.host}')
# showroom-showroom-kw8j5-1-user1.apps.cluster-kw8j5.dynamic.redhatworkshops.io
# Pattern: <route-name>-<namespace>.apps.<cluster-domain>

NAMESPACE=$(oc project -q)
# Extract base domain: everything after the namespace portion
BASE_DOMAIN=$(echo "$SHOWROOM_HOST" | sed "s/^showroom-${NAMESPACE}\.//")

# Construct new host for showroom-8002
NEW_HOST="showroom-8002-${NAMESPACE}.${BASE_DOMAIN}"

echo "Creating Service and Route for port 8002..."
echo "Host will be: https://${NEW_HOST}"

# Create Service
oc apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: showroom-8002
spec:
  selector:
    app.kubernetes.io/name: showroom
  ports:
    - port: 8002
      targetPort: 8002
      protocol: TCP
EOF

# Create Route with explicit host
oc apply -f - <<EOF
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: showroom-8002
spec:
  host: ${NEW_HOST}
  port:
    targetPort: 8002
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
  to:
    kind: Service
    name: showroom-8002
    weight: 100
EOF

# Verify
echo ""
echo "Route created:"
oc get route showroom-8002
