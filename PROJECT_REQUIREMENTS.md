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
| **Success criteria** | Generated content is clearly distinguishable from generic ChatGPT output; all content references specific outcomes, named frameworks, and real experiences; pipeline runs end-to-end; uniqueness scores consistently below 15% cosine similarity vs generic AI |

---

## 2. Input / Output / Databases

### 2.1 Input

| Input | Content Type | Description |
|-------|-------------|-------------|
| Topic string | LinkedIn post | Free-text topic or angle |
| Tone selector | LinkedIn post | personal_story / industry_observation / thought_leadership |
| Length selector | Executive bio | short (100w) / medium (250w) / long (500w) |
| Purpose selector | Executive bio | general / speaking / board / job_application |
| Mode selector | AI commentary | story_summary / personal_commentary / multi_story_synthesis |
| News source toggle | AI commentary | Browse HackerNews / Search by Topic |
| HN topic filter | AI commentary | Optional keyword — blank returns top AI stories by score |
| Source checkboxes | AI commentary | HackerNews / Dev.to / TechCrunch / General Web |
| Max results slider | AI commentary | 3–10 results per fetch |
| Framework name | Leadership signature | e.g. "QMI", "Engineering Manifesto", "60/40 model" |
| Format selector | Leadership signature | explanation / linkedin_post / speaking_abstract |
| Category selector | KB management | Auto-routes entry to the correct KB file |
| Content textarea | KB management | New entry to append to the knowledge base |

### 2.2 Output

| Output | Format | Description |
|--------|--------|-------------|
| LinkedIn post | Plain text | 150–250 word post in Ioanna's voice, ready to paste |
| Executive bio | Plain text | Role-appropriate bio in third person |
| AI commentary | Plain text | Story summary / personal commentary / multi-story synthesis |
| Leadership signature | Plain text | Framework explanation, LinkedIn post, or speaking abstract |
| Saved content file | Markdown (.md) | All outputs saved to output/ with timestamp in filename |
| KB entry | Markdown append | New entry appended to the appropriate knowledge base file |
| Quality metrics | UI display | Uniqueness score, readability, personal refs, specificity |
| Cost summary | UI display + log | Tokens and USD per generation; session total |
| Quality log | quality_log.md | Full metrics table appended after every generation |
| Cost log | cost_log.md | Every generation: tokens, cost, metadata |

### 2.3 Primary Knowledge Base
**Location:** `knowledge_base/primary/`

| File | Content | Purpose |
|------|---------|---------|
| `bio.md` | Career story, short/medium/long bios | Background for all content types |
| `leadership_philosophy.md` | QMI, Engineering Manifesto, 60/40 model, values | Leadership signature and thought leadership |
| `case_studies.md` | AUDI A8, DH QMI, sennder incidents, ML outcomes, AI tooling | Specific proof points and quantified outcomes |
| `positioning.md` | Target roles, voice guidelines, brand tone | Ensures all content stays on-brand |

**Update policy:** Update whenever career story, frameworks, or positioning evolves. Use the KB Management tab in the Gradio UI or edit files directly — changes are available to the next generation immediately, no restart required.

### 2.4 Secondary Knowledge Base
**Location:** `knowledge_base/secondary/`

| File | Content | Purpose |
|------|---------|---------|
| `ai_trends.md` | AI adoption in engineering orgs, governance gap, platform trends | Grounds AI commentary in market reality |
| `cto_market.md` | VP/CTO compensation, hiring criteria, fractional market | Informs positioning and career-focused posts |

**Update policy:** Refresh quarterly or when significant market shifts occur. Secondary KB is used only in modes that explicitly request web or industry context.

---

## 3. Scope

### 3.1 In Scope (completed)

- [x] Document processing — ingest and parse all markdown from both knowledge bases
- [x] Primary knowledge base — bio, leadership philosophy, case studies, positioning
- [x] Secondary knowledge base — AI trends, CTO market
- [x] Context assembly — select relevant documents per content type
- [x] OpenAI API integration — GPT-4o-mini with rate limiting and cost tracking
- [x] Prompt template: LinkedIn post (3 tones, including web-grounded modes)
- [x] Prompt template: Executive bio (3 lengths × 4 purposes)
- [x] Prompt template: AI commentary (3 modes — redesigned Week 2)
- [x] Prompt template: Leadership signature
- [x] Content pipeline — orchestration of all content types
- [x] Gradio web UI — 6 tabs
- [x] Output saving — generated content as markdown files with timestamps
- [x] Cost tracking — per-session token and USD summary + cost_log.md
- [x] Content quality analysis — content_analyzer.py (uniqueness, readability, specificity)
- [x] HackerNews API — live AI news feed, topic-filtered or top-stories mode
- [x] Web researcher — multi-source search (HN Algolia, Dev.to, TechCrunch, InfoQ RSS)
- [x] Knowledge Base management — kb_manager.py, Save to KB button on every tab, Browse tab
- [x] Uniqueness comparison documentation (vs ChatGPT — LinkedIn and Bio)
- [x] Prompt refinement based on output testing — faithfulness rule, conditional KB anchoring
- [x] Trello integration — automated board setup via Trello API
- [x] README.md and requirements.txt

