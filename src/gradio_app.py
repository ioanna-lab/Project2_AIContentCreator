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
from content_analyzer import format_metrics_for_display
import kb_manager

logger   = logging.getLogger("gradio_app")
pipeline = ContentPipeline()
hn       = HackerNewsProcessor()

_hn_cache: list[dict] = []
_search_cache: list[str] = []         # formatted text per topic-search result
_search_cache_choices: list[str] = []  # choice labels for Select All

WEB_TONES       = ("industry observation", "thought leadership")
CATEGORIES      = kb_manager.CATEGORIES
PRIMARY_FILES   = kb_manager.PRIMARY_FILES
SECONDARY_FILES = kb_manager.SECONDARY_FILES


# ── HackerNews browse handlers ────────────────────────────────────────────────

def fetch_hn_stories(topic: str, max_stories: int) -> tuple:
    """
    Fetch HN stories. If topic is provided, searches by keyword via Algolia.
    If empty, falls back to top AI stories (original behaviour).
    """
    global _hn_cache
    max_n = int(max_stories)

    if topic.strip():
        # Keyword search on HN via Algolia
        try:
            import requests
            from urllib.parse import quote
            url  = (f"https://hn.algolia.com/api/v1/search"
                    f"?query={quote(topic.strip())}&tags=story&hitsPerPage={max_n * 2}")
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            hits = resp.json().get("hits", [])
            _hn_cache = []
            for hit in hits[:max_n]:
                title     = hit.get("title", "No title")
                score     = hit.get("points", 0)
                obj_id    = hit.get("objectID", "")
                story_url = hit.get("url") or f"https://news.ycombinator.com/item?id={obj_id}"
                _hn_cache.append({
                    "title":      title,
                    "score":      score,
                    # Pre-format so select_hn_story doesn't need hn.format_for_prompt
                    "_formatted": (
                        f"Title: {title}\n"
                        f"Source: Hacker News\n"
                        f"Score: {score} points\n"
                        f"URL: {story_url}"
                    ),
                })
        except Exception as e:
            logger.warning("HN topic search failed: %s", e)
            _hn_cache = []
    else:
        # No topic — fetch top AI stories as before
        _hn_cache = hn.fetch_ai_stories(max_stories=max_n)

    if not _hn_cache:
        return gr.Dropdown(choices=[], value=None), "No stories found"

    choices = [f"{i+1}. [{s['score']} pts] {s['title']}" for i, s in enumerate(_hn_cache)]
    status  = f"✓ {len(_hn_cache)} stories fetched"
    if topic.strip():
        status += f" matching '{topic.strip()}'"
    return gr.Dropdown(choices=choices, value=None), status


def select_hn_story(selection) -> str:
    """Auto-fill news textbox. Handles single string or list (multiselect)."""
    global _hn_cache
    if not selection or not _hn_cache:
        return ""
    if isinstance(selection, str):
        selection = [selection]
    items = []
    for sel in selection:
        try:
            idx   = int(sel.split(".")[0]) - 1
            story = _hn_cache[idx]
            # Topic-search entries are pre-formatted; top-story entries use hn.format_for_prompt
            text  = story.get("_formatted") or hn.format_for_prompt(story)
            items.append(text)
        except (ValueError, IndexError):
            continue
    return "\n\n---\n\n".join(items) if items else ""


# ── Topic search handlers ─────────────────────────────────────────────────────

def _format_single_web_result(r) -> tuple[str, str]:
    """
    Safely extract (dropdown_label, prompt_text) from one web result object.
    Handles both dict and object structures defensively.
    """
    if isinstance(r, dict):
        title   = r.get("title") or r.get("headline") or "Untitled"
        source  = r.get("source") or r.get("domain") or "Web"
        url     = r.get("url")   or r.get("link")    or ""
        snippet = (r.get("snippet") or r.get("description")
                   or r.get("content") or r.get("text") or "")
        label   = f"[{source}] {title}"
        text    = f"Title: {title}\nSource: {source}"
        if url:
            text += f"\nURL: {url}"
        if snippet:
            text += f"\nSummary: {str(snippet)[:400]}"
        return label, text
    # Fallback for unknown structure
    s = str(r)
    return s[:60], s


