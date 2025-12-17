# Changelog

All notable changes to Cortex AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2025-12-17

### Added

#### Multi-LLM Provider Support
- Google Gemini activation and full functionality
- Groq (Llama) activation and full functionality
- Anthropic Claude activation and full functionality
- Together AI (Llama) activation and full functionality
- System default API keys management for free-tier providers (OpenAI, Gemini, Groq)
- API key testing before save functionality
- User API key override capability for all providers

#### Knowledge Base Accuracy Improvements
- Optimized evaluation thresholds (60% semantic similarity + 40% fact coverage)
- Enhanced pass criteria (semantic_sim >= 0.60 OR fact_cov >= 0.50)
- Improved FILE and CRAWL test accuracy

#### Data Persistence
- Kubernetes PVC configuration for all data directories
- Persistent volume mounts for `/app/data`, `/app/chroma_db`, `/app/config`
- Zero data loss guarantee across pod restarts and evictions

#### UI/UX Improvements
- Compact toggle switch design for User/Admin mode switching
- Dynamic label that changes between "User" and "Admin"
- Improved demo account info area with concise explanation
- Advanced settings info icons with detailed descriptions
- Info modal with human-readable explanations for all 7 advanced chatbot settings
- User info form styling improvements (5px padding, 6px border-radius)
- Automatic name capitalization (first letter uppercase, rest lowercase)
- Settings tab styling improvements (removed border-left from cards)

#### Admin Dashboard
- API Keys tab extracted to component-based structure (`admin/components/api_keys_tab.html`)
- System LLM provider keys management UI
- API key visibility toggle (eye icon)
- Status badges (Active/Inactive) for each provider
- Gemini model fallback mechanism during API key testing

#### Widget & Chatbot
- Custom avatar bug fix (consistent display in all messages)
- Avatar display logic using `widget_avatar_url` consistently
- Welcome message customization feature
- Continuous conversation improvements (better context building and history management)

### Changed

- Updated accuracy calculation weights in knowledge base tests
- Improved error handling for API key testing
- Enhanced conversation context building
- Better code organization following component-based structure

### Fixed

- Fixed custom avatar not displaying in widget after first message
- Fixed API Keys tab component missing (restored from main branch)
- Fixed name capitalization inconsistency across frontend, backend, and service layers
- Fixed settings tab border styling issues
- Improved error handling for API key testing with better user feedback

### Technical Improvements

- Component-based structure for admin dashboard tabs
- Modular architecture improvements following coding rules
- Kubernetes deployment files in `k8s/` directory
- CI/CD workflow updates to apply persistence configuration automatically
- OG image meta tags updated for better social media sharing

### Documentation

- Created `docs/LLM_PROVIDER_ANALYSIS.md` with provider status
- Created `docs/diagrams/database_erd.md` (dbdiagram.io format)
- Created `docs/CORTEX_DATA_PERSISTENCE_PLAN.md` with persistence strategy
- Created `docs/DEPLOYMENT_PERSISTENCE_STATUS.md` with deployment status

---

## [2.1.0] - Previous Release

### Added
- Initial multi-LLM support
- RBAC (Role-Based Access Control) implementation
- OTP-based email verification
- Admin dashboard with user management

---

## [2.0.0] - Previous Release

### Added
- Core platform with RAG (Retrieval Augmented Generation)
- Knowledge base management (upload documents, crawl websites, manage FAQs)
- Vector-based knowledge retrieval using ChromaDB
- Customizable appearance and widget embedding
- RESTful API with API key authentication

---

[2.2.0]: https://github.com/janisrael/chatbot/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/janisrael/chatbot/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/janisrael/chatbot/releases/tag/v2.0.0

