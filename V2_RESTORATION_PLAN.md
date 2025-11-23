# 🔄 V2 Restoration Plan - Restore v1 Behavior

**Date:** 2025-11-23  
**Status:** Planning Phase  
**Goal:** Restore all v1 functionality to v2 (except chatbot integration which is already working)

## ⚠️ CRITICAL REMINDER: MODULARIZATION FIRST

**Why we restructured:** Too much code in single files  
**Rule:** Always split large files into smaller, reusable components  
**Applies to:** HTML, JavaScript, Python files  

### Current Large Files (Need Splitting):
- `templates/dashboard.html` - **1881 lines** ⚠️ CRITICAL
- `templates/index.html` - **593 lines** ⚠️ HIGH
- Check all Python blueprints for size

### Modularization Strategy:
1. **HTML Templates:** Split into components (header, sidebar, tabs, etc.)
2. **JavaScript:** Separate into modules by functionality
3. **Python:** Keep blueprints focused, extract complex logic to services
4. **CSS:** Already separated, maintain separation

---

## 📊 Executive Summary

After restructuring from v1 (monolithic app.py) to v2 (blueprint-based), several endpoints and features were lost. This plan outlines the systematic restoration of v1 behavior.

---

## ✅ PHASE 1: Quick Fixes (COMPLETED)

### 1.1 Registration Flow
- ✅ **Fixed:** Registration redirects to `/login` (not dashboard)
- ✅ **Fixed:** Registration does NOT auto-login user
- ✅ **Fixed:** Success message shows in green (not error color)

**Status:** ✅ DONE

---

## 📋 PHASE 2: Route Comparison

### V1 Routes: 46 total
- **Pages:** 14 routes
- **API:** 29 endpoints
- **Chat:** 3 routes

### V2 Routes: 16 total
- **Pages:** 9 routes
- **API:** 6 endpoints
- **Chat:** 1 route

### Missing Routes: 30 total

#### Missing Pages (6):
1. `/health` - Health check endpoint
2. `/refresh` - Refresh functionality
3. `/reset-all` - Reset all data
4. `/template` - Template page
5. `/update_faq` - FAQ update page
6. `/website-a` - Website demo page

#### Missing API Endpoints (18):
1. `/api/backup-knowledge` - Backup knowledge base
2. `/api/categories` - Get categories
3. `/api/category-analytics` - Category analytics
4. `/api/clear-logs` - Clear logs
5. `/api/crawl` - Web crawling
6. `/api/files-by-category` - Files filtered by category
7. `/api/list-backups` - List all backups
8. `/api/llm-config` - LLM configuration
9. `/api/prompt` - Get/Set prompt
10. `/api/reset-knowledge` - Reset knowledge base
11. `/api/restore-knowledge` - Restore from backup
12. `/api/test-llm` - Test LLM connection
13. `/api/website-config` - Get website config
14. `/api/website/<website_id>` - Manage website (PUT/DELETE)
15. `/api/website/<website_id>/analytics` - Website analytics
16. `/api/website/<website_id>/stats` - Website statistics
17. `/api/websites` - List all websites
18. `/api/websites/bulk` - Bulk website operations

#### Missing Chat Routes (1):
1. `/chat-interface` - Already exists but needs verification

---

## 🎯 PHASE 3: Priority Classification

### 🔴 CRITICAL (Must Restore - Breaks Core Functionality)

1. **`/api/prompt`** - Prompt management (GET/POST)
   - **Impact:** Settings tab broken
   - **Priority:** CRITICAL
   - **Complexity:** Medium

2. **`/api/categories`** - Category management
   - **Impact:** File organization broken
   - **Priority:** CRITICAL
   - **Complexity:** Low

3. **`/api/files-by-category`** - Filter files by category
   - **Impact:** Knowledge base tab broken
   - **Priority:** CRITICAL
   - **Complexity:** Low

4. **`/api/websites`** - Website management
   - **Impact:** Dashboard initialization broken
   - **Priority:** CRITICAL
   - **Complexity:** Medium

5. **`/api/website/<website_id>/stats`** - Website statistics
   - **Impact:** Analytics tab broken
   - **Priority:** CRITICAL
   - **Complexity:** Medium

### 🟡 HIGH PRIORITY (Important Features)

