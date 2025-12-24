# Cortex AI - Intelligent Chatbot Platform

**Version**: 2.2  
**Status**: Production Ready  
**Live URL**: https://cortex.janisrael.com

## Overview

**Cortex AI** is a full-stack AI-powered chatbot platform with RAG (Retrieval Augmented Generation), multi-LLM support, knowledge base management, and comprehensive admin dashboard. Built for businesses and developers who need intelligent, context-aware chatbots that learn from their content.

![Chatbot Interface](docs/details/chatbot-screenshot.png)

### Key Value Propositions

- **Multi-LLM Support**: OpenAI GPT-4o-mini, Google Gemini, Anthropic Claude, Groq Llama, DeepSeek, Together AI
- **RAG-Powered Responses**: Vector-based knowledge retrieval using ChromaDB for context-aware answers
- **Knowledge Base Management**: Upload documents, crawl websites, manage FAQs with automatic ingestion
- **User Isolation**: Complete data isolation per user with separate vectorstores and databases
- **Customizable Appearance**: Theme customization, custom avatars, widget embedding
- **Admin Dashboard**: User management, analytics, system monitoring, API key management
- **Production Ready**: Kubernetes deployment with persistent storage, health checks, and CI/CD

---

## System Architecture

![System Architecture](docs/details/system-architecture.png)

**Deployment Architecture**: Kubernetes (k3s) on Hetzner Cloud with persistent volumes

- **Container**: Docker image `cortex:latest` running Flask application
- **Namespace**: `cortex` (isolated from other projects)
- **Storage**: 3 Persistent Volume Claims (Database: 1Gi, ChromaDB: 10Gi, Config: 1Gi)
- **Database**: MySQL (external) + SQLite (fallback in pod)
- **Port**: 6001 (internal ClusterIP service)
- **Resources**: CPU 300m-1, Memory 512Mi-1Gi

---

## Application Architecture

![Application Architecture](docs/details/application-architecture.png)

### Frontend Components

- **Dashboard Core** (`dashboard-core.js`) - Main dashboard orchestration
- **Dashboard Overview** (`dashboard-overview.js`) - Overview tab with metrics
- **Dashboard LLM** (`dashboard-llm.js`) - LLM provider selection and configuration
- **Dashboard Appearance** (`dashboard-appearance.js`) - Theme and widget customization
- **Dashboard Knowledge** (`knowledge.js`) - Knowledge base management
- **Dashboard Prompt** (`dashboard-prompt.js`) - Prompt customization
- **File Management** (`file_management.js`) - File upload and management
- **FAQ Management** (`faq_management.js`) - FAQ creation and management
- **Website Crawler** (`website.js`) - Website crawling interface
- **Admin Dashboard** (`admin-dashboard.js`) - Admin panel functionality
- **Chat Interface** (`chat_interface.js`) - Chat widget functionality
- **Floating Share Widget** (`floating-share-widget.js`) - Share widget component

### Backend Blueprints

- **Auth Blueprint** (`auth.py`) - User authentication, OTP verification, login/logout
- **API Blueprint** (`api.py`) - RESTful API endpoints for knowledge base, files, config
- **Chat Blueprint** (`chat.py`) - Chat interface and message handling
- **Dashboard Blueprint** (`dashboard.py`) - User dashboard data and views
- **Widget Blueprint** (`widget.py`) - Widget embedding and API
- **Admin Blueprint** (`admin.py`) - Admin dashboard and user management
- **Conversations Blueprint** (`conversations.py`) - Conversation history management

### Service Layer

- **Chatbot Service** (`chatbot_service.py`) - RAG orchestration, LLM integration, response generation
- **Knowledge Service** (`knowledge_service.py`) - ChromaDB vectorstore management, embeddings
- **LLM Service** (`llm_service.py`) - Multi-provider LLM factory (OpenAI, Gemini, Claude, Groq, etc.)
- **File Service** (`file_service.py`) - File upload, text extraction, processing
- **Conversation Service** (`conversation_service.py`) - Conversation context building, history
- **Admin Service** (`admin_service.py`) - Admin operations, user management
- **Config Service** (`config_service.py`) - User chatbot configuration management
- **OTP Service** (`otp_service.py`) - OTP generation and verification
- **User Info Service** (`user_info_service.py`) - User information management

### Model Layer

