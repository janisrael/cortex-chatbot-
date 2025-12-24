# Auth Service - Detailed Architecture Diagram

## Overview
The Auth Service handles authentication, authorization, session management, and OAuth integration.

```mermaid
graph TB
    subgraph "Auth Service Architecture"
        subgraph "API Layer"
            LoginAPI[POST /api/auth/login<br/>User Login]
            RegisterAPI[POST /api/auth/register<br/>User Registration]
            RefreshAPI[POST /api/auth/refresh<br/>Token Refresh]
            LogoutAPI[POST /api/auth/logout<br/>User Logout]
            VerifyAPI[GET /api/auth/verify<br/>Token Verification]
            OAuthAPI[GET /api/auth/oauth/:provider<br/>OAuth Flow]
        end
        
        subgraph "Service Layer"
            AuthService[Auth Service<br/>Authentication Logic]
            TokenService[Token Service<br/>JWT Management]
            SessionService[Session Service<br/>Session Management]
            OAuthService[OAuth Service<br/>OAuth Providers]
            PasswordService[Password Service<br/>Hash & Verify]
        end
        
        subgraph "Database - Auth Schema"
            Users[(USERS<br/>id PK<br/>email UK<br/>username<br/>password_hash<br/>role<br/>created_at<br/>last_login)]
            Sessions[(SESSIONS<br/>id PK<br/>user_id FK<br/>session_token<br/>refresh_token<br/>expires_at<br/>ip_address<br/>user_agent<br/>created_at)]
            Tokens[(TOKENS<br/>id PK<br/>user_id FK<br/>token_type<br/>access_token<br/>refresh_token<br/>expires_at<br/>created_at)]
            OAuthProviders[(OAUTH_PROVIDERS<br/>id PK<br/>user_id FK<br/>provider<br/>provider_user_id<br/>access_token<br/>refresh_token<br/>expires_at<br/>created_at)]
            PasswordResets[(PASSWORD_RESETS<br/>id PK<br/>user_id FK<br/>reset_token<br/>expires_at<br/>used<br/>created_at)]
        end
        
        subgraph "External Services"
            RedisCache[(Redis Cache<br/>Session Storage<br/>Token Blacklist)]
            CoreService[Core Service<br/>User Creation Events]
            RabbitMQ[(RabbitMQ<br/>Auth Events)]
        end
    end
    
    subgraph "Data Flow - Login"
        User[User] --> LoginAPI
        LoginAPI --> AuthService
        AuthService --> PasswordService
        PasswordService --> Users
        Users -->|Verify Password| AuthService
        
        AuthService --> TokenService
        TokenService -->|Generate JWT| Tokens
        TokenService -->|Generate Refresh| Tokens
        
        AuthService --> SessionService
        SessionService --> Sessions
        SessionService --> RedisCache
        
        AuthService --> RabbitMQ
        RabbitMQ -->|user.logged_in| CoreService
        
        AuthService -->|Tokens| LoginAPI
        LoginAPI -->|JSON Response| User
    end
    
    subgraph "Data Flow - Registration"
        User --> RegisterAPI
        RegisterAPI --> AuthService
        AuthService --> PasswordService
        PasswordService -->|Hash Password| Users
        Users -->|Create User| AuthService
        
        AuthService --> TokenService
        TokenService --> Tokens
        
        AuthService --> RabbitMQ
        RabbitMQ -->|user.created| CoreService
        
        AuthService -->|User + Tokens| RegisterAPI
        RegisterAPI -->|JSON Response| User
    end
    
    subgraph "Data Flow - OAuth"
        User --> OAuthAPI
        OAuthAPI --> OAuthService
        OAuthService -->|Redirect| Google[Google OAuth]
        Google -->|Callback| OAuthAPI
        OAuthAPI --> OAuthService
        OAuthService --> OAuthProviders
        OAuthService --> Users
        OAuthService --> TokenService
        TokenService --> Tokens
        OAuthService -->|Tokens| OAuthAPI
        OAuthAPI -->|JSON Response| User
    end
    
    subgraph "Data Flow - Token Refresh"
        User --> RefreshAPI
        RefreshAPI --> TokenService
        TokenService --> Tokens
        Tokens -->|Validate Refresh Token| TokenService
        TokenService -->|Generate New Access| Tokens
        TokenService -->|Response| RefreshAPI
        RefreshAPI -->|New Tokens| User
    end
    
    Users -->|has| Sessions
    Users -->|has| Tokens
    Users -->|has| OAuthProviders
    Users -->|has| PasswordResets
    
    style LoginAPI fill:#ff6b6b
    style AuthService fill:#ff6b6b
    style Sessions fill:#3498db
    style Tokens fill:#3498db
    style RedisCache fill:#e74c3c
    style OAuthService fill:#3498db
```

