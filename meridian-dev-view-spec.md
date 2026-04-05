# Meridian Developer View — Feature Specification

**Project:** Meridian (Controlled Substances Prescribing Framework)  
**Document type:** Feature spec for Claude Code plan mode  
**Audience:** Claude Code / software engineer handoff  
**Status:** Pre-implementation — use this to generate a detailed technical plan and sprint breakdown  
**Last updated:** April 2026 — v3: schema-driven content model, reference pool system, view mode clarifications

-----

## 1. Background & Context

Meridian is a structured clinical reference tool currently implemented as a static HTML/CSS single-page application. Content is authored in versioned markdown files (one per module), and a rendering pipeline converts those files into the published HTML. The production site is hosted on Cloudflare Pages, with branches deployed as separate preview URLs. Version control lives on GitHub (personal), with the local development environment on a Linux machine.

The current content iteration loop is:

1. Receive feedback (via embedded feedback button → Power Automate → Microsoft List)
1. Triage feedback manually in the List
1. Author changes in markdown
1. Use Claude Code to translate markdown → updated HTML/CSS
1. Push to a GitHub branch → Cloudflare Pages auto-deploys a preview URL
1. Evaluate; merge to main if approved

**The problem this spec addresses:** This loop requires developer intervention at every step and does not support collaborative review or structured content editing. The goal is to replace steps 3–6 with a browser-based interface, introduce a schema-enforced content model, and enable collaborative annotation — while keeping the production rendering pipeline intact.

**Key architectural shift:** Markdown is no longer the live source of truth. It becomes an import/export format only. The database is the live source of truth. Each module is an instance of a typed template schema with enforced structural constraints.

-----

## 2. Project Constraints

- **Current stack:** Static HTML/CSS frontend, markdown content files, Python scripting layer, GitHub + Cloudflare Pages CI/CD
- **Near-term hosting target:** Azure (within Optum’s tenant) + Entra ID authentication — design with this migration in mind, do not block on it
- **Compliance posture:** All components should be containerizable and portable; avoid hard dependencies on personal cloud accounts
- **Iteration philosophy:** Proof of concept first; prioritize working software over perfect architecture
- **Mobile rendering:** The production view (Modes 1 and 2) must fit within one iPhone screen width. This is a design constraint on content volume, not just CSS.

-----

## 3. View Mode Model

Meridian has three view modes on a spectrum from passive consumption to active editing. Each is a superset of the previous.

### Mode 1 — Standard View (current production)

Collapsed by default. Click-through navigation to reference layers. No authentication. Available to all users including eventual clinical end users. A **Compact / Expanded toggle** is present, allowing any user to switch to Mode 2 at any time without authentication.

### Mode 2 — Expanded View

Full module rendered in a single scrollable, collapsible outline. No click-through required. All reference sections (FAQs, SmartPhrases, Resources) visible inline via superscript reference numbers. Inline annotations visible (count badge; expandable thread). Authentication required only for submitting annotations — reading is open.

**This is a production feature, not a developer-only feature.** All clinical users have access to it via the toggle. It is also the primary interface for Reviewer and Collaborator roles.

### Mode 3 — Developer / Editor View

Full editing interface. Schema-driven template editor, branch management, publish workflow, branch tree visualizer. Restricted to Editor role. Collaborator role accesses a sandboxed inline editor within Mode 2 that writes to a personal draft branch.

### Feature Matrix

|Feature                              |Mode 1|Mode 2  |Mode 3    |
|-------------------------------------|------|--------|----------|
|Collapsed default view               |✓     |—       |—         |
|Compact/Expanded toggle              |✓     |✓       |✓         |
|Full expanded outline                |—     |✓       |✓         |
|Superscript reference links          |—     |✓       |✓         |
|View annotations                     |—     |✓       |✓         |
|Submit annotations                   |—     |✓ (auth)|✓         |
|Inline outline editing (Collaborator)|—     |✓ (role)|✓         |
|Resolve / manage annotations         |—     |—       |✓         |
|Template editor (schema fields)      |—     |—       |✓         |
|Branch management                    |—     |—       |✓         |
|Publish workflow                     |—     |—       |✓ (Editor)|
|Branch tree visualizer               |—     |—       |✓         |
|MS List feedback panel               |—     |—       |✓         |