- **User Model** (`user.py`) - User authentication, RBAC, user data
- **FAQ Model** (`faq.py`) - FAQ entries with user isolation
- **UploadedFile Model** (`uploaded_file.py`) - File uploads with extracted text
- **CrawledUrl Model** (`crawled_url.py`) - Crawled website data
- **Conversation Model** (`conversation.py`) - Conversation sessions
- **Message Model** (`message.py`) - Individual chat messages
- **OTP Model** (`otp.py`) - OTP codes for email verification
- **Chatbot Appearance Model** (`chatbot_appearance.py`) - Widget appearance settings
- **Prompt Preset Model** (`prompt_preset.py`) - Predefined prompt templates
- **API Key Model** (`api_key.py`) - System API key management

---

## Database Schema

![Database Schema](docs/details/database-schema.png)

### Core Tables

**User Management:**
- `users` - User accounts with RBAC (admin, user, viewer roles)
- `otp` - OTP codes for email verification

**Knowledge Base:**
- `faqs` - FAQ entries (user-isolated)
- `uploaded_files` - Uploaded documents with extracted text (user-isolated)
- `crawled_urls` - Crawled website data (user-isolated)

**Conversations:**
- `conversations` - Conversation sessions (user-isolated)
- `messages` - Individual chat messages (conversation-linked)

**Configuration:**
- `chatbot_appearance` - Widget appearance settings (user-specific)
- `prompt_presets` - Predefined prompt templates (system-wide)
- `system_api_keys` - System API keys for LLM providers (encrypted)

---

## Request Flow

![Request Flow](docs/details/request-flow.png)

### Detailed Flow

1. **User Request** → Browser sends HTTPS request to `https://cortex.janisrael.com`
2. **Nginx/Ingress** → SSL termination and routing (if configured)
3. **Kubernetes Service** → ClusterIP service routes to pod
4. **Cortex Pod** → Flask application receives request
5. **Blueprint Routing** → Request routed to appropriate blueprint (auth, api, chat, etc.)
6. **Authentication** → Flask-Login verifies user session
7. **Service Layer** → Business logic executed (RAG, LLM, file processing)
8. **Data Layer** → Database queries, vectorstore searches
9. **Response** → JSON response returned to client
10. **Frontend** → JavaScript updates UI dynamically

---

## RAG Flow

![RAG Flow](docs/details/rag-flow.png)

The RAG (Retrieval Augmented Generation) process retrieves relevant context from the knowledge base before generating responses.

---

## Knowledge Ingestion Flow

![Knowledge Ingestion Flow](docs/details/knowledge-ingestion-flow.png)

Documents, URLs, and FAQs are automatically processed and ingested into the vectorstore for retrieval.

---

## Deployment Flow

![Deployment Flow](docs/details/deployment-flow.png)

CI/CD pipeline automatically builds and deploys to Kubernetes on code push.

---

## User Isolation

![User Isolation](docs/details/user-isolation.png)

Each user has completely isolated data: separate vectorstores, file directories, and configuration files.

---

## LLM Provider Flow

![LLM Provider Flow](docs/details/llm-provider-flow.png)

API key resolution and provider selection logic for multi-LLM support.

---

## Project Structure

![Project Structure](docs/details/project-structure.png)

