# Expected PNG Diagram Files

Please create the following PNG files from the Mermaid scripts in this directory:

## Required PNG Files

1. **system-architecture.png** - System infrastructure diagram
   - Source: `system-architecture.mmd`
   - Shows: Hetzner server, Kubernetes cluster, PVCs, external services

2. **application-architecture.png** - Application layer diagram
   - Source: `application-architecture.mmd`
   - Shows: Frontend, Blueprints, Services, Models, Data layer

3. **database-schema.png** - Database ERD diagram
   - Source: `database-schema.mmd`
   - Shows: All tables with relationships and fields

4. **request-flow.png** - Request sequence diagram
   - Source: `request-flow.mmd`
   - Shows: Complete request flow from user to LLM response

5. **rag-flow.png** - RAG process flowchart
   - Source: `rag-flow.mmd`
   - Shows: RAG (Retrieval Augmented Generation) process steps

6. **knowledge-ingestion-flow.png** - Knowledge ingestion flowchart
   - Source: `knowledge-ingestion-flow.mmd`
   - Shows: How files/URLs/FAQs are ingested into vectorstore

7. **deployment-flow.png** - CI/CD deployment flowchart
   - Source: `deployment-flow.mmd`
   - Shows: GitHub Actions → Docker → Kubernetes deployment process

8. **user-isolation.png** - User data isolation diagram
   - Source: `user-isolation.mmd`
   - Shows: How user data is isolated (vectorstores, files, configs)

9. **llm-provider-flow.png** - LLM provider selection flowchart
   - Source: `llm-provider-flow.mmd`
   - Shows: API key resolution and provider selection logic

10. **project-structure.png** - Project folder structure diagram
    - Source: `project-structure.mmd`
    - Shows: Visual representation of project directory structure

## File Location

All PNG files should be placed in:
```
docs/diagrams/
```

## How to Convert

1. Open each `.mmd` file in Mermaid Live Editor: https://mermaid.live/
2. Copy the Mermaid code from the `.mmd` file
3. Paste into Mermaid Live Editor
4. Export as PNG
5. Save as the corresponding `.png` filename listed above

## Example

- Open `system-architecture.mmd`
- Copy all content
- Paste into https://mermaid.live/
- Export as PNG
- Save as `docs/diagrams/system-architecture.png`

Repeat for all 10 diagrams.
