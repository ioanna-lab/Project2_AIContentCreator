# 🎯 AI Content Creator — Personal Brand Engine

> *Not generic AI — your voice, your frameworks, your proof points.*

**Ironhack AI Engineering · Module 2 Project**
Built by [Ioanna Renta](https://github.com/ioannarenta) · VP Engineering · Berlin

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Gradio](https://img.shields.io/badge/UI-Gradio-orange)](https://gradio.app/)
[![GPT-4o-mini](https://img.shields.io/badge/LLM-GPT--4o--mini-green)](https://openai.com/)
[![Trello Board](https://img.shields.io/badge/Trello-Project%20Board-blue)](https://trello.com/b/kteKFdzb)

---

## The Problem

Generic AI produces generic content.

Ask any LLM to write a LinkedIn post about engineering culture and you get:
> *"Build a culture of psychological safety and focus on clear communication."*

Ask this engine the same question and you get:
> *"50% of the org voluntarily adopted QMI within six months. Voluntary adoption is the only honest signal — if people use it because they fear consequences, the data is corrupted."*

The difference: **specificity, evidence, and a point of view that only comes from real experience.**

This engine is grounded in a structured knowledge base of real career outcomes, frameworks, and proof points. Every generation is measured for uniqueness against generic AI output. Similarity scores consistently land at 6–13% — meaning 87–94% of the content could not have been written without knowing the specific background it draws from.

---

## What It Does

A **6-tab Gradio web application** that generates four types of content — each grounded in a personal knowledge base and measured for quality on every generation.

| Tab | Output | Key feature |
|---|---|---|
| 💼 LinkedIn Post | Thought leadership post | 3 tones: personal story / industry observation / thought leadership |
| 👤 Executive Bio | Professional bio | 6 variants: 3 lengths × 4 purposes (general / speaking / board / job application) |
| 🤖 AI Commentary | Commentary on tech news | 3 modes: story summary / personal commentary / multi-story synthesis |
| 🏆 Leadership Signature | Framework explainer | QMI, Engineering Manifesto, 60/40 model |
| 📚 Knowledge Base | KB management | Add entries, browse files, auto-routing to the right file |
| 💰 Cost & Quality | Session metrics | Token count, cost per generation, quality log |

---

## Architecture

```
knowledge_base/
├── primary/          ← Personal KB (bio, case studies, philosophy, positioning)
└── secondary/        ← Research layer (AI trends, CTO market)

src/
├── document_processor.py   ← Reads KB, assembles context subset per content type
├── prompt_templates.py     ← 5 template functions, shared voice system prompt
├── content_pipeline.py     ← Orchestrates all modules, saves outputs, logs costs
├── llm_integration.py      ← OpenAI GPT-4o-mini wrapper, cost tracking
├── web_researcher.py       ← Multi-source web search (HN, Dev.to, TechCrunch, RSS)
├── hn_processor.py         ← HackerNews Algolia API, topic filter or top stories
├── kb_manager.py           ← KB read/write, 6 categories auto-route to right file
├── content_analyzer.py     ← Uniqueness scoring, readability, quality metrics
├── trello_manager.py       ← Trello REST API, project management integration
└── gradio_app.py           ← 6-tab web UI, all handlers and wiring

output/                     ← All generated content saved as .md with timestamps
├── cost_log.md             ← Every generation: tokens, cost, metadata
└── quality_log.md          ← Uniqueness scores, readability, personal ref counts
```

**Design principle:** The knowledge base IS the product. The LLM is the rendering engine.

---

## Knowledge Base Structure

```
knowledge_base/
├── primary/
│   ├── bio.md                    ← Career story, short/medium/long bios
│   ├── case_studies.md           ← AUDI A8, Delivery Hero ML, sennder incidents
│   ├── leadership_philosophy.md  ← QMI, Engineering Manifesto, 60/40 model
│   └── positioning.md            ← Target roles, voice guidelines, brand tone
└── secondary/
    ├── ai_trends.md              ← AI adoption in engineering orgs, governance gap
    └── cto_market.md             ← VP/CTO compensation, hiring criteria
```

The KB is Markdown. It reads fresh on every generation — adding a new entry is immediately available to the next call, no restart required. Use the **Knowledge Base tab** in the UI, or edit the files directly.

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/ioannarenta/Project2_AIContentCreator
cd Project2_AIContentCreator
pip install -r requirements.txt
```

### 2. Set your OpenAI API key

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your-key-here
```

Or export it in your shell:

```bash
export OPENAI_API_KEY=your-key-here
```

### 3. Run

```bash
cd src
python gradio_app.py
```

Then open [http://127.0.0.1:7860](http://127.0.0.1:7860) in your browser.

---

## Usage

### LinkedIn Post

1. Enter a topic or angle
2. Select tone: **Personal Story** (KB only), **Industry Observation** (web search), or **Thought Leadership** (web + KB hybrid)
3. For web-grounded tones, click **Fetch industry context** first
4. Click **Generate LinkedIn Post**

### AI Commentary

1. Choose a generation mode:
   - **📰 Story Summary** — faithful overview, no personal references forced
   - **💬 Personal Commentary** — summary + KB angle only if genuinely relevant
   - **🔄 Multi-Story Synthesis** — cross-story trend narrative across multiple items
2. Choose a news source:
   - **Browse HackerNews** — top AI stories by score, or filter by topic
   - **Search by Topic** — searches HN + Dev.to + TechCrunch + General Web
3. Select stories (multi-select / Select All supported)
4. Click **Generate Commentary**

### Knowledge Base Management

- **Add New Entry** — select category (auto-routes to the right file), paste content, save
- **Browse** — read any KB file inline, switch primary/secondary, refresh after edits
- **Save to KB from any tab** — every output tab has a 💾 Save to KB button that pre-fills from the generated output

---

## Quality Metrics

Every generation produces a quality report:

| Metric | What it measures |
|---|---|
| **Uniqueness vs generic AI** | Cosine similarity against a generic LLM response to the same prompt. Lower = more unique. |
| **Personal refs** | Count of KB-grounded references (names, companies, specific numbers). |
| **Specificity score** | Count of proper nouns and specific numbers. |
| **Vocabulary richness** | Type-token ratio — variety of words used. |
| **Readability** | Flesch reading ease score. |
| **Web sources used** | Number of live sources incorporated. |

Results are saved to `output/quality_log.md` after every generation.

---

## Cost

GPT-4o-mini at $0.15/M input tokens, $0.60/M output tokens.

| Content type | Typical cost |
|---|---|
| LinkedIn Post | ~$0.0003 |
| Executive Bio (short) | ~$0.0008 |
| AI Commentary | ~$0.0009 |
| Full 4-type session | ~$0.002 |

Cost is shown inline after every generation and logged to `output/cost_log.md`.

---

## Uniqueness: This Engine vs ChatGPT

Same prompt, same topic. ChatGPT produced an 800-word instructional essay with no voice, no specific proof points, and zero personal references — not LinkedIn-appropriate without a full rewrite.

This engine produced three genuinely different, platform-ready posts — each with distinct angle, real grounding, and under 10 seconds.

| Dimension | This engine | ChatGPT |
|---|---|---|
| Personal refs | 7–9 per post (KB grounded) | 0 |
| Proof points | QMI, 20→2 incidents, 35% growth | Generic patterns |
| Uniqueness | 6–13% similarity ✅ | Baseline |
| LinkedIn-ready | ✅ Yes, as-is | ❌ Needs full rewrite |

---

## Project Management

Tracked on Trello: [trello.com/b/kteKFdzb](https://trello.com/b/kteKFdzb)

Built across two weeks:
- **Week 1** — KB structure, pipeline architecture, 4 content types, cost tracking, Gradio UI
- **Week 2** — AI Commentary redesign (3 modes), multi-source web search, KB management, uniqueness comparison, prompt refinement

---

## Course Context

**Ironhack AI Engineering Bootcamp · Module 2**
Focus: building production-ready AI applications with prompt engineering, knowledge base design, and real-world API integration.

---

*Built in Berlin · May 2026*