```
chatbot/
├── app.py                      # Main Flask application entry point
├── auth.py                     # Authentication utilities
├── db_config.py                # Database configuration
├── migrations.py               # Database migration runner
│
├── blueprints/                 # Route blueprints (MVC controllers)
│   ├── __init__.py            # Blueprint registration
│   ├── auth.py                # Authentication routes (login, register, OTP)
│   ├── api.py                 # REST API endpoints (knowledge, files, config)
│   ├── chat.py                # Chat interface routes
│   ├── dashboard.py          # User dashboard routes
│   ├── widget.py              # Widget embedding routes
│   ├── admin.py               # Admin dashboard routes
│   └── conversations.py       # Conversation history routes
│
├── models/                     # Database models (data layer)
│   ├── __init__.py
│   ├── user.py                # User model with RBAC
│   ├── faq.py                 # FAQ model
│   ├── uploaded_file.py       # File upload model
│   ├── crawled_url.py         # Crawled URL model
│   ├── conversation.py        # Conversation model
│   ├── message.py             # Message model
│   ├── otp.py                 # OTP model
│   ├── chatbot_appearance.py  # Appearance settings model
│   ├── prompt_preset.py       # Prompt preset model
│   └── api_key.py             # API key management model
│
├── services/                   # Business logic services
│   ├── __init__.py
│   ├── chatbot_service.py     # RAG orchestration, LLM integration
│   ├── knowledge_service.py   # ChromaDB vectorstore management
│   ├── llm_service.py         # Multi-provider LLM factory
│   ├── file_service.py        # File upload and processing
│   ├── conversation_service.py # Conversation context building
│   ├── admin_service.py       # Admin operations
│   ├── config_service.py      # User configuration management
│   ├── otp_service.py         # OTP generation/verification
│   └── user_info_service.py   # User information management
│
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── email_utils.py         # SMTP email sending
│   ├── helpers.py             # General helper functions
│   ├── prompts.py             # Default prompt templates
│   └── api_key.py             # API key utilities
│
├── templates/                  # HTML templates
│   ├── auth/                  # Authentication pages
│   │   ├── login.html
│   │   ├── register.html
│   │   └── verify_otp.html
│   ├── components/            # Reusable components
│   │   ├── dashboard_*.html  # Dashboard components
│   │   ├── chat_*.html        # Chat components
│   │   └── floating_share_widget.html
│   ├── admin/                 # Admin dashboard
│   │   ├── dashboard.html
│   │   └── components/
│   ├── widget/                # Widget templates
│   │   ├── widget.html
│   │   ├── widget_embed.html
│   │   └── preview.html
│   ├── dashboard.html         # User dashboard
│   ├── index.html             # Landing page
│   └── landing.html           # Public landing
│
├── static/                    # Static assets
│   ├── css/                   # Stylesheets
│   │   ├── auth.css
│   │   ├── dashboard.css
│   │   ├── chat_interface.css
│   │   └── widget_preview.css
│   ├── js/                    # JavaScript files
│   │   ├── chat/              # Chat interface JS
│   │   ├── dashboard/         # Dashboard JS modules
│   │   └── user_info_form.js
│   ├── v2/                    # Version 2 assets
│   │   ├── css/               # V2 stylesheets
│   │   └── js/                # V2 JavaScript modules
│   ├── img/                   # Images
│   │   ├── avatar/            # Bot avatars
│   │   └── providers/         # LLM provider logos
│   └── embed.js               # Widget embed script
│
├── k8s/                       # Kubernetes manifests
│   ├── namespace.yaml         # Cortex namespace
│   ├── deployment.yaml        # Pod deployment config
│   ├── service.yaml           # ClusterIP service
│   ├── pvc.yaml               # Persistent volume claims
│   ├── README.md              # K8s deployment docs
│   └── *.sh                   # Deployment scripts
│
├── migrations/                # Database migrations
│   └── create_otp_table.py   # OTP table migration
│
├── config/                    # Configuration files
│   ├── constants.py           # App constants
│   └── settings.py            # App settings
│
├── .github/                   # CI/CD workflows
│   └── workflows/
│       ├── deploy.yml         # Main deployment workflow
│       └── README.md          # CI/CD documentation
│
├── Dockerfile                 # Multi-stage Docker build
├── requirements-prod.txt     # Production dependencies
├── requirements.txt          # Development dependencies
└── README.md                 # This file
```

---

## Infrastructure Details

### Kubernetes Deployment

**Namespace**: `cortex` (isolated from other projects)

**Deployment Configuration:**
- **Replicas**: 1
- **Strategy**: RollingUpdate (maxSurge: 25%, maxUnavailable: 25%)
- **Image**: `cortex:latest`
- **Port**: 6001 (TCP)
- **Resources**:
  - Requests: CPU 300m, Memory 512Mi
  - Limits: CPU 1, Memory 1Gi

**Persistent Volumes:**
- `cortex-db-pvc` (1Gi) → `/app/data` - SQLite database files
- `cortex-chromadb-pvc` (10Gi) → `/app/chroma_db` - ChromaDB vectorstore
- `cortex-config-pvc` (1Gi) → `/app/config` - User configuration files

**Service:**
- **Type**: ClusterIP
- **Port**: 6001
- **Selector**: `app: cortex`

**Health Checks:**
- **Liveness Probe**: HTTP GET `/health` (delay: 40s, period: 10s)
- **Readiness Probe**: HTTP GET `/health` (delay: 20s, period: 5s)