6. **`/api/knowledge-stats-detailed`** - Detailed knowledge stats
   - **Impact:** Analytics incomplete
   - **Priority:** HIGH
   - **Complexity:** Low

7. **`/api/crawl`** - Web crawling functionality
   - **Impact:** Web crawling feature missing
   - **Priority:** HIGH
   - **Complexity:** High

8. **`/api/backup-knowledge`** - Backup knowledge base
   - **Impact:** Backup feature missing
   - **Priority:** HIGH
   - **Complexity:** Medium

9. **`/api/list-backups`** - List backups
   - **Impact:** Backup management missing
   - **Priority:** HIGH
   - **Complexity:** Low

10. **`/api/restore-knowledge`** - Restore from backup
    - **Impact:** Restore feature missing
    - **Priority:** HIGH
    - **Complexity:** Medium

11. **`/api/reset-knowledge`** - Reset knowledge base
    - **Impact:** Reset feature missing
    - **Priority:** HIGH
    - **Complexity:** Low

### 🟢 MEDIUM PRIORITY (Nice to Have)

12. **`/api/website-config`** - Get website config
    - **Impact:** Widget configuration
    - **Priority:** MEDIUM
    - **Complexity:** Low

13. **`/api/website/<website_id>`** - Manage website
    - **Impact:** Website CRUD operations
    - **Priority:** MEDIUM
    - **Complexity:** Medium

14. **`/api/website/<website_id>/analytics`** - Website analytics
    - **Impact:** Advanced analytics
    - **Priority:** MEDIUM
    - **Complexity:** Medium

15. **`/api/category-analytics`** - Category analytics
    - **Impact:** Category insights
    - **Priority:** MEDIUM
    - **Complexity:** Medium

16. **`/api/websites/bulk`** - Bulk operations
    - **Impact:** Bulk website management
    - **Priority:** MEDIUM
    - **Complexity:** Medium

17. **`/api/llm-config`** - LLM configuration
    - **Impact:** LLM settings
    - **Priority:** MEDIUM
    - **Complexity:** Low

18. **`/api/test-llm`** - Test LLM connection
    - **Impact:** LLM testing
    - **Priority:** MEDIUM
    - **Complexity:** Low

### ⚪ LOW PRIORITY (Optional)

19. **`/health`** - Health check
    - **Impact:** Monitoring
    - **Priority:** LOW
    - **Complexity:** Very Low

20. **`/refresh`** - Refresh functionality
    - **Impact:** Manual refresh
    - **Priority:** LOW
    - **Complexity:** Low

21. **`/reset-all`** - Reset all data
    - **Impact:** Admin function
    - **Priority:** LOW
    - **Complexity:** Medium

22. **`/template`** - Template page
    - **Impact:** Template management
    - **Priority:** LOW
    - **Complexity:** Low

23. **`/update_faq`** - FAQ update
    - **Impact:** FAQ management
    - **Priority:** LOW
    - **Complexity:** Low

24. **`/website-a`** - Website demo
    - **Impact:** Demo page
    - **Priority:** LOW
    - **Complexity:** Low

25. **`/api/clear-logs`** - Clear logs
    - **Impact:** Log management
    - **Priority:** LOW
    - **Complexity:** Low

---

## 📝 PHASE 4: Implementation Plan

### ⚠️ MODULARIZATION FIRST (Before Adding Features)

#### Step 0: Split Large Files (MUST DO FIRST)
1. **Split `dashboard.html` (1881 lines)**
   - [ ] Extract header → `templates/components/header.html`
   - [ ] Extract tabs → `templates/components/dashboard_tabs.html`
   - [ ] Extract JavaScript → `static/js/dashboard/` (split by feature)
   - [ ] Extract CSS → Already in `<style>`, consider moving to separate file
   - [ ] Main dashboard.html should only include components

2. **Split `index.html` (593 lines)**
   - [ ] Extract chat interface → `templates/components/chat_interface.html`
   - [ ] Extract JavaScript → `static/js/chat/chat_interface.js`
   - [ ] Keep main file minimal

3. **Review Python Blueprints**
   - [ ] Check `api.py` size - split if > 500 lines
   - [ ] Check `widget.py` size - split if > 500 lines
   - [ ] Extract complex logic to services (already done, verify)

