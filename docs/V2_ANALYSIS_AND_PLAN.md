# V2 Analysis & Restructure Plan

## 📊 Current State Analysis

### Code Statistics
- **app.py**: 3,165 lines (⚠️ VIOLATES CODING RULES - should be < 200 lines)
- **Templates**: 27 HTML files (many duplicates)
- **Static Files**: 15 JS/CSS files (some duplicates)
- **Routes**: ~20+ routes all in app.py

### Current User Flow

```
1. User visits site
   ↓
2. Login/Register (auth.py)
   ↓
3. Dashboard (dashboard_v1.html)
   ├── Overview Tab
   ├── LLM Configuration Tab
   ├── Knowledge Management Tab
   ├── Prompt Editor Tab
   ├── Widget Integration Tab
   └── System Management Tab
   ↓
4. Configure Chatbot
   ├── Set chatbot name
   ├── Upload knowledge base files
   ├── Customize prompt
   └── Get embed script
   ↓
5. Test/Demo
   ├── /demo - Preview widget
   └── /chat-interface - Test chat
   ↓
6. Deploy
   └── Copy embed script to website
```

## 🎯 UI Evaluation - What We Really Need

### ✅ ESSENTIAL Pages/Templates

1. **Authentication** (2 pages)
   - `login.html` ✅ KEEP
   - `register.html` ✅ KEEP

2. **Dashboard** (1 page)
   - `dashboard_v1.html` ✅ KEEP (rename to `dashboard.html`)
   - **Tabs needed:**
     - Overview (stats, file list)
     - Knowledge Management (upload files)
     - Prompt Editor (name + prompt)
     - Widget Integration (embed script)
     - System Management (optional - can be removed for v2)

3. **Widget/Demo** (2 pages)
   - `widget.html` ✅ KEEP (for embed)
   - `demo_chatbox.html` ✅ KEEP (for preview)

### ❌ REMOVE - Duplicates/Unused

**Templates to DELETE:**
- `dashboard_v1_backup.html`
- `dashboard_v1_before_*.html` (7 files)
- `dashboard_v1_old*.html` (6 files)
- `dashboard_v1_working.html`
- `dashboard_v1_b.html`
- `dashboard.html` (if different from dashboard_v1.html)
- `index copy.html`
- `widget33.html`
- `analytics.html` (if not used)
- `tree_diagram.html` (if not used)
- `website_a.html` (if not used)
- `index.html` (check if used by /chat-interface)

**Static Files to DELETE:**
- `static/embed copy.js`
- `static/embed copy 2.js`
- `static/embed_xx.js`
- `static/v2/css/dashboard_backup.css`
- `static/v2/js/test-alert.js`

## 📁 Proposed V2 Structure

```
chatbot/
├── app.py                    # ~100 lines - Flask initialization only
├── config/
│   ├── __init__.py
│   ├── settings.py          # Flask config classes
│   └── constants.py         # Constants (SUGGESTED_MESSAGES, etc.)
├── models/
│   ├── __init__.py
│   └── user.py              # User model (from models.py)
├── blueprints/
│   ├── __init__.py          # Register all blueprints
│   ├── auth.py              # Login, register, logout
│   ├── dashboard.py         # Dashboard route
│   ├── api.py                # All /api/* endpoints
│   ├── widget.py             # /widget, /embed.js, /demo
│   └── chat.py               # /chat endpoint
├── services/
│   ├── __init__.py
│   ├── chatbot_service.py   # Chat logic, RAG, LLM calls
│   ├── knowledge_service.py # File upload, vectorstore, knowledge base
│   ├── config_service.py    # User config (name, prompt, API keys)
│   └── file_service.py      # File operations
├── utils/
│   ├── __init__.py
│   ├── api_key.py           # API key generation/validation
│   ├── prompts.py            # Prompt templates
│   └── helpers.py            # General utilities
├── templates/
│   ├── base.html             # Base template (NEW)
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── dashboard/
│   │   └── dashboard.html    # Main dashboard (renamed from dashboard_v1.html)
│   └── widget/
│       ├── widget.html
│       └── demo.html         # Renamed from demo_chatbox.html
├── static/
│   ├── css/
│   │   ├── auth.css
│   │   └── dashboard.css     # Moved from v2/css/dashboard.css
│   ├── js/
│   │   ├── auth.js           # NEW - if needed
│   │   ├── dashboard/
│   │   │   ├── core.js       # From v2/js/dashboard-core.js
│   │   │   ├── overview.js   # From v2/js/dashboard-overview.js
│   │   │   ├── prompt.js     # From v2/js/dashboard-prompt.js
│   │   │   ├── system.js     # From v2/js/dashboard-system.js
│   │   │   └── utils.js      # From v2/js/dashboard-utils.js
│   │   └── embed.js          # Main embed script
│   └── img/
│       └── favicon.svg
├── migrations/
│   └── (keep as is)
└── tests/
    ├── test_functionality.py
    └── test_knowledge_base.py
```

