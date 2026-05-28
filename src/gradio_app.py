"""
Gradio Web Interface — AI Content Creator Personal Brand Engine.

Run with:
    python3 gradio_app.py
Then open: http://127.0.0.1:7860
"""
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr
from content_pipeline import ContentPipeline
from hn_processor import HackerNewsProcessor

logger = logging.getLogger("gradio_app")

pipeline = ContentPipeline()
hn       = HackerNewsProcessor()

# Cache fetched stories
_hn_cache: list[dict] = []


# ── HackerNews handlers ───────────────────────────────────────────────────────

def fetch_hn_stories(max_stories: int) -> tuple[list, str]:
    """
    Fetch top AI stories and return updated dropdown choices + status.
    Dropdown is always visible — we just update its choices, never hide/show it.
    """
    global _hn_cache
    _hn_cache = hn.fetch_ai_stories(max_stories=int(max_stories))

    if not _hn_cache:
        return gr.Dropdown(choices=[], value=None), "No stories found — check network"

    choices = [
        f"{i+1}. [{s['score']} pts] {s['title']}"
        for i, s in enumerate(_hn_cache)
    ]
    status = f"✓ {len(_hn_cache)} stories fetched — select one below"
    return gr.Dropdown(choices=choices, value=None), status


def select_hn_story(selection: str) -> str:
    """Populate news input when a story is selected from the dropdown."""
    global _hn_cache
    if not selection or not _hn_cache:
        return ""
    try:
        idx   = int(selection.split(".")[0]) - 1
        return hn.format_for_prompt(_hn_cache[idx])
    except (ValueError, IndexError):
        return ""


# ── Content generation handlers ───────────────────────────────────────────────

def generate_linkedin(topic: str, tone: str) -> tuple[str, str, str]:
    if not topic.strip():
        return "Please enter a topic.", "", ""
    result    = pipeline.generate_linkedin_post(topic=topic, tone=tone)
    path      = pipeline.save_result(result)
    cost      = pipeline.llm.cost_tracker.summary()
    cost_line = f"Cost: ${cost['average_cost']:.6f} | Session total: ${cost['total_cost']:.4f} | Tokens: {cost['total_tokens']:,}"
    return result["content"], str(path), cost_line


def generate_bio(length: str, purpose: str) -> tuple[str, str, str]:
    result    = pipeline.generate_executive_bio(length=length, purpose=purpose)
    path      = pipeline.save_result(result)
    cost      = pipeline.llm.cost_tracker.summary()
    cost_line = f"Cost: ${cost['average_cost']:.6f} | Session total: ${cost['total_cost']:.4f} | Tokens: {cost['total_tokens']:,}"
    return result["content"], str(path), cost_line


def generate_commentary(news_item: str, source: str) -> tuple[str, str, str]:
    if not news_item.strip():
        return "Please paste a news item or fetch from HackerNews.", "", ""
    result    = pipeline.generate_ai_commentary(news_item=news_item, source=source)
    path      = pipeline.save_result(result)
    cost      = pipeline.llm.cost_tracker.summary()
    cost_line = f"Cost: ${cost['average_cost']:.6f} | Session total: ${cost['total_cost']:.4f} | Tokens: {cost['total_tokens']:,}"
    return result["content"], str(path), cost_line


def generate_leadership(framework: str, format_type: str) -> tuple[str, str, str]:
    if not framework.strip():
        return "Please enter a framework name.", "", ""
    result    = pipeline.generate_leadership_signature(framework=framework, format_type=format_type)
    path      = pipeline.save_result(result)
    cost      = pipeline.llm.cost_tracker.summary()
    cost_line = f"Cost: ${cost['average_cost']:.6f} | Session total: ${cost['total_cost']:.4f} | Tokens: {cost['total_tokens']:,}"
    return result["content"], str(path), cost_line


def get_cost_summary() -> str:
    s = pipeline.llm.cost_tracker.summary()
    if s["total_requests"] == 0:
        return "No generations yet in this session."
    return (
        f"**Total requests:** {s['total_requests']}\n\n"
        f"**Total tokens:** {s['total_tokens']:,}\n\n"
        f"**Total cost:** ${s['total_cost']:.4f}\n\n"
        f"**Average per request:** ${s['average_cost']:.6f}"
    )


# ── UI ────────────────────────────────────────────────────────────────────────

