# V2 Restructure Plan

## 🎯 Goal
Create a clean, modular v2 following coding rules:
- Component-based structure
- Proper folder organization
- No duplicate/backup files
- Modular, reusable code

## 📋 Phase 1: Cleanup (Remove Duplicates)

### Files to DELETE:

#### Templates (Duplicates/Backups)
- `templates/dashboard_v1_backup.html`
- `templates/dashboard_v1_before_js_core.html`
- `templates/dashboard_v1_before_llm.html`
- `templates/dashboard_v1_before_overview.html`
- `templates/dashboard_v1_before_prompt.html`
- `templates/dashboard_v1_before_system.html`
- `templates/dashboard_v1_before_utils.html`
- `templates/dashboard_v1_old.html`
- `templates/dashboard_v1_old_inline.html`
- `templates/dashboard_v1_old_inline_all.html`
- `templates/dashboard_v1_old_no_llm.html`
- `templates/dashboard_v1_old_no_overview.html`
- `templates/dashboard_v1_old_no_prompt.html`
- `templates/dashboard_v1_old_no_utils.html`
- `templates/dashboard_v1_working.html`
- `templates/dashboard_v1_b.html`
- `templates/index copy.html`
- `templates/widget33.html`
- `templates/test_alert.html`

#### Static Files (Duplicates)
- `static/embed copy.js`
- `static/embed copy 2.js`
- `static/embed_xx.js`
- `static/v2/css/dashboard_backup.css`
- `static/v2/js/test-alert.js`

#### Archive (Keep for reference, but not in v2)
- `archive/` - Move to separate location or keep as reference

#### Backups (Not needed in v2)
- `backups/` - Remove from v2

#### Test Files (Keep only essential)
- Keep: `test_functionality.py`, `test_knowledge_base.py`
- Remove: `test_upload.txt`, `test_alert.html`

### Files to KEEP:

#### Core Application
- `app.py` (will be refactored)
- `models.py`
- `auth.py`
- `db_config.py`
- `migrations.py`
- `requirements.txt`

#### Active Templates
- `templates/login.html`
- `templates/register.html`
- `templates/dashboard_v1.html` (main dashboard)
- `templates/widget.html`
- `templates/demo_chatbox.html`
- `templates/index.html` (if used)

#### Active Static Files
- `static/css/auth.css`
- `static/v2/css/dashboard.css`
- `static/v2/js/dashboard-*.js` (all active dashboard JS)
- `static/embed.js` (main embed script)
- `static/chat-widget.css`
- `static/favicon.svg`

