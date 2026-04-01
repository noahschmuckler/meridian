# Meridian — Collaboration & Feedback Architecture
## Page ID: collab
## Header Title: How Meridian Gets Better

---

### INTRO TEXT
Meridian is a living document, not a static policy. This page
describes how provider feedback flows from the point of care
into reviewed, agreed-upon updates to the content you are
reading. The system is designed to work at whatever tier of
infrastructure is currently available — starting with something
functional today and evolving toward a continuously improving
clinical intelligence platform. Reviewers and administrators
can use this page to understand the current state and the
pathway forward.

---

### TIER OVERVIEW

Current Status: [TO BE UPDATED BY ADMINISTRATOR]
Active Tier: Tier 1

---

## TIER 1 — Email-Based Feedback
### Status: Available immediately. No IT required.

HOW IT WORKS:
Each item in Meridian has a speech bubble icon. Tapping it
opens a pre-addressed email in your mail client with the
module name and item pre-filled in the subject line. You add
your comment and send. Emails route automatically to a
dedicated Meridian Feedback folder via Outlook rule.
An administrator reviews the folder periodically and
consolidates feedback manually.

WHAT YOU NEED TO DO:
Write your comment. Hit send. That's it.

WHAT HAPPENS NEXT:
The module owner reviews submissions on a defined cadence
(target: monthly). Accepted changes are incorporated into
the next version of the relevant module. You will see a
version number update in the footer of each module.

LIMITATIONS:
- No aggregated view for reviewers without manual work
- Submitter has no visibility into whether feedback was received
- No threading or discussion between reviewers
- Suitable for low-volume feedback during early prototype phase

---

## TIER 2 — Power Automate + Shared Repository
### Status: Requires Power Automate access (typically included
### in M365 license). Low IT lift — may be self-service.

HOW IT WORKS:
Speech bubble emails continue as in Tier 1, but a Power
Automate flow monitors the Meridian Feedback inbox and
automatically parses each submission. Module name and item
are extracted from the subject line. A structured row is
appended to a shared Excel file or SharePoint List with
columns for: timestamp, submitter, module, item reference,
and comment body. A notification is posted to a designated
Teams channel so the review team sees submissions in
real time.

WHAT YOU NEED TO DO:
Same as Tier 1 — write your comment, hit send.

WHAT ADMINISTRATORS SEE:
A shared spreadsheet or SharePoint List, filterable by
module, date, and review status. Your boss and designated
reviewers have read access at all times. No manual
aggregation required.

UPGRADE PATH FROM TIER 1:
One Power Automate flow connecting Outlook to SharePoint.
Estimated setup time with IT support: half a day.
Can be built against the Cloudflare prototype as a spec
before enterprise deployment.

LIMITATIONS:
- Feedback still arrives as unstructured email text
- No in-app confirmation to submitter
- Review and discussion still happen outside the system
- Version control is manual

---

## TIER 3 — Microsoft Forms + SharePoint + Planner
### Status: Requires IT involvement. Standard M365 stack.
### Recommended architecture for enterprise deployment.

HOW IT WORKS:
Speech bubble opens a Microsoft Form (not an email) with
structured fields: module name (pre-filled), item reference
(pre-filled), comment type (factual correction / clinical
disagreement / suggested addition / other), comment text,
and optional submitter name. Submission triggers a Power
Automate flow that: creates a SharePoint List item with
all fields, creates a Planner task in the Meridian Feedback
plan under the relevant module bucket, and posts a Teams
notification to the review channel.

WHAT REVIEWERS SEE:
A Planner kanban board with one column per module. Each
piece of feedback is a card. Cards move across columns:
Submitted → Under Review → Accepted → Incorporated →
Deferred. Your boss and designated reviewers can comment
on cards, assign them, set due dates, and track resolution
without leaving Teams.

WHAT HAPPENS TO ACCEPTED CHANGES:
A Power Automate flow generates a Word document from all
Accepted items in the SharePoint List, structured by module
with item-level comments. This document is the update spec
passed to the development workflow to revise Meridian
content. Version history is maintained in SharePoint.

UPGRADE PATH FROM TIER 2:
Replace mailto links with Microsoft Forms links.
Add Planner integration to existing Power Automate flow.
Estimated additional setup time: half a day.

LIMITATIONS:
- Requires login for form submission (M365 account)
- Planner visibility limited to licensed users
- Still a periodic review cycle, not continuous

---

## TIER 4 — Continuous Intelligence Platform
### Status: Reach objective. Requires development investment
### and IT partnership. This is the long-term vision.

### COMPONENT A — Continuous Provider Feedback Loop
Speech bubbles remain but now write directly to a
structured database. Submissions are timestamped, tagged
to specific content versions, and visible to submitters
with a status indicator (Received / Under Review /
Incorporated / Deferred with reason). High-frequency
feedback on a specific item surfaces automatically as
a priority signal — if twelve providers flag the same
bullet in the same month, the system flags it for
expedited review without anyone having to notice manually.
Review cycles shift from periodic to rolling. A monthly
Meridian review meeting works from a live dashboard
rather than a pile of emails.

### COMPONENT B — Meridian Chatbot
A conversational interface available within the app.
Providers type natural language questions and receive
answers grounded exclusively in Meridian content plus
a curated corpus of authoritative clinical sources.
The chatbot does not answer general medical questions —
it answers questions about our institutional approach.
Example interactions:
- "What do I document when I inherit a patient on
  opiates and benzos?"
- "My CKD patient's cystatin C eGFR is 28. What
  do I do today?"
- "What's the e-consult ask for unexplained anemia?"
The chatbot cites the specific Meridian module and
item that supports each answer. When the question
falls outside Meridian's scope, it says so explicitly
and directs to the appropriate external resource.
It does not hallucinate institutional policy.

### COMPONENT C — Curated External Knowledge Links
Each module item and FAQ answer can carry optional
external reference links, maintained by the module
owner and reviewed on a defined cadence. Categories:
- Guidelines: KDIGO, CDC, APA, ACR, ASH — primary
  society guidelines for each clinical domain
- Evidence: key trials cited in framework decisions
  (SPRINT for CKD BP target, CDC 2022 for opioid MME
  thresholds, etc.)
- Tools: calculators, staging systems, validated
  scales (CKD-EPI calculator, MME calculator,
  GAD-7 scoring)
- Patient resources: plain-language materials
  providers can share at point of care
Links are versioned — when a guideline is updated,
the link owner is notified and the reference is
reviewed before the next module version publishes.

### COMPONENT D — Chatbot Web Retrieval
For questions at the edge of the curated corpus,
the chatbot can fetch current information from
pre-approved external sources — society guideline
pages, FDA drug safety communications, CDC clinical
guidance — and synthesize an answer that combines
Meridian's institutional position with the latest
external evidence. The approved source list is
maintained by the module owner and medical director.
The chatbot never fetches from unapproved sources
and always distinguishes between institutional
policy and external reference.

### COMPONENT E — Version Control and Audit Trail
Every change to Meridian content is tracked with:
author, date, source feedback item(s) that drove
the change, reviewer who approved, and prior version
preserved for reference. Providers can see when
any item was last reviewed and what changed.
Leadership can demonstrate to regulators or
accreditors that the framework is actively
maintained with a documented review process.
This transforms Meridian from a reference tool
into an auditable clinical governance artifact.

### COMPONENT F — Analytics Layer
Aggregate, de-identified data on which modules
are accessed most, which items generate the most
feedback, which FAQ questions are opened most
frequently, and what chatbot questions are asked
most often. This data answers questions like:
- Which clinical area has the most provider
  uncertainty right now?
- Which module items are generating the most
  disagreement?
- Are providers actually using this at point of care
  or only during onboarding?
Analytics inform both content priorities and the
case for continued investment in the platform.

---

### GOVERNANCE PRINCIPLES (ALL TIERS)

CONTENT OWNERSHIP:
Each clinical module has a named owner responsible
for review cadence and accuracy. Module owner is
the first reviewer of all feedback for that domain.
Medical director approval required for any change
that modifies a clinical threshold or escalation
criterion.

FEEDBACK DESTINATION:
Feedback that arrives without a response is worse
than no feedback mechanism at all. Every submission
receives at minimum an automated acknowledgment.
Substantive responses to accepted or deferred items
are provided on the module review cadence.

VERSION DISCIPLINE:
Footer version numbers are updated with every
content change. Major changes (new module, revised
clinical threshold) increment the first digit.
Minor changes (clarified language, added FAQ)
increment the second. Providers can always see
what version they are reading.

STABILITY BEFORE EXPANSION:
New modules are not added until existing modules
have completed at least one full feedback cycle.
A framework that grows faster than it can be
reviewed loses credibility.

---

### FOOTER
Version: v0.1
Org: Crystal Run Healthcare
Note: For internal use only. This architecture document
is itself subject to the feedback process it describes.