## Database Schema Details

### USERS Table
- **Primary Key**: `id` (int)
- **Unique Key**: `email` (string)
- **Fields**: username, password_hash, role, created_at, last_login
- **Indexes**: email (unique), username

### SESSIONS Table
- **Primary Key**: `id` (int)
- **Foreign Key**: `user_id` → USERS.id
- **Fields**: session_token, refresh_token, expires_at, ip_address, user_agent, created_at
- **Indexes**: session_token (unique), user_id, expires_at
- **TTL**: Auto-delete expired sessions

### TOKENS Table
- **Primary Key**: `id` (int)
- **Foreign Key**: `user_id` → USERS.id
- **Fields**: token_type, access_token, refresh_token, expires_at, created_at
- **Indexes**: access_token (unique), refresh_token (unique), user_id, expires_at
- **TTL**: Auto-delete expired tokens

### OAUTH_PROVIDERS Table
- **Primary Key**: `id` (int)
- **Foreign Key**: `user_id` → USERS.id
- **Fields**: provider, provider_user_id, access_token, refresh_token, expires_at, created_at
- **Indexes**: provider + provider_user_id (unique), user_id
- **Supported Providers**: Google, GitHub, Microsoft

### PASSWORD_RESETS Table
- **Primary Key**: `id` (int)
- **Foreign Key**: `user_id` → USERS.id
- **Fields**: reset_token, expires_at, used, created_at
- **Indexes**: reset_token (unique), user_id, expires_at
- **TTL**: Auto-delete expired/used tokens

## Service Responsibilities

### Auth Service
- Validate user credentials
- Manage authentication flow
- Coordinate with other services
- Handle authorization checks

### Token Service
- Generate JWT access tokens
- Generate refresh tokens
- Validate token signatures
- Manage token expiration
- Blacklist revoked tokens

### Session Service
- Create and manage user sessions
- Store session data in Redis
- Validate session tokens
- Handle session expiration

### OAuth Service
- Handle OAuth provider integration
- Manage OAuth tokens
- Link OAuth accounts to users
- Support multiple providers

### Password Service
- Hash passwords (bcrypt)
- Verify password hashes
- Generate password reset tokens
- Enforce password policies

## API Endpoints

### POST /api/auth/login
- **Input**: `email`, `password`
- **Output**: `access_token`, `refresh_token`, `user`
- **Flow**: Validate → Hash Check → Generate Tokens → Create Session → Return

### POST /api/auth/register
- **Input**: `email`, `username`, `password`
- **Output**: `access_token`, `refresh_token`, `user`
- **Flow**: Validate → Hash Password → Create User → Generate Tokens → Create Session → Emit Event → Return

### POST /api/auth/refresh
- **Input**: `refresh_token`
- **Output**: `access_token`, `refresh_token`
- **Flow**: Validate Refresh Token → Generate New Tokens → Return

### POST /api/auth/logout
- **Input**: `access_token` (header)
- **Output**: Success message
- **Flow**: Validate Token → Blacklist Token → Delete Session → Return

### GET /api/auth/verify
- **Input**: `access_token` (header)
- **Output**: `user`, `valid`
- **Flow**: Validate Token → Check Blacklist → Return User Info

### GET /api/auth/oauth/:provider
- **Input**: `provider` (path), `code` (query)
- **Output**: `access_token`, `refresh_token`, `user`
- **Flow**: Redirect to Provider → Handle Callback → Exchange Code → Create/Link User → Generate Tokens → Return

## Security Features

### JWT Tokens
- **Access Token**: Short-lived (15 minutes), contains user info
- **Refresh Token**: Long-lived (7 days), stored securely
- **Algorithm**: HS256 or RS256
- **Claims**: user_id, email, role, exp, iat

### Password Security
- **Hashing**: bcrypt with salt rounds (12)
- **Validation**: Minimum 8 characters, complexity requirements
- **Reset**: Secure token generation, time-limited

### Session Security
- **Storage**: Redis with TTL
- **Validation**: Token signature + expiration check
- **Revocation**: Blacklist in Redis

### OAuth Security
- **State Parameter**: CSRF protection
- **PKCE**: For public clients
- **Token Storage**: Encrypted in database

## Integration Points

### Redis Cache
- **Purpose**: Session storage, token blacklist
- **TTL**: Sessions (30 days), Blacklist (token expiration)
- **Data**: Session data, blacklisted token IDs

### Core Service
- **Purpose**: User creation events
- **Method**: RabbitMQ message
- **Event**: `user.created` → Create user profile

### RabbitMQ
- **Purpose**: Auth event publishing
- **Events**: `user.created`, `user.logged_in`, `user.logged_out`
- **Consumers**: Core Service, Analytics Service

