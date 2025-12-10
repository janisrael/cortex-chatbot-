# CI/CD Workflow Documentation

## Overview
This repository uses GitHub Actions for continuous integration and deployment:
- **Main branch** → Deploys to **Hetzner Kubernetes** (k3s)
- **v2-appearance branch** → Deploys to **AWS EC2** (legacy, kept for compatibility)
- **v2 branch** → Deploys to **AWS EC2** (legacy, kept for compatibility)

## Workflows

### Main Deployment (`deploy.yml`)

**Triggers:**
- Push to `main` branch → Production deployment to **Hetzner Kubernetes** (standard)
- Push to `v2-appearance` branch → Staging deployment to **AWS EC2** (legacy)
- Push to `v2` branch → Production deployment to **AWS EC2** (legacy)
- Manual trigger via `workflow_dispatch`

**Jobs:**

1. **Test** (runs on all branches)
   - Python 3.11 setup
   - Install dependencies from `requirements-prod.txt`
   - Run linting (flake8)
   - Check for syntax errors
   - Verify imports

2. **Deploy Production** (main/v2/v2-appearance branches)
   - **Main branch**: Deploys to Hetzner Kubernetes
     - Builds Docker image
     - Uploads to Hetzner server
     - Imports into k3s
     - Restarts Kubernetes deployment
   - **v2-appearance/v2 branches**: Deploys to AWS EC2
     - Configure SSH access
     - Create deployment script
     - Deploy code to EC2 via SSH
     - Restart application in screen session
   - Verify deployment health

## Required GitHub Secrets

### For Main Branch (Hetzner Kubernetes)
| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `HETZNER_SSH_PRIVATE_KEY` | SSH private key content for Hetzner | Content of `~/.ssh/swordfishproject.pem` |
| `HETZNER_HOST` | Hetzner server IP address | `178.156.162.135` |
| `HETZNER_APP_URL` | Application URL (optional) | `https://cortex.janisrael.com` |

### For v2-appearance/v2 Branches (AWS EC2)
| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `AWS_SSH_PRIVATE_KEY` | SSH private key content | Content of `~/.ssh/swordfishproject.pem` |
| `AWS_EC2_HOST` | EC2 instance IP address | `16.52.149.96` |
| `AWS_EC2_USER` | SSH username | `ubuntu` |
| `AWS_DEPLOY_PATH` | Production deployment path | `/var/www/portfolio/chatbot` |
| `AWS_DEPLOY_PATH_STAGING` | Staging deployment path (optional) | `/var/www/portfolio/chatbot/staging` |
| `AWS_APP_PORT` | Application port (optional) | `6001` |
| `AWS_APP_PORT_STAGING` | Staging app port (optional) | `6002` |
| `AWS_APP_URL` | Production URL (optional) | `https://cortex.janisrael.com` |

## Getting SSH Private Key

On your local machine:

```bash
# Display the private key
cat ~/.ssh/swordfishproject.pem

# Copy the ENTIRE output including:
# -----BEGIN RSA PRIVATE KEY-----
# ... (all the key content) ...
# -----END RSA PRIVATE KEY-----
```

**Important**: Copy the entire key including the BEGIN and END lines.

## Adding Secrets in GitHub

1. Go to your repository on GitHub
2. Click `Settings` tab
3. Navigate to `Secrets and variables > Actions`
4. Click `New repository secret`
5. Enter the secret name (exactly as listed above)
6. Paste the value
7. Click `Add secret`
8. Repeat for all secrets

## Deployment Process

1. **Test Phase:**
   - Code is checked out
   - Dependencies installed
   - Linting and syntax checks
   - Import verification

2. **Deploy Phase:**
   - SSH connection configured
   - Deployment script created
   - Code pulled/cloned to server
   - Virtual environment activated
   - Dependencies installed
   - Application restarted in screen session
   - Health check verification

## Application Management

The application runs in a screen session for easy management:

```bash
# SSH to server
ssh -i ~/.ssh/swordfishproject.pem ubuntu@16.52.149.96

# View running screen sessions
screen -list

# Attach to application screen
screen -r chatbot-app        # Production
screen -r chatbot-app-staging  # Staging

# Detach from screen: Press Ctrl+A then D

# Check application health
curl http://localhost:6001/health
```

## Health Check

The application exposes a `/health` endpoint that returns:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-24T12:00:00Z"
}
```

## Troubleshooting

### Test Fails
- Check `requirements-prod.txt` for dependency issues
- Verify Python version compatibility
- Check GitHub Actions logs

### Deployment Fails

**Issue**: SSH connection fails
- Verify `AWS_EC2_HOST` and `AWS_EC2_USER` are correct
- Check SSH key is correctly formatted (include BEGIN/END lines)
- Ensure EC2 security group allows SSH from GitHub Actions IPs

**Issue**: Deployment fails
- Check deployment logs in Actions tab
- SSH to server and check manually
- Verify `AWS_DEPLOY_PATH` is correct
- Ensure Git repository is initialized on server

**Issue**: Application doesn't start
- Check screen sessions: `screen -list`
- View logs: `screen -r chatbot-app`
- Verify Python dependencies: `pip list`
- Check application logs in the screen session

### Health Check Fails
- Verify `/health` endpoint is accessible
- Check application is running: `screen -list`
- Verify port is correct and accessible
- Check nginx/load balancer configuration

## Manual Deployment

If automated deployment fails, deploy manually:

```bash
ssh -i ~/.ssh/swordfishproject.pem ubuntu@16.52.149.96
cd /var/www/portfolio/chatbot
git pull origin main
source venv-prod/bin/activate
pip install -r requirements-prod.txt

# Restart application
screen -S chatbot-app -X quit
screen -dmS chatbot-app bash -c "source venv-prod/bin/activate && python app.py"
```

## Manual Workflow Trigger

You can manually trigger deployments via GitHub Actions UI:
1. Go to Actions tab
2. Select "Deploy to AWS" workflow
3. Click "Run workflow"
4. Select branch and click "Run workflow"

