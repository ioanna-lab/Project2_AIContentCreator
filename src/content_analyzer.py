"""
Content Analyzer — Quality metrics for generated content.

Runs after every generation and produces a metrics dict covering:
- Basic stats (word count, sentence count, generation time)
- Vocabulary richness (unique word ratio, avg word length)
- Readability (Flesch Reading Ease — computed manually, no external lib)
- Specificity score (numbers, named entities, proper nouns)
- Personal reference count (KB-specific terms like QMI, sennder, etc.)
- Cosine similarity vs a generic ChatGPT-style baseline
- Content type label (for cross-tab comparison)

All metrics appended to output/quality_log.md after every generation.
This is the evidence file for the uniqueness comparison.
"""
import re
import math
import json
import logging
from datetime import datetime
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("content_analyzer")

OUTPUT_DIR   = Path(__file__).parent.parent / "output"
QUALITY_LOG  = OUTPUT_DIR / "quality_log.md"

# ── Generic baselines per content type ───────────────────────────────────────
# These are representative generic ChatGPT-style outputs used as the
# comparison baseline for cosine similarity. Low similarity = more unique.
GENERIC_BASELINES = {
    "linkedin_post": (
        "Leadership is about empowering your team to do their best work. "
        "Great leaders focus on clear communication, building trust, and creating "
        "a culture of psychological safety. When teams feel supported, they innovate "
        "and deliver outstanding results. Investing in your people is the most "
        "important thing you can do as a leader. Remember to celebrate wins, "
        "learn from failures, and always keep the human element at the center "
        "of your technical decisions."
    ),
    "executive_bio": (
        "Jane Smith is an experienced technology executive with over 15 years "
        "of experience leading engineering teams. She has a strong track record "
        "of delivering results and building high-performing organizations. "
        "Jane is passionate about technology, innovation, and developing talent. "
        "She holds advanced degrees and has worked at several leading companies "
        "in the technology sector."
    ),
    "ai_commentary": (
        "This is an interesting development in the AI space. The technology "
        "continues to evolve rapidly and organizations need to think carefully "
        "about how to adopt these tools responsibly. There are both opportunities "
        "and challenges to consider. Leaders should focus on building the right "
        "foundations and ensuring their teams are prepared for the changes ahead."
    ),
    "leadership_signature": (
        "This framework helps organizations improve their engineering practices "
        "by focusing on key dimensions of quality and performance. By measuring "
        "what matters and creating accountability, teams can continuously improve "
        "and deliver better outcomes for their customers and stakeholders."
    ),
}

# Terms that indicate personal KB grounding (specific to Ioanna's background)
PERSONAL_MARKERS = [
    "qmi", "engineering manifesto", "sennder", "delivery hero", "here technologies",
    "audi", "a8", "siemens", "unify", "60/40", "p1 incident", "mttr",
    "quality maturity", "team athena", "librechat", "mcp server",
    "blameless", "strangler fig", "regrettable attrition",
    "20 per week", "2 per month", "55 seconds", "5 seconds",
    "35%", "60%", "50%", "240", "150",
]


def count_syllables(word: str) -> int:
    """Estimate syllable count for a word (for Flesch score)."""
    word = word.lower().strip(".,!?;:")
    if len(word) <= 3:
        return 1
    count = 0
    vowels = "aeiouy"
    prev_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    # Adjust for silent e
    if word.endswith("e"):
        count -= 1
    return max(1, count)


def flesch_reading_ease(text: str) -> float:
    """
    Compute Flesch Reading Ease score (0-100, higher = easier).

    Formula: 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
    LinkedIn target: 60-70 (standard/fairly easy)
    """
    sentences = max(1, len(re.split(r"[.!?]+", text)))
    words     = re.findall(r"\b\w+\b", text)
    if not words:
        return 0.0
    total_syllables = sum(count_syllables(w) for w in words)
    asl  = len(words) / sentences        # average sentence length
    asw  = total_syllables / len(words)  # average syllables per word
    return round(206.835 - 1.015 * asl - 84.6 * asw, 1)


