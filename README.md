# Cortex AI - Intelligent Chatbot Platform

A full-stack AI-powered chatbot platform with RAG (Retrieval Augmented Generation), multi-LLM support, knowledge base management, and comprehensive admin dashboard.

## Features

- **Multi-LLM Support**: OpenAI GPT-4o-mini, Mistral-7B, CodeLlama-7B, Phi-3-mini
- **RAG (Retrieval Augmented Generation)**: Vector-based knowledge retrieval using ChromaDB
- **Knowledge Base Management**: Upload documents, crawl websites, manage FAQs
- **User Authentication**: OTP-based email verification, RBAC (Role-Based Access Control)
- **Admin Dashboard**: User management, analytics, system monitoring
- **Customizable Appearance**: Theme customization, widget embedding
- **API Integration**: RESTful API with API key authentication

## Tech Stack

- **Backend**: Python Flask, SQLAlchemy
- **Frontend**: Vue.js, JavaScript, HTML/CSS
- **Database**: MySQL (production), SQLite (fallback)
- **Vector DB**: ChromaDB
- **AI/ML**: LangChain, HuggingFace Transformers
- **Deployment**: Docker, Kubernetes (k3s), Hetzner Cloud

## Quick Start

### Prerequisites

- Python 3.11+
- MySQL (or SQLite for development)
- Docker (for containerized deployment)

### Installation

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
   python migrations/create_otp_table.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

## Environment Variables

See `.env.example` for required environment variables:

- `OPENAI_API_KEY`: OpenAI API key for GPT models
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`: Database configuration
- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`: Email configuration
- `FLASK_SECRET_KEY`: Flask session secret key

## Deployment

### Kubernetes (Hetzner)

The main branch automatically deploys to Hetzner Kubernetes via GitHub Actions.

**Manual deployment:**
```bash
# Build Docker image
docker build -t cortex:latest .

# Deploy to Kubernetes
kubectl apply -f k8s/
kubectl rollout restart deployment/cortex-app -n cortex
```

### AWS EC2 (Legacy)

The v2-appearance branch deploys to AWS EC2 via GitHub Actions.

See [.github/workflows/README.md](.github/workflows/README.md) for detailed deployment documentation.

## Project Structure

```
chatbot/
├── app.py                 # Main Flask application
├── blueprints/           # Route blueprints (auth, api, chat, dashboard, admin)
├── models/               # Database models (user, otp, chatbot_appearance, etc.)
├── services/             # Business logic services
├── utils/                # Helper functions (email, API keys, prompts)
├── templates/            # HTML templates
├── static/               # CSS, JavaScript, images
├── migrations/           # Database migration scripts
├── k8s/                  # Kubernetes manifests
└── .github/workflows/    # CI/CD workflows
```

## API Documentation

### Authentication
- `POST /register` - User registration with OTP
- `POST /verify-otp` - Verify OTP code
- `POST /login` - User login
- `POST /logout` - User logout

### Chat
- `POST /api/chat` - Send chat message
- `GET /api/chat/history` - Get chat history
- `POST /api/chat/clear` - Clear chat history

### Knowledge Base
- `POST /api/knowledge/upload` - Upload document
- `POST /api/knowledge/crawl` - Crawl website
- `GET /api/knowledge/files` - List uploaded files
- `DELETE /api/knowledge/files/<id>` - Delete file

### Admin
- `GET /admin/dashboard` - Admin dashboard (admin role required)
- `GET /admin/users` - List all users
- `POST /admin/users/<id>/role` - Update user role

## Development

### Running Tests
```bash
python test_rbac_otp.py
```

### Database Migrations
```bash
python migrations/create_otp_table.py
```

### Code Style
- Follow PEP 8
- Use flake8 for linting
- Run `flake8 .` before committing

## CI/CD

This project uses GitHub Actions for continuous integration and deployment:

- **Main branch** → Deploys to **Hetzner Kubernetes** (k3s)
- **v2-appearance branch** → Deploys to **AWS EC2** (legacy)

See [.github/workflows/README.md](.github/workflows/README.md) for detailed CI/CD documentation.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary and confidential.

## Support

For issues and questions, please contact the development team.

---

**Live URL**: https://cortex.janisrael.com

# Trigger CI/CD to rebuild Cortex image
# Trigger Cortex rebuild
# Add admin credentials to login page
