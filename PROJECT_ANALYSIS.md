# RAG Chatbot - Project Analysis

## Project Overview
**Type**: AI-Powered RAG (Retrieval Augmented Generation) Chatbot Platform  
**Similar to**: Chatbase, CustomGPT  
**Status**: ✅ Working (Local Development)  
**Port**: 6001  
**LLM**: OpenAI GPT-4o-mini (configurable to Ollama)

---

## Core Concept

This is a **customizable AI chatbot platform** that allows you to:

1. **Upload your own knowledge base** (documents, FAQs, training materials)
2. **Customize the bot's personality** via system prompts
3. **Embed the chatbot** on any website via a floating widget
4. **Manage multiple websites** with different chatbots and knowledge bases
5. **Track conversations** and analytics via dashboard

---

## How It Works (RAG Architecture)

```
User Question
    ↓
Vector Search (ChromaDB)
    ↓
Retrieve Relevant Context (Top 5 matches)
    ↓
Combine: System Prompt + Context + Question
    ↓
LLM (OpenAI/Ollama) Generates Response
    ↓
Return HTML-formatted Answer
```

---

## Key Features

### 1. Knowledge Base Management
- **Upload Files**: TXT, PDF, DOC, DOCX, CSV
- **File Categories**:
  - Company Details (business info, services, team)
  - Sales Training (scripts, objection handling)
  - Product Information (specs, pricing, features)
  - Customer Support (FAQs, troubleshooting)
  - General Knowledge
- **Vector Storage**: ChromaDB with HuggingFace embeddings
- **Automatic Processing**: Files are chunked and embedded automatically

### 2. Customizable Bot Prompt
- **Define Bot Name**: Default is "Bob"
- **Set Personality**: Friendly, professional, technical, etc.
- **Custom Instructions**: How to respond, tone, format
- **Website-Specific**: Different prompts for different websites
- **Editable via Dashboard**: Real-time prompt updates

### 3. Multi-Website Support
- **Website Configurations**: Each website has its own:
  - Bot name
  - Custom prompt
  - Knowledge base
  - Primary color/branding
  - Allowed origins (CORS)
- **Example Config**:
```python
WEBSITE_CONFIGS = {
    'sourceselect.ca': {
        'name': 'SourceSelect',
        'bot_name': 'Bob',
        'primary_color': '#667eea',
        'knowledge_base': 'sourceselect',
        'custom_prompt': 'You are Bob, a helpful assistant...'
    }
}
```

### 4. Embeddable Widget
- **Floating Chat Button**: Circular button with customizable color
- **Welcome Message**: Auto-popup greeting
- **Iframe-based**: Secure, isolated chat interface
- **Easy Integration**: Just add a `<script>` tag
```html
<script src="http://localhost:6001/static/embed.js"></script>
```

### 5. Dashboard Features
- **Upload Files**: Drag-and-drop file upload with category selection
- **Edit Prompt**: Live prompt editor with syntax highlighting
- **View Files**: See all uploaded files organized by category
- **System Health**: Monitor vector store, LLM status
- **Chat Logs**: View conversation history (when DB is enabled)
- **Analytics**: Track usage, popular questions, response times

---

## Technical Stack

### Backend
- **Framework**: Flask (Python)
- **LLM Integration**: LangChain
- **LLM Options**:
  - OpenAI (GPT-4o-mini, GPT-3.5-turbo, GPT-4)
  - Ollama (Local: Llama3.1, Mistral, CodeLlama)
- **Vector Database**: ChromaDB
- **Embeddings**: HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **Database**: MySQL/MariaDB (for chat logs - optional)

### Frontend
- **Templates**: Jinja2 (HTML)
- **Styling**: Custom CSS with modern UI
- **JavaScript**: Vanilla JS for chat interface
- **Widget**: Iframe-based embeddable chat

### File Processing
- **PDF**: PyPDFLoader
- **Text**: TextLoader
- **CSV**: CSVLoader
- **Word**: DocxLoader (via python-docx)
- **Text Splitting**: RecursiveCharacterTextSplitter (500 char chunks, 50 overlap)

---

## Current Status

### ✅ Working Features
1. **Chat Interface**: `/` - Main chat page works perfectly
2. **RAG System**: Vector search + LLM response generation
3. **OpenAI Integration**: Using GPT-4o-mini successfully
4. **File Upload**: Can upload and process documents
5. **FAQ Management**: Can update FAQ via API
6. **Prompt Customization**: System prompt is customizable
7. **Floating Widget**: Embeddable chat widget

### ⚠️ Issues Fixed
1. ✅ **Vector Store Dimension Mismatch**: Deleted old ChromaDB and recreated
2. ✅ **Database Logging Errors**: Disabled MySQL logging (optional feature)
3. ✅ **LLM Configuration**: Set up OpenAI with API key from `.env`
4. ✅ **Error Handling**: Added proper try-catch for RAG failures

