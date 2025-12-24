# 🛡️ PRE-DEPLOYMENT CHECKLIST

**CRITICAL:** Always run these checks before pushing to `main` branch to prevent CI/CD failures and pod evictions.

---

## ✅ Mandatory Pre-Deployment Checks

### 1. Check Server Status (REQUIRED)
```bash
./check_server_status.sh
```

**What it checks:**
- ✅ Memory usage (must be < 85%)
- ✅ Disk usage (must be < 90%)
- ✅ CPU load (must be < 90%)
- ✅ Pod evictions (no recent evictions)
- ✅ Cortex namespace status
- ✅ Other namespaces health

**If checks fail:** DO NOT DEPLOY. Fix server issues first.

---

### 2. Run Pre-Deployment Tests (REQUIRED)
```bash
python3 pre_deploy_test.py
```

**What it checks:**
- ✅ Critical imports (Flask, LangChain, ChromaDB, etc.)
- ✅ Application imports (app, blueprints, services, models)
- ✅ LangChain version compatibility
- ✅ Python syntax validation
- ✅ Requirements file validation

**If tests fail:** DO NOT DEPLOY. Fix code issues first.

---

### 3. Verify Changes (RECOMMENDED)
```bash
# Review what you're about to push
git status
git diff origin/main

# Ensure only production code is included
git status --short | grep -E "(test_|\.pyc|__pycache__|\.db|chroma_db|logs/)"
# Should return nothing (no test files, cache, or local data)
```

---

## 🚨 Critical Rules

1. **NEVER push if server memory > 85%**
   - Risk of pod evictions
   - Check with: `./check_server_status.sh`

2. **NEVER push if imports fail**
   - CI/CD will fail
   - Check with: `python3 pre_deploy_test.py`

3. **NEVER push test files or local data**
   - Keep repository clean
   - Check with: `git status`

4. **ALWAYS check server status manually before pushing**
   - Don't rely on CI/CD to catch server issues
   - Run: `./check_server_status.sh`

---

## 📋 Quick Pre-Push Command

Run this before every push to main:

```bash
# 1. Check server status
./check_server_status.sh && \

# 2. Run pre-deployment tests
python3 pre_deploy_test.py && \

# 3. Verify git status
echo "=== Git Status ===" && \
git status --short && \

# 4. If all pass, show summary
echo "" && \
echo "✅ All checks passed - Safe to push!" && \
echo "Run: git push origin main"
```

---

## 🔍 What Each Check Prevents

| Check | Prevents |
|-------|----------|
| **Server Status** | Pod evictions, deployment failures, resource exhaustion |
| **Pre-Deployment Tests** | Import errors, dependency conflicts, syntax errors |
| **Git Status** | Accidental commits of test files, local data, cache |

---

## ⚠️ If Checks Fail

1. **Server Status Failed:**
   - Check server resources manually
   - Clean up evicted pods if needed
   - Wait for resources to free up
   - Re-run check before deploying

2. **Pre-Deployment Tests Failed:**
   - Fix import errors
   - Resolve dependency conflicts
   - Fix syntax errors
   - Re-run tests until all pass

3. **Git Status Shows Issues:**
   - Remove test files: `git rm --cached <file>`
   - Update `.gitignore` if needed
   - Clean up local data

---

**Remember:** It's better to wait and fix issues than to deploy broken code and cause production problems!