-----

## 4. Content Schema

### 4.1 Design Philosophy

Each module is an **instance of a fixed template**. The template enforces structural constraints so that no editor — human or otherwise — can produce a module that breaks the layout or exceeds the iPhone screen budget. Constraints are enforced at the database and UI layer, not just by convention.

Markdown is used only as an **import/export format**:

- **Import:** A new module drafted in Claude Chat can be output as structured markdown, then uploaded and parsed into a new module record in the database.
- **Export:** Any module can be exported as structured markdown for backup, handoff, or Claude Code processing.

The database is the live source of truth for all module content.

-----

### 4.2 Module Template Schema

A module consists of the following typed sections, in fixed order:

```
Module
├── [META]   Module header
├── [BODY]   Checkbox items              [max 4]
│              └── reference tags → FAQ, SmartPhrase, Resource pools
├── [BODY]   Middle block                [exactly 1]
│              └── reference tags → SmartPhrase pool
├── [BODY]   Escalation items            [max 10]
│              └── reference tags → FAQ, SmartPhrase, Resource pools
├── [REF-F]  FAQ section                 [shared pool; tagged from items]
├── [REF-S]  SmartPhrase section         [shared pool; tagged from items]
└── [REF-R]  Resource section            [shared pool; tagged from items]
```

**Critical structural insight:** FAQs, SmartPhrases, and Resources exist as **shared reference pools** at the module level, not as children of individual items. Each Checkbox and Escalation item carries reference numbers that link into these pools. A single FAQ entry can be referenced by multiple checkboxes and/or multiple escalation items simultaneously. This eliminates duplication and makes cross-cutting clinical concerns explicit.

-----

### 4.3 Section Definitions

#### [META] Module Header

|Field            |Type     |Notes                                      |
|-----------------|---------|-------------------------------------------|
|`module_id`      |UUID     |Stable; assigned at creation; never changes|
|`title`          |string   |Display name (e.g., “ADHD”)                |
|`substance_class`|string   |Controlled substance category              |
|`version`        |string   |Semantic version                           |
|`status`         |enum     |draft / review / published                 |
|`last_updated`   |timestamp|                                           |
|`author`         |string   |Creator display name                       |

-----

#### [BODY] Checkbox Items

**Constraint: maximum 4 items.**

|Field             |Type             |Notes                                        |
|------------------|-----------------|---------------------------------------------|
|`item_id`         |UUID             |Stable; anchor for annotations and references|
|`position`        |integer          |1–4; swappable via up/down controls          |
|`statement`       |string           |Checkbox label; one clinical assertion       |
|`sub_statement`   |string (nullable)|Brief qualifier beneath statement            |
|`faq_refs`        |UUID[]           |Array of FAQ entry IDs tagged to this item   |
|`smartphrase_refs`|UUID[]           |Array of SmartPhrase entry IDs               |
|`resource_refs`   |UUID[]           |Array of Resource entry IDs                  |

Superscript reference numbers render inline after the statement text per convention in §4.7.

-----

#### [BODY] Middle Block

**Constraint: exactly 1 per module.**

|Field             |Type             |Notes                                         |
|------------------|-----------------|----------------------------------------------|
|`block_id`        |UUID             |Stable                                        |
|`narrative_text`  |string           |Free prose paragraph                          |
|`context`         |string (nullable)|Optional framing sentence                     |
|`smartphrase_refs`|UUID[]           |SmartPhrase entries applicable to this section|

-----

#### [BODY] Escalation Items

**Constraint: maximum 10 items (iPhone screen budget).**

Same structure as Checkbox Items:

