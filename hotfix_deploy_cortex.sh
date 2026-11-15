#!/bin/bash
# Cortex-only hotfix to Hetzner (k3s). Run from a machine that can SSH to the server.
# Credentials: workspace hetzner rule / check_server_status.sh
set -euo pipefail

HETZNER_HOST="${HETZNER_HOST:-178.156.162.135}"
HETZNER_USER="${HETZNER_USER:-root}"
HETZNER_PASS="${HETZNER_PASS:-rFRLpamP94tC}"
KEY="${HETZNER_SSH_KEY:-$HOME/.ssh/swordfishproject.pem}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

SSH_OPTS=(-o StrictHostKeyChecking=no -o ConnectTimeout=30 -o ServerAliveInterval=30)
if [[ -f "$KEY" ]]; then
  SSH_OPTS+=(-i "$KEY" -o IdentitiesOnly=yes)
  SCP=(scp "${SSH_OPTS[@]}")
  SSH=(ssh "${SSH_OPTS[@]}" "${HETZNER_USER}@${HETZNER_HOST}")
else
  if ! command -v sshpass &>/dev/null; then
    echo "Install sshpass or set HETZNER_SSH_KEY to a PEM file"
    exit 1
  fi
  SCP=(sshpass -p "$HETZNER_PASS" scp -o StrictHostKeyChecking=no -o ConnectTimeout=30)
  SSH=(sshpass -p "$HETZNER_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 "${HETZNER_USER}@${HETZNER_HOST}")
fi

echo "=== Cortex hotfix: tarball + Docker build on Hetzner only ==="
tar --exclude='.git' --exclude='venv*' --exclude='__pycache__' --exclude='*.pyc' \
    --exclude='.env' --exclude='chroma_db' --exclude='uploads' --exclude='*.db' \
    --exclude='logs' --exclude='data' -czf /tmp/cortex-hotfix.tar.gz .

"${SCP[@]}" /tmp/cortex-hotfix.tar.gz "${HETZNER_USER}@${HETZNER_HOST}:/tmp/"
rm -f /tmp/cortex-hotfix.tar.gz

"${SSH[@]}" bash -s <<'REMOTE'
set -e
cd /tmp && rm -rf cortex-build && mkdir cortex-build && cd cortex-build
tar -xzf /tmp/cortex-hotfix.tar.gz && rm -f /tmp/cortex-hotfix.tar.gz
docker build -t cortex:latest .
docker save cortex:latest | k3s ctr images import -
kubectl apply -f k8s/deployment.yaml -n cortex 2>/dev/null || kubectl rollout restart deployment/cortex-app -n cortex
kubectl rollout status deployment/cortex-app -n cortex --timeout=180s
echo "Health:"
kubectl get pods -n cortex -l app=cortex
REMOTE

echo "=== Public check ==="
curl -sf https://cortex.janisrael.com/health && echo ""