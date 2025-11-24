# AWS Size Optimization Investigation Report
**Date:** November 24, 2025  
**Project:** Chatbot (RAG-based AI Chatbot)

## Executive Summary

The project is currently **7.3GB** in total size, with the virtual environment (`venv`) consuming **7.2GB** (99% of total size). This is primarily due to heavy ML/AI dependencies that are not needed for production deployment, especially since we're removing local LLM (Ollama) functionality.

## Current Size Breakdown

```
Total Project Size: 7.3GB
├── venv/                   7.2GB  (99%) ⚠️ MAJOR ISSUE
├── db/                     32MB
├── uploads/                5.0MB
├── chroma_db/              4.1MB
├── archive/                711KB
├── backups/                517KB
├── static/                 485KB
├── templates/              230KB
├── blueprints/             181KB
├── models/                 133KB
└── services/               92KB
```

## Root Causes

### 1. **Heavy ML/AI Dependencies (7.2GB in venv/)**

The virtual environment contains massive dependencies that are NOT needed for production:

#### **PyTorch & CUDA Libraries (~3-4GB)**
- `torch==2.7.1` - Full PyTorch installation
- `nvidia-cublas-cu12`, `nvidia-cuda-*`, `nvidia-cudnn-*` - CUDA libraries
- **Issue:** These are only needed for local model training/inference
- **Solution:** Remove entirely - we're using OpenAI API, not local models

#### **Transformers & Sentence-Transformers (~1-2GB)**
- `transformers==4.53.2` - HuggingFace transformers library
- `sentence-transformers==5.0.0` - For embeddings
- **Issue:** Only `sentence-transformers` is needed for embeddings (HuggingFaceEmbeddings)
- **Solution:** Keep minimal sentence-transformers, remove full transformers

#### **ChromaDB (~500MB)**
- `chromadb==1.0.15` - Vector database
- **Issue:** Includes unnecessary dependencies
- **Solution:** Keep but optimize

#### **Other Heavy Dependencies**
- `datasets==4.0.0` - Not needed (only for training)
- `scikit-learn==1.7.0` - May not be needed
- `pandas==2.3.1` - May not be needed
- `numpy==2.3.1` - Needed but can be optimized

### 2. **Ollama-Related Code (To Remove)**

Found **208 references** to Ollama across the codebase:
- `app.py` - Ollama LLM initialization
- `blueprints/api.py` - Ollama configuration endpoints
- `templates/components/dashboard_llm_tab.html` - Ollama UI
- `static/v2/js/dashboard-llm.js` - Ollama JavaScript
- `archive/ollama_rag_chatbot/` - Old Ollama code (711KB)

**Action Required:** Remove all Ollama code and UI elements.

### 3. **Unnecessary Files & Directories**

#### **Development Files (Should be in .gitignore)**
- `__pycache__/` directories (248KB total)
- `*.pyc` files (25 files found)
- `*.log` files (240KB)
- `users.db` (120KB) - Should use MySQL in production
- `chroma_db/` (4.1MB) - User data, should be on S3 or external storage
- `uploads/` (5.0MB) - User uploads, should be on S3

#### **Archive & Backups (1.2MB)**
- `archive/ollama_rag_chatbot/` (711KB) - Old code
- `backups/20251112_222256/` (517KB) - Old backups
- **Action:** Remove or move to separate archive repository

### 4. **Missing .gitignore Entries**

Current `.gitignore` only has:
```
venv/
myenv/.env
.env.env
.env
.env
```

**Missing:**
- `__pycache__/`
- `*.pyc`
- `*.log`
- `*.db`
- `chroma_db/`
- `uploads/`
- `config/user_*/`
- `backups/`
- `archive/`

## Optimization Recommendations

### Priority 1: Remove Heavy Dependencies (Expected: ~6GB reduction)

1. **Remove PyTorch & CUDA** (~3-4GB)
   ```bash
   # Remove from requirements.txt:
   - torch==2.7.1
   - nvidia-* (all packages)
   - triton==3.3.1
   ```

