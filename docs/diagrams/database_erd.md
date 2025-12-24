# Cortex Database ERD (Entity Relationship Diagram)

This diagram shows the current database schema with all tables, fields, and relationships.

## dbdiagram.io Format

Use this code in [dbdiagram.io](https://dbdiagram.io) to visualize the database schema:

```dbml
// Cortex Database Schema
// Copy this code to https://dbdiagram.io to visualize

Table users {
  id int [pk, increment]
  email varchar(255) [unique, not null]
  username varchar(100) [unique, not null]
  password_hash varchar(255) [not null]
  role enum('admin', 'user', 'viewer') [default: 'user']
  created_at datetime [default: `CURRENT_TIMESTAMP`]
  last_login datetime
  
  Note: 'User authentication and RBAC'
}

Table conversations {
  id int [pk, increment]
  user_id int [ref: > users.id, note: 'CASCADE DELETE']
  session_id varchar(255) [not null]
  title varchar(500)
  created_at datetime [default: `CURRENT_TIMESTAMP`]
  updated_at datetime [default: `CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`]
  message_count int [default: 0]
  is_active boolean [default: true]
  metadata text [note: 'JSON']
  
  indexes {
    user_id
    session_id
    created_at
  }
  
  Note: 'Chat session management'
}

Table messages {
  id int [pk, increment]
  conversation_id int [ref: > conversations.id, note: 'CASCADE DELETE']
  role varchar(20) [not null, note: 'user or assistant']
  content text [not null]
  created_at datetime [default: `CURRENT_TIMESTAMP`]
  metadata text [note: 'JSON']
  
  indexes {
    conversation_id
    created_at
    role
  }
  
  Note: 'Individual chat messages'
}

Table chatbot_appearance {
  id int [pk, increment]
  user_id int [ref: > users.id, unique, note: 'CASCADE DELETE, One-to-One']
  short_info varchar(200)
  primary_color text [note: 'JSON']
  avatar_type enum('preset', 'upload', 'generated') [default: 'preset']
  avatar_value varchar(255)
  suggested_messages text [note: 'JSON']
  welcome_message text
  created_at datetime [default: `CURRENT_TIMESTAMP`]
  updated_at datetime [default: `CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`]
  
  indexes {
    user_id
  }
  
  Note: 'User-specific chatbot appearance settings'
}

Table uploaded_files {
  id int [pk, increment]
  user_id int [ref: > users.id, note: 'CASCADE DELETE']
  filename varchar(255) [not null]
  filepath varchar(500) [not null]
  category varchar(50) [default: 'company_details']
  extracted_text text
  word_count int [default: 0]
  char_count int [default: 0]
  status enum('preview', 'ingested', 'deleted') [default: 'preview']
  uploaded_at datetime [default: `CURRENT_TIMESTAMP`]
  ingested_at datetime
  created_at datetime [default: `CURRENT_TIMESTAMP`]
  updated_at datetime [default: `CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`]
  
  indexes {
    user_id
    status
    filename
  }
  
  Note: 'User-isolated file uploads with soft delete'
}

Table faqs {
  id int [pk, increment]
  user_id int [ref: > users.id, note: 'CASCADE DELETE']
  question text [not null]
  answer text [not null]
  category varchar(50) [default: 'company_details']
  status enum('draft', 'active', 'deleted') [default: 'draft']
  ingested_at datetime
  created_at datetime [default: `CURRENT_TIMESTAMP`]
  updated_at datetime [default: `CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`]
  
  indexes {
    user_id
    status
  }
  
  Note: 'User-isolated FAQ entries with soft delete'
}

Table crawled_urls {
  id int [pk, increment]
  user_id int [ref: > users.id, note: 'CASCADE DELETE']
  url varchar(500) [not null]
  title varchar(255)
  extracted_text text
  word_count int [default: 0]
  char_count int [default: 0]
  status enum('preview', 'ingested', 'deleted') [default: 'preview']
  category varchar(50) [default: 'company_details']
  crawled_at datetime [default: `CURRENT_TIMESTAMP`]
  ingested_at datetime
  created_at datetime [default: `CURRENT_TIMESTAMP`]
  updated_at datetime [default: `CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`]
  
  indexes {
    user_id
    status
    url
  }
  
  Note: 'User-isolated web crawl data with soft delete'
}

Table admin_api_keys {
  id int [pk, increment]
  name varchar(255) [not null]
  key_hash varchar(255) [unique, not null]
  key_type enum('default', 'fallback', 'custom') [default: 'custom']
  is_active boolean [default: true]
  created_at datetime [default: `CURRENT_TIMESTAMP`]
  updated_at datetime [default: `CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`]
  created_by int [ref: > users.id, note: 'Optional FK']
  
  indexes {
    key_hash
    key_type
    is_active
  }
  
  Note: 'Widget access API keys (hashed for security)'
}

Table system_api_keys {
  id int [pk, increment]
  key_type varchar(50) [not null]
  provider varchar(50) [not null, note: 'openai, gemini, groq']
  key_value text [not null, note: 'encrypted']
  created_at datetime [default: `CURRENT_TIMESTAMP`]
  updated_at datetime [default: `CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`]
  
  indexes {
    provider
    (key_type, provider) [unique]
  }
  
  Note: 'System default LLM provider API keys'
}

Table prompt_presets {
  id int [pk, increment]
  name varchar(100) [not null]
  icon varchar(50) [not null]
  description text [not null]
  prompt text [not null]
  created_at datetime [default: `CURRENT_TIMESTAMP`]
  updated_at datetime [default: `CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`]
  
  Note: 'Global prompt templates (shared across all users)'
}

Table otp_verifications {
  id int [pk, increment]
  user_id int [ref: > users.id, note: 'Optional FK']
  email varchar(255) [not null]
  otp_code varchar(6) [not null]
  purpose varchar(50) [not null, note: 'registration, forgot_password']
  expires_at datetime [not null]
  verified boolean [default: false]
  attempts int [default: 0]
  created_at datetime [default: `CURRENT_TIMESTAMP`]
  verified_at datetime
  
  Note: 'Email verification OTP codes with expiration tracking'
}
```

## Relationships Summary

### One-to-Many Relationships
- `users` → `conversations` (CASCADE DELETE)
- `users` → `uploaded_files` (CASCADE DELETE)
- `users` → `faqs` (CASCADE DELETE)
- `users` → `crawled_urls` (CASCADE DELETE)
- `users` → `otp_verifications` (Optional FK)
- `users` → `admin_api_keys` (Optional FK via `created_by`)
- `conversations` → `messages` (CASCADE DELETE)

### One-to-One Relationships
- `users` → `chatbot_appearance` (UNIQUE constraint, CASCADE DELETE)

### No User Relationship
- `system_api_keys` (System-wide defaults)
- `prompt_presets` (Global templates)

## Key Features

### Data Isolation
All user-specific data is isolated by `user_id`:
- ✅ Conversations and messages
- ✅ Uploaded files
- ✅ FAQs
- ✅ Crawled URLs
- ✅ Chatbot appearance settings

### Soft Deletes
The following tables use status-based soft deletes:
- `uploaded_files.status` → `'deleted'`
- `faqs.status` → `'deleted'`
- `crawled_urls.status` → `'deleted'`

### Cascade Deletes
All user-related tables use `ON DELETE CASCADE`:
- Deleting a user automatically deletes:
  - All conversations and messages
  - All uploaded files
  - All FAQs
  - All crawled URLs
  - Chatbot appearance config

### JSON Metadata Fields
- `conversations.metadata` - Stores conversation metadata (user info, etc.)
- `messages.metadata` - Stores message metadata
- `chatbot_appearance.primary_color` - Stores color configuration as JSON
- `chatbot_appearance.suggested_messages` - Stores suggested messages array as JSON

### Security
- `admin_api_keys.key_hash` - API keys are hashed (SHA-256) before storage
- `system_api_keys.key_value` - System API keys are base64 encoded (consider upgrading to proper encryption)

### Database Support
- **Production:** MySQL (InnoDB engine)
- **Development/Fallback:** SQLite
- All models support both database types with automatic fallback

## Usage

1. Copy the code block above (between the ```dbml markers)
2. Go to [https://dbdiagram.io](https://dbdiagram.io)
3. Paste the code into the editor
4. Click "Generate" to visualize the ERD

## Table Count

- **Total Tables:** 11
- **User-related Tables:** 8 (with `user_id` FK)
- **Global Tables:** 2 (`system_api_keys`, `prompt_presets`)
- **Authentication Tables:** 1 (`otp_verifications`)