|Field             |Type             |Notes                                  |
|------------------|-----------------|---------------------------------------|
|`item_id`         |UUID             |Stable                                 |
|`position`        |integer          |Swappable via up/down                  |
|`statement`       |string           |Escalation label                       |
|`sub_statement`   |string (nullable)|Optional qualifier                     |
|`faq_refs`        |UUID[]           |FAQ entries tagged to this item        |
|`smartphrase_refs`|UUID[]           |SmartPhrase entries tagged to this item|
|`resource_refs`   |UUID[]           |Resource entries tagged to this item   |

-----

#### [REF-F] FAQ Section

A flat pool of FAQ entries for the module. Referenced by one or more Checkbox or Escalation items.

**Constraint: maximum 5 FAQ entries per module in v1** (revisit as content grows).

|Field          |Type  |Notes                                                                                                            |
|---------------|------|-----------------------------------------------------------------------------------------------------------------|
|`faq_id`       |UUID  |Stable                                                                                                           |
|`ref_number`   |string|Display label (F1, F2, F3…)                                                                                      |
|`question`     |string|Broad question or topic header                                                                                   |
|`answer_blocks`|JSONB |Ordered list of answer components; each block is prose paragraph, bullet list, or nested sub-question with answer|
|`tagged_from`  |UUID[]|item_ids of checkboxes/escalation items that reference this entry                                                |

**Unified object type note:** FAQs and escalation item sub-items are the same object type. Both are entries in the FAQ pool. What differs is only which items reference them. The expanded view renders all FAQ entries in a single collapsible block at the module bottom — readers can work through the full FAQ section without per-item nesting.

-----

#### [REF-S] SmartPhrase Section

A pool of Epic SmartPhrase entries and associated consultation language.

|Field                    |Type             |Notes                                              |
|-------------------------|-----------------|---------------------------------------------------|
|`smartphrase_id`         |UUID             |Stable                                             |
|`ref_number`             |string           |Display label (S1, S2…)                            |
|`situation`              |string           |Brief label for when this phrase applies           |
|`smartphrase_text`       |string           |Full SmartPhrase text as entered in Epic           |
|`econsult_language`      |string (nullable)|Specific verbiage for e-consult or referral request|
|`consult_recommendations`|string (nullable)|Structured recommendations for the consult scenario|
|`tagged_from`            |UUID[]           |item_ids that reference this entry                 |

Multiple SmartPhrase variants exist for different clinical situations within the same module. All live in this shared pool.

-----

#### [REF-R] Resource Section

A pool of document and external links.

|Field          |Type  |Notes                                                |
|---------------|------|-----------------------------------------------------|
|`resource_id`  |UUID  |Stable                                               |
|`ref_number`   |string|Display label (R1, R2…)                              |
|`display_text` |string|Human-readable label                                 |
|`url`          |string|SharePoint, OneDrive, or external URL                |
|`resource_type`|enum  |sharepoint / onedrive / external / policy / guideline|
|`tagged_from`  |UUID[]|item_ids that reference this entry                   |

In Mode 2 (expanded): resources render as clickable inline links.  
In Mode 1 (compact): resources appear behind a “Resources” affordance per item.

-----

### 4.4 Reference Number Convention

All reference numbers render as superscript inline links, anchored at the relevant item, jumping to the entry in its reference section.

|Prefix|Type                    |Examples  |
|------|------------------------|----------|
|F     |FAQ entry               |F1, F2, F3|
|S     |SmartPhrase / e-consult |S1, S2    |
|R     |Resource / document link|R1, R2, R3|

Example inline rendering:

> ☐ Patient has completed PDMP check within 90 days ᶠ¹ ᶠ³ ˢ¹

In the expanded outline, all three reference sections render as collapsible blocks at the module bottom. A reader can work through FAQs, SmartPhrases, and Resources in unified sections rather than navigating per-item — appropriate for the expanded reading mode.

-----

### 4.5 Structural Constraints Summary

