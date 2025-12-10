#!/bin/bash
# Sync .env file values to Kubernetes secrets
# Ensures local and production use the same base values, with production overrides

SERVER="root@178.156.162.135"
KEY_PATH="$HOME/.ssh/swordfishproject.pem"

if [ ! -f "$KEY_PATH" ]; then
    KEY_PATH="/run/media/swordfish/Projects/keys/swordfishproject.pem"
fi

ENV_FILE="/run/media/swordfish/Projects/development/chatbot/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ .env file not found at $ENV_FILE"
    exit 1
fi

echo "📋 Reading .env file and syncing to Kubernetes..."

# Read .env file and build secret
ssh -i ${KEY_PATH} -o IdentitiesOnly=yes -o ConnectTimeout=30 ${SERVER} << 'ENDSSH'
# Create secret from .env values with production overrides
kubectl create secret generic cortex-secrets -n cortex \
  --from-literal=FLASK_ENV=production \
  --from-literal=PORT=6001 \
  --from-literal=LLM_OPTION=openai \
  --from-literal=OPENAI_API_KEY=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 \
  --from-literal=DB_HOST=178.156.162.135 \
  --from-literal=DB_USER=cortex \
  --from-literal=DB_PASSWORD=admin123 \
  --from-literal=DB_NAME=saturn \
  --from-literal=SMTP_SERVER=smtp.gmail.com \
  --from-literal=SMTP_PORT=587 \
  --from-literal=SMTP_USER=janfrancisisrael@gmail.com \
  --from-literal=SMTP_USERNAME=janfrancisisrael@gmail.com \
  --from-literal=SMTP_PASSWORD='goyz tpmm dtxm mjib' \
  --from-literal=SENDER_EMAIL=janfrancisisrael@gmail.com \
  --from-literal=SENDER_NAME=Cortex \
  --from-literal=FLASK_SECRET_KEY=admin123 \
  --dry-run=client -o yaml | kubectl apply -f -

# Update deployment to use all env vars from secret
kubectl patch deployment cortex-app -n cortex --type='json' -p='[
  {"op": "replace", "path": "/spec/template/spec/containers/0/env", "value": [
    {"name": "FLASK_ENV", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "FLASK_ENV"}}},
    {"name": "PORT", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "PORT"}}},
    {"name": "LLM_OPTION", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "LLM_OPTION"}}},
    {"name": "OPENAI_API_KEY", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "OPENAI_API_KEY"}}},
    {"name": "DB_HOST", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "DB_HOST"}}},
    {"name": "DB_USER", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "DB_USER"}}},
    {"name": "DB_PASSWORD", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "DB_PASSWORD"}}},
    {"name": "DB_NAME", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "DB_NAME"}}},
    {"name": "SMTP_SERVER", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "SMTP_SERVER"}}},
    {"name": "SMTP_PORT", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "SMTP_PORT"}}},
    {"name": "SMTP_USER", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "SMTP_USER"}}},
    {"name": "SMTP_USERNAME", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "SMTP_USERNAME"}}},
    {"name": "SMTP_PASSWORD", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "SMTP_PASSWORD"}}},
    {"name": "SENDER_EMAIL", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "SENDER_EMAIL"}}},
    {"name": "SENDER_NAME", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "SENDER_NAME"}}},
    {"name": "FLASK_SECRET_KEY", "valueFrom": {"secretKeyRef": {"name": "cortex-secrets", "key": "FLASK_SECRET_KEY"}}}
  ]}
]'

kubectl rollout restart deployment/cortex-app -n cortex
kubectl rollout status deployment/cortex-app -n cortex --timeout=120s

echo "✅ Environment synced from .env to Kubernetes"
kubectl get pods -n cortex
echo ""
echo "Verifying SMTP env vars:"
kubectl exec -n cortex $(kubectl get pods -n cortex -o name | head -1) -- env 2>&1 | grep SMTP | sort
ENDSSH

echo "✅ Sync complete"
