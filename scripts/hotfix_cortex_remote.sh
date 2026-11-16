#!/bin/bash
# Run ON Hetzner as root after cortex-source.tar.gz is in /tmp
set -euo pipefail

cd /tmp
rm -rf cortex-build
mkdir -p cortex-build
cd cortex-build
tar -xzf /tmp/cortex-source.tar.gz
rm -f /tmp/cortex-source.tar.gz

echo "=== Sync dashboard static assets to nginx path (cortex only) ==="
mkdir -p /opt/cortex/static/v2/js
cp -a static/v2/js/dashboard-core.js static/v2/js/dashboard-appearance.js /opt/cortex/static/v2/js/
chmod 644 /opt/cortex/static/v2/js/dashboard-*.js

build_and_import() {
  local tag="cortex:latest"
  if command -v docker >/dev/null 2>&1; then
    systemctl restart docker || true
    sleep 5
    docker pull python:3.11-slim || true
    if docker build -f Dockerfile.hotfix -t "$tag" .; then
      docker save "$tag" | k3s ctr images import -
      return 0
    fi
    echo "⚠️ docker build failed, trying nerdctl/podman..."
  fi
  if command -v nerdctl >/dev/null 2>&1; then
    nerdctl build -f Dockerfile.hotfix -t "$tag" . && nerdctl save "$tag" | k3s ctr images import - && return 0
  fi
  if ! command -v podman >/dev/null 2>&1; then
    apt-get update -qq && apt-get install -y -qq podman || true
  fi
  if command -v podman >/dev/null 2>&1; then
    podman build -f Dockerfile.hotfix -t localhost/cortex:latest . \
      && podman save localhost/cortex:latest | k3s ctr images import - && return 0
  fi
  return 1
}

rollout_k8s() {
  kubectl apply -f k8s/namespace.yaml 2>/dev/null || kubectl create namespace cortex 2>/dev/null || true
  kubectl apply -f k8s/pvc.yaml 2>/dev/null || true
  kubectl apply -f k8s/deployment.yaml
  kubectl apply -f k8s/service.yaml 2>/dev/null || true
  if kubectl get deployment cortex-app -n cortex >/dev/null 2>&1; then
    kubectl rollout restart deployment/cortex-app -n cortex
    kubectl rollout status deployment/cortex-app -n cortex --timeout=300s
    return 0
  fi
  return 1
}

deploy_systemd() {
  echo "=== Cortex hotfix: systemd /opt/cortex ==="
  mkdir -p /opt/cortex
  rsync -a --exclude 'venv-prod' --exclude 'chroma_db' --exclude 'uploads' --exclude '.git' \
    ./ /opt/cortex/
  if [ -f deployments/systemd/cortex.service ]; then
    cp deployments/systemd/cortex.service /etc/systemd/system/cortex.service
    systemctl daemon-reload
  fi
  systemctl enable cortex.service 2>/dev/null || true
  systemctl restart cortex.service
  systemctl is-active cortex.service
}

if build_and_import; then
  if ! rollout_k8s; then
    deploy_systemd
  fi
else
  echo "=== Image build failed: patching running pod (until next pod recreate) ==="
  POD=$(kubectl get pods -n cortex -l app=cortex -o jsonpath='{.items[0].metadata.name}')
  for rel in app.py blueprints/api.py models/chatbot_appearance.py templates/dashboard/dashboard.html; do
    kubectl cp "$rel" "cortex/${POD}:/app/${rel}"
  done
  kubectl exec -n cortex "$POD" -- python -c "from migrations import run_migrations; run_migrations()"
  echo "⚠️ Pod patch only (no image). Trying systemd..."
  deploy_systemd || true
fi

POD=$(kubectl get pods -n cortex -l app=cortex -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)
if [ -n "$POD" ]; then
  kubectl exec -n cortex "$POD" -- curl -sf http://localhost:6001/health || true
fi
echo "✅ Cortex hotfix script finished"