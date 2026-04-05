# Meridian

Controlled substances prescribing reference framework for primary care clinicians.

## Quick Start

```bash
python3 server.py        # http://localhost:8090
# or open index-rendered.html directly
```

**Production:** https://meridian-3x6.pages.dev/index-rendered.html

## Architecture

All content lives in structured JSON files. The browser renders everything client-side — no backend required.

```
Content Pipeline:
  Word (DOCX template) → Upload → JSON → Webapp / PDF / PPTX

File Structure:
  modules/
  ├── index.json          Module registry (titles, metadata)
  ├── adhd.json           One JSON file per clinical module
  ├── ckd.json
  ├── opiates.json
  ├── benzos.json
  └── anemia.json

  index.html              Original static HTML (legacy, still functional)
  index-rendered.html     JSON-driven renderer (production)

  extract_modules.py      HTML → JSON extraction (one-time migration tool)
  generate_pptx.py        JSON → PPTX via CLI (Python, batch generation)
  generate_docx.py        JSON → DOCX template via CLI (Python, batch generation)

  templates/              Pre-generated Word templates (one per module)
  presentations/          Pre-generated PowerPoint decks (one per module)
```

## Features

- **Compact view** — Click-through checklist with interactive checkboxes, session-persisted state, per-module completion animations
- **Expanded view** — Full scrollable outline with collapsible sections, superscript FAQ reference tags (F1, F2...) as anchor links
- **Download PDF** — Print stylesheet with clean formatting, all sections expanded
- **Download PPTX** — Client-side PowerPoint generation via PptxGenJS (title, checklist, escalation, FAQ slides)
- **Upload/Download DOCX** — Structured Word template round-trip via mammoth.js; edit modules in Word, upload to preview
- **Module search** — Searchbar filters modules by title; dynamic tabs (max 5 open, closeable, scrollable, renamable)
- **Feedback system** — Speech bubble icons on every item open pre-filled mailto feedback; module-level and app-level feedback rows

## Deployment

```bash
# Deploy to production (main branch)
npx wrangler pages deploy . --project-name=meridian --branch=main --commit-dirty=true

# Deploy preview branch
npx wrangler pages deploy . --project-name=meridian --branch=<branch> --commit-dirty=true
```

## CLI Tools

```bash
# Extract module content from legacy index.html to JSON (one-time)
python3 extract_modules.py

# Generate Word templates for all modules
python3 generate_docx.py

# Generate PowerPoint decks for all modules
python3 generate_pptx.py

# Single module
python3 generate_pptx.py modules/adhd.json
python3 generate_docx.py modules/adhd.json
```

## DOCX Template Format

The Word template uses strict heading styles for reliable round-trip parsing:

- **Heading 1** — Module title (e.g., "ADHD Stimulants — Inherited Patient")
- **Heading 2** — Section markers: Introduction, Checklist Items, Green Zone, Escalation Items, Context, Footer, FAQ Reference
- **Heading 3** — Items with `[id]` prefix: `[pdmp] PDMP reviewed — no concerning pattern`
- **Field markers** — `Label:`, `Narrative:`, `SmartPhrase:`, `FAQ Title:`, `Question:`
- **Instructions** — Lines starting with `>>>` are stripped on upload

## Next Steps (Post-Migration)

- M365 Copilot agent for template enforcement and direct JSON conversion
- One-click publish workflow (depends on hosting target)
- Migration to Optum Azure infrastructure with Entra ID authentication