def vocabulary_richness(text: str) -> float:
    """
    Type-Token Ratio: unique words / total words.
    Higher = more varied vocabulary. Range: 0.0-1.0
    """
    words  = re.findall(r"\b\w+\b", text.lower())
    if not words:
        return 0.0
    return round(len(set(words)) / len(words), 3)


def specificity_score(text: str) -> int:
    """
    Count evidence of specificity: numbers, percentages, named proper nouns.
    Higher = more evidence-based content.
    """
    numbers     = len(re.findall(r"\b\d+(?:\.\d+)?(?:%|x|k|m|bn)?\b", text, re.IGNORECASE))
    percentages = len(re.findall(r"\d+%", text))
    # Capitalized words that aren't at sentence start (likely proper nouns)
    proper_nouns = len(re.findall(r"(?<!\. )(?<!\? )(?<!\! )\b[A-Z][a-z]{2,}\b", text))
    return numbers + percentages + proper_nouns


def personal_reference_count(text: str) -> int:
    """Count how many personal KB markers appear in the text."""
    text_lower = text.lower()
    return sum(1 for marker in PERSONAL_MARKERS if marker in text_lower)


def cosine_similarity_vs_generic(text: str, content_type: str) -> float:
    """
    Compute cosine similarity between generated text and a generic baseline.

    Lower score = more unique (less like generic AI output).
    Range: 0.0 (completely different) to 1.0 (identical).

    Args:
        text:         The generated content
        content_type: One of the pipeline content type strings

    Returns:
        Similarity score rounded to 3 decimal places
    """
    baseline = GENERIC_BASELINES.get(content_type, GENERIC_BASELINES["linkedin_post"])
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf      = vectorizer.fit_transform([text, baseline])
        similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return round(float(similarity), 3)
    except Exception as e:
        logger.warning("Cosine similarity failed: %s", e)
        return 0.0


def analyze(
    content: str,
    content_type: str,
    metadata: dict,
    generation_time_s: float,
    tone: str = "",
    web_sources_used: int = 0,
) -> dict:
    """
    Run all quality metrics on a piece of generated content.

    Args:
        content:           The generated text
        content_type:      e.g. "linkedin_post", "executive_bio"
        metadata:          The metadata dict from the pipeline result
        generation_time_s: How long generation took in seconds
        tone:              Tone used (for LinkedIn posts)
        web_sources_used:  Number of web sources fed into the prompt

    Returns:
        Dict of all metrics
    """
    words     = re.findall(r"\b\w+\b", content)
    sentences = max(1, len(re.split(r"[.!?]+", content.strip())))

    metrics = {
        # ── Identity ──────────────────────────────────────────────────────────
        "timestamp":          datetime.now().isoformat(),
        "content_type":       content_type,
        "tone":               tone or metadata.get("tone", ""),
        "metadata_summary":   json.dumps(metadata)[:120],

        # ── Basic stats ───────────────────────────────────────────────────────
        "word_count":         len(words),
        "sentence_count":     sentences,
        "char_count":         len(content),
        "avg_sentence_length": round(len(words) / sentences, 1),
        "generation_time_s":  round(generation_time_s, 2),

        # ── Vocabulary ────────────────────────────────────────────────────────
        "vocabulary_richness":  vocabulary_richness(content),
        "avg_word_length":      round(sum(len(w) for w in words) / max(len(words), 1), 2),

        # ── Readability ───────────────────────────────────────────────────────
        "flesch_reading_ease":  flesch_reading_ease(content),

        # ── Uniqueness signals ────────────────────────────────────────────────
        "specificity_score":       specificity_score(content),
        "personal_reference_count": personal_reference_count(content),
        "cosine_similarity_vs_generic": cosine_similarity_vs_generic(content, content_type),

        # ── Source grounding ──────────────────────────────────────────────────
        "web_sources_used":   web_sources_used,
        "kb_grounded":        personal_reference_count(content) > 0,
    }

    logger.info(
        "Analyzed %s: %d words, richness=%.2f, specificity=%d, "
        "cosine_vs_generic=%.3f, personal_refs=%d",
        content_type,
        metrics["word_count"],
        metrics["vocabulary_richness"],
        metrics["specificity_score"],
        metrics["cosine_similarity_vs_generic"],
        metrics["personal_reference_count"],
    )
    return metrics


