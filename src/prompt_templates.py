"""
Prompt Engineering Templates — Week 1 MVP.

Each template function returns a (system_prompt, user_prompt) tuple.
The system prompt sets Ioanna's voice and persona.
The user prompt injects knowledge base context and the specific request.

Design principle: templates are functions, not strings, so they can
receive dynamic inputs (news items, topics, length preferences) and
produce contextually relevant prompts every time.

Week 1 includes: LinkedIn post, Executive Bio
Week 2 will add: AI Commentary (with HackerNews), Leadership Signature
"""

# ── System prompt shared across all templates ─────────────────────────────────
# This is the foundation of uniqueness — it tells the LLM exactly whose
# voice to adopt and what makes that voice different from generic AI output.

IOANNA_SYSTEM_PROMPT = """You are writing content on behalf of Ioanna Renta, a VP of Engineering and technology executive with 20+ years of experience leading engineering transformations at companies including HERE Technologies, Delivery Hero, and sennder.

VOICE GUIDELINES:
- Direct and evidence-based: every claim backed by a specific number or named experience
- Confident but not arrogant: confidence comes from experience, not ego
- Warm but not soft: caring about people does not mean avoiding hard conversations
- Curious and specific: always prefer the concrete detail over the general principle

WHAT IOANNA SOUNDS LIKE:
- Uses specific numbers: "reduced from 20/week to 2/month" not "significantly improved"
- References real frameworks by name: QMI, Engineering Manifesto, 60/40 model
- Challenges conventional wisdom but with evidence, not just opinion
- Treats engineering culture as infrastructure, not as a soft concept

WHAT IOANNA DOES NOT SOUND LIKE:
- Generic leadership platitudes ("people are our greatest asset")
- Vague claims without evidence ("strong track record of delivery")
- AI-generated filler: no buzzwords without substance
- Humble-bragging disguised as storytelling

The knowledge base context provided contains Ioanna's actual background, frameworks, case studies, and positioning. Use it to ground every piece of content in her real experience."""


# ── Template 1: LinkedIn Post ─────────────────────────────────────────────────

def linkedin_post_template(
    context: str,
    topic: str,
    tone: str = "thought leadership",
) -> tuple[str, str]:
    """
    Generate a LinkedIn thought leadership post in Ioanna's voice.

    Args:
        context:  Assembled knowledge base context from document_processor
        topic:    The specific topic or angle for this post
        tone:     "thought leadership", "personal story", or "industry observation"

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system_prompt = IOANNA_SYSTEM_PROMPT

    user_prompt = f"""Using the knowledge base context below, write a LinkedIn post for Ioanna Renta on the following topic:

TOPIC: {topic}
TONE: {tone}

LINKEDIN FORMAT RULES:
- Start with a specific observation, counterintuitive claim, or concrete number — something that earns the "see more" click
- 4-6 short paragraphs, each doing one job
- Use line breaks generously — LinkedIn is not an essay platform
- End with a clear point of view or a genuine question (not a call to action)
- Total length: 150-250 words
- Do NOT use hashtags or emojis unless they serve a specific purpose
- Do NOT start with "I" as the first word

UNIQUENESS CHECK: Before finalising, ask yourself: could a generic AI have written this without knowing Ioanna's specific background? If yes, add a specific data point, named framework, or real situation from her career.

KNOWLEDGE BASE CONTEXT:
{context}

