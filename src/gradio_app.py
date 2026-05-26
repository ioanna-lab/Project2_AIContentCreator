"""
Gradio Web Interface — AI Content Creator Personal Brand Engine.

A clean web UI on top of the existing content pipeline.
Replaces the CLI for demo and presentation purposes.

Run with:
    python3 gradio_app.py

Then open: http://127.0.0.1:7860
"""
import sys
import logging
from pathlib import Path

# Add src/ to path so imports work when running from project root
sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr
from content_pipeline import ContentPipeline

logger = logging.getLogger("gradio_app")

# Single pipeline instance shared across all tab interactions
pipeline = ContentPipeline()


# ── Tab handlers ──────────────────────────────────────────────────────────────

def generate_linkedin(topic: str, tone: str) -> tuple[str, str, str]:
    """
    Generate a LinkedIn post and return (content, file_path, cost_line).
    """
    if not topic.strip():
        return "Please enter a topic.", "", ""

    result = pipeline.generate_linkedin_post(topic=topic, tone=tone)
    path   = pipeline.save_result(result)
    cost   = pipeline.llm.cost_tracker.summary()

    cost_line = (
        f"This generation: ${cost['average_cost']:.6f} | "
        f"Session total: ${cost['total_cost']:.4f} | "
        f"Tokens: {cost['total_tokens']:,}"
    )
    return result["content"], str(path), cost_line


def generate_bio(length: str, purpose: str) -> tuple[str, str, str]:
    """Generate an executive bio."""
    result = pipeline.generate_executive_bio(length=length, purpose=purpose)
    path   = pipeline.save_result(result)
    cost   = pipeline.llm.cost_tracker.summary()

    cost_line = (
        f"This generation: ${cost['average_cost']:.6f} | "
        f"Session total: ${cost['total_cost']:.4f} | "
        f"Tokens: {cost['total_tokens']:,}"
    )
    return result["content"], str(path), cost_line


def generate_commentary(news_item: str, source: str) -> tuple[str, str, str]:
    """Generate AI news commentary."""
    if not news_item.strip():
        return "Please paste a news item.", "", ""

    result = pipeline.generate_ai_commentary(news_item=news_item, source=source)
    path   = pipeline.save_result(result)
    cost   = pipeline.llm.cost_tracker.summary()

    cost_line = (
        f"This generation: ${cost['average_cost']:.6f} | "
        f"Session total: ${cost['total_cost']:.4f} | "
        f"Tokens: {cost['total_tokens']:,}"
    )
    return result["content"], str(path), cost_line


def generate_leadership(framework: str, format_type: str) -> tuple[str, str, str]:
    """Generate leadership signature content."""
    if not framework.strip():
        return "Please enter a framework name.", "", ""

    result = pipeline.generate_leadership_signature(
        framework=framework, format_type=format_type
    )
    path = pipeline.save_result(result)
    cost = pipeline.llm.cost_tracker.summary()

    cost_line = (
        f"This generation: ${cost['average_cost']:.6f} | "
        f"Session total: ${cost['total_cost']:.4f} | "
        f"Tokens: {cost['total_tokens']:,}"
    )
    return result["content"], str(path), cost_line


def get_cost_summary() -> str:
    """Return formatted cost summary for the session."""
    s = pipeline.llm.cost_tracker.summary()
    if s["total_requests"] == 0:
        return "No generations yet in this session."
    return (
        f"**Total requests:** {s['total_requests']}\n\n"
        f"**Total tokens:** {s['total_tokens']:,}\n\n"
        f"**Total cost:** ${s['total_cost']:.4f}\n\n"
        f"**Average per request:** ${s['average_cost']:.6f}"
    )


# ── Shared output components style ───────────────────────────────────────────

OUTPUT_LINES = 12


# ── Build Gradio UI ───────────────────────────────────────────────────────────