|Section            |Min|Max|Notes                       |
|-------------------|---|---|----------------------------|
|Checkbox items     |1  |4  |Hard constraint             |
|Escalation items   |1  |10 |iPhone screen budget        |
|FAQ entries (pool) |0  |5  |v1 constraint; revisit later|
|SmartPhrase entries|0  |—  |No hard limit               |
|Resource entries   |0  |—  |No hard limit               |
|Middle block       |1  |1  |Always exactly one          |

Constraints enforced at API layer (reject violating saves) and UI layer (disable “Add” button at max; show count indicator).

-----

### 4.6 Item Mobility and Lifecycle

**Reordering:** Up/down arrow controls swap the `position` integer between adjacent items. Annotations anchor to `item_id`, not position — reordering never affects annotation integrity.

**Duplicating an item:** “Duplicate” button creates a new record with a new `item_id`, copying all field values including reference arrays. Annotations are NOT copied — they belong to the original item.

**Copy-paste as object:** Clipboard payload is a serialized item JSON. Pasting creates a new item record with a new `item_id`. Allows building new modules from parts of existing ones without re-entry. Annotations not copied.

**Deleting an item:** Soft delete only. An item with unresolved annotations cannot be deleted. The editor is shown the annotation count and must resolve or reassign each thread before deletion proceeds. Soft-deleted items retain a `deleted_at` timestamp and are not rendered in any view.

**Drag-and-drop reordering:** Out of scope for v1. Up/down arrows are sufficient.

**Cross-section type promotion** (e.g., moving a Checkbox item to Escalation): Out of scope for v1. Requires validation logic; park for later.

-----

## 5. Detailed Feature Specifications

### 5.1 Expanded View — Sprint 1

**Description:** A toggle on the production site rendering the full module as a scrollable, collapsible outline. Available to all users for reading; annotation submission requires lightweight auth.

**Requirements:**

- “Compact / Expanded” toggle button persistent on production page
- Expanded rendering order: Checkboxes → Middle Block → Escalation Items → FAQ section → SmartPhrase section → Resource section
- Superscript reference numbers as anchor links jumping to reference entries
- All sections individually collapsible; “Collapse all / Expand all” global toggle
- Resource links render as clickable hyperlinks with display text
- Annotation count badge per item (mock data in Sprint 1; live in Sprint 2)
- No backend required — pure frontend CSS/JS against existing static content

**Implementation note:** This sprint works against existing static HTML. The schema-driven rendering pipeline (Sprint 3) will replace this. The visual design established here is the reference for all subsequent rendering.

-----

### 5.2 Annotation System — Sprint 2

**Description:** Threaded comments anchored to stable item UUIDs. Visible in Modes 2 and 3. Distinct from MS List end-user feedback.

**Data model:**

|Field                 |Type           |Notes                         |
|----------------------|---------------|------------------------------|
|`annotation_id`       |UUID           |                              |
|`module_id`           |UUID           |                              |
|`item_id`             |UUID           |Anchored item (any item type) |
|`branch`              |string         |Branch-scoped                 |
|`author_display_name` |string         |No full account required in v1|
|`body`                |text           |Plain text with line breaks   |
|`parent_annotation_id`|UUID (nullable)|Threading                     |
|`resolved`            |boolean        |                              |
|`resolved_by`         |string         |                              |
|`resolved_at`         |timestamp      |                              |
|`created_at`          |timestamp      |                              |

**Display:**

- Badge per item: open annotation count; click to expand thread
- Resolved annotations greyed but preserved; full thread always visible
- Mode 2: submit new annotation or reply (invite token auth)
- Mode 3: additionally resolve, link to MS List feedback item

**Soft delete enforcement:** Item with unresolved annotations cannot be deleted. Editor must resolve or reassign each thread before deletion proceeds.

-----

### 5.3 Template Editor — Sprint 3

**Description:** Schema-driven form editor. Each module section is a typed, bounded field panel. Editors cannot exceed constraints or add undefined sections.

**Requirements:**

