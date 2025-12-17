# Cortex Kubernetes Deployment Files

This directory contains Kubernetes manifests for deploying Cortex with proper data persistence.

## Files

- `namespace.yaml` - Cortex namespace
- `pvc.yaml` - Persistent Volume Claims for database, ChromaDB, and config files
- `deployment.yaml` - Main deployment with correct volume mounts
- `service.yaml` - ClusterIP service for internal access
- `fix-persistence.sh` - Script to apply persistence fixes

## Data Persistence

The deployment ensures three critical data directories are persisted:

1. **Database** (`/app/data`) - SQLite database files
   - PVC: `cortex-db-pvc` (1Gi)
   - Mount: `/app/data`

2. **ChromaDB** (`/app/chroma_db`) - Vector database for RAG
   - PVC: `cortex-chromadb-pvc` (10Gi)
   - Mount: `/app/chroma_db`

3. **Config Files** (`/app/config`) - User chatbot configurations
   - PVC: `cortex-config-pvc` (1Gi)
   - Mount: `/app/config`

## Usage

### Initial Setup

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create PVCs (if not already created)
kubectl apply -f k8s/pvc.yaml

# Deploy application
kubectl apply -f k8s/deployment.yaml

# Create service
kubectl apply -f k8s/service.yaml
```

### Fix Persistence (if deployment has incorrect mounts)

```bash
# Run the fix script
bash k8s/fix-persistence.sh
```

### Verify Persistence

```bash
# Check PVCs
kubectl get pvc -n cortex

# Check volume mounts
kubectl get deployment cortex-app -n cortex -o yaml | grep -A 10 volumeMounts

# Verify data directories in pod
POD=$(kubectl get pods -n cortex -l app=cortex -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n cortex $POD -- ls -la /app/ | grep -E "(data|chroma_db|config)"
```

## Important Notes

- All PVCs use `local-path` storage class
- PVCs are bound to the volume disk (not root disk) for better persistence
- Data survives pod evictions and restarts
- PVCs are retained even if deployment is deleted (unless manually deleted)

## Storage Requirements

- Database: ~120KB (1Gi PVC is sufficient)
- ChromaDB: Can grow with vector data (10Gi PVC recommended)
- Config: ~10KB per user (1Gi PVC is sufficient)