with gr.Blocks(
    title="AI Content Creator — Ioanna Renta",
    theme=gr.themes.Soft(),
) as app:

    gr.Markdown(
        """
        # 🎯 AI Content Creator — Personal Brand Engine
        Generates unique, evidence-based content grounded in a real knowledge base.
        Not generic AI — your voice, your frameworks, your proof points.
        """
    )

    with gr.Tabs():

        # ── Tab 1: LinkedIn Post ──────────────────────────────────────────────
        with gr.TabItem("💼 LinkedIn Post"):
            gr.Markdown(
                "Generate a thought leadership post in Ioanna's voice. "
                "Content references specific outcomes and named frameworks — "
                "not generic leadership advice."
            )
            with gr.Row():
                with gr.Column(scale=2):
                    linkedin_topic = gr.Textbox(
                        label="Topic or angle",
                        placeholder="e.g. Why most engineering quality frameworks fail — and what makes QMI different",
                        lines=2,
                    )
                    linkedin_tone = gr.Radio(
                        choices=["thought leadership", "personal story", "industry observation"],
                        value="thought leadership",
                        label="Tone",
                    )
                    linkedin_btn = gr.Button("Generate LinkedIn Post", variant="primary")

                with gr.Column(scale=3):
                    linkedin_output = gr.Textbox(
                        label="Generated post",
                        lines=OUTPUT_LINES,
                        interactive=False,
                    )
                    linkedin_file = gr.Textbox(
                        label="Saved to",
                        interactive=False,
                        max_lines=1,
                    )
                    linkedin_cost = gr.Textbox(
                        label="Cost",
                        interactive=False,
                        max_lines=1,
                    )

            linkedin_btn.click(
                fn=generate_linkedin,
                inputs=[linkedin_topic, linkedin_tone],
                outputs=[linkedin_output, linkedin_file, linkedin_cost],
            )

        # ── Tab 2: Executive Bio ──────────────────────────────────────────────
        with gr.TabItem("👤 Executive Bio"):
            gr.Markdown(
                "Generate a role-appropriate executive bio in third person. "
                "Choose the length and purpose — the bio adapts emphasis accordingly."
            )
            with gr.Row():
                with gr.Column(scale=2):
                    bio_length = gr.Radio(
                        choices=["short", "medium", "long"],
                        value="medium",
                        label="Length",
                    )
                    bio_purpose = gr.Radio(
                        choices=["general", "speaking", "board", "job_application"],
                        value="general",
                        label="Purpose",
                    )
                    bio_btn = gr.Button("Generate Bio", variant="primary")

                with gr.Column(scale=3):
                    bio_output = gr.Textbox(
                        label="Generated bio",
                        lines=OUTPUT_LINES,
                        interactive=False,
                    )
                    bio_file = gr.Textbox(
                        label="Saved to",
                        interactive=False,
                        max_lines=1,
                    )
                    bio_cost = gr.Textbox(
                        label="Cost",
                        interactive=False,
                        max_lines=1,
                    )

            bio_btn.click(
                fn=generate_bio,
                inputs=[bio_length, bio_purpose],
                outputs=[bio_output, bio_file, bio_cost],
            )

        # ── Tab 3: AI Commentary ──────────────────────────────────────────────
        with gr.TabItem("🤖 AI Commentary"):
            gr.Markdown(
                "Paste any AI or tech news item and get Ioanna's personal take — "
                "grounded in her real experience with AI adoption at engineering organisations."
            )
            with gr.Row():
                with gr.Column(scale=2):
                    commentary_news = gr.Textbox(
                        label="News item",
                        placeholder="Paste a headline or summary here...",
                        lines=5,
                    )
                    commentary_source = gr.Textbox(
                        label="Source (optional)",
                        placeholder="e.g. Hacker News, TechCrunch",
                        lines=1,
                    )
                    commentary_btn = gr.Button("Generate Commentary", variant="primary")

                with gr.Column(scale=3):
                    commentary_output = gr.Textbox(
                        label="Generated commentary",
                        lines=OUTPUT_LINES,
                        interactive=False,
                    )
                    commentary_file = gr.Textbox(
                        label="Saved to",
                        interactive=False,
                        max_lines=1,
                    )
                    commentary_cost = gr.Textbox(
                        label="Cost",
                        interactive=False,
                        max_lines=1,
                    )

            commentary_btn.click(
                fn=generate_commentary,
                inputs=[commentary_news, commentary_source],
                outputs=[commentary_output, commentary_file, commentary_cost],
            )

        # ── Tab 4: Leadership Signature ───────────────────────────────────────
        with gr.TabItem("🏆 Leadership Signature"):
            gr.Markdown(
                "Generate content explaining one of Ioanna's signature frameworks — "
                "QMI, Engineering Manifesto, 60/40 model, or others."
            )
            with gr.Row():
                with gr.Column(scale=2):
                    leadership_framework = gr.Dropdown(
                        choices=[
                            "QMI",
                            "Engineering Manifesto",
                            "60/40 model",
                            "Pre-emptive Scaling",
                            "Zero Regrettable Attrition",
                        ],
                        value="QMI",
                        label="Framework",
                        allow_custom_value=True,
                    )
                    leadership_format = gr.Radio(
                        choices=["linkedin_post", "explanation", "speaking_abstract"],
                        value="linkedin_post",
                        label="Format",
                    )
                    leadership_btn = gr.Button("Generate Content", variant="primary")

                with gr.Column(scale=3):
                    leadership_output = gr.Textbox(
                        label="Generated content",
                        lines=OUTPUT_LINES,
                        interactive=False,
                    )
                    leadership_file = gr.Textbox(
                        label="Saved to",
                        interactive=False,
                        max_lines=1,
                    )
                    leadership_cost = gr.Textbox(
                        label="Cost",
                        interactive=False,
                        max_lines=1,
                    )

            leadership_btn.click(
                fn=generate_leadership,
                inputs=[leadership_framework, leadership_format],
                outputs=[leadership_output, leadership_file, leadership_cost],
            )

        # ── Tab 5: Session Cost Summary ───────────────────────────────────────
        with gr.TabItem("💰 Cost Summary"):
            gr.Markdown("Running cost for this session across all content types.")
            refresh_btn   = gr.Button("Refresh", variant="secondary")
            cost_display  = gr.Markdown("Click Refresh to see current session costs.")
            refresh_btn.click(fn=get_cost_summary, inputs=[], outputs=[cost_display])

    gr.Markdown(
        "---\n"
        "*Powered by OpenAI GPT-4o-mini · "
        "Knowledge base: primary (bio, philosophy, case studies, positioning) + "
        "secondary (AI trends, CTO market)*"
    )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    app.launch()