- Module selector sidebar with status indicators
- Section panels: Checkbox items, Middle block, Escalation items, FAQ pool, SmartPhrase pool, Resource pool
- Reference tag picker: select which pool entries to tag to each item
- Constraint enforcement: “Add” button disabled at max; count shown
- Unsaved changes indicator; save writes versioned snapshot to DB
- Rendered preview toggle (Mode 2 rendering of current draft)
- Import from structured markdown: parse and pre-fill form for editor review before saving

**Collaborator access:** Same editor surface, scoped to personal draft branch only.

-----

### 5.4 Reference Pool Management — Sprint 4

**Requirements:**

- FAQ entry CRUD: question field, answer block builder (prose / bullets / nested sub-question), tagged_from display
- SmartPhrase entry CRUD: situation, phrase text, e-consult language, consult recommendations fields, tagged_from display
- Resource entry CRUD: display text, URL, resource_type selector, tagged_from display
- All pool editors accessible within the template editor as collapsible side panels
- Markdown import parser maps structured markdown fields to pool entries

-----

### 5.5 Versioned Content Store — Sprint 5

**Requirements:**

- Every save creates a `module_version` snapshot (full module state as JSONB)
- Fields: `version_id`, `module_id`, `branch`, `author`, `timestamp`, `snapshot_json`, `commit_message`
- Version history browser in editor sidebar
- Restore: load prior snapshot into editor; explicit save required to persist
- DB → filesystem sync: explicit action serializes DB state to markdown export files and commits to active branch; not automatic

-----

### 5.6 Branch Management — Sprint 6

**Requirements:**

- Active branch displayed in editor header
- Create branch from HEAD (name input)
- Switch branch (unsaved-change guard)
- Merge to main (confirmation; conflict → terminal instruction surfaced)
- Branch list: name, last commit, last modified, preview URL, status
- Collaborator draft branch: auto-named (e.g., `draft/displayname`)

Backend: Python/FastAPI wrapper around git CLI. No browser-side git operations.

-----

### 5.7 Publish Workflow — Sprint 7

**Requirements:**

- Publish triggers: DB → filesystem sync → git push → Cloudflare Pages build
- Confirmation dialog: branch name, target preview URL
- Build status inline: pending → building → deployed / failed
- On success: clickable preview URL
- On failure: error log or link

-----

### 5.8 MS List Feedback Panel — Sprint 8

**Requirements:**

- Per-module feedback items from MS List surfaced inline in editor
- Display: timestamp, submitter, text, status, developer comment
- Filter by status
- Editor can update status and add comment (Graph API or Power Automate webhook)
- Mock data fallback for development without live credentials
- Link feedback item to annotation thread for traceability

-----

### 5.9 Branch Tree Visualizer — Sprint 9

**Requirements:**

- Visual tree of all branches with relationships
- Each node: name, status, preview URL, last commit message
- Click node → navigate to branch in editor
- Compare two branches: module-by-module diff summary
- “Approve module version from branch” → generates note/task (no auto-merge in v1)

-----

## 6. System Architecture

```
[ Browser ]
    ├── Modes 1 & 2 — Static Cloudflare Pages (no backend for rendering)
    │       ├── Compact/Expanded toggle (pure JS/CSS)
    │       ├── Annotation read      → Backend API
    │       └── Annotation submit    → Backend API (invite token auth)
    └── Mode 3 — Developer View
            └── All actions          → Backend API (Editor/Collaborator token)

[ Backend — Python/FastAPI ]
    ├── /api/modules          Module template CRUD
    ├── /api/references       FAQ, SmartPhrase, Resource pool CRUD
    ├── /api/versions         Version snapshot read/restore
    ├── /api/annotations      Annotation CRUD and threading
    ├── /api/branches         Git branch operations
    ├── /api/publish          Filesystem sync + git push + Cloudflare trigger
    └── /api/feedback         Proxy to Microsoft Graph / Power Automate

[ Data ]
    ├── PostgreSQL            Modules, reference pools, annotations, version
    │                         snapshots — Linux server (v1); Azure DB (v2)
    ├── Filesystem            Markdown export files (git-tracked; deployment artifacts)
    └── Microsoft List        End-user feedback (external; Graph API read/write)

[ CI/CD ]
    └── Cloudflare Pages      Auto-deploys on branch push
```