### 3.2 Out of Scope

| Item | Reason |
|------|--------|
| Vector databases / full RAG | Not required for MVP; markdown → prompt → LLM is sufficient for this KB size |
| Automated LinkedIn publishing | Requires OAuth; adds complexity without proportional value for 2-week project |
| Multi-user / white-label frontend | Architecture supports it (KB is a folder swap); deferred post-project |
| Analytics and performance tracking | No feedback loop in scope for 2-week project |
| Fine-tuning / custom model training | Out of scope for this module |
| Video demo | Replaced by in-app screenshots and comparison slides in presentation |

---

## 4. Functional Requirements

| ID | Requirement | Acceptance Criteria | Priority | Status |
|----|-------------|---------------------|----------|--------|
| FR-001 | Ingest primary knowledge base | All 4 markdown files load without error | Must Have | ✅ Done |
| FR-002 | Ingest secondary knowledge base | Both markdown files load without error | Must Have | ✅ Done |
| FR-003 | Context assembly per content type | Returns relevant docs concatenated for any content_type string | Must Have | ✅ Done |
| FR-004 | OpenAI API generates content | Given prompts, LLM returns response string; cost tracked | Must Have | ✅ Done |
| FR-005 | LinkedIn post — unique output | Generated post references specific data points; cosine similarity vs generic < 15% | Must Have | ✅ Done |
| FR-006 | Executive bio — purpose-appropriate | Bio length and emphasis match requested purpose; 6 variants available | Must Have | ✅ Done |
| FR-007 | AI commentary — mode-appropriate | Story summary: no forced KB refs; personal: KB only if genuine connection; synthesis: cross-story narrative | Must Have | ✅ Done |
| FR-008 | Leadership signature — real framework | Output explains framework with origin, problem solved, and quantified outcome | Must Have | ✅ Done |
| FR-009 | Cost tracking per session | Cost summary shows total tokens and USD after every generation and session | Must Have | ✅ Done |
| FR-010 | Output saved to file | Markdown file exists in output/ with timestamp after generation | Must Have | ✅ Done |
| FR-011 | HackerNews live news feed | Topic-filtered Algolia search or top AI stories; returns N stories in under 2 seconds | Should Have | ✅ Done |
| FR-012 | Uniqueness comparison | Side-by-side showing system vs generic ChatGPT for LinkedIn post and Executive Bio | Must Have | ✅ Done |
| FR-013 | Trello board auto-setup | trello_manager.py setup creates all columns and cards with FR IDs | Should Have | ✅ Done |
| FR-014 | AI Commentary — 3 modes | Three genuinely different prompt paths; no forced KB anchoring in summary/synthesis | Must Have | ✅ Done |
| FR-015 | Multi-source topic search | web_researcher.py searches HN + Dev.to + TechCrunch + InfoQ; max_results respected per source | Should Have | ✅ Done |
| FR-016 | Knowledge Base management | kb_manager.py: append to KB by category; read any file; changes available without restart | Should Have | ✅ Done |
| FR-017 | Gradio 6-tab web UI | All content types accessible via UI; KB management tab; Cost & Quality tab | Must Have | ✅ Done |
| FR-018 | Content quality metrics | Every generation produces uniqueness score, readability, specificity, personal refs; logged to quality_log.md | Should Have | ✅ Done |

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
| 9 | content_analyzer.py | FR-018 | ✅ Done |
| 10 | main.py — CLI | — | ✅ Done |
| 11 | trello_manager.py | FR-013 | ✅ Done |
| 12 | gradio_app.py — initial 5-tab UI | FR-017 | ✅ Done |

