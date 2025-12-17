# Architecture Diagrams

This folder contains detailed architecture diagrams for the Cortex AI microservices system.

## Overview Diagram

- **[combined_data_architecture.md](./combined_data_architecture.md)** - Single comprehensive diagram combining Database Schema Distribution, ChromaDB Collection Isolation, Config File Sync, and Backup & Recovery Strategy

## Service-Specific Diagrams

Each service has its own detailed diagram with:
- API layer structure
- Service layer responsibilities
- Database schema details
- Data flow diagrams
- Integration points
- API endpoints documentation

### Core Services

1. **[core_service.md](./core_service.md)** - Main chatbot service
   - Chat endpoint
   - Conversation management
   - User profiles
   - Widget serving

2. **[auth_service.md](./auth_service.md)** - Authentication & authorization
   - User login/registration
   - JWT token management
   - OAuth integration
   - Session management

3. **[widget_service.md](./widget_service.md)** - Widget serving
   - Embed script generation
   - Widget HTML serving
   - Configuration management
   - CDN integration

### Feature Services

4. **[knowledge_service.md](./knowledge_service.md)** - Knowledge base & RAG
   - File upload & processing
   - FAQ management
   - Web crawling
   - ChromaDB vector operations

5. **[analytics_service.md](./analytics_service.md)** - Analytics & insights
   - Conversation analytics
   - Pattern recognition
   - Success rate calculation
   - Report generation

6. **[marketing_service.md](./marketing_service.md)** - Email marketing
   - Subscriber management
   - Campaign creation
   - Email templates
   - Campaign analytics

### Advanced Services

7. **[langgraph_service.md](./langgraph_service.md)** - Advanced AI workflows
   - Workflow orchestration
   - Appointment scheduling
   - Task automation
   - Multi-agent coordination

8. **[helper_agent_service.md](./helper_agent_service.md)** - Conversation optimization
   - Real-time conversation analysis
   - Pattern matching
   - Guidance generation
   - A/B testing framework

## Diagram Structure

Each service diagram includes:

1. **Architecture Overview**
   - API layer endpoints
   - Service layer components
   - Database schema
   - External service integrations

2. **Data Flow Diagrams**
   - Request/response flows
   - Service interactions
   - Database operations
   - External API calls

3. **Database Schema Details**
   - Table structures
   - Relationships
   - Indexes
   - Field descriptions

4. **Service Responsibilities**
   - Core functions
   - Business logic
   - Data processing

5. **API Endpoints**
   - Endpoint definitions
   - Input/output formats
   - Request/response flows

6. **Integration Points**
   - External services
   - Message queues
   - Caching layers
   - Database connections

## Viewing Diagrams

These Mermaid diagrams can be viewed in:

- **GitHub**: Automatically renders Mermaid diagrams in markdown files
- **VS Code**: Install "Markdown Preview Mermaid Support" extension
- **Online**: Use [Mermaid Live Editor](https://mermaid.live/)
- **CLI**: Use Mermaid CLI to export as PNG/SVG

## Related Documentation

- **[full_scale_architecture_plan.md](../full_scale_architecture_plan.md)** - Complete architecture planning document
- **[architecture_diagrams.md](../architecture_diagrams.md)** - All architecture diagrams (25 diagrams)
- **[todo.md](../todo.md)** - Development todo list

## Diagram Count

- **Combined Diagram**: 1
- **Service Diagrams**: 8
- **Total**: 9 detailed service diagrams

Each diagram is optimized to be comprehensive yet focused on a single service, making it easier to understand and maintain.