**Environment Variables:**
- Database: `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- SMTP: From Kubernetes secrets (`cortex-secrets`)
- OpenAI: From Kubernetes secrets (`cortex-secrets`)

### Server Infrastructure

**Production Server**: Hetzner Cloud (178.156.162.135)

**Kubernetes Cluster**: k3s (lightweight Kubernetes)

**Other Projects on Server** (isolated in separate namespaces):
- `default/janisrael-app`
- `gabay/gabay-app`
- `leadfinder/leadfinder-app`
- `prism/prism-app`
- `sandata/sandata-app`

**Database**: MySQL (178.156.162.135:3306)
- Database: `saturn`
- User: `cortex`
- Fallback: SQLite in pod (`/app/data/users.db`)

---

## Features

### Multi-LLM Support
- **OpenAI**: GPT-4o-mini, GPT-4, GPT-3.5-turbo
- **Google Gemini**: gemini-pro, gemini-1.5-pro
- **Anthropic Claude**: claude-3-5-sonnet, claude-3-opus
- **Groq**: Llama 3.3 70B, Mixtral 8x7B
- **DeepSeek**: deepseek-chat
- **Together AI**: Llama 2, Mistral

![LLM Settings](docs/details/llm-settings.png)

### RAG (Retrieval Augmented Generation)
- **Vector Database**: ChromaDB with HuggingFace embeddings
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2
- **Knowledge Sources**: FAQs, uploaded files, crawled websites
- **Priority Ordering**: FAQ > Crawl > File Upload
- **Context Building**: Top 5 relevant documents per query

### Knowledge Base Management
- **File Uploads**: PDF, DOCX, TXT, CSV with automatic text extraction
- **Website Crawling**: Extract clean text from URLs
- **FAQ Management**: Create, edit, delete FAQs with categories
- **Automatic Ingestion**: Documents automatically added to vectorstore
- **User Isolation**: Each user has separate vectorstore

![Knowledge Base](docs/details/knowledge-base.png)

![File Ingestion Preview](docs/details/file-ingestion-preview.png)

### User Features
- **OTP Authentication**: Email-based verification
- **RBAC**: Role-based access control (admin, user, viewer)
- **Customizable Widget**: Theme, avatar, welcome message
- **Conversation History**: Persistent chat history
- **Prompt Customization**: Custom system prompts and presets
- **LLM Selection**: Choose provider and model per user

![Appearance Settings](docs/details/appearance-settings.png)

![Prompt Settings](docs/details/prompt-settings.png)

![Widget Integration](docs/details/widget-integration.png)

### Admin Features
- **User Management**: View, edit, delete users
- **System Monitoring**: LLM status, vectorstore health, database status
- **API Key Management**: System-wide API keys for LLM providers
- **Analytics**: User statistics, knowledge base metrics

---

## Tech Stack

### Backend
- **Framework**: Flask 3.1.1
- **ORM**: Custom models with MySQL connector + SQLite fallback
- **AI/ML**: LangChain, HuggingFace Transformers
- **Vector DB**: ChromaDB
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2

### Frontend
- **JavaScript**: Vanilla JS (component-based architecture)
- **CSS**: Custom stylesheets with Material Symbols icons
- **Widget**: Embeddable chat widget (iframe or script)

### Database
- **Production**: MySQL (external server)
- **Fallback**: SQLite (in-pod)
- **Vectorstore**: ChromaDB (persistent volumes)

### Deployment
- **Container**: Docker (multi-stage build)
- **Orchestration**: Kubernetes (k3s)
- **Cloud**: Hetzner Cloud
- **CI/CD**: GitHub Actions

### External Services
- **LLM APIs**: OpenAI, Google Gemini, Anthropic Claude, Groq, DeepSeek, Together AI
- **Email**: SMTP (Gmail)
- **Storage**: Kubernetes Persistent Volumes

---

## Quick Start

### Prerequisites

- Python 3.11+
- MySQL (or SQLite for development)
- Docker (for containerized deployment)
- Kubernetes cluster (for production)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/janisrael/chatbot.git
   cd chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements-prod.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize database**
   ```bash
   python migrations.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Web Interface: http://localhost:6001
   - Default Admin: `admin@example.com` (password set during init)

### Production Deployment