def search_news_by_topic(
    topic: str,
    sources: list,
    max_results: int,
) -> tuple:
    """
    Search for news about a topic across HackerNews (Algolia) and/or the web.

    Returns updated dropdown choices + status message.
    Results are stored in _search_cache for retrieval on selection.
    """
    global _search_cache
    _search_cache = []

    if not topic.strip():
        return gr.Dropdown(choices=[], value=None), "Please enter a search topic."

    choices      = []
    status_parts = []
    max_n        = int(max_results)

    # ── HackerNews via Algolia keyword search ─────────────────────────────────
    if "HackerNews" in sources:
        try:
            import requests
            from urllib.parse import quote
            url  = (f"https://hn.algolia.com/api/v1/search"
                    f"?query={quote(topic)}&tags=story&hitsPerPage={max_n}")
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            hits = resp.json().get("hits", [])
            for hit in hits:
                title   = hit.get("title", "No title")
                score   = hit.get("points", 0)
                obj_id  = hit.get("objectID", "")
                story_url = hit.get("url") or f"https://news.ycombinator.com/item?id={obj_id}"
                text = (
                    f"Title: {title}\n"
                    f"Source: Hacker News\n"
                    f"Score: {score} points\n"
                    f"URL: {story_url}"
                )
                _search_cache.append(text)
                choices.append(f"{len(_search_cache)}. [HN] {title}")
            status_parts.append(f"{len(hits)} from HackerNews")
        except Exception as e:
            logger.warning("HN topic search failed: %s", e)
            status_parts.append(f"HackerNews unavailable")

    # ── Web search via WebResearcher (Dev.to / TechCrunch / General) ──────────
    web_sources_selected = [s for s in sources if s != "HackerNews"]
    if web_sources_selected:
        try:
            # Build a scoped query if specific sources were chosen
            query = topic
            if web_sources_selected and "General Web" not in web_sources_selected:
                site_hints = " OR ".join(
                    f"site:{_SOURCE_DOMAINS[s]}"
                    for s in web_sources_selected
                    if s in _SOURCE_DOMAINS
                )
                query = f"{topic} ({site_hints})" if site_hints else topic

            web_results = pipeline.researcher.search(query, max_results=max_n)
            web_count   = 0
            for r in web_results:
                label, text = _format_single_web_result(r)
                _search_cache.append(text)
                choices.append(f"{len(_search_cache)}. {label}")
                web_count += 1
            if web_count:
                status_parts.append(f"{web_count} from web")
        except Exception as e:
            logger.warning("Web topic search failed: %s", e)
            status_parts.append("Web search unavailable")

    if not _search_cache:
        return gr.CheckboxGroup(choices=[], value=[]), "No results found — try a different topic."

    status = f"✓ {len(_search_cache)} results — " + ", ".join(status_parts)
    _search_cache_choices[:] = choices   # update in-place for Select All
    return gr.CheckboxGroup(choices=choices, value=[]), status


# Domain hints for scoped web search
_SOURCE_DOMAINS = {
    "Dev.to":     "dev.to",
    "TechCrunch": "techcrunch.com",
}


def select_search_result(selection) -> str:
    """Auto-fill news textbox from topic-search checkboxes."""
    global _search_cache
    if not selection or not _search_cache:
        return ""
    if isinstance(selection, str):
        selection = [selection]
    items = []
    for sel in selection:
        try:
            idx = int(sel.split(".")[0]) - 1
            if 0 <= idx < len(_search_cache):
                items.append(_search_cache[idx])
        except (ValueError, IndexError):
            continue
    return "\n\n---\n\n".join(items) if items else ""


