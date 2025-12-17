#!/bin/bash
# Fix Cortex Deployment Persistence Configuration
# This script updates the deployment to ensure all data is persisted correctly

set -e

echo "=== Fixing Cortex Deployment Persistence ==="

# Apply the corrected deployment
kubectl apply -f k8s/deployment.yaml

echo "=== Waiting for deployment rollout ==="
kubectl rollout status deployment/cortex-app -n cortex --timeout=120s

echo "=== Verifying volume mounts ==="
POD=$(kubectl get pods -n cortex -l app=cortex -o jsonpath='{.items[0].metadata.name}')
if [ -n "$POD" ]; then
    echo "Pod: $POD"
    echo "Volume mounts:"
    kubectl get pod "$POD" -n cortex -o jsonpath='{.spec.containers[0].volumeMounts[*].mountPath}' | tr ' ' '\n'
    echo ""
    echo "Verifying directories exist:"
    kubectl exec -n cortex "$POD" -- ls -la /app/ | grep -E "(data|chroma_db|config)"
fi

echo "=== ✅ Persistence configuration fixed ==="