**Automatic (CI/CD):**
- Push to `main` branch → Auto-deploys to Hetzner Kubernetes

**Manual:**
```bash
# Build Docker image
docker build -t cortex:latest .

# Deploy to Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Verify deployment
kubectl get pods -n cortex
kubectl logs -n cortex -l app=cortex
```

---

## Environment Variables

### Required

- `DB_HOST` - Database host (default: localhost)
- `DB_USER` - Database username (default: root)
- `DB_PASSWORD` - Database password
- `DB_NAME` - Database name (default: saturn)
- `FLASK_SECRET_KEY` - Flask session secret (auto-generated if not set)

### Optional

- `OPENAI_API_KEY` - OpenAI API key (or use system keys in database)
- `SMTP_SERVER` - SMTP server (default: smtp.gmail.com)
- `SMTP_PORT` - SMTP port (default: 587)
- `SMTP_USERNAME` - SMTP username
- `SMTP_PASSWORD` - SMTP password
- `OPENAI_MODEL` - Default OpenAI model (default: gpt-4o-mini)
- `OPENAI_TEMPERATURE` - Default temperature (default: 0.3)

---

## API Documentation

### Authentication

- `POST /register` - User registration with email
- `POST /verify-otp` - Verify OTP code sent to email
- `POST /login` - User login (email + password)
- `POST /logout` - User logout

### Chat

- `POST /api/chat` - Send chat message, get AI response
- `GET /api/chat/history` - Get chat history
- `POST /api/chat/clear` - Clear chat history

### Knowledge Base

- `POST /api/knowledge/upload` - Upload document
- `POST /api/knowledge/crawl` - Crawl website URL
- `GET /api/knowledge/files` - List uploaded files
- `GET /api/knowledge-stats` - Get knowledge base statistics
- `POST /api/files/<id>/ingest` - Ingest file to vectorstore
- `DELETE /api/files/<id>` - Delete file

### User Configuration

- `GET /api/user/chatbot-config` - Get user's chatbot configuration
- `POST /api/user/chatbot-config` - Update chatbot configuration
- `GET /api/prompt` - Get user's custom prompt
- `POST /api/prompt` - Update user's custom prompt
- `GET /api/prompt-presets` - Get available prompt presets
- `GET /api/llm-config` - Get LLM provider configuration

### Admin

- `GET /admin/dashboard` - Admin dashboard (admin role required)
- `GET /admin/users` - List all users
- `POST /admin/users/<id>/role` - Update user role
- `GET /admin/api-keys` - Manage system API keys

---

## Development

### Running Tests

```bash
python test_rbac_otp.py
```

### Database Migrations

```bash
python migrations.py
```

### Code Style

- Follow PEP 8
- Use flake8 for linting
- Run `flake8 .` before committing
- Remove all `console.log()` statements
- Use proper logging instead of `print()`

### Project Structure Guidelines

- **Blueprints**: Route handlers (MVC controllers)
- **Services**: Business logic (reusable across blueprints)
- **Models**: Database models (data layer)
- **Utils**: Helper functions (no business logic)
- **Templates**: HTML templates (component-based)
- **Static**: CSS, JavaScript, images (organized by type)

---

## CI/CD

This project uses GitHub Actions for continuous integration and deployment:

- **Main branch** → Deploys to **Hetzner Kubernetes** (k3s)
- **v2-appearance branch** → Deploys to **AWS EC2** (legacy)

**Deployment Process:**
1. Run tests (linting, syntax checks, import verification)
2. Build Docker image on Hetzner server
3. Import image into k3s
4. Apply Kubernetes manifests
5. Rolling update with health checks
6. Verify deployment success

See [.github/workflows/README.md](.github/workflows/README.md) for detailed CI/CD documentation.

---

## Version History

### Version 2.2 (Current)
- Multi-LLM provider support (OpenAI, Gemini, Claude, Groq, DeepSeek, Together AI)
- System API key management in database
- Data persistence with Kubernetes PVCs
- Enhanced knowledge base accuracy
- UI/UX improvements (dashboard, login, admin)

### Version 2.1
- Initial multi-LLM support
- RBAC implementation
- Admin dashboard

### Version 2.0
- Core platform with RAG
- Knowledge base management
- User isolation

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is proprietary and confidential.

---

## Support

For issues and questions, please contact the development team.

**Live URL**: https://cortex.janisrael.com
