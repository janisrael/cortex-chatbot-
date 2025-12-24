# PNG Diagram Creation Guide

## Summary

All Mermaid source files (`.mmd`) are ready in `docs/diagrams/`.
The README.md has been updated to reference PNG images instead of inline Mermaid code.

## Required PNG Files (10 total)

Create these PNG files in `docs/diagrams/`:

1. **system-architecture.png** ← from `system-architecture.mmd`
2. **application-architecture.png** ← from `application-architecture.mmd`
3. **database-schema.png** ← from `database-schema.mmd`
4. **request-flow.png** ← from `request-flow.mmd`
5. **rag-flow.png** ← from `rag-flow.mmd`
6. **knowledge-ingestion-flow.png** ← from `knowledge-ingestion-flow.mmd`
7. **deployment-flow.png** ← from `deployment-flow.mmd`
8. **user-isolation.png** ← from `user-isolation.mmd`
9. **llm-provider-flow.png** ← from `llm-provider-flow.mmd`
10. **project-structure.png** ← from `project-structure.mmd`

## How to Create PNG Files

### Method 1: Mermaid Live Editor (Recommended)

1. Go to https://mermaid.live/
2. Open the corresponding `.mmd` file from `docs/diagrams/`
3. Copy all content from the `.mmd` file
4. Paste into Mermaid Live Editor
5. Click "Actions" → "Download PNG"
6. Save as the exact filename (e.g., `system-architecture.png`)
7. Place in `docs/diagrams/` directory

### Method 2: VS Code Extension

1. Install "Markdown Preview Mermaid Support" extension
2. Open `.mmd` file in VS Code
3. Right-click → "Export Diagram" → "PNG"
4. Save to `docs/diagrams/`

### Method 3: Command Line (Mermaid CLI)

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i docs/diagrams/system-architecture.mmd -o docs/diagrams/system-architecture.png
# Repeat for all 10 files
```

## Verification

After creating all PNG files, verify:

```bash
cd docs/diagrams
ls -1 *.png | wc -l  # Should output: 10
```

## Current Status

✅ Mermaid source files: 10/10 created
✅ README.md updated: 10/10 PNG references added
⏳ PNG files: 0/10 (pending creation)

## File Locations

- **Source**: `docs/diagrams/*.mmd` (10 files)
- **Target**: `docs/diagrams/*.png` (10 files to create)
- **Documentation**: `README.md` (already updated with PNG references)
