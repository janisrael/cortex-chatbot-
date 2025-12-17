#!/bin/bash
# Verify Cortex Data Persistence Configuration
# This script checks that all data directories are properly persisted

set -e

echo "=== Verifying Cortex Data Persistence ==="

# Check PVCs
echo ""
echo "1. Checking PVCs..."
kubectl get pvc -n cortex

# Check deployment volume mounts
echo ""
echo "2. Checking deployment volume mounts..."
kubectl get deployment cortex-app -n cortex -o jsonpath='{.spec.template.spec.containers[0].volumeMounts[*]}' | jq -r '.[] | "\(.name) -> \(.mountPath)"' 2>/dev/null || \
kubectl get deployment cortex-app -n cortex -o yaml | grep -A 3 "volumeMounts:" | grep -E "(mountPath|name)"

# Check volumes
echo ""
echo "3. Checking volumes..."
kubectl get deployment cortex-app -n cortex -o jsonpath='{.spec.template.spec.volumes[*]}' | jq -r '.[] | "\(.name) -> \(.persistentVolumeClaim.claimName)"' 2>/dev/null || \
kubectl get deployment cortex-app -n cortex -o yaml | grep -A 3 "volumes:" | grep -E "(name|claimName)"

# Check pod mounts
echo ""
echo "4. Checking pod volume mounts..."
POD=$(kubectl get pods -n cortex -l app=cortex -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
if [ -n "$POD" ]; then
    echo "Pod: $POD"
    echo "Mounted paths:"
    kubectl get pod "$POD" -n cortex -o jsonpath='{.spec.containers[0].volumeMounts[*].mountPath}' | tr ' ' '\n'
    echo ""
    echo "Verifying directories exist in pod:"
    kubectl exec -n cortex "$POD" -- ls -ld /app/data /app/chroma_db /app/config 2>/dev/null || echo "⚠️ Some directories may not exist yet"
else
    echo "⚠️ No running pod found"
fi

# Expected configuration
echo ""
echo "5. Expected Configuration:"
echo "   - /app/data -> cortex-db-pvc (Database)"
echo "   - /app/chroma_db -> cortex-chromadb-pvc (ChromaDB)"
echo "   - /app/config -> cortex-config-pvc (Config files)"

echo ""
echo "=== ✅ Verification complete ==="