with gr.Blocks(title="AI Content Creator — Ioanna Renta", theme=gr.themes.Soft()) as app:

    gr.Markdown(
        "# 🎯 AI Content Creator — Personal Brand Engine\n"
        "Generates unique, evidence-based content grounded in a real knowledge base. "
        "Not generic AI — your voice, your frameworks, your proof points."
    )

    with gr.Tabs():

        # ── Tab 1: LinkedIn Post ──────────────────────────────────────────────
        with gr.TabItem("💼 LinkedIn Post"):
            with gr.Row():
                with gr.Column(scale=2):
                    linkedin_topic = gr.Textbox(
                        label="Topic or angle", lines=2,
                        placeholder="e.g. Why most engineering quality frameworks fail")
                    linkedin_tone  = gr.Radio(
                        choices=["thought leadership", "personal story", "industry observation"],
                        value="thought leadership", label="Tone")
                    linkedin_btn   = gr.Button("Generate LinkedIn Post", variant="primary")
                with gr.Column(scale=3):
                    linkedin_out  = gr.Textbox(label="Generated post", lines=12, interactive=False)
                    linkedin_file = gr.Textbox(label="Saved to", interactive=False, max_lines=1)
                    linkedin_cost = gr.Textbox(label="Cost", interactive=False, max_lines=1)
            linkedin_btn.click(generate_linkedin,
                inputs=[linkedin_topic, linkedin_tone],
                outputs=[linkedin_out, linkedin_file, linkedin_cost])

        # ── Tab 2: Executive Bio ──────────────────────────────────────────────
        with gr.TabItem("👤 Executive Bio"):
            with gr.Row():
                with gr.Column(scale=2):
                    bio_length  = gr.Radio(
                        choices=["short", "medium", "long"],
                        value="medium", label="Length")
                    bio_purpose = gr.Radio(
                        choices=["general", "speaking", "board", "job_application"],
                        value="general", label="Purpose")
                    bio_btn     = gr.Button("Generate Bio", variant="primary")
                with gr.Column(scale=3):
                    bio_out  = gr.Textbox(label="Generated bio", lines=12, interactive=False)
                    bio_file = gr.Textbox(label="Saved to", interactive=False, max_lines=1)
                    bio_cost = gr.Textbox(label="Cost", interactive=False, max_lines=1)
            bio_btn.click(generate_bio,
                inputs=[bio_length, bio_purpose],
                outputs=[bio_out, bio_file, bio_cost])

        # ── Tab 3: AI Commentary ──────────────────────────────────────────────
        with gr.TabItem("🤖 AI Commentary"):
            gr.Markdown(
                "Get Ioanna's personal take on AI/tech news. "
                "Fetch live stories from HackerNews or paste any news item manually."
            )
            with gr.Row():

                # ── Left column: inputs ───────────────────────────────────────
                with gr.Column(scale=2):
                    gr.Markdown("#### 📡 Live from HackerNews")

                    with gr.Row():
                        hn_max      = gr.Slider(
                            minimum=3, maximum=10, value=5, step=1,
                            label="Number of stories", scale=2)
                        hn_fetch_btn = gr.Button(
                            "Fetch stories", variant="secondary", scale=1)

                    hn_status   = gr.Textbox(
                        label="", interactive=False, max_lines=1,
                        placeholder="Click Fetch to load live HackerNews stories...")

                    # Always-visible dropdown — choices updated after fetch
                    hn_dropdown = gr.Dropdown(
                        choices=[], value=None,
                        label="Select a story → auto-fills the input below",
                        interactive=True)

                    gr.Markdown("#### ✏️ News item")
                    commentary_news = gr.Textbox(
                        label="",
                        placeholder="Select a story above or paste manually...",
                        lines=5)
                    commentary_source = gr.Textbox(
                        label="Source (optional)",
                        placeholder="e.g. Hacker News, TechCrunch",
                        lines=1)
                    commentary_btn = gr.Button("Generate Commentary", variant="primary")

                # ── Right column: outputs ─────────────────────────────────────
                with gr.Column(scale=3):
                    commentary_out  = gr.Textbox(
                        label="Generated commentary", lines=12, interactive=False)
                    commentary_file = gr.Textbox(
                        label="Saved to", interactive=False, max_lines=1)
                    commentary_cost = gr.Textbox(
                        label="Cost", interactive=False, max_lines=1)

            # Fetch → update dropdown choices (always visible, no show/hide)
            hn_fetch_btn.click(
                fn=fetch_hn_stories,
                inputs=[hn_max],
                outputs=[hn_dropdown, hn_status])

            # Select story → fill news input instantly
            hn_dropdown.change(
                fn=select_hn_story,
                inputs=[hn_dropdown],
                outputs=[commentary_news])

            # Generate
            commentary_btn.click(
                fn=generate_commentary,
                inputs=[commentary_news, commentary_source],
                outputs=[commentary_out, commentary_file, commentary_cost])

        # ── Tab 4: Leadership Signature ───────────────────────────────────────
        with gr.TabItem("🏆 Leadership Signature"):
            with gr.Row():
                with gr.Column(scale=2):
                    leadership_framework = gr.Dropdown(
                        choices=["QMI", "Engineering Manifesto", "60/40 model",
                                 "Pre-emptive Scaling", "Zero Regrettable Attrition"],
                        value="QMI", label="Framework", allow_custom_value=True)
                    leadership_format = gr.Radio(
                        choices=["linkedin_post", "explanation", "speaking_abstract"],
                        value="linkedin_post", label="Format")
                    leadership_btn = gr.Button("Generate Content", variant="primary")
                with gr.Column(scale=3):
                    leadership_out  = gr.Textbox(
                        label="Generated content", lines=12, interactive=False)
                    leadership_file = gr.Textbox(
                        label="Saved to", interactive=False, max_lines=1)
                    leadership_cost = gr.Textbox(
                        label="Cost", interactive=False, max_lines=1)
            leadership_btn.click(generate_leadership,
                inputs=[leadership_framework, leadership_format],
                outputs=[leadership_out, leadership_file, leadership_cost])

        # ── Tab 5: Cost Summary ───────────────────────────────────────────────
        with gr.TabItem("💰 Cost Summary"):
            refresh_btn  = gr.Button("Refresh", variant="secondary")
            cost_display = gr.Markdown("Click Refresh to see current session costs.")
            refresh_btn.click(get_cost_summary, inputs=[], outputs=[cost_display])

    gr.Markdown(
        "---\n*Powered by OpenAI GPT-4o-mini · "
        "Knowledge base: primary + secondary · Live news: HackerNews*"
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")
    app.launch()