### Priority 3 — Enhancement (Week 2, Days 1–3) — COMPLETE
| # | Task | Requirement | Status |
|---|------|-------------|--------|
| 13 | hn_processor.py — Algolia API + topic filter | FR-011 | ✅ Done |
| 14 | web_researcher.py — multi-source search + max_results fix | FR-015 | ✅ Done |
| 15 | AI Commentary redesign — 3 modes, faithfulness rule | FR-007, FR-014 | ✅ Done |
| 16 | kb_manager.py — KB management layer | FR-016 | ✅ Done |
| 17 | gradio_app.py — expanded to 6 tabs, Save to KB, CheckboxGroup | FR-017 | ✅ Done |
| 18 | Prompt refinement — conditional KB anchoring across all templates | FR-005–008 | ✅ Done |

### Priority 4 — Delivery (Week 2, Days 3–4) — COMPLETE
| # | Task | Requirement | Status |
|---|------|-------------|--------|
| 19 | Uniqueness comparison (LinkedIn + Bio vs ChatGPT) | FR-012 | ✅ Done |
| 20 | README.md final polish | — | ✅ Done |
| 21 | requirements.txt verified against all modules | — | ✅ Done |
| 22 | Kanban screenshots (planning, midpoint, final) | — | ✅ Done |
| 23 | Presentation — 18 slides with demo evidence | — | ✅ Done |
| 24 | GitHub push — all src files, KB, output samples | — | ✅ Done |

---

## 6. Non-Functional Requirements

| Category | Requirement | Status |
|----------|-------------|--------|
| **Reliability** | Pipeline handles missing markdown files gracefully (log warning, continue) | ✅ Done |
| **Privacy** | All API keys in .env, never committed; .gitignore enforced | ✅ Done |
| **Maintainability** | Each module has single responsibility; new content types added by one template function + one pipeline method | ✅ Done |
| **Usability** | Gradio UI is self-explanatory; first-time user generates content within 5 minutes of setup | ✅ Done |
| **Cost control** | Cost tracker logs every API call; session summary shown inline; ~$0.002 for a full session | ✅ Done |
| **Uniqueness** | Every output must pass: "Could generic AI have written this without Ioanna's specific background?" Built into every prompt template. | ✅ Done |
| **Liveness** | AI Commentary sources live news in real time — not static KB content only | ✅ Done (Week 2) |
| **KB freshness** | New KB entries available to next generation without restart | ✅ Done (Week 2) |

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

| Screenshot | When | Filename |
|------------|------|----------|
| Planning | After initial board setup | p2-kanban-planning.png |
| Midpoint | End of Week 1 | p2-kanban-midpoint.png |
| Final | Before submission | p2-kanban-final.png |

---

## 8. AI Coding-Agent Rules

- **Agent:** Claude (claude.ai)
- **Allowed:** Generate modules, suggest architecture, write KB content, write templates, debug, refactor, iterate on UI/UX
- **Not allowed:** Access real API keys, commit code directly, make deployments
- **Human review:** Every generated module read line by line, tested manually, adjusted before commit
- **Secret protection:** .env in .gitignore; only .env.example with placeholders committed

---

## 9. Prompt Tracking Log