2. **Remove Full Transformers** (~1-2GB)
   ```bash
   # Keep only sentence-transformers for embeddings
   - transformers==4.53.2  # Remove
   + sentence-transformers==5.0.0  # Keep (minimal)
   ```

3. **Remove Training Dependencies** (~500MB)
   ```bash
   - datasets==4.0.0
   - scikit-learn==1.7.0  # Check if needed
   - pandas==2.3.1  # Check if needed
   ```

### Priority 2: Remove Ollama Code (Expected: ~1MB reduction)

1. Remove Ollama imports and initialization from `app.py`
2. Remove Ollama UI from `dashboard_llm_tab.html`
3. Remove Ollama JavaScript from `dashboard-llm.js`
4. Remove Ollama API endpoints from `blueprints/api.py`
5. Delete `archive/ollama_rag_chatbot/` directory

### Priority 3: Clean Up Development Files (Expected: ~10MB reduction)

1. Add proper `.gitignore` entries
2. Remove `__pycache__/` directories
3. Remove `*.log` files
4. Move `chroma_db/` and `uploads/` to external storage (S3)
5. Remove `backups/` and `archive/` directories

### Priority 4: Optimize Production Dependencies

1. Use `--no-cache-dir` in pip install
2. Use Alpine Linux base image for Docker (smaller)
3. Multi-stage Docker builds
4. Remove development dependencies

## Expected Size After Optimization

```
Current:  7.3GB
After:   ~500MB-1GB (production-ready)
Reduction: ~85-93%
```

**Breakdown:**
- Application code: ~2MB
- Optimized dependencies: ~300-500MB
- Static assets: ~500KB
- Templates: ~230KB

## CI/CD Implementation Plan

### 1. **GitHub Actions Workflow**

Create `.github/workflows/deploy.yml`:
- **Trigger:** Push to `main` or `v2` branch
- **Steps:**
  1. Checkout code
  2. Set up Python 3.11
  3. Install dependencies (production only)
  4. Run tests
  5. Build Docker image
  6. Push to ECR (AWS)
  7. Deploy to ECS/EC2

### 2. **Dockerfile Optimization**

- Multi-stage build
- Alpine Linux base
- Only production dependencies
- No development tools

### 3. **Environment Variables**

- Store secrets in GitHub Secrets
- Use AWS Systems Manager Parameter Store
- No `.env` files in production

### 4. **Deployment Targets**

- **Staging:** Auto-deploy on push to `v2` branch
- **Production:** Manual approval required

## Action Items

### Immediate (This Week)
- [ ] Remove Ollama code from codebase
- [ ] Update `.gitignore`
- [ ] Remove `archive/` and `backups/` directories
- [ ] Clean up `__pycache__/` and `*.pyc` files

### Short-term (Next Week)
- [ ] Create optimized `requirements.txt` (production only)
- [ ] Remove PyTorch and CUDA dependencies
- [ ] Remove full transformers library
- [ ] Test with minimal dependencies

### Medium-term (Next 2 Weeks)
- [ ] Set up GitHub Actions CI/CD
- [ ] Create optimized Dockerfile
- [ ] Move `chroma_db/` and `uploads/` to S3
- [ ] Set up AWS deployment pipeline

## Files to Modify

1. `requirements.txt` - Remove heavy dependencies
2. `app.py` - Remove Ollama code
3. `blueprints/api.py` - Remove Ollama endpoints
4. `templates/components/dashboard_llm_tab.html` - Remove Ollama UI
5. `static/v2/js/dashboard-llm.js` - Remove Ollama JavaScript
6. `.gitignore` - Add missing entries
7. `.github/workflows/deploy.yml` - Create CI/CD workflow
8. `Dockerfile` - Create optimized production image

## Estimated Time Savings

- **Deployment Time:** 7.3GB → 500MB = **93% faster**
- **Build Time:** Reduced by ~80%
- **Storage Costs:** Reduced by ~93%
- **Bandwidth Costs:** Reduced by ~93%

---

**Next Steps:** Review this report and approve optimization plan before proceeding.