#### Documentation
- Keep all `.md` files (they're documentation)

## 📁 Phase 2: Restructure (Following Coding Rules)

### Target Structure:

```
chatbot/
├── app.py                    # Main Flask app (minimal, just initialization)
├── config/
│   ├── __init__.py
│   ├── settings.py          # Configuration classes
│   └── constants.py         # Constants
├── models/
│   ├── __init__.py
│   └── user.py              # User model (move from models.py)
├── blueprints/
│   ├── __init__.py
│   ├── auth.py              # Login, register, logout routes
│   ├── dashboard.py         # Dashboard routes
│   ├── api.py               # API endpoints
│   ├── widget.py            # Widget/demo routes
│   └── chat.py              # Chat endpoint
├── services/
│   ├── __init__.py
│   ├── chatbot_service.py   # Chatbot logic
│   ├── knowledge_service.py # Knowledge base operations
│   ├── vectorstore_service.py # Vectorstore management
│   ├── file_service.py      # File upload/management
│   └── config_service.py    # User config management
├── utils/
│   ├── __init__.py
│   ├── api_key.py           # API key generation/validation
│   ├── prompts.py           # Prompt templates
│   └── helpers.py           # General helpers
├── templates/
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── dashboard/
│   │   └── dashboard.html
│   ├── widget/
│   │   ├── widget.html
│   │   └── demo.html
│   └── base.html            # Base template
├── static/
│   ├── css/
│   │   ├── auth.css
│   │   └── dashboard.css
│   ├── js/
│   │   ├── auth.js
│   │   ├── dashboard/
│   │   │   ├── core.js
│   │   │   ├── overview.js
│   │   │   ├── prompt.js
│   │   │   ├── system.js
│   │   │   └── utils.js
│   │   └── embed.js
│   └── img/
│       └── favicon.svg
├── migrations/
│   └── (keep as is)
├── tests/
│   ├── test_functionality.py
│   └── test_knowledge_base.py
└── requirements.txt
```

## 🔧 Phase 3: Code Refactoring

### app.py Breakdown:

**Current (3000+ lines)** → **Target (~100 lines)**

```python
# app.py (v2) - Minimal initialization
from flask import Flask
from config.settings import Config
from blueprints import register_blueprints

app = Flask(__name__)
app.config.from_object(Config)

register_blueprints(app)

if __name__ == '__main__':
    app.run()
```

### Route Distribution:

#### `blueprints/auth.py`
- `/login` (GET, POST)
- `/register` (GET, POST)
- `/logout`

#### `blueprints/dashboard.py`
- `/dashboard` (GET)
- `/demo` (GET)

#### `blueprints/api.py`
- `/api/user/chatbot-config` (GET, POST)
- `/api/knowledge-stats` (GET)
- `/api/files` (GET)
- `/api/files/<filename>` (DELETE)
- `/api/upload` (POST)
- `/api/llm-config` (GET)
- `/api/test-llm` (POST)

#### `blueprints/widget.py`
- `/widget` (GET)
- `/embed.js` (GET)

#### `blueprints/chat.py`
- `/chat` (POST)

### Service Layer:

#### `services/chatbot_service.py`
- `get_chatbot_response(user_id, message, context)`
- `load_user_prompt(user_id)`
- `get_user_config(user_id)`

#### `services/knowledge_service.py`
- `upload_file(user_id, file, category)`
- `delete_file(user_id, filename, category)`
- `get_user_vectorstore(user_id)`
- `remove_from_vectorstore(user_id, filename)`
- `get_knowledge_stats(user_id)`

#### `services/vectorstore_service.py`
- `create_vectorstore(user_id)`
- `get_retriever(user_id, k=5)`
- `search_documents(user_id, query, k=5)`

#### `services/file_service.py`
- `save_uploaded_file(user_id, file, category)`
- `list_user_files(user_id)`
- `delete_user_file(user_id, filename, category)`

#### `services/config_service.py`
- `load_user_chatbot_config(user_id)`
- `save_user_chatbot_config(user_id, config)`
- `get_user_api_key(user_id)`
- `validate_api_key(api_key)`

## 📝 Phase 4: Implementation Steps

1. **Create folder structure**
   - Create all directories
   - Add `__init__.py` files

2. **Move models**
   - Split `models.py` → `models/user.py`

3. **Extract services**
   - Move business logic from `app.py` to services

4. **Create blueprints**
   - Extract routes from `app.py` to blueprints

5. **Update imports**
   - Fix all import statements
   - Update template paths

6. **Clean up static files**
   - Remove duplicates
   - Organize by type

7. **Update templates**
   - Remove duplicates
   - Use base template
   - Update paths

8. **Test**
   - Run all tests
   - Verify functionality

## ✅ Success Criteria

- [ ] `app.py` < 200 lines
- [ ] All routes in blueprints
- [ ] All business logic in services
- [ ] No duplicate files
- [ ] Proper folder structure
- [ ] All tests passing
- [ ] All functionality working

## 🚀 Next Steps

1. Push v1 branch ✅
2. Create v2 branch from main
3. Start cleanup (Phase 1)
4. Restructure (Phase 2)
5. Refactor code (Phase 3)
6. Test everything
7. Merge v2 to main

---

**Status**: Planning Complete
**Next**: Create v2 branch and start cleanup

