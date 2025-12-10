#!/bin/bash
# Update Cortex SMTP Configuration
# Run this when SSH connection is available

SERVER="root@178.156.162.135"
KEY_PATH="$HOME/.ssh/swordfishproject.pem"

if [ ! -f "$KEY_PATH" ]; then
    KEY_PATH="/run/media/swordfish/Projects/keys/swordfishproject.pem"
fi

echo "Updating Cortex SMTP configuration..."

ssh -i ${KEY_PATH} -o IdentitiesOnly=yes -o ConnectTimeout=30 ${SERVER} << 'ENDSSH'
# Update cortex secret with correct SMTP credentials
kubectl create secret generic cortex-secrets -n cortex \
  --from-literal=OPENAI_API_KEY=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 \
  --from-literal=SMTP_SERVER=smtp.gmail.com \
  --from-literal=SMTP_PORT=587 \
  --from-literal=SMTP_USERNAME=janfrancisisrael@gmail.com \
  --from-literal=SMTP_USER=janfrancisisrael@gmail.com \
  --from-literal=SMTP_PASSWORD='goyz tpmm dtxm mjib' \
  --from-literal=SENDER_EMAIL=janfrancisisrael@gmail.com \
  --from-literal=SENDER_NAME=Cortex \
  --dry-run=client -o yaml | kubectl apply -f -

# Update deployment with all SMTP env vars
kubectl patch deployment cortex-app -n cortex --type='json' -p='[
  {"op": "replace", "path": "/spec/template/spec/containers/0/env", "value": [
    {"name": "OPENAI_API_KEY", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "OPENAI_API_KEY"}}},
    {"name": "DB_HOST", "value": "178.156.162.135"},
    {"name": "DB_USER", "value": "cortex"},
    {"name": "DB_PASSWORD", "value": "admin123"},
    {"name": "DB_NAME", "value": "saturn"},
    {"name": "SMTP_SERVER", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "SMTP_SERVER"}}},
    {"name": "SMTP_PORT", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "SMTP_PORT"}}},
    {"name": "SMTP_USERNAME", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "SMTP_USERNAME"}}},
    {"name": "SMTP_USER", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "SMTP_USER"}}},
    {"name": "SMTP_PASSWORD", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "SMTP_PASSWORD"}}},
    {"name": "SENDER_EMAIL", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "SENDER_EMAIL"}}},
    {"name": "SENDER_NAME", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "SENDER_NAME"}}}
  ]}
]'

kubectl rollout restart deployment/cortex-app -n cortex
kubectl rollout status deployment/cortex-app -n cortex --timeout=120s

echo "✅ Cortex SMTP configuration updated"
kubectl get pods -n cortex
kubectl exec -n cortex $(kubectl get pods -n cortex -o name | head -1) -- env 2>&1 | grep SMTP | head -5
ENDSSH

echo "✅ SMTP update complete"