| Date | Tool | Prompt Goal | Prompt Summary | Output Used? | Human Review Notes | Commit |
|------|------|-------------|----------------|--------------|--------------------|--------|
| 2026-05-20 | Claude | Project architecture | Designed full project structure for personal brand content creator | Yes | Adjusted context assembly to be content-type-specific | Initial |
| 2026-05-20 | Claude | bio.md | Wrote bio markdown using Ioanna's real background | Yes | Verified all career facts and numbers | KB |
| 2026-05-20 | Claude | leadership_philosophy.md | Documented QMI, Manifesto, 60/40 model from real experience | Yes | Confirmed framework descriptions match actual implementations | KB |
| 2026-05-20 | Claude | case_studies.md | Wrote case studies with quantified outcomes | Yes | Cross-checked all numbers (P1 incidents, ML %, migration timeline) | KB |
| 2026-05-21 | Claude | prompt_templates.py | Created templates for unique evidence-based content | Partially | Added uniqueness test; adjusted tone guidelines | Templates |
| 2026-05-21 | Claude | content_pipeline.py | Built orchestration layer | Yes | Reviewed temperature settings; adjusted max_tokens | Pipeline |
| 2026-05-21 | Claude | content_analyzer.py | Built quality metrics: cosine similarity, Flesch (manual), specificity, personal refs | Yes | Verified Flesch formula; confirmed no external readability library needed | Analyzer |
| 2026-05-21 | Claude | trello_manager.py | Built Trello API integration for board auto-setup | Yes | Verified all FR IDs mapped to correct cards | Trello |
| 2026-05-21 | Claude | gradio_app.py (v1) | Built initial 5-tab Gradio UI | Yes | Tested all tabs; confirmed cost display and file save | UI |
| 2026-05-22 | Claude | PROJECT_REQUIREMENTS.md | Wrote comprehensive requirements covering all 6 areas | Yes | Reviewed all scope decisions and backlog priorities | Requirements |
| 2026-05-27 | Claude | AI Commentary redesign | Redesigned commentary tab: 3 modes (summary/personal/synthesis); faithfulness rule to prevent forced KB anchoring | Yes | Tested all 3 modes with same topic; confirmed QMI no longer appears in summary mode | Commentary |
| 2026-05-27 | Claude | web_researcher.py fix | Fixed max_results hardcoding bug — was 3/3/2/2 regardless of slider; now passes max_results to every source | Yes | Verified slider now returns requested count | WebResearcher |
| 2026-05-27 | Claude | hn_processor.py upgrade | Added optional topic filter to Browse HackerNews panel; topic search via Algolia keyword API | Yes | Tested with and without topic; confirmed fallback to top AI stories when empty | HN |
| 2026-05-28 | Claude | kb_manager.py | Built KB management layer: 6 categories, auto-routing, append with timestamp, read any file | Yes | Tested Save to KB from each tab; confirmed entries appear in next generation | KB Manager |
| 2026-05-28 | Claude | gradio_app.py (v2) | Expanded to 6 tabs: added KB Management tab, Save to KB accordion on every output tab, CheckboxGroup for search results with Select All/Clear | Yes | Fixed show_copy_button Gradio 6.x incompatibility; removed stale Source field from Commentary | UI v2 |
| 2026-05-28 | Claude | Search by Topic panel | Added topic-based multi-source search (HN Algolia, Dev.to, TechCrunch, General Web) to Commentary tab | Yes | Verified CheckboxGroup reliable across Gradio versions; confirmed Select All works | Search |
| 2026-05-29 | Claude | README.md | Wrote full project README: architecture, setup, usage, quality metrics table, cost table, uniqueness comparison | Yes | Verified all install steps; confirmed file paths match actual structure | Docs |
| 2026-05-29 | Claude | Presentation (18 slides) | Built and iterated full project presentation: architecture, KB design, demo screenshots, ChatGPT comparison, design decisions, Week 1→2 timeline | Yes | Reviewed all slides; fixed overlapping content; added Technical Implementation 3×3 grid | Presentation |

---

## 10. Change Log

| Date | Change | Why | Approved By |
|------|--------|-----|-------------|
| 2026-05-20 | RAG/vector store moved Out of Scope | Markdown → prompt → LLM sufficient for 2-week MVP | Ioanna |
| 2026-05-20 | HackerNews moved to Week 2 | Core pipeline takes priority in Week 1 | Ioanna |
| 2026-05-21 | Trello integration added to In Scope | Demonstrates API integration beyond LLM; adds PM value | Ioanna |
| 2026-05-21 | Flesch readability implemented manually | content_analyzer.py computes syllables without external library; textstat removed from requirements | Ioanna |
| 2026-05-27 | AI Commentary single mode → 3 modes | Original mode forced KB anchoring regardless of relevance (MIT 2016 lecture → QMI reference); redesigned with faithfulness rule | Ioanna |
| 2026-05-27 | max_results bug fixed in web_researcher.py | Parameter was accepted but not passed to individual sources; hardcoded at 3/3/2/2 silently | Ioanna |
| 2026-05-28 | CLI interface → Gradio 6-tab web UI | Better demonstration of capabilities; supports multi-select, live feedback, KB browsing | Ioanna |
| 2026-05-28 | KB management added to In Scope | The ability to update the KB at any stage without restart is a core capability, not a nice-to-have | Ioanna |
| 2026-05-28 | gr.Dropdown(multiselect=True) → gr.CheckboxGroup | Dropdown expand arrow broken in Gradio 6.x; CheckboxGroup is reliable and supports Select All pattern | Ioanna |
| 2026-05-28 | Source (optional) field removed from Commentary | Source is now embedded in structured result format; field had no effect on output | Ioanna |
| 2026-05-29 | textstat removed from requirements.txt | Not used — Flesch score implemented manually in content_analyzer.py | Ioanna |