**Multi-user access:** End users hit static Cloudflare Pages — no backend, no Tailscale enrollment. Only the backend VPS needs Tailscale access to the Linux PostgreSQL host. No end user touches backend infrastructure.

-----

## 7. Authentication & Access Control

### Roles

**Reviewer**

- Mode 2 read (open); annotation submission with invite token (no account required)
- Auth: open for reading; short-lived signed invite token for submission

**Collaborator**

- Mode 2 + template editor scoped to personal draft branch
- Can: annotate, create/edit draft branch, preview, share draft URL
- Cannot: edit main, merge, publish, resolve annotations
- Auth v1: individual token; v2: Entra ID Collaborator role

**Editor**

- Full Mode 3
- Can: all Collaborator actions + full template editor on any branch, merge to main, publish, resolve annotations, manage MS List feedback panel
- Auth v1: individual token; v2: Entra ID Editor role

### Implementation

- Pluggable auth middleware: v1 tokens swapped for Entra ID in v2 with no route refactoring
- Mode 1 production: unauthenticated
- Reviewer invite links: HMAC-signed short-lived tokens; no user accounts required

-----

## 8. Non-Goals (v1)

- Patient-facing or clinical-user-facing features
- Real-time collaborative editing (multiple simultaneous editors on same document)
- Automated clinical content validation
- Full Git conflict resolution UI
- Drag-and-drop reordering (up/down arrows are sufficient)
- Cross-section item type promotion (checkbox → escalation)
- Mobile-optimized Developer View (Mode 3 desktop-first; Modes 1 and 2 mobile-optimized)

-----

## 9. Sprint Breakdown

> **Instruction to Claude Code:** In plan mode, expand each sprint into specific tasks, file-level changes, and complexity estimates. Resolve open questions in §10 before Sprint 0 begins. Sprint 0 must complete before any other sprint begins.

**Sprint 0 — Architecture & Scaffolding**

- Define complete PostgreSQL schema: modules, checkbox_items, middle_block, escalation_items, faq_entries, smartphrase_entries, resource_entries, item_reference_tags, module_versions, annotations
- Define stable UUID ID scheme for all item types
- Scaffold FastAPI backend
- Scaffold frontend (subdirectory vs. separate repo — resolve here)
- Docker Compose: app + PostgreSQL
- OpenAPI contract for all routes
- Define structured markdown import/export dialect (maps to schema fields)

**Sprint 1 — Expanded View (frontend only)**

- Compact/Expanded toggle on production page
- Full outline rendering with all sections in schema order
- Superscript reference number rendering with anchor links
- Collapsible sections; collapse all / expand all
- Resource links as clickable hyperlinks
- Annotation count badge (mock data)

**Sprint 2 — Annotation System**

- PostgreSQL annotations table and API routes
- Badge → thread expand UI per item
- Annotation submission (display name + body; invite token auth)
- Resolved state display
- Soft-delete enforcement (block deletion if unresolved annotations)

**Sprint 3 — Template Editor**

- Module selector sidebar
- Schema-driven section panels for all types
- Reference tag picker
- Constraint enforcement (max items, count indicators)
- Save to DB (versioned snapshot)
- Unsaved change guard
- Rendered preview toggle

**Sprint 4 — Reference Pool Management**

- FAQ CRUD with answer block builder
- SmartPhrase CRUD with e-consult fields
- Resource CRUD with type selector
- Pool editor panels within template editor
- Markdown import parser

**Sprint 5 — Versioned Content Store**

- Version snapshot on every save
- Version history browser
- Restore prior version
- DB → filesystem sync action

**Sprint 6 — Branch Management**

