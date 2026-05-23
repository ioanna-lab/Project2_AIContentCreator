# AI Content Creator — Personal Brand Engine

A content generation system that produces unique, evidence-based personal brand content grounded in a real knowledge base — not generic AI output.

Built for Ioanna Renta (VP Engineering / CTO consultant) as Week 1 MVP. Designed to be extended to a white-label consultancy tool.

## What It Does

Reads two knowledge bases (personal background + industry research), assembles the right context for each content type, and generates content that could only have been written by someone with Ioanna's specific background.

**Pipeline:**
```
Knowledge Base (markdown) → Document Processor → Context Assembly
→ Prompt Template → OpenAI LLM → Formatted Output → Saved File
```

## File Map

```
ai-content-creator/
├── knowledge_base/
│   ├── primary/                  # Personal brand documents
│   │   ├── bio.md                # Career story and biography
│   │   ├── leadership_philosophy.md  # Frameworks and values
│   │   ├── case_studies.md       # Proof points and outcomes
│   │   └── positioning.md        # Target roles and voice guidelines
│   └── secondary/                # Industry research
│       ├── ai_trends.md          # AI in engineering organisations
│       └── cto_market.md         # VP/CTO market landscape
├── src/
│   ├── document_processor.py     # Markdown ingestion and context assembly
│   ├── llm_integration.py        # OpenAI wrapper with cost tracking
│   ├── prompt_templates.py       # One template per content type
│   ├── content_pipeline.py       # Orchestration layer
│   └── main.py                   # CLI entry point
├── output/                       # Generated content (gitignored)
├── PROJECT_REQUIREMENTS.md       # Specs, Kanban links, prompt tracking
├── requirements.txt
├── .env.example
└── .gitignore
```

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create your `.env` file
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Run the application
```bash
cd src
python main.py
```

## Content Types (Week 1 MVP)

| # | Content Type | Description |
|---|---|---|
| 1 | LinkedIn post | Thought leadership post in Ioanna's voice |
| 2 | Executive bio | Short/medium/long bio for different purposes |
| 3 | AI news commentary | Personal take on AI/tech news grounded in real experience |
| 4 | Leadership signature | Explains QMI, Engineering Manifesto, or other frameworks |

## Why This Is Not Generic AI Content

Generic AI output:
> "Focus on clear communication and building a culture of psychological safety."

This system's output (grounded in knowledge base):
> "We had 20 P1 incidents a week. Within six months we had 2 a month. The fix wasn't technical — it was a post-mortem culture that was blameless but not consequence-free. Here's what changed."

The difference: specificity, evidence, and a point of view that only comes from real experience.

## Trello Board
Board name: `ACFT0520 - Project 2 - Ioanna`
[Add board URL here]

## Week 2 Additions (Coming)
- HackerNews API integration for live AI news feed
- Additional free news/blog sources
- Uniqueness comparison documentation
- Refined prompts based on Week 1 testing
