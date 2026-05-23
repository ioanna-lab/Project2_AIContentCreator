"""
Content Pipeline — Week 1 MVP.

Orchestrates the full workflow:
  Document → Brief → Generate → Review → Save

Week 1 implements: Document → Generate → Save
Week 2 will add:   Monitor (HackerNews), Brief refinement, Iterate loop

The pipeline is the glue between document_processor, prompt_templates,
and llm_integration. Callers only need to interact with this module.
"""
import logging
import json
from datetime import datetime
from pathlib import Path
from document_processor import get_context_for_content_type
from prompt_templates import (
    linkedin_post_template,
    executive_bio_template,
    ai_commentary_template,
    leadership_signature_template,
)
from llm_integration import LLMClient

logger = logging.getLogger("content_pipeline")

# Output directory for generated content
OUTPUT_DIR = Path(__file__).parent.parent / "output"


class ContentPipeline:
    """
    Main content generation pipeline.

    Usage:
        pipeline = ContentPipeline()
        result = pipeline.generate_linkedin_post(topic="AI governance in engineering")
        print(result["content"])
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.llm    = LLMClient(model=model)
        self.history = []   # In-memory history of generated content
        OUTPUT_DIR.mkdir(exist_ok=True)
        logger.info("ContentPipeline initialised")

    def _generate_and_record(
        self,
        content_type: str,
        system_prompt: str,
        user_prompt:   str,
        metadata:      dict,
        temperature:   float = 0.7,
        max_tokens:    int   = 1500,
    ) -> dict:
        """
        Internal helper: call the LLM, record the result, return a result dict.

        Args:
            content_type:  One of the pipeline content type strings
            system_prompt: The persona/voice prompt
            user_prompt:   The specific content request with context
            metadata:      Additional info to store with the result
            temperature:   LLM creativity setting
            max_tokens:    Maximum response length

        Returns:
            Dict with content, metadata, timestamp, content_type
        """
        logger.info("Generating %s content...", content_type)

        content = self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        result = {
            "content_type": content_type,
            "content":      content,
            "metadata":     metadata,
            "generated_at": datetime.now().isoformat(),
            "model":        self.llm.model,
        }

        self.history.append(result)
        logger.info("✓ %s content generated (%d chars)", content_type, len(content))
        return result

    # ── Public pipeline methods ───────────────────────────────────────────────

    def generate_linkedin_post(
        self,
        topic: str,
        tone: str = "thought leadership",
    ) -> dict:
        """
        Generate a LinkedIn thought leadership post.

        Args:
            topic: The topic or angle for the post
            tone:  "thought leadership", "personal story", or "industry observation"

        Returns:
            Result dict with content and metadata
        """
        context = get_context_for_content_type("linkedin")
        system_prompt, user_prompt = linkedin_post_template(context, topic, tone)

        return self._generate_and_record(
            content_type="linkedin_post",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata={"topic": topic, "tone": tone},
            temperature=0.8,   # Higher creativity for social content
            max_tokens=400,
        )

    def generate_executive_bio(
        self,
        length: str = "medium",
        purpose: str = "general",
    ) -> dict:
        """
        Generate an executive bio.

        Args:
            length:  "short", "medium", or "long"
            purpose: "general", "speaking", "board", or "job_application"

        Returns:
            Result dict with content and metadata
        """
        context = get_context_for_content_type("bio")
        system_prompt, user_prompt = executive_bio_template(context, length, purpose)

        return self._generate_and_record(
            content_type="executive_bio",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata={"length": length, "purpose": purpose},
            temperature=0.5,   # Lower creativity for bio — accuracy matters more
            max_tokens=800,
        )

    def generate_ai_commentary(
        self,
        news_item: str,
        source: str = "",
    ) -> dict:
        """
        Generate Ioanna's commentary on an AI/tech news item.

        Args:
            news_item: The news headline or summary to comment on
            source:    Optional source name

        Returns:
            Result dict with content and metadata
        """
        context = get_context_for_content_type("ai_commentary")
        system_prompt, user_prompt = ai_commentary_template(context, news_item, source)

        return self._generate_and_record(
            content_type="ai_commentary",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata={"news_item": news_item[:100], "source": source},
            temperature=0.75,
            max_tokens=400,
        )

    def generate_leadership_signature(
        self,
        framework: str,
        format_type: str = "linkedin_post",
    ) -> dict:
        """
        Generate content about one of Ioanna's signature frameworks.

        Args:
            framework:   Framework name (e.g. "QMI", "Engineering Manifesto")
            format_type: "explanation", "linkedin_post", or "speaking_abstract"

        Returns:
            Result dict with content and metadata
        """
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
        )

    def save_result(self, result: dict, filename: str = None) -> Path:
        """
        Save a generated result to a markdown file.

        Args:
            result:   Result dict from any generate_* method
            filename: Optional custom filename (auto-generated if not provided)

        Returns:
            Path to the saved file
        """
        if not filename:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{result['content_type']}_{ts}.md"

        output_path = OUTPUT_DIR / filename

        # Write as markdown with metadata header
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Generated Content: {result['content_type']}\n\n")
            f.write(f"**Generated:** {result['generated_at']}\n")
            f.write(f"**Model:** {result['model']}\n")
            f.write(f"**Metadata:** {json.dumps(result['metadata'])}\n\n")
            f.write("---\n\n")
            f.write(result["content"])

        logger.info("Saved to: %s", output_path)
        return output_path

    def print_cost_summary(self):
        """Print cost summary for this pipeline session."""
        self.llm.print_cost_summary()


# ── Quick smoke test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s | %(levelname)-8s | %(message)s")

    pipeline = ContentPipeline()

    print("\nGenerating LinkedIn post...")
    result = pipeline.generate_linkedin_post(
        topic="Why measuring engineering quality without punishing teams is the hardest thing in engineering leadership"
    )
    print(f"\n{'='*60}")
    print(result["content"])
    print(f"{'='*60}")

    saved = pipeline.save_result(result)
    print(f"\nSaved to: {saved}")

    pipeline.print_cost_summary()