## 🔧 Refactoring Plan

### Phase 1: Cleanup (Remove Duplicates)

**Step 1.1: Delete Duplicate Templates**
```bash
# Remove all backup/old templates
rm templates/dashboard_v1_*.html (except dashboard_v1.html)
rm templates/index copy.html
rm templates/widget33.html
# ... etc
```

**Step 1.2: Delete Duplicate Static Files**
```bash
rm static/embed copy*.js
rm static/embed_xx.js
rm static/v2/css/dashboard_backup.css
rm static/v2/js/test-alert.js
```

**Step 1.3: Archive Old Code**
- Keep `archive/` folder for reference
- Remove from active codebase

### Phase 2: Create Folder Structure

**Step 2.1: Create Directories**
```bash
mkdir -p config models blueprints services utils
mkdir -p templates/{auth,dashboard,widget}
mkdir -p static/{css,js/dashboard,img}
mkdir -p tests
```

**Step 2.2: Create __init__.py files**
- All Python packages need `__init__.py`

### Phase 3: Extract Models

**Step 3.1: Move User Model**
- `models.py` → `models/user.py`
- Update imports

### Phase 4: Extract Services

**Step 4.1: Create `services/chatbot_service.py`**
```python
# Functions to extract from app.py:
- get_chatbot_response(user_id, message, context)
- load_user_prompt(user_id)
- format_chat_response(reply)
```

**Step 4.2: Create `services/knowledge_service.py`**
```python
# Functions to extract:
- upload_file(user_id, file, category)
- delete_file(user_id, filename, category)
- get_user_vectorstore(user_id)
- remove_from_vectorstore(user_id, filename)
- get_knowledge_stats(user_id)
```

**Step 4.3: Create `services/config_service.py`**
```python
# Functions to extract:
- load_user_chatbot_config(user_id)
- save_user_chatbot_config(user_id, config)
- get_user_api_key(user_id)
- validate_api_key(api_key)
- generate_user_api_key(user_id)
```

**Step 4.4: Create `services/file_service.py`**
```python
# Functions to extract:
- save_uploaded_file(user_id, file, category)
- list_user_files(user_id)
- delete_user_file(user_id, filename, category)
- process_file_for_user(user_id, file, category)
```

### Phase 5: Extract Blueprints

**Step 5.1: Create `blueprints/auth.py`**
```python
# Routes:
- /login (GET, POST)
- /register (GET, POST)
- /logout
```

**Step 5.2: Create `blueprints/dashboard.py`**
```python
# Routes:
- /dashboard (GET)
- /chat-interface (GET) - if needed
```

**Step 5.3: Create `blueprints/api.py`**
```python
# Routes:
- /api/user/chatbot-config (GET, POST)
- /api/knowledge-stats (GET)
- /api/files (GET)
- /api/files/<filename> (DELETE)
- /api/files/bulk (DELETE)
- /api/upload (POST)
- /api/llm-config (GET)
- /api/test-llm (POST)
```