- FastAPI git wrapper
- Branch selector in editor header
- Create branch modal; Collaborator draft auto-naming
- Branch list with metadata

**Sprint 7 — Publish Workflow**

- Publish pipeline: DB sync → git push → Cloudflare build
- Build status polling; success/failure UI

**Sprint 8 — MS List Feedback Panel**

- Mock data layer + panel UI
- Status filter; developer comment
- Graph API integration
- Link to annotation thread

**Sprint 9 — Branch Tree Visualizer**

- Branch relationship tree
- Module diff summary
- Navigate-to-branch from node

**Sprint 10 — Auth + Hardening**

- Three-role token middleware
- HMAC invite link generation
- Environment config (dev / staging / prod)
- Error handling, logging
- Backend route test coverage

-----

## 10. Open Questions for Claude Code Plan Mode

1. Should the Developer View frontend be a subdirectory of the existing Meridian repo, or a separate repository? Tradeoff: shared CSS access vs. clean separation of concerns.
1. What is the cleanest DB ↔ git sync pattern? Explicit “Sync to filesystem” action (current spec) vs. post-save auto-commit — what are the failure modes of each?
1. For the rendered preview pane, how is production Meridian CSS injected without duplication? (Symlink? Build step? Shared CDN path?)
1. Cloudflare Pages build status: webhook vs. timer polling?
1. At what point should the backend move to a containerized service to ensure clean Azure migration?
1. Should annotations be strictly branch-scoped (only visible on the branch where created) or globally visible with branch metadata attached? Consider: a Collaborator creates an annotation on their draft branch — should the Editor see it when on main?
1. What is the full spec for the structured markdown import/export dialect? Propose a format that maps cleanly to the template schema, enabling Claude Chat outputs to be imported without manual re-entry.
1. For item copy-paste as objects: should the clipboard payload be internal-only (within the Meridian editor tab) or serialized to the system clipboard (allowing copy between browser sessions)?

-----

## 11. Design Decisions Log

**Markdown is import/export only.** Database is the live source of truth. Markdown remains useful as a Claude Chat output format and for git-tracked deployment artifacts but is no longer edited directly in the live workflow.

**Schema-driven template, not free-form editing.** Structural constraints enforced at API and UI layer. Editors fill typed fields; they cannot break the layout.

**Shared reference pools with tagging.** FAQs, SmartPhrases, and Resources exist as module-level pools. Items tag into pools via UUID arrays. A single entry can be referenced by multiple checkboxes and escalation items simultaneously, eliminating duplication.

**FAQs and escalation sub-items are unified.** Both are entries in the FAQ pool. The distinction is only which items reference them. In expanded view, all FAQ entries render as one collapsible block at the module bottom.

**SmartPhrases include e-consult language.** Each SmartPhrase entry carries: situation label, Epic phrase text, e-consult verbiage, and consult recommendations as distinct fields.

**Superscript reference convention:** F# for FAQs, S# for SmartPhrases, R# for Resources.

**Expanded view is a production feature.** The Compact/Expanded toggle is available to all clinical users without authentication.

**Soft delete with annotation guard.** Items with unresolved annotations cannot be deleted. User must resolve or reassign each thread before deletion proceeds.

**Annotations anchor to item_id, not content.** Reordering and text editing never orphan annotations.

**Multi-user access.** End users hit static Cloudflare Pages — no backend, no Tailscale. Only the backend VPS needs Tailscale access to the Linux PostgreSQL host.

**Porting strategy.** Goal is containment (Azure hosting + Entra ID), not a rebuild. Power Apps is not the target. Azure static web hosting + Azure Database for PostgreSQL is the v2 target.

-----

*Spec authored: April 2026*  
*Last updated: April 2026 — v3: schema-driven content model, reference pool system, unified FAQ object type, SmartPhrase e-consult fields, item mobility, soft delete with annotation guard*  
*Next step: Claude Code plan mode — resolve §10 open questions, then expand Sprint 0 schema definition before any code is written.*