def select_all_search_results() -> gr.CheckboxGroup:
    """Select every result in the search checkboxes."""
    return gr.CheckboxGroup(value=_search_cache_choices)


def clear_search_results() -> gr.CheckboxGroup:
    """Deselect all search results."""
    return gr.CheckboxGroup(value=[])


def toggle_news_source(mode: str) -> tuple:
    """Show/hide HN browse vs topic search panels."""
    is_hn     = mode == "📡 Browse HackerNews"
    is_search = mode == "🔍 Search by Topic"
    return (
        gr.Column(visible=is_hn),
        gr.Column(visible=is_search),
    )


# ── LinkedIn handlers ─────────────────────────────────────────────────────────

def on_tone_change(tone: str) -> tuple:
    """Show/hide web context panel based on tone selection."""
    needs_web = tone in WEB_TONES
    return (
        gr.Row(visible=needs_web),
        gr.Textbox(value=""),
        gr.Textbox(value=""),
        gr.Textbox(value=""),
    )


def fetch_web_context(topic: str, tone: str) -> str:
    if not topic.strip():
        return "Please enter a topic first."
    if tone not in WEB_TONES:
        return ""
    results = pipeline.researcher.search(topic, max_results=5)
    display = pipeline.researcher.format_for_display(results)
    return display if display else "No results found — will use knowledge base only."


def generate_linkedin(topic: str, tone: str) -> tuple:
    if not topic.strip():
        return "Please enter a topic.", "", "", ""
    result, web_display = pipeline.generate_linkedin_post(topic=topic, tone=tone)
    path      = pipeline.save_result(result)
    cost      = pipeline.llm.cost_tracker.summary()
    metrics   = format_metrics_for_display(result["metrics"])
    cost_line = f"Cost: ${cost['average_cost']:.6f} | Session: ${cost['total_cost']:.4f} | Tokens: {cost['total_tokens']:,}"
    return result["content"], str(path), cost_line, metrics


# ── Bio handler ───────────────────────────────────────────────────────────────

def generate_bio(length: str, purpose: str) -> tuple:
    result    = pipeline.generate_executive_bio(length=length, purpose=purpose)
    path      = pipeline.save_result(result)
    cost      = pipeline.llm.cost_tracker.summary()
    metrics   = format_metrics_for_display(result["metrics"])
    cost_line = f"Cost: ${cost['average_cost']:.6f} | Session: ${cost['total_cost']:.4f} | Tokens: {cost['total_tokens']:,}"
    return result["content"], str(path), cost_line, metrics


# ── Commentary handler ────────────────────────────────────────────────────────

def generate_commentary(news_item: str, mode: str) -> tuple:
    if not news_item.strip():
        return "Please select a story or paste a news item.", "", "", ""
    mode_key = {
        "📰 Story Summary":         "summary",
        "💬 Personal Commentary":   "personal",
        "🔄 Multi-Story Synthesis": "synthesis",
    }.get(mode, "summary")
    result    = pipeline.generate_ai_commentary(
        news_item=news_item, source="", mode=mode_key)
    path      = pipeline.save_result(result)
    cost      = pipeline.llm.cost_tracker.summary()
    metrics   = format_metrics_for_display(result["metrics"])
    cost_line = f"Cost: ${cost['average_cost']:.6f} | Session: ${cost['total_cost']:.4f} | Tokens: {cost['total_tokens']:,}"
    return result["content"], str(path), cost_line, metrics


# ── Leadership handler ────────────────────────────────────────────────────────

def generate_leadership(framework: str, format_type: str) -> tuple:
    if not framework.strip():
        return "Please enter a framework name.", "", "", ""
    result    = pipeline.generate_leadership_signature(
        framework=framework, format_type=format_type)
    path      = pipeline.save_result(result)
    cost      = pipeline.llm.cost_tracker.summary()
    metrics   = format_metrics_for_display(result["metrics"])
    cost_line = f"Cost: ${cost['average_cost']:.6f} | Session: ${cost['total_cost']:.4f} | Tokens: {cost['total_tokens']:,}"
    return result["content"], str(path), cost_line, metrics


