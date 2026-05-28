"""
Content Pipeline — orchestration layer.

Connects document_processor → prompt_templates → llm_integration.
Now also integrates web_researcher (for web-grounded LinkedIn posts)
and content_analyzer (for quality metrics on every generation).

Every generation:
  1. Assembles context (KB and/or web)
  2. Builds prompt
  3. Calls LLM and times it
  4. Saves output to output/<type>_<timestamp>.md
  5. Appends to output/cost_log.md
  6. Runs quality analysis and appends to output/quality_log.md
"""
import time
import logging
import json
from datetime import datetime
from pathlib import Path

from document_processor import get_context_for_content_type
from prompt_templates import (
    linkedin_post_template,
    linkedin_industry_template,
    executive_bio_template,
    ai_commentary_template,
    leadership_signature_template,
)
from llm_integration import LLMClient
from web_researcher import WebResearcher
from content_analyzer import analyze, append_to_quality_log, format_metrics_for_display

logger    = logging.getLogger("content_pipeline")
OUTPUT_DIR = Path(__file__).parent.parent / "output"


class ContentPipeline:
    """
    Main content generation pipeline.

    Public methods return a result dict with:
      content, content_type, metadata, generated_at, model, metrics
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.llm        = LLMClient(model=model)
        self.researcher = WebResearcher()
        self.history    = []
        OUTPUT_DIR.mkdir(exist_ok=True)
        logger.info("ContentPipeline initialised")

    # ── Internal helper ───────────────────────────────────────────────────────

    def _generate_and_record(
        self,
        content_type: str,
        system_prompt: str,
        user_prompt: str,
        metadata: dict,
        temperature: float = 0.7,
        max_tokens: int = 1500,
        tone: str = "",
        web_sources_used: int = 0,
    ) -> dict:
        """Call LLM, run quality analysis, record result."""
        logger.info("Generating %s content...", content_type)

        start   = time.time()
        content = self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        elapsed = time.time() - start

        # Run quality analysis on every generation
        metrics = analyze(
            content=content,
            content_type=content_type,
            metadata=metadata,
            generation_time_s=elapsed,
            tone=tone,
            web_sources_used=web_sources_used,
        )
        append_to_quality_log(metrics)

        # Print cost inline
        cost = self.llm.cost_tracker.summary()
        print(
            f"\n💰 Cost: ${cost['average_cost']:.6f} | "
            f"Session total: ${cost['total_cost']:.4f} | "
            f"Tokens: {cost['total_tokens']:,}"
        )

        result = {
            "content_type": content_type,
            "content":      content,
            "metadata":     metadata,
            "generated_at": datetime.now().isoformat(),
            "model":        self.llm.model,
            "metrics":      metrics,
        }

        self.history.append(result)
        logger.info("✓ %s generated (%d chars, %.1fs)", content_type, len(content), elapsed)
        return result

    # ── Public pipeline methods ───────────────────────────────────────────────

    def generate_linkedin_post(
        self,
        topic: str,
        tone: str = "thought leadership",
    ) -> tuple[dict, str]:
        """
        Generate a LinkedIn post.

        For "industry observation" and "thought leadership" tones,
        fetches live web context first and shows what was found.

        Returns:
            Tuple of (result dict, web_sources_display string)
        """
        web_display    = ""
        web_sources_n  = 0

        if tone in ("industry observation", "thought leadership"):
            # Fetch live web context for these tones
            logger.info("Fetching web context for '%s' tone...", tone)
            web_results   = self.researcher.search(topic, max_results=5)
            web_display   = self.researcher.format_for_display(web_results)
            web_context   = self.researcher.format_for_prompt(web_results)
            web_sources_n = len(web_results)

            kb_context = get_context_for_content_type("linkedin") if tone == "thought leadership" else ""
            system_prompt, user_prompt = linkedin_industry_template(
                kb_context=kb_context,
                web_context=web_context,
                topic=topic,
                tone=tone,
            )
        else:
            # Personal story — KB only
            context = get_context_for_content_type("linkedin")
            system_prompt, user_prompt = linkedin_post_template(context, topic, tone)

        result = self._generate_and_record(
            content_type="linkedin_post",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata={"topic": topic, "tone": tone},
            temperature=0.8,
            max_tokens=400,
            tone=tone,
            web_sources_used=web_sources_n,
        )
        return result, web_display

    def generate_executive_bio(
        self,
        length: str = "medium",
        purpose: str = "general",
    ) -> dict:
        """Generate an executive bio."""
        context = get_context_for_content_type("bio")
        system_prompt, user_prompt = executive_bio_template(context, length, purpose)

        return self._generate_and_record(
            content_type="executive_bio",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata={"length": length, "purpose": purpose},
            temperature=0.5,
            max_tokens=800,
            tone=f"{length}/{purpose}",
        )

    def generate_ai_commentary(
        self,
        news_item: str,
        source: str = "",
        mode: str = "summary",
    ) -> dict:
        """
        Generate AI news commentary.

        Args:
            news_item: Formatted news text. For "synthesis" mode, multiple
                       items separated by "---" should be passed as one string.
            source:    Optional source name (e.g. "Hacker News")
            mode:      "summary"   — faithful overview, no forced personal refs
                       "personal"  — overview + KB angle only if genuinely relevant
                       "synthesis" — multi-story trend narrative
        """
        # Personal mode is the only one that uses KB context.
        # Summary and synthesis intentionally do not, to avoid forced anchoring.
        context = get_context_for_content_type("ai_commentary") if mode == "personal" else ""

        system_prompt, user_prompt = ai_commentary_template(
            context, news_item, source, mode=mode
        )

        return self._generate_and_record(
            content_type="ai_commentary",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata={"news_item": news_item[:100], "source": source, "mode": mode},
            temperature=0.75,
            # Synthesis over multiple stories may need a little more room
            max_tokens=500 if mode == "synthesis" else 400,
            tone=f"commentary/{mode}",
        )

    def generate_leadership_signature(
        self,
        framework: str,
        format_type: str = "linkedin_post",
    ) -> dict:
        """Generate leadership signature content."""
        context = get_context_for_content_type("leadership")
        system_prompt, user_prompt = leadership_signature_template(
            context, framework, format_type
        )

        return self._generate_and_record(
            content_type="leadership_signature",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata={"framework": framework, "format_type": format_type},
            temperature=0.7,
            max_tokens=600,
            tone=format_type,
        )

    def save_result(self, result: dict, filename: str = None) -> Path:
        """Save generated content to a markdown file and update cost log."""
        if not filename:
            ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{result['content_type']}_{ts}.md"

        output_path = OUTPUT_DIR / filename

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Generated Content: {result['content_type']}\n\n")
            f.write(f"**Generated:** {result['generated_at']}\n")
            f.write(f"**Model:** {result['model']}\n")
            f.write(f"**Metadata:** {json.dumps(result['metadata'])}\n\n")
            f.write("---\n\n")
            f.write(result["content"])

        logger.info("Saved to: %s", output_path)
        self._append_cost_log(result, output_path)
        return output_path

    def _append_cost_log(self, result: dict, output_path: Path) -> None:
        """Append one row to output/cost_log.md."""
        cost_log = OUTPUT_DIR / "cost_log.md"
        summary  = self.llm.cost_tracker.summary()

        if not cost_log.exists():
            with open(cost_log, "w", encoding="utf-8") as f:
                f.write("# Cost Log\n\n")
                f.write("| Timestamp | Content Type | Metadata | Tokens | Cost (USD) | Total Session |\n")
                f.write("|-----------|-------------|----------|--------|------------|---------------|\n")

        with open(cost_log, "a", encoding="utf-8") as f:
            f.write(
                f"| {result['generated_at']} "
                f"| {result['content_type']} "
                f"| {json.dumps(result['metadata'])} "
                f"| {summary['total_tokens']:,} "
                f"| ${summary['average_cost']:.6f} "
                f"| ${summary['total_cost']:.4f} |\n"
            )

    def print_cost_summary(self):
        """Print cost summary for this session."""
        self.llm.print_cost_summary()