Write the LinkedIn post now:"""

    return system_prompt, user_prompt


# ── Template 2: Executive Bio ─────────────────────────────────────────────────

def executive_bio_template(
    context: str,
    length: str = "medium",
    purpose: str = "general",
) -> tuple[str, str]:
    """
    Generate an executive bio in Ioanna's voice.

    Args:
        context: Assembled knowledge base context
        length:  "short" (100w), "medium" (250w), or "long" (500w)
        purpose: "general", "speaking", "board", or "job_application"

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    length_guide = {
        "short":  "approximately 80-100 words",
        "medium": "approximately 200-250 words",
        "long":   "approximately 450-500 words",
    }

    purpose_guide = {
        "general":         "general professional profile",
        "speaking":        "conference speaker bio — emphasise thought leadership and speaking topics",
        "board":           "board/advisory bio — emphasise strategic impact and governance experience",
        "job_application": "executive job application — emphasise transformation track record and outcomes",
    }

    system_prompt = IOANNA_SYSTEM_PROMPT

    user_prompt = f"""Using the knowledge base context below, write an executive bio for Ioanna Renta.

LENGTH: {length_guide.get(length, length_guide['medium'])}
PURPOSE: {purpose_guide.get(purpose, purpose_guide['general'])}

BIO RULES:
- Written in third person
- Lead with the most relevant credential or achievement for the purpose
- Include at least two specific quantified outcomes (numbers, percentages, timeframes)
- Reference at least one named framework or methodology she created
- End with location and current focus
- Do NOT include generic leadership phrases — every sentence must earn its place
- The bio must be clearly identifiable as Ioanna's, not a generic executive profile

KNOWLEDGE BASE CONTEXT:
{context}

Write the executive bio now:"""

    return system_prompt, user_prompt


# ── Template 3: AI News Commentary (Week 1 placeholder, full in Week 2) ───────

def ai_commentary_template(
    context: str,
    news_item: str,
    source: str = "",
) -> tuple[str, str]:
    """
    Generate Ioanna's personal commentary on an AI/tech news item.

    This is the template that makes the news commentary content unique:
    the same news item filtered through Ioanna's specific experience and
    frameworks produces a completely different output than generic AI summary.

    Args:
        context:   Assembled knowledge base context
        news_item: The news headline, summary, or URL content to comment on
        source:    Optional source name (e.g. "Hacker News", "TechCrunch")

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    source_line = f"Source: {source}" if source else ""

    system_prompt = IOANNA_SYSTEM_PROMPT

    user_prompt = f"""Using the knowledge base context below, write Ioanna Renta's commentary on the following news item for LinkedIn.

NEWS ITEM:
{news_item}
{source_line}

COMMENTARY RULES:
- Start by connecting this news to something specific in Ioanna's experience or background
- Provide a point of view that only someone with her background could give
- Reference at least one of her frameworks, case studies, or real experiences
- Challenge or add nuance to the obvious interpretation of the news
- Length: 150-200 words
- Tone: informed practitioner, not tech journalist
- Do NOT just summarise the news — readers can read the original. Add a unique perspective.

UNIQUENESS TEST: Would this commentary make sense if written by someone without Ioanna's specific background? If yes, it is not unique enough. Ground it in her real experience.

KNOWLEDGE BASE CONTEXT:
{context}

Write the commentary now:"""

    return system_prompt, user_prompt


# ── Template 4: Leadership Signature Content ──────────────────────────────────

def leadership_signature_template(
    context: str,
    framework: str,
    format_type: str = "explanation",
) -> tuple[str, str]:
    """
    Generate content explaining one of Ioanna's signature frameworks.

    Args:
        context:     Assembled knowledge base context
        framework:   Name of the framework (e.g. "QMI", "Engineering Manifesto")
        format_type: "explanation", "linkedin_post", or "speaking_abstract"

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    format_guide = {
        "explanation":       "a clear explanation of the framework for someone encountering it for the first time",
        "linkedin_post":     "a LinkedIn post introducing the framework with the key insight and one concrete example",
        "speaking_abstract": "a speaking session abstract (150 words) for a tech leadership conference",
    }

    system_prompt = IOANNA_SYSTEM_PROMPT

    user_prompt = f"""Using the knowledge base context below, create content about Ioanna Renta's {framework} framework.

FORMAT: {format_guide.get(format_type, format_guide['explanation'])}

CONTENT RULES:
- Lead with the problem the framework solves, not the framework itself
- Include the specific context where it was created and the measurable outcome it produced
- Explain the key insight in one sentence that someone could remember and repeat
- Make it clear this came from real experience, not theory
- Do NOT make it sound like a management consulting framework — it should sound like a practitioner's solution

KNOWLEDGE BASE CONTEXT:
{context}

Write the content now:"""

    return system_prompt, user_prompt
