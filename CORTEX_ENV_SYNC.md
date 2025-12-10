# Cortex Environment Sync

## Current Status
- ✅ OTP table created in MySQL
- ✅ SMTP credentials configured in script
- ⏳ Waiting for SSH connection to apply

## .env File Values
```
FLASK_ENV=development
PORT=6001
LLM_OPTION=openai
OPENAI_API_KEY=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
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=saturn
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=janfrancisisrael@gmail.com
SMTP_PASSWORD=goyz tpmm dtxm mjib
```

## Production Overrides
- `DB_HOST`: `178.156.162.135` (instead of localhost)
- `DB_USER`: `cortex` (instead of root)
- `DB_PASSWORD`: `admin123` (instead of empty)
- `FLASK_ENV`: `production` (instead of development)

## To Apply
Run: `bash /run/media/swordfish/Projects/development/chatbot/sync-env-to-k8s.sh`

This will:
1. Create/update Kubernetes secret with all .env values
2. Apply production overrides for DB connection
3. Update deployment to use all env vars from secret
4. Restart Cortex deployment

## Verification
After running, check:
```bash
kubectl exec -n cortex <pod-name> -- env | grep SMTP
kubectl exec -n cortex <pod-name> -- env | grep DB_
```