def append_to_quality_log(metrics: dict) -> None:
    """
    Append one row to output/quality_log.md.
    Creates the file with a header if it doesn't exist yet.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Write header if file is new
    if not QUALITY_LOG.exists():
        with open(QUALITY_LOG, "w", encoding="utf-8") as f:
            f.write("# Content Quality Log\n\n")
            f.write(
                "| Timestamp | Type | Tone | Words | Sentences | "
                "Vocab Richness | Flesch | Specificity | "
                "Personal Refs | Cosine vs Generic | Web Sources | Time (s) |\n"
            )
            f.write(
                "|-----------|------|------|-------|-----------|"
                "---------------|--------|-------------|"
                "--------------|-------------------|-------------|----------|\n"
            )

    # Append one row
    with open(QUALITY_LOG, "a", encoding="utf-8") as f:
        f.write(
            f"| {metrics['timestamp'][:19]} "
            f"| {metrics['content_type']} "
            f"| {metrics['tone'] or '-'} "
            f"| {metrics['word_count']} "
            f"| {metrics['sentence_count']} "
            f"| {metrics['vocabulary_richness']:.3f} "
            f"| {metrics['flesch_reading_ease']} "
            f"| {metrics['specificity_score']} "
            f"| {metrics['personal_reference_count']} "
            f"| {metrics['cosine_similarity_vs_generic']:.3f} "
            f"| {metrics['web_sources_used']} "
            f"| {metrics['generation_time_s']} |\n"
        )

    logger.debug("Quality log updated: %s", QUALITY_LOG)


def format_metrics_for_display(metrics: dict) -> str:
    """
    Format metrics as a short readable summary for the Gradio UI.

    Args:
        metrics: Dict from analyze()

    Returns:
        Multi-line string for display in a Gradio textbox
    """
    # Cosine similarity interpretation
    sim = metrics["cosine_similarity_vs_generic"]
    if sim < 0.15:
        uniqueness = "🟢 Very unique"
    elif sim < 0.30:
        uniqueness = "🟡 Moderately unique"
    else:
        uniqueness = "🔴 Similar to generic AI"

    # Flesch interpretation
    flesch = metrics["flesch_reading_ease"]
    if flesch >= 70:
        readability = "Easy (great for LinkedIn)"
    elif flesch >= 50:
        readability = "Standard"
    else:
        readability = "Complex"

    return (
        f"📊 CONTENT QUALITY METRICS\n"
        f"{'─'*35}\n"
        f"Type:              {metrics['content_type']}\n"
        f"Tone:              {metrics['tone'] or '—'}\n"
        f"Words:             {metrics['word_count']}\n"
        f"Sentences:         {metrics['sentence_count']}\n"
        f"Avg sentence len:  {metrics['avg_sentence_length']} words\n"
        f"Vocabulary richness: {metrics['vocabulary_richness']:.1%}\n"
        f"Readability:       {flesch} ({readability})\n"
        f"Specificity score: {metrics['specificity_score']} (numbers/proper nouns)\n"
        f"Personal refs:     {metrics['personal_reference_count']} (KB grounding)\n"
        f"Web sources used:  {metrics['web_sources_used']}\n"
        f"Generation time:   {metrics['generation_time_s']}s\n"
        f"{'─'*35}\n"
        f"Uniqueness vs generic AI: {sim:.1%} similarity\n"
        f"→ {uniqueness}\n"
        f"(Saved to quality_log.md)"
    )


# ── Quick smoke test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s")

    sample = (
        "We had 20 P1 incidents a week at sennder. Within six months we had 2 a month. "
        "The fix wasn't technical — it was a post-mortem culture that was blameless "
        "but not consequence-free. Here's exactly what changed. "
        "The QMI framework gave us a shared language. 50% of the org adopted it voluntarily."
    )

    metrics = analyze(
        content=sample,
        content_type="linkedin_post",
        metadata={"topic": "incident reduction", "tone": "personal story"},
        generation_time_s=2.3,
        tone="personal story",
        web_sources_used=0,
    )

    print(format_metrics_for_display(metrics))
    append_to_quality_log(metrics)
    print(f"\nQuality log written to: {QUALITY_LOG}")