#### Step 1: Extract v1 Implementations
- [ ] Extract `/api/prompt` implementation from v1
- [ ] Extract `/api/categories` implementation from v1
- [ ] Extract `/api/files-by-category` implementation from v1
- [ ] Extract `/api/websites` implementation from v1
- [ ] Extract `/api/website/<website_id>/stats` implementation from v1
- [ ] Extract all other missing endpoints

### Step 2: Adapt to v2 Architecture
- [ ] Convert to blueprint format
- [ ] Use user-based isolation (not website-based)
- [ ] Update imports and dependencies
- [ ] Ensure proper authentication

### Step 3: Implement Critical Endpoints (Priority Order)
1. [ ] `/api/prompt` (GET/POST)
2. [ ] `/api/categories` (GET)
3. [ ] `/api/files-by-category` (GET)
4. [ ] `/api/websites` (GET) - Return empty/default for now
5. [ ] `/api/website/<website_id>/stats` (GET) - Return default stats

### Step 4: Implement High Priority Endpoints
6. [ ] `/api/knowledge-stats-detailed` (GET)
7. [ ] `/api/backup-knowledge` (POST)
8. [ ] `/api/list-backups` (GET)
9. [ ] `/api/restore-knowledge` (POST)
10. [ ] `/api/reset-knowledge` (POST)
11. [ ] `/api/crawl` (POST)

### Step 5: Implement Medium Priority Endpoints
12. [ ] `/api/website-config` (GET)
13. [ ] `/api/website/<website_id>` (PUT/DELETE)
14. [ ] `/api/website/<website_id>/analytics` (GET)
15. [ ] `/api/category-analytics` (GET)
16. [ ] `/api/websites/bulk` (POST)
17. [ ] `/api/llm-config` (GET/POST)
18. [ ] `/api/test-llm` (POST)

### Step 6: Implement Low Priority Endpoints (Optional)
19. [ ] `/health` (GET)
20. [ ] `/refresh` (GET/POST)
21. [ ] `/reset-all` (POST) - Admin only
22. [ ] `/template` (GET)
23. [ ] `/update_faq` (GET/POST)
24. [ ] `/website-a` (GET)
25. [ ] `/api/clear-logs` (POST)

### Step 7: Testing
- [ ] Test each endpoint after implementation
- [ ] Verify response formats match v1
- [ ] Test error handling
- [ ] Test authentication/authorization
- [ ] Test user isolation

### Step 8: Documentation
- [ ] Update API documentation
- [ ] Document any intentional changes from v1
- [ ] Update INVESTIGATION_REPORT.md

---

## 🔍 PHASE 5: Detailed Investigation Required

Before implementing, need to:

1. **Study v1 `/api/prompt` implementation**
   - How it stores/retrieves prompts
   - User-specific or global?
   - Response format

2. **Study v1 `/api/categories` implementation**
   - How categories are managed
   - Default categories
   - Category structure

3. **Study v1 `/api/websites` implementation**
   - Website management system
   - How it relates to users
   - Default website handling

4. **Study v1 dashboard behavior**
   - How dashboard initializes
   - What data it expects
   - Error handling

5. **Study v1 file upload flow**
   - Category assignment
   - File organization
   - Knowledge base integration

---

## ⚠️ Important Notes

1. **User Isolation:** v2 uses user-based isolation, v1 used website-based. Need to adapt.

2. **Chatbot Integration:** Already working in v2, exclude from restoration.

3. **Response Formats:** Must match v1 exactly for frontend compatibility.

4. **Authentication:** All endpoints must use `@login_required` and user isolation.

5. **Testing:** Test after each implementation to catch issues early.

---

## 📊 Progress Tracking

- **Phase 1:** ✅ COMPLETE
- **Phase 2:** 🔄 IN PROGRESS
- **Phase 3:** ⏳ PENDING
- **Phase 4:** ⏳ PENDING
- **Phase 5:** ⏳ PENDING

---

## 🎯 Next Steps

1. **Complete v1 investigation** - Extract all endpoint implementations
2. **Create detailed implementation specs** - For each missing endpoint
3. **Get approval** - Review plan with user
4. **Implement step by step** - One endpoint at a time
5. **Test thoroughly** - After each implementation

---

**Last Updated:** 2025-11-23  
**Next Review:** After v1 investigation complete