# ── Cost summary ──────────────────────────────────────────────────────────────

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


# ── KB handlers ───────────────────────────────────────────────────────────────

def save_content_to_kb(content: str, category: str, source_tab: str) -> str:
    """Save generated content to the KB. Used by per-tab Save buttons."""
    if not content.strip():
        return "⚠️ Nothing to save — generate content first."
    success, message = kb_manager.append_to_kb_by_category(
        content=content, category=category, source_tab=source_tab
    )
    return message


def open_kb_save_panel(content: str) -> tuple:
    """Reveal the KB save panel and pre-fill with generated content."""
    return gr.Accordion(open=True), content


def update_file_choices(kb_type: str) -> gr.Dropdown:
    """Update the file dropdown when KB type changes in Browse section."""
    choices = PRIMARY_FILES if kb_type == "primary" else SECONDARY_FILES
    return gr.Dropdown(choices=choices, value=choices[0] if choices else None)


def browse_kb_file(kb_type: str, filename: str) -> str:
    """Load a KB file for display in the Browse section."""
    if not filename:
        return ""
    return kb_manager.read_kb_file(kb_type, filename)


def save_manual_kb_entry(content: str, category: str) -> str:
    """Save a manually typed KB entry from the KB Management tab."""
    if not content.strip():
        return "⚠️ Please enter some content before saving."
    success, message = kb_manager.append_to_kb_by_category(
        content=content, category=category, source_tab="KB Management tab"
    )
    return message


# ── Shared KB save accordion builder ─────────────────────────────────────────
# Each content tab gets one of these. Returns the accordion component +
# the wiring instructions as a dict so the caller can connect the buttons.

def _kb_save_section(default_category: str, source_tab: str):
    """
    Build a reusable 'Save to KB' accordion panel for a content tab.

    Returns:
        (accordion, kb_edit_box, category_drop, open_btn, confirm_btn, status_box)
    """
    with gr.Accordion("💾 Save to Knowledge Base", open=False) as accordion:
        gr.Markdown(
            "_Edit the content below before saving if needed. "
            "Changes are available in the next generation — no restart required._"
        )
        kb_edit = gr.Textbox(
            label="Content to save",
            lines=6,
            placeholder="Will be pre-filled when you click 'Save to KB' above...",
            interactive=True,
        )
        with gr.Row():
            kb_cat = gr.Dropdown(
                choices=CATEGORIES,
                value=default_category,
                label="Category",
                scale=3,
            )
            kb_confirm = gr.Button("Confirm Save", variant="primary", scale=1)
        kb_status = gr.Textbox(label="", interactive=False, max_lines=2)

    return accordion, kb_edit, kb_cat, kb_confirm, kb_status


# ── UI ────────────────────────────────────────────────────────────────────────

