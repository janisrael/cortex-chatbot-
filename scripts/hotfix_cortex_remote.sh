#!/bin/bash
# Run ON Hetzner as root after cortex-source.tar.gz is in /tmp
set -euo pipefail

BUILD_DIR="/tmp/cortex-build"
cd /tmp
rm -rf cortex-build
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"
tar -xzf /tmp/cortex-source.tar.gz
rm -f /tmp/cortex-source.tar.gz

echo "=== Sync dashboard static assets to nginx path (cortex only) ==="
mkdir -p /opt/cortex/static/v2/js
cp -a static/v2/js/dashboard-core.js static/v2/js/dashboard-appearance.js /opt/cortex/static/v2/js/
chmod 644 /opt/cortex/static/v2/js/dashboard-*.js

deploy_systemd() {
  echo "=== Cortex hotfix: sync /opt/cortex + restart gunicorn ==="
  mkdir -p /opt/cortex
  rsync -a --exclude 'venv-prod' --exclude 'chroma_db' --exclude 'uploads' --exclude '.git' \
    "$BUILD_DIR/" /opt/cortex/
  if [ ! -d /opt/cortex/venv-prod ]; then
    python3 -m venv /opt/cortex/venv-prod
    /opt/cortex/venv-prod/bin/pip install --upgrade pip
    /opt/cortex/venv-prod/bin/pip install --no-cache-dir --use-deprecated=legacy-resolver -r /opt/cortex/requirements-prod.txt
    /opt/cortex/venv-prod/bin/pip install gunicorn
  fi
  if [ -f /opt/cortex/deployments/systemd/cortex.service ]; then
    cp /opt/cortex/deployments/systemd/cortex.service /etc/systemd/system/cortex.service
    systemctl daemon-reload
  fi
  systemctl enable cortex.service 2>/dev/null || true
  systemctl restart cortex.service
  systemctl is-active cortex.service
}

build_and_import() {
  local tag="cortex:latest"
  if ! command -v docker >/dev/null 2>&1; then
    return 1
  fi
  systemctl restart docker || true
  sleep 5
  docker pull python:3.11-slim || true
  if docker build -f "$BUILD_DIR/Dockerfile.hotfix" -t "$tag" "$BUILD_DIR"; then
    docker save "$tag" | k3s ctr images import -
    return 0
  fi
  echo "⚠️ docker build failed (k8s image not updated; systemd deploy still applied)"
  return 1
}

rollout_k8s() {
  kubectl apply -f "$BUILD_DIR/k8s/namespace.yaml" 2>/dev/null || kubectl create namespace cortex 2>/dev/null || true
  kubectl apply -f "$BUILD_DIR/k8s/pvc.yaml" 2>/dev/null || true
  kubectl apply -f "$BUILD_DIR/k8s/deployment.yaml" 2>/dev/null || true
  kubectl apply -f "$BUILD_DIR/k8s/service.yaml" 2>/dev/null || true
  if kubectl get deployment cortex-app -n cortex >/dev/null 2>&1; then
    kubectl rollout restart deployment/cortex-app -n cortex
    kubectl rollout status deployment/cortex-app -n cortex --timeout=300s
    return 0
  fi
  return 1
}

# Primary hotfix path: systemd + nginx (production serves cortex on :6001 this way)
deploy_systemd

echo "=== Run appearance DB schema patch ==="
if [ -x /opt/cortex/venv-prod/bin/python ]; then
  (cd /opt/cortex && /opt/cortex/venv-prod/bin/python -c "
from models.chatbot_appearance import ChatbotAppearance
cols = ChatbotAppearance.ensure_schema()
print('chatbot_appearance columns:', 'welcome_message' in (cols or set()))
")
fi

if build_and_import; then
  rollout_k8s || true
fi

curl -sf http://127.0.0.1:6001/health || true
echo "✅ Cortex hotfix script finished"