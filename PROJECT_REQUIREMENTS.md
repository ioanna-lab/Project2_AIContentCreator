# PROJECT_REQUIREMENTS.md
## AI Content Creator — Personal Brand Engine

**Course:** ACFT0520 — Module 2
**Student:** Ioanna Renta
**Duration:** 2 weeks
**Board:** ACFT0520 - Project 2 - Ioanna
**Board URL:** https://trello.com/b/kteKFdzb/treloforleadership

---

## 1. Project Summary

| Field | Detail |
|-------|--------|
| **Project name** | AI Content Creator — Personal Brand Engine |
| **Problem** | Generic AI tools produce homogenised content that lacks personal voice, specific evidence, and authentic positioning. Senior professionals need content that reflects their actual experience. |
| **Target user** | Ioanna Renta (Week 1–2 MVP); any executive or consultant (future white-label version) |
| **Success criteria** | Generated content is clearly distinguishable from generic ChatGPT output; all content references specific outcomes, named frameworks, and real experiences; pipeline runs end-to-end |

---

## 2. Input / Output / Databases

### 2.1 Input

The system accepts the following inputs depending on content type:

| Input | Content Type | Description |
|-------|-------------|-------------|
| Topic string | LinkedIn post | Free-text topic or angle |
| Tone selector | LinkedIn post | thought_leadership / personal_story / industry_observation |
| Length selector | Executive bio | short (100w) / medium (250w) / long (500w) |
| Purpose selector | Executive bio | general / speaking / board / job_application |
| News item text | AI commentary | Pasted headline or summary from any news source |
| Source name | AI commentary | Optional — e.g. "Hacker News", "TechCrunch" |
| Framework name | Leadership signature | e.g. "QMI", "Engineering Manifesto", "60/40 model" |
| Format selector | Leadership signature | explanation / linkedin_post / speaking_abstract |
| Live HN feed | AI commentary (Week 2) | Automatic — fetched from HackerNews API by topic |

### 2.2 Output

| Output | Format | Description |
|--------|--------|-------------|
| LinkedIn post | Plain text | 150–250 word post in Ioanna's voice, ready to paste |
| Executive bio | Plain text | Role-appropriate bio in third person |
| AI news commentary | Plain text | 150–200 word personal take on a news item |
| Leadership signature | Plain text | Framework explanation, LinkedIn post, or speaking abstract |
| Saved content file | Markdown (.md) | All outputs saved to output/ with timestamp in filename |
| Cost summary | Console print | Total tokens and USD spent per session |
| Session log | content_creator.log | Full DEBUG-level audit trail |

### 2.3 Primary Knowledge Base
**Location:** `knowledge_base/primary/`
These are Ioanna's own documents — the foundation of content uniqueness.

| File | Content | Purpose |
|------|---------|---------|
| `bio.md` | Career story, short/medium/long bios | Background for all content types |
| `leadership_philosophy.md` | QMI, Engineering Manifesto, 60/40 model, values | Leadership signature and thought leadership |
| `case_studies.md` | AUDI A8, DH QMI, sennder incidents, ML outcomes | Specific proof points and quantified outcomes |
| `positioning.md` | Target roles, voice guidelines, brand tone | Ensures all content stays on-brand |

**Update policy:** Update whenever career story, frameworks, or positioning evolves.

### 2.4 Secondary Knowledge Base
**Location:** `knowledge_base/secondary/`
Industry context that positions Ioanna's experience within broader market trends.

| File | Content | Purpose |
|------|---------|---------|
| `ai_trends.md` | AI adoption in engineering orgs, governance gap, platform trends | Grounds AI commentary in market reality |
| `cto_market.md` | VP/CTO compensation, hiring criteria, fractional market | Informs positioning and career-focused posts |

**Update policy:** Refresh quarterly or when significant market shifts occur.

---

## 3. Scope

### 3.1 In Scope (MVP)

- [x] Document processing — ingest and parse all markdown from both knowledge bases
- [x] Primary knowledge base — bio, leadership philosophy, case studies, positioning
- [x] Secondary knowledge base — AI trends, CTO market
- [x] Context assembly — select relevant documents per content type
- [x] OpenAI API integration — GPT-4o-mini with rate limiting and cost tracking
- [x] Prompt template: LinkedIn post
- [x] Prompt template: Executive bio
- [x] Prompt template: AI commentary
- [x] Prompt template: Leadership signature
- [x] Content pipeline — orchestration of all content types
- [x] CLI interface — interactive menu
- [x] Output saving — generated content as markdown files
- [x] Cost tracking — per-session token and USD summary
- [x] Trello integration — automated board setup via Trello API
- [ ] HackerNews API — live AI news feed (Week 2)
- [ ] Uniqueness comparison documentation (Week 2)
- [ ] Prompt iteration based on Week 1 testing (Week 2)

### 3.2 Out of Scope

| Item | Reason |
|------|--------|
| Vector databases / full RAG | Not required for MVP; markdown → prompt → LLM is sufficient |
| Automated LinkedIn publishing | Requires OAuth; adds complexity without proportional value |
| Multi-user / white-label frontend | Architecture supports it; deferred post-project |
| Analytics and performance tracking | No feedback loop in scope for 2-week project |
| Mobile interface | CLI + future Gradio UI is sufficient |
| Fine-tuning / custom model training | Out of scope for this module |

---

## 4. Functional Requirements

| ID | Requirement | Acceptance Criteria | Priority | Status |
|----|-------------|---------------------|----------|--------|
| FR-001 | Ingest primary knowledge base | All 4 markdown files load without error | Must Have | ✅ Done |
| FR-002 | Ingest secondary knowledge base | Both markdown files load without error | Must Have | ✅ Done |
| FR-003 | Context assembly per content type | Returns relevant docs concatenated for any content_type string | Must Have | ✅ Done |
| FR-004 | OpenAI API generates content | Given prompts, LLM returns response string; cost tracked | Must Have | ✅ Done |
| FR-005 | LinkedIn post — unique output | Generated post references specific Ioanna data points, not generic claims | Must Have | ✅ Done |
| FR-006 | Executive bio — purpose-appropriate | Bio length and emphasis match requested purpose | Must Have | ✅ Done |
| FR-007 | AI commentary — grounded in experience | Commentary references at least one Ioanna framework or case study | Must Have | ✅ Done |
| FR-008 | Leadership signature — real framework | Output explains framework with origin, problem solved, and outcome | Must Have | ✅ Done |
| FR-009 | Cost tracking per session | Cost summary shows total tokens and USD after session | Must Have | ✅ Done |
| FR-010 | Output saved to file | Markdown file exists in output/ with timestamp after generation | Must Have | ✅ Done |
| FR-011 | HackerNews live news feed | Given topic, returns top N relevant HN stories | Should Have | ⬜ Week 2 |
| FR-012 | Uniqueness comparison | Side-by-side showing system vs generic ChatGPT for same prompt | Must Have | ⬜ Week 2 |
| FR-013 | Trello board auto-setup | trello_manager.py setup creates all columns and cards | Should Have | ✅ Done |

---

## 5. Backlog & Priority

### Priority 1 — Foundation (Week 1, Days 1–2) — COMPLETE
| # | Task | Requirement | Status |
|---|------|-------------|--------|
| 1 | knowledge_base/primary/ — 4 markdown files | FR-001 | ✅ Done |
| 2 | knowledge_base/secondary/ — 2 markdown files | FR-002 | ✅ Done |
| 3 | document_processor.py | FR-003 | ✅ Done |
| 4 | llm_integration.py | FR-004 | ✅ Done |
| 5 | .env, requirements.txt, .gitignore | — | ✅ Done |
| 6 | PROJECT_REQUIREMENTS.md | — | ✅ Done |

### Priority 2 — Core Pipeline (Week 1, Days 2–3) — COMPLETE
| # | Task | Requirement | Status |
|---|------|-------------|--------|
| 7 | prompt_templates.py — all 4 templates | FR-005–008 | ✅ Done |
| 8 | content_pipeline.py | FR-009, FR-010 | ✅ Done |
| 9 | main.py — CLI | — | ✅ Done |
| 10 | trello_manager.py | FR-013 | ✅ Done |
| 11 | README.md | — | ✅ Done |

### Priority 3 — Enhancement (Week 2, Days 1–2)
| # | Task | Requirement | Status |
|---|------|-------------|--------|
| 12 | HackerNews API integration | FR-011 | ⬜ To Do |
| 13 | Additional free news sources | FR-011 | ⬜ To Do |
| 14 | Prompt refinement based on Week 1 testing | FR-005–008 | ⬜ To Do |

### Priority 4 — Delivery (Week 2, Days 3–4)
| # | Task | Requirement | Status |
|---|------|-------------|--------|
| 15 | Uniqueness comparison documentation | FR-012 | ⬜ To Do |
| 16 | README final polish | — | ⬜ To Do |
| 17 | Demo preparation | — | ⬜ To Do |
| 18 | Kanban screenshots (planning, midpoint, final) | — | ⬜ To Do |

---

## 6. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| **Reliability** | Pipeline handles missing markdown files gracefully (log warning, continue) |
| **Privacy** | All API keys in .env, never committed; .gitignore enforced |
| **Maintainability** | Each module has single responsibility; new content types added by one template function + one pipeline method |
| **Usability** | CLI menu is self-explanatory; first-time user generates content within 5 minutes of setup |
| **Cost control** | Cost tracker logs every API call; session summary printed on exit |
| **Uniqueness** | Every output must pass: "Could generic AI have written this without Ioanna's specific background?" |

---

## 7. Kanban / Project Management

- **Board name:** ACFT0520 - Project 2 - Ioanna
- **Board URL:** https://trello.com/b/kteKFdzb/treloforleadership
- **Workflow:** Backlog → This Week → In Progress [WIP: 2] → Review → Done
- **WIP limit:** Maximum 2 cards In Progress at any time
- **Definition of Done:**
  - Code committed to GitHub
  - Tested manually (python module.py passes)
  - Output file generated if applicable
  - README updated if applicable
  - Prompt tracking log updated

| Screenshot | When | Filename |
|------------|------|----------|
| Planning | After initial board setup | p2-kanban-planning.png |
| Midpoint | End of Week 1 | p2-kanban-midpoint.png |
| Final | Before submission | p2-kanban-final.png |

---

## 8. AI Coding-Agent Rules

- **Agent:** Claude (claude.ai)
- **Allowed:** Generate modules, suggest architecture, write KB content, write templates, debug, refactor
- **Not allowed:** Access real API keys, commit code directly, make deployments
- **Human review:** Every generated module read line by line, tested manually, adjusted before commit
- **Secret protection:** .env in .gitignore; only .env.example with placeholders committed

---

## 9. Prompt Tracking Log

| Date | Tool | Prompt Goal | Prompt Summary | Output Used? | Human Review Notes | Commit |
|------|------|-------------|----------------|--------------|--------------------|--------|
| 2026-05-XX | Claude | Project architecture | Designed full project structure for personal brand content creator | Yes | Adjusted context assembly to be content-type-specific | Initial |
| 2026-05-XX | Claude | bio.md | Wrote bio markdown using Ioanna's real background | Yes | Verified all career facts and numbers | KB |
| 2026-05-XX | Claude | leadership_philosophy.md | Documented QMI, Manifesto, 60/40 model from real experience | Yes | Confirmed framework descriptions match actual implementations | KB |
| 2026-05-XX | Claude | case_studies.md | Wrote case studies with quantified outcomes | Yes | Cross-checked all numbers (P1 incidents, ML %, migration timeline) | KB |
| 2026-05-XX | Claude | prompt_templates.py | Created templates for unique evidence-based content | Partially | Added uniqueness test; adjusted tone guidelines | Templates |
| 2026-05-XX | Claude | content_pipeline.py | Built orchestration layer | Yes | Reviewed temperature settings; adjusted max_tokens | Pipeline |
| 2026-05-XX | Claude | trello_manager.py | Built Trello API integration for board auto-setup | Yes | Verified all FR IDs mapped to correct cards | Trello |
| 2026-05-XX | Claude | PROJECT_REQUIREMENTS.md | Wrote comprehensive requirements covering all 6 areas | Yes | Reviewed all scope decisions and backlog priorities | Requirements |

---

## 10. Change Log

| Date | Change | Why | Approved By |
|------|--------|-----|-------------|
| 2026-05-XX | RAG/vector store moved Out of Scope | Markdown → prompt → LLM sufficient for 2-week MVP | Ioanna |
| 2026-05-XX | HackerNews moved to Week 2 | Core pipeline takes priority in Week 1 | Ioanna |
| 2026-05-XX | Trello integration added to In Scope | Demonstrates API integration beyond LLM; adds PM value | Ioanna |
