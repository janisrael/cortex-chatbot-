# GitHub Secrets Setup Guide for Chatbot CI/CD

## Step-by-Step Instructions

### 1. Go to GitHub Repository Settings

1. Open your chatbot repository on GitHub: `https://github.com/janisrael/chatbot`
2. Click on **Settings** tab (top menu)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret** button

---

## Required Secrets (Add These 4)

### Secret 1: `AWS_SSH_PRIVATE_KEY`

**Name:** `AWS_SSH_PRIVATE_KEY`

**Value:** Copy the entire content of your SSH private key file

**How to get it:**
```bash
cat ~/.ssh/swordfishproject.pem
```

**Important:** 
- Copy EVERYTHING including:
  - `-----BEGIN RSA PRIVATE KEY-----`
  - All the key content in between
  - `-----END RSA PRIVATE KEY-----`
- Make sure there are no extra spaces or line breaks

**Example format:**
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
(many lines of key content)
...
-----END RSA PRIVATE KEY-----
```

---

### Secret 2: `AWS_EC2_HOST`

**Name:** `AWS_EC2_HOST`

**Value:** `16.52.149.96`

(This is your EC2 instance IP address from aws-key.mdc)

---

### Secret 3: `AWS_EC2_USER`

**Name:** `AWS_EC2_USER`

**Value:** `ubuntu`

(This is the SSH username from aws-key.mdc)

---

### Secret 4: `AWS_DEPLOY_PATH`

**Name:** `AWS_DEPLOY_PATH`

**Value:** `/var/www/portfolio/cortex`

(This is where Cortex will be deployed on the server - note: project is called Cortex, not chatbot)

---

## Optional Secrets (Add if needed)

### Optional Secret 1: `AWS_APP_PORT`

**Name:** `AWS_APP_PORT`

**Value:** `6002`

(Cortex runs on port 6002. Only add if different)

---

### Optional Secret 2: `AWS_APP_PORT_STAGING`

**Name:** `AWS_APP_PORT_STAGING`

**Value:** `6002`

(Default port for staging. Only add if different from 6002)

---

### Optional Secret 3: `AWS_APP_URL`

**Name:** `AWS_APP_URL`

**Value:** `https://cortex.janisrael.com`

(Cortex production domain URL for health checks)

---

### Optional Secret 4: `AWS_DEPLOY_PATH_STAGING`

**Name:** `AWS_DEPLOY_PATH_STAGING`

**Value:** `/var/www/portfolio/cortex/staging`

(Only add if you want staging in a separate directory)

---

## Quick Copy-Paste Checklist

Go to GitHub → Settings → Secrets and variables → Actions → New repository secret

Add these one by one:

- [ ] **Name:** `AWS_SSH_PRIVATE_KEY`  
  **Value:** (Copy from `cat ~/.ssh/swordfishproject.pem`)

- [ ] **Name:** `AWS_EC2_HOST`  
  **Value:** `16.52.149.96`

- [ ] **Name:** `AWS_EC2_USER`  
  **Value:** `ubuntu`

- [ ] **Name:** `AWS_DEPLOY_PATH`  
  **Value:** `/var/www/portfolio/cortex`

---

## Verification

After adding all secrets:

1. Go to **Actions** tab
2. You should see the workflow listed
3. Try pushing to `v2-appearance` branch to test staging deployment
4. Or manually trigger: **Actions** → **Deploy to AWS** → **Run workflow**

---

## Troubleshooting

### If SSH key doesn't work:
- Make sure you copied the ENTIRE key including BEGIN/END lines
- Check there are no extra spaces
- Verify the key file exists: `ls -la ~/.ssh/swordfishproject.pem`

### If deployment fails:
- Check GitHub Actions logs
- Verify EC2 security group allows SSH from GitHub Actions IPs
- Test SSH manually: `ssh -i ~/.ssh/swordfishproject.pem ubuntu@16.52.149.96`

---

**Note:** These are the same secrets used for Sandata project, so if you already have them set up for Sandata, you can reuse the same values (except `AWS_DEPLOY_PATH` which should be different).

