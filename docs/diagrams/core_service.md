# Core Service - Detailed Architecture Diagram

## Overview
The Core Service is the main chatbot service handling conversations, user profiles, and widget serving.

```mermaid
graph TB
    subgraph "Core Service Architecture"
        subgraph "API Layer"
            ChatAPI[POST /api/chat<br/>Chat Endpoint]
            ConversationsAPI[GET/POST /api/conversations<br/>Conversation Management]
            UserProfilesAPI[GET/PUT /api/user-profiles<br/>Profile Management]
            WidgetAPI[GET /widget<br/>Widget Serving]
        end
        
        subgraph "Service Layer"
            ChatbotService[Chatbot Service<br/>Response Generation]
            ConversationService[Conversation Service<br/>History Management]
            UserInfoService[User Info Service<br/>Profile Operations]
            LLMService[LLM Service<br/>AI Integration]
        end
        
        subgraph "Database - Core Schema"
            Users[(USERS<br/>id PK<br/>email UK<br/>username<br/>password_hash<br/>role<br/>created_at)]
            UserProfiles[(USER_PROFILES<br/>id PK<br/>user_id FK<br/>email UK<br/>name<br/>phone<br/>email_subscribed<br/>created_at)]
            Conversations[(CONVERSATIONS<br/>id PK<br/>user_id FK<br/>user_profile_id FK<br/>session_id<br/>title<br/>message_count<br/>metadata JSON<br/>is_active<br/>created_at<br/>updated_at)]
            Messages[(MESSAGES<br/>id PK<br/>conversation_id FK<br/>role<br/>content TEXT<br/>metadata JSON<br/>created_at)]
            ChatbotAppearance[(CHATBOT_APPEARANCE<br/>id PK<br/>user_id FK<br/>bot_name<br/>welcome_message<br/>avatar JSON<br/>primary_color JSON<br/>created_at<br/>updated_at)]
            AdminAPIKeys[(ADMIN_API_KEYS<br/>id PK<br/>user_id FK<br/>name<br/>key_hash<br/>type<br/>active<br/>created_at)]
        end
        
        subgraph "External Services"
            KnowledgeService[Knowledge Service<br/>RAG Queries]
            HelperAgent[Helper Agent Service<br/>Guidance]
            AnalyticsService[Analytics Service<br/>Event Logging]
            RedisCache[(Redis Cache<br/>Session Cache<br/>Rate Limiting)]
            RabbitMQ[(RabbitMQ<br/>Async Tasks)]
        end
    end
    
    subgraph "Data Flow - Chat Request"
        User[User] --> WidgetAPI
        WidgetAPI --> ChatAPI
        ChatAPI --> ChatbotService
        
        ChatbotService --> ConversationService
        ConversationService --> Conversations
        ConversationService --> Messages
        ConversationService --> UserProfiles
        
        ChatbotService --> KnowledgeService
        KnowledgeService -->|Context| ChatbotService
        
        ChatbotService --> HelperAgent
        HelperAgent -->|Guidance| ChatbotService
        
        ChatbotService --> LLMService
        LLMService -->|AI Response| ChatbotService
        
        ChatbotService --> AnalyticsService
        ChatbotService --> RabbitMQ
        
        ChatbotService --> RedisCache
        ChatbotService -->|Response| ChatAPI
        ChatAPI -->|JSON| User
    end
    
    subgraph "Data Flow - User Profile"
        User --> UserProfilesAPI
        UserProfilesAPI --> UserInfoService
        UserInfoService --> UserProfiles
        UserInfoService --> Conversations
        UserInfoService -->|Update Metadata| Conversations
    end
    
    subgraph "Data Flow - Conversation Management"
        User --> ConversationsAPI
        ConversationsAPI --> ConversationService
        ConversationService --> Conversations
        ConversationService --> Messages
        ConversationService -->|Build Context| ChatbotService
    end
    
    Users -->|has| UserProfiles
    Users -->|creates| Conversations
    UserProfiles -->|configures| ChatbotAppearance
    UserProfiles -->|owns| AdminAPIKeys
    Conversations -->|contains| Messages
    
    style ChatAPI fill:#50c878
    style ChatbotService fill:#50c878
    style Conversations fill:#3498db
    style Messages fill:#3498db
    style UserProfiles fill:#3498db
    style KnowledgeService fill:#ffa500
    style HelperAgent fill:#1abc9c
    style RedisCache fill:#e74c3c
```

