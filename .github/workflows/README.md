# CI/CD Workflow Documentation

## Overview
This repository uses GitHub Actions for continuous integration and deployment to AWS ECS.

## Workflows

### Main Deployment (`deploy.yml`)

**Triggers:**
- Push to `main` branch → Production deployment
- Push to `v2` branch → Production deployment  
- Push to `v2-appearance` branch → Staging deployment
- Manual trigger via `workflow_dispatch`

**Jobs:**

1. **Test** (runs on all branches)
   - Python 3.11 setup
   - Install dependencies from `requirements-prod.txt`
   - Run linting (flake8)
   - Check for syntax errors
   - Verify imports

2. **Build and Deploy** (main/v2 branches only)
   - Build Docker image
   - Push to ECR: `chatbot:latest` and `chatbot:{sha}`
   - Deploy to ECS: `chatbot-cluster/chatbot-service`
   - Wait for deployment stabilization
   - Verify deployment health

3. **Deploy Staging** (v2-appearance branch only)
   - Build Docker image
   - Push to ECR: `chatbot-staging:latest` and `chatbot-staging:staging-{sha}`
   - Deploy to ECS: `chatbot-cluster-staging/chatbot-service-staging`
   - Verify deployment

## Required GitHub Secrets

- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key

## AWS Resources Required

### Production:
- ECR Repository: `chatbot`
- ECS Cluster: `chatbot-cluster`
- ECS Service: `chatbot-service`

### Staging:
- ECR Repository: `chatbot-staging`
- ECS Cluster: `chatbot-cluster-staging`
- ECS Service: `chatbot-service-staging`

## Docker Configuration

- **Base Image:** `python:3.11-slim`
- **Multi-stage build:** Yes (builder + runtime)
- **Port:** 6001
- **Health Check:** `/health` endpoint
- **Requirements:** `requirements-prod.txt` (optimized, no PyTorch/CUDA)

## Health Check

The application exposes a `/health` endpoint that returns:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-24T12:00:00Z"
}
```

## Deployment Process

1. **Test Phase:**
   - Code is checked out
   - Dependencies installed
   - Linting and syntax checks
   - Import verification

2. **Build Phase:**
   - Docker image built using multi-stage Dockerfile
   - Image tagged with commit SHA and `latest`
   - Image pushed to ECR

3. **Deploy Phase:**
   - ECS service updated with new image
   - Force new deployment triggered
   - Service waits for stabilization
   - Health check verification

## Troubleshooting

### Build Fails
- Check `requirements-prod.txt` for dependency issues
- Verify Dockerfile syntax
- Check GitHub Actions logs

### Deployment Fails
- Verify AWS credentials in GitHub Secrets
- Check ECR repository exists
- Verify ECS cluster and service names
- Check AWS region matches (`us-east-1`)

### Health Check Fails
- Verify `/health` endpoint is accessible
- Check application logs in CloudWatch
- Verify port 6001 is exposed and accessible

## Manual Deployment

You can manually trigger deployments via GitHub Actions UI:
1. Go to Actions tab
2. Select "Deploy to AWS" workflow
3. Click "Run workflow"
4. Select branch and click "Run workflow"