with gr.Blocks(title="AI Content Creator — Ioanna Renta", theme=gr.themes.Soft()) as app:

    gr.Markdown(
        "# 🎯 AI Content Creator — Personal Brand Engine\n"
        "Generates unique, evidence-based content. "
        "Not generic AI — your voice, your frameworks, your proof points."
    )

    with gr.Tabs():

        # ── Tab 1: LinkedIn Post ──────────────────────────────────────────────
        with gr.TabItem("💼 LinkedIn Post"):
            gr.Markdown(
                "Three genuinely different modes:\n"
                "- **Personal Story** — draws from your KB (bio, case studies, frameworks)\n"
                "- **Industry Observation** — searches the web, synthesises what others are saying\n"
                "- **Thought Leadership** — industry context + your personal experience anchored in KB"
            )
            with gr.Row():
                with gr.Column(scale=2):
                    linkedin_topic = gr.Textbox(
                        label="Topic or angle", lines=2,
                        placeholder="e.g. AI governance in engineering teams")
                    linkedin_tone = gr.Radio(
                        choices=["personal story", "industry observation", "thought leadership"],
                        value="personal story", label="Tone")

                    with gr.Row(visible=False) as web_row:
                        with gr.Column():
                            fetch_web_btn    = gr.Button("🌐 Fetch industry context (5-10s)", variant="secondary")
                            web_sources_disp = gr.Textbox(
                                label="Industry sources found", lines=6, interactive=False,
                                placeholder="Click above to fetch live industry context...")

                    linkedin_btn = gr.Button("Generate LinkedIn Post", variant="primary")

                with gr.Column(scale=3):
                    linkedin_out     = gr.Textbox(label="Generated post", lines=10, interactive=True)
                    linkedin_file    = gr.Textbox(label="Saved to", interactive=False, max_lines=1)
                    linkedin_cost    = gr.Textbox(label="Cost", interactive=False, max_lines=1)
                    linkedin_metrics = gr.Textbox(label="Quality metrics", lines=12, interactive=False)

                    linkedin_kb_btn = gr.Button("💾 Save to KB", variant="secondary")
                    li_accordion, li_kb_edit, li_kb_cat, li_kb_confirm, li_kb_status = \
                        _kb_save_section("Philosophy / Framework", "LinkedIn Post tab")

            # Tone change → show/hide web panel
            linkedin_tone.change(
                fn=on_tone_change,
                inputs=[linkedin_tone],
                outputs=[web_row, web_sources_disp, linkedin_out, linkedin_metrics])

            fetch_web_btn.click(
                fn=fetch_web_context,
                inputs=[linkedin_topic, linkedin_tone],
                outputs=[web_sources_disp])

            linkedin_btn.click(
                fn=generate_linkedin,
                inputs=[linkedin_topic, linkedin_tone],
                outputs=[linkedin_out, linkedin_file, linkedin_cost, linkedin_metrics])

            # KB save wiring
            linkedin_kb_btn.click(
                fn=open_kb_save_panel,
                inputs=[linkedin_out],
                outputs=[li_accordion, li_kb_edit])
            li_kb_confirm.click(
                fn=lambda content, cat: save_content_to_kb(content, cat, "LinkedIn Post"),
                inputs=[li_kb_edit, li_kb_cat],
                outputs=[li_kb_status])

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
                    bio_out     = gr.Textbox(label="Generated bio", lines=10, interactive=True)
                    bio_file    = gr.Textbox(label="Saved to", interactive=False, max_lines=1)
                    bio_cost    = gr.Textbox(label="Cost", interactive=False, max_lines=1)
                    bio_metrics = gr.Textbox(label="Quality metrics", lines=12, interactive=False)

                    bio_kb_btn = gr.Button("💾 Save to KB", variant="secondary")
                    bio_accordion, bio_kb_edit, bio_kb_cat, bio_kb_confirm, bio_kb_status = \
                        _kb_save_section("Bio / Positioning", "Executive Bio tab")

            bio_btn.click(
                fn=generate_bio,
                inputs=[bio_length, bio_purpose],
                outputs=[bio_out, bio_file, bio_cost, bio_metrics])

            bio_kb_btn.click(
                fn=open_kb_save_panel,
                inputs=[bio_out],
                outputs=[bio_accordion, bio_kb_edit])
            bio_kb_confirm.click(
                fn=lambda content, cat: save_content_to_kb(content, cat, "Executive Bio"),
                inputs=[bio_kb_edit, bio_kb_cat],
                outputs=[bio_kb_status])

        # ── Tab 3: AI Commentary ──────────────────────────────────────────────
        with gr.TabItem("🤖 AI Commentary"):
            gr.Markdown(
                "**Generation mode** — choose what kind of output you want:\n"
                "- **📰 Story Summary** — faithful overview, no personal references forced\n"
                "- **💬 Personal Commentary** — overview first, then Ioanna's angle "
                "*only if there is a genuine connection*\n"
                "- **🔄 Multi-Story Synthesis** — select 2-5 stories, one trend narrative"
            )
            with gr.Row():
                with gr.Column(scale=2):

                    commentary_mode = gr.Radio(
                        choices=[
                            "📰 Story Summary",
                            "💬 Personal Commentary",
                            "🔄 Multi-Story Synthesis",
                        ],
                        value="📰 Story Summary",
                        label="Generation mode",
                    )

                    # ── News source toggle ────────────────────────────────────
                    news_source_toggle = gr.Radio(
                        choices=["📡 Browse HackerNews", "🔍 Search by Topic"],
                        value="📡 Browse HackerNews",
                        label="News source",
                    )

                    # ── Panel A: Browse HackerNews (default visible) ───────────
                    with gr.Column(visible=True) as hn_browse_panel:
                        gr.Markdown("#### 📡 Browse HackerNews")
                        hn_topic = gr.Textbox(
                            label="Filter by topic (optional)",
                            placeholder="e.g. AI agents, LLM in production… "
                                        "leave empty for top AI stories",
                            lines=1,
                        )
                        with gr.Row():
                            hn_max       = gr.Slider(minimum=3, maximum=10, value=5,
                                step=1, label="Stories", scale=2)
                            hn_fetch_btn = gr.Button("Fetch", variant="secondary", scale=1)
                        hn_status   = gr.Textbox(label="", interactive=False, max_lines=1)
                        hn_dropdown = gr.Dropdown(
                            choices=[], value=None, multiselect=True,
                            label="Select stories → auto-fills below "
                                  "(multi-select for Synthesis)",
                            interactive=True,
                        )

                    # ── Panel B: Search by Topic (default hidden) ─────────────
                    with gr.Column(visible=False) as topic_search_panel:
                        gr.Markdown("#### 🔍 Search by topic")
                        search_topic = gr.Textbox(
                            label="Topic to search",
                            placeholder="e.g. AI agents in production engineering",
                            lines=1,
                        )
                        search_sources = gr.CheckboxGroup(
                            choices=["HackerNews", "Dev.to", "TechCrunch", "General Web"],
                            value=["HackerNews", "General Web"],
                            label="Sources",
                        )
                        with gr.Row():
                            search_max = gr.Slider(
                                minimum=3, maximum=10, value=5, step=1,
                                label="Max results (actual count depends on source availability)",
                                scale=3)
                            search_btn = gr.Button(
                                "🔍 Search", variant="secondary", scale=1)
                        search_status   = gr.Textbox(
                            label="", interactive=False, max_lines=1)
                        search_checkboxes = gr.CheckboxGroup(
                            choices=[],
                            value=[],
                            label="Select results to include (multi-select supported)",
                            interactive=True,
                        )
                        with gr.Row():
                            select_all_btn = gr.Button("Select All", variant="secondary", scale=1)
                            clear_sel_btn  = gr.Button("Clear",       variant="secondary", scale=1)

                    # ── Shared news textbox (fed by both panels) ──────────────
                    gr.Markdown("#### ✏️ News item(s)")
                    commentary_news = gr.Textbox(
                        label="",
                        placeholder="Auto-filled from selection above, or paste manually. "
                                    "Multiple items are separated by --- for Synthesis mode.",
                        lines=5,
                    )
                    commentary_btn = gr.Button("Generate Commentary", variant="primary")

                with gr.Column(scale=3):
                    commentary_out     = gr.Textbox(label="Generated commentary",
                        lines=10, interactive=True)
                    commentary_file    = gr.Textbox(label="Saved to",
                        interactive=False, max_lines=1)
                    commentary_cost    = gr.Textbox(label="Cost",
                        interactive=False, max_lines=1)
                    commentary_metrics = gr.Textbox(label="Quality metrics",
                        lines=12, interactive=False)

                    commentary_kb_btn = gr.Button("💾 Save to KB", variant="secondary")
                    com_accordion, com_kb_edit, com_kb_cat, com_kb_confirm, com_kb_status = \
                        _kb_save_section("Industry Observation", "AI Commentary tab")

            # ── Commentary tab wiring ─────────────────────────────────────────

            # Toggle between browse and search panels
            news_source_toggle.change(
                fn=toggle_news_source,
                inputs=[news_source_toggle],
                outputs=[hn_browse_panel, topic_search_panel])

            # HN browse
            hn_fetch_btn.click(
                fn=fetch_hn_stories,
                inputs=[hn_topic, hn_max],
                outputs=[hn_dropdown, hn_status])
            hn_dropdown.change(
                fn=select_hn_story,
                inputs=[hn_dropdown],
                outputs=[commentary_news])

            # Topic search
            search_btn.click(
                fn=search_news_by_topic,
                inputs=[search_topic, search_sources, search_max],
                outputs=[search_checkboxes, search_status])
            search_checkboxes.change(
                fn=select_search_result,
                inputs=[search_checkboxes],
                outputs=[commentary_news])
            select_all_btn.click(
                fn=select_all_search_results,
                inputs=[],
                outputs=[search_checkboxes])
            clear_sel_btn.click(
                fn=clear_search_results,
                inputs=[],
                outputs=[search_checkboxes])

            # Generate
            commentary_btn.click(
                fn=generate_commentary,
                inputs=[commentary_news, commentary_mode],
                outputs=[commentary_out, commentary_file,
                         commentary_cost, commentary_metrics])

            # KB save
            commentary_kb_btn.click(
                fn=open_kb_save_panel,
                inputs=[commentary_out],
                outputs=[com_accordion, com_kb_edit])
            com_kb_confirm.click(
                fn=lambda content, cat: save_content_to_kb(content, cat, "AI Commentary"),
                inputs=[com_kb_edit, com_kb_cat],
                outputs=[com_kb_status])

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
                    leadership_out     = gr.Textbox(label="Generated content",
                        lines=10, interactive=True)
                    leadership_file    = gr.Textbox(label="Saved to",
                        interactive=False, max_lines=1)
                    leadership_cost    = gr.Textbox(label="Cost",
                        interactive=False, max_lines=1)
                    leadership_metrics = gr.Textbox(label="Quality metrics",
                        lines=12, interactive=False)

                    leadership_kb_btn = gr.Button("💾 Save to KB", variant="secondary")
                    lea_accordion, lea_kb_edit, lea_kb_cat, lea_kb_confirm, lea_kb_status = \
                        _kb_save_section("Philosophy / Framework", "Leadership Signature tab")

            leadership_btn.click(
                fn=generate_leadership,
                inputs=[leadership_framework, leadership_format],
                outputs=[leadership_out, leadership_file,
                         leadership_cost, leadership_metrics])

            leadership_kb_btn.click(
                fn=open_kb_save_panel,
                inputs=[leadership_out],
                outputs=[lea_accordion, lea_kb_edit])
            lea_kb_confirm.click(
                fn=lambda content, cat: save_content_to_kb(content, cat, "Leadership Signature"),
                inputs=[lea_kb_edit, lea_kb_cat],
                outputs=[lea_kb_status])

        # ── Tab 5: Knowledge Base ─────────────────────────────────────────────
        with gr.TabItem("📚 Knowledge Base"):
            gr.Markdown(
                "Add new entries or browse existing knowledge base files.\n\n"
                "All changes are immediately available to the next generation — "
                "no restart needed. The pipeline reads KB files fresh on every call."
            )
            with gr.Row():

                # Left: Add new entry manually
                with gr.Column(scale=2):
                    gr.Markdown("### ➕ Add New Entry")
                    gr.Markdown(
                        "Use this to add a new story, achievement, observation, "
                        "or insight directly — without going through a content tab."
                    )
                    manual_category = gr.Dropdown(
                        choices=CATEGORIES,
                        value=CATEGORIES[0],
                        label="Category",
                    )
                    manual_target = gr.Textbox(
                        label="Target file (auto-selected from category)",
                        interactive=False,
                        max_lines=1,
                        value=f"primary / case_studies.md",
                    )
                    manual_content = gr.Textbox(
                        label="Content",
                        lines=12,
                        placeholder=(
                            "Paste or type the entry to add to the knowledge base.\n\n"
                            "Examples:\n"
                            "• A new case study: what was the problem, what did you do, "
                            "what was the outcome (with numbers)?\n"
                            "• A new industry observation: what trend are you seeing?\n"
                            "• A new framework insight: what is the principle and why?"
                        ),
                    )
                    manual_save_btn = gr.Button("💾 Save Entry", variant="primary")
                    manual_status   = gr.Textbox(
                        label="Save status", interactive=False, max_lines=2)

                # Right: Browse KB
                with gr.Column(scale=3):
                    gr.Markdown("### 📖 Browse Knowledge Base")
                    gr.Markdown(
                        "_Read-only view. Edit files directly in your editor "
                        "for structural changes._"
                    )
                    with gr.Row():
                        browse_kb_type = gr.Radio(
                            choices=["primary", "secondary"],
                            value="primary",
                            label="KB",
                            scale=1,
                        )
                        browse_file = gr.Dropdown(
                            choices=PRIMARY_FILES,
                            value=PRIMARY_FILES[0],
                            label="File",
                            interactive=True,
                            scale=2,
                        )
                        browse_refresh = gr.Button("🔄 Refresh", scale=1)

                    browse_content = gr.Textbox(
                        label="File content",
                        lines=24,
                        interactive=False,
                    )

            # KB tab wiring

            # Update target file label when category changes
            def _update_target_label(category: str) -> str:
                if category in kb_manager.CATEGORY_TO_FILE:
                    kb_type, filename = kb_manager.CATEGORY_TO_FILE[category]
                    return f"{kb_type} / {filename}.md"
                return "unknown"

            manual_category.change(
                fn=_update_target_label,
                inputs=[manual_category],
                outputs=[manual_target])

            manual_save_btn.click(
                fn=save_manual_kb_entry,
                inputs=[manual_content, manual_category],
                outputs=[manual_status])

            # Update file choices when KB type changes
            browse_kb_type.change(
                fn=update_file_choices,
                inputs=[browse_kb_type],
                outputs=[browse_file])

            # Load file content when file or KB type changes
            browse_file.change(
                fn=browse_kb_file,
                inputs=[browse_kb_type, browse_file],
                outputs=[browse_content])

            browse_refresh.click(
                fn=browse_kb_file,
                inputs=[browse_kb_type, browse_file],
                outputs=[browse_content])

        # ── Tab 6: Cost & Quality ─────────────────────────────────────────────
        with gr.TabItem("💰 Cost & Quality"):
            gr.Markdown(
                "Session costs and quality log.\n\n"
                "Full quality metrics with cosine similarity, vocabulary richness, "
                "specificity scores, and personal reference counts are saved to "
                "`output/quality_log.md` after every generation."
            )
            refresh_btn  = gr.Button("Refresh cost summary", variant="secondary")
            cost_display = gr.Markdown("Click Refresh to see current session costs.")
            refresh_btn.click(get_cost_summary, inputs=[], outputs=[cost_display])

    gr.Markdown(
        "---\n*Powered by OpenAI GPT-4o-mini · "
        "KB: primary + secondary · Live news: HackerNews + Dev.to + TechCrunch*"
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")
    app.launch()