**Step 5.4: Create `blueprints/widget.py`**
```python
# Routes:
- /widget (GET)
- /embed.js (GET)
- /demo (GET)
```

**Step 5.5: Create `blueprints/chat.py`**
```python
# Routes:
- /chat (POST)
```

### Phase 6: Extract Utils

**Step 6.1: Create `utils/api_key.py`**
```python
- generate_user_api_key(user_id)
- get_user_api_key(user_id)
- validate_api_key(api_key)
```

**Step 6.2: Create `utils/prompts.py`**
```python
- get_default_prompt_with_name(bot_name)
- get_default_prompt()
```

**Step 6.3: Create `utils/helpers.py`**
```python
- allowed_file(filename)
- format_file_size(bytes)
- Other general helpers
```

### Phase 7: Extract Config

**Step 7.1: Create `config/settings.py`**
```python
- DevelopmentConfig
- ProductionConfig
- TestingConfig
```

**Step 7.2: Create `config/constants.py`**
```python
- SUGGESTED_MESSAGES
- ALLOWED_EXTENSIONS
- FILE_CATEGORIES
- Other constants
```

### Phase 8: Refactor app.py

**Step 8.1: Minimal app.py**
```python
from flask import Flask
from config.settings import Config
from blueprints import register_blueprints
from auth import setup_login_manager

app = Flask(__name__)
app.config.from_object(Config)

setup_login_manager(app)
register_blueprints(app)

if __name__ == '__main__':
    app.run()
```

### Phase 9: Update Templates

**Step 9.1: Create base.html**
- Common layout
- Header, footer
- Include all CSS/JS

**Step 9.2: Update template paths**
- Update all `render_template()` calls
- Update static file paths

**Step 9.3: Organize templates**
- Move to subdirectories
- Update imports

### Phase 10: Update Static Files

**Step 10.1: Reorganize CSS**
- Move `v2/css/dashboard.css` → `css/dashboard.css`
- Update template links

**Step 10.2: Reorganize JS**
- Move `v2/js/dashboard-*.js` → `js/dashboard/*.js`
- Update template script tags

### Phase 11: Testing

**Step 11.1: Update test imports**
- Fix all import paths
- Run tests

**Step 11.2: Manual testing**
- Test all routes
- Test all functionality
- Verify UI works

## 📋 Implementation Checklist

### Cleanup
- [ ] Delete 20+ duplicate template files
- [ ] Delete duplicate static files
- [ ] Remove unused test files
- [ ] Clean up archive folder

### Structure
- [ ] Create all directories
- [ ] Create __init__.py files
- [ ] Move templates to subdirectories
- [ ] Reorganize static files

### Code Refactoring
- [ ] Extract models
- [ ] Extract services (4 files)
- [ ] Extract blueprints (5 files)
- [ ] Extract utils (3 files)
- [ ] Extract config (2 files)
- [ ] Refactor app.py to < 200 lines

### Testing
- [ ] Fix all imports
- [ ] Run automated tests
- [ ] Manual testing
- [ ] Verify all features work

## 🎯 Success Criteria

1. ✅ `app.py` < 200 lines
2. ✅ All routes in blueprints
3. ✅ All business logic in services
4. ✅ No duplicate files
5. ✅ Proper folder structure (following coding rules)
6. ✅ All tests passing
7. ✅ All functionality working
8. ✅ Clean, maintainable codebase

## 🚀 Next Steps

1. **Review this plan** - Confirm approach
2. **Start Phase 1** - Cleanup duplicates
3. **Create folder structure** - Phase 2
4. **Extract code** - Phases 3-7
5. **Refactor app.py** - Phase 8
6. **Update templates/static** - Phases 9-10
7. **Test everything** - Phase 11

---

**Status**: ✅ Plan Complete
**Ready to Start**: Awaiting approval