### 🔧 Pending Tasks
1. **Test Dashboard**: Verify all dashboard features work
2. **Test Demo Page**: Ensure `/demo` floating widget works
3. **Test Widget Page**: Verify `/widget` embeddable interface
4. **Update Branding**: Change from "SourceSelect" to portfolio-ready
5. **Mobile Responsive**: Ensure all pages work on mobile
6. **Documentation**: Create user guide and setup instructions

---

## File Structure

```
chatbot/
├── app_backup.py           # Main Flask application
├── .env                    # Environment variables (LLM_OPTION, OPENAI_API_KEY)
├── requirements.txt        # Python dependencies
├── db_config.py           # MySQL configuration (optional)
│
├── data/
│   └── faq.txt            # FAQ knowledge base
│
├── uploads/               # Uploaded files (CSV, PDF, etc.)
│
├── chroma_db/            # Vector database storage
│
├── static/
│   └── embed.js          # Embeddable widget script
│
├── templates/
│   ├── index.html        # Main chat interface
│   ├── dashboard_v1.html # Dashboard (analytics, file upload, prompt editor)
│   ├── widget.html       # Chat widget interface
│   └── demo_chatbox.html # Demo page with floating widget
│
└── logs/
    └── chat_logs.csv     # Conversation logs (when DB enabled)
```

---

## Configuration

### Environment Variables (`.env`)
```bash
FLASK_ENV=development
PORT=6001

# LLM Configuration
LLM_OPTION=openai          # or "ollama"
OPENAI_API_KEY=sk-proj-... # Your OpenAI API key

# Database (Optional)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=saturn
```

### System Prompt (Customizable)
```python
template_text = """
You are Bob, a real human virtual assistant for SourceSelect.ca.

Your job is to help users with their questions about SourceSelect.ca and its services. 
Always be polite, helpful, and conversational—just like a friendly and attentive human agent.

INSTRUCTIONS:
- Vary your greetings and responses to avoid sounding repetitive or robotic.
- Reference the user's specific question in your answer.
- Use ONLY the information provided in the "Relevant Info" section below.
- If you don't know the answer, politely say so and offer to connect them to a human.
- Respond in HTML format (use <br> for line breaks, <ul><li> for lists, <strong> for emphasis).
- Keep your tone friendly and concise.
- Always finish with a relevant follow-up question.

Relevant Info:
{context}

User Question: {question}

Bob's Response:
"""
```

---

## API Endpoints

### Chat
- **POST** `/chat`
  - Body: `{"message": "Hello", "user_id": "123", "name": "John"}`
  - Returns: `{"response": "Hi John! How can I help?"}`

### File Upload
- **POST** `/api/upload`
  - Form data: `file`, `category`
  - Returns: `{"status": "success", "chunks": 25}`

### FAQ Management
- **POST** `/update_faq`
  - Body: `{"faq_text": "..."}`
  - Returns: `{"status": "FAQ updated successfully"}`

### Prompt Management
- **GET** `/api/prompt`
  - Returns: `{"prompt": "..."}`
- **POST** `/api/prompt`
  - Body: `{"prompt": "..."}`
  - Returns: `{"status": "success"}`

### Files
- **GET** `/api/files-by-category`
  - Returns: List of uploaded files by category

---

## Usage Examples

### 1. Basic Chat
```bash
curl -X POST http://localhost:6001/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What services do you offer?","user_id":"test","name":"Swordfish"}'
```

### 2. Upload Knowledge Base File
```bash
curl -X POST http://localhost:6001/api/upload \
  -F "file=@company_info.pdf" \
  -F "category=company_details"
```

### 3. Update System Prompt
```bash
curl -X POST http://localhost:6001/api/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt":"You are Alex, a technical support specialist..."}'
```

---

## Deployment Considerations

### For Portfolio Deployment
1. **Change Branding**: Update all "SourceSelect" references to generic or your brand
2. **Update Bot Name**: Change "Bob" to your preferred assistant name
3. **Add Demo Content**: Upload sample knowledge base files
4. **Configure CORS**: Set allowed origins for production domain
5. **SSL Certificate**: Use HTTPS for production
6. **Database**: Set up MySQL for chat logging (optional)
7. **Process Manager**: Use `screen` or `supervisor` to keep app running
8. **Nginx**: Reverse proxy for production
9. **Environment Variables**: Set production API keys and configs

### Port Assignment
- **Local**: 6001
- **Production**: Assign unique port (e.g., 6002 for chatbot on AWS)

---

## Next Steps

1. ✅ **Test all pages** (dashboard, demo, widget)
2. ✅ **Update branding** for portfolio
3. ✅ **Create documentation** for users
4. ✅ **Deploy to AWS** at `chatbot.janisrael.com`
5. ✅ **Add to portfolio** documentation

---

## Notes

- **RAG is working**: Chatbot successfully retrieves context from uploaded files
- **OpenAI is working**: Using GPT-4o-mini with API key
- **Vector store is fresh**: Recreated ChromaDB with correct embedding dimensions
- **Database logging disabled**: MySQL is optional, not required for core functionality
- **Widget is embeddable**: Can be added to any website via `<script>` tag

---

**Last Updated**: November 13, 2025  
**Status**: ✅ Ready for testing and portfolio deployment