## Database Schema Details

### USERS Table
- **Primary Key**: `id` (int)
- **Unique Key**: `email` (string)
- **Fields**: username, password_hash, role, created_at
- **Relationships**: One-to-many with USER_PROFILES, CONVERSATIONS

### USER_PROFILES Table
- **Primary Key**: `id` (int)
- **Foreign Key**: `user_id` → USERS.id
- **Unique Key**: `email` (string)
- **Fields**: name, phone, email_subscribed, created_at
- **Relationships**: One-to-many with CONVERSATIONS, CHATBOT_APPEARANCE

### CONVERSATIONS Table
- **Primary Key**: `id` (int)
- **Foreign Keys**: `user_id` → USERS.id, `user_profile_id` → USER_PROFILES.id
- **Fields**: session_id, title, message_count, metadata (JSON), is_active, created_at, updated_at
- **Relationships**: One-to-many with MESSAGES

### MESSAGES Table
- **Primary Key**: `id` (int)
- **Foreign Key**: `conversation_id` → CONVERSATIONS.id
- **Fields**: role (user/bot), content (TEXT), metadata (JSON), created_at
- **Indexes**: conversation_id, created_at

### CHATBOT_APPEARANCE Table
- **Primary Key**: `id` (int)
- **Foreign Key**: `user_id` → USERS.id
- **Fields**: bot_name, welcome_message, avatar (JSON), primary_color (JSON), created_at, updated_at

### ADMIN_API_KEYS Table
- **Primary Key**: `id` (int)
- **Foreign Key**: `user_id` → USERS.id
- **Fields**: name, key_hash, type, active, created_at

## Service Responsibilities

### Chatbot Service
- Generate chatbot responses using LLM
- Integrate RAG context from Knowledge Service
- Receive guidance from Helper Agent
- Format responses with markdown/HTML

### Conversation Service
- Create and manage conversations
- Store and retrieve message history
- Build conversation context for LLM
- Handle session management

### User Info Service
- Manage user profiles
- Store user information (name, email, phone)
- Link profiles to conversations
- Handle user metadata

## API Endpoints

### POST /api/chat
- **Input**: `message`, `conversation_id`, `session_id`, `api_key`
- **Output**: `response`, `conversation_id`, `is_new_conversation`
- **Flow**: Validate → Get Context → Generate Response → Store Message

### GET /api/conversations
- **Input**: `user_id` (from session)
- **Output**: List of conversations
- **Flow**: Query → Format → Return

### POST /api/conversations
- **Input**: `user_id`, `session_id`
- **Output**: `conversation_id`
- **Flow**: Create → Return ID

### GET /api/user-profiles
- **Input**: `user_id` (from session)
- **Output**: User profile data
- **Flow**: Query → Return

### PUT /api/user-profiles
- **Input**: `user_id`, `name`, `email`, `phone`
- **Output**: Updated profile
- **Flow**: Validate → Update → Return

### GET /widget
- **Input**: `api_key` (query param)
- **Output**: Widget HTML with configuration
- **Flow**: Validate API Key → Get Config → Render Widget

## Integration Points

### Knowledge Service
- **Purpose**: Retrieve relevant context for RAG
- **Method**: REST API call
- **Data**: Query → Context documents

### Helper Agent Service
- **Purpose**: Get conversation guidance
- **Method**: REST API call (async)
- **Data**: Conversation state → Guidance suggestions

### Analytics Service
- **Purpose**: Log conversation events
- **Method**: RabbitMQ message
- **Data**: Conversation events, metrics

### Redis Cache
- **Purpose**: Session cache, rate limiting
- **Data**: Session data, API key validation cache

### RabbitMQ
- **Purpose**: Async task processing
- **Data**: Analytics events, background tasks

