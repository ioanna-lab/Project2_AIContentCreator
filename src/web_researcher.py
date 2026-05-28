"""
Web Researcher — Fetches live industry context for content generation.

Used by the LinkedIn "Industry Observation" and "Thought Leadership" tones
to ground content in what the industry is saying RIGHT NOW, not just
what's in the static knowledge base.

Sources (all free, no API key required):
- HackerNews via Algolia search API
- Dev.to public API
- RSS feeds (TechCrunch, InfoQ Engineering)

Target: return 3-5 relevant snippets in under 10 seconds.
"""
import requests
import logging
import time
from datetime import datetime

logger = logging.getLogger("web_researcher")

# ── Source endpoints ──────────────────────────────────────────────────────────
HN_ALGOLIA      = "https://hn.algolia.com/api/v1/search"
DEVTO_API       = "https://dev.to/api/articles"
TECHCRUNCH_RSS  = "https://techcrunch.com/feed/"
INFOQ_RSS       = "https://feed.infoq.com/articles/ai"

REQUEST_TIMEOUT = 6  # seconds per source — keeps total under 10s


class WebResearcher:
    """
    Fetches live industry context from multiple free sources.

    Designed to be fast — each source has a hard timeout so the
    total fetch time stays under 10 seconds even if one source is slow.
    """

    def search(self, topic: str, max_results: int = 5) -> list[dict]:
        """
        Search all sources in parallel (sequential with timeouts).

        Args:
            topic:       The topic to search for
            max_results: Maximum total results to return

        Returns:
            List of result dicts with keys:
            title, snippet, source, url, published
        """
        logger.info("Searching web for: '%s'", topic)
        start = time.time()

        results = []

        # Each source is asked for max_results items so the deduplication step
        # has enough candidates to reach the requested total.
        # Previously these were hardcoded (3, 3, 2, 2) which ignored max_results.
        results += self._search_hackernews(topic, max_results=max_results)
        results += self._search_devto(topic, max_results=max_results)
        results += self._search_rss(TECHCRUNCH_RSS, topic, source="TechCrunch", max_results=max_results)
        results += self._search_rss(INFOQ_RSS, topic, source="InfoQ", max_results=max_results)

        # Deduplicate by title and limit to max_results
        seen   = set()
        unique = []
        for r in results:
            key = r["title"].lower()[:60]
            if key not in seen:
                seen.add(key)
                unique.append(r)
            if len(unique) >= max_results:
                break

        elapsed = time.time() - start
        logger.info(
            "Found %d results from %d sources in %.1fs",
            len(unique), 4, elapsed
        )
        return unique

    def _search_hackernews(self, topic: str, max_results: int = 3) -> list[dict]:
        """Search HackerNews via Algolia."""
        try:
            response = requests.get(
                HN_ALGOLIA,
                params={"query": topic, "tags": "story", "hitsPerPage": max_results * 2},
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            hits = response.json().get("hits", [])
            results = []
            for hit in hits[:max_results]:
                if not hit.get("title"):
                    continue
                ts = hit.get("created_at_i", 0)
                published = datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else ""
                results.append({
                    "title":     hit.get("title", ""),
                    "snippet":   hit.get("story_text", "")[:300] if hit.get("story_text") else "",
                    "source":    "Hacker News",
                    "url":       hit.get("url", f"https://news.ycombinator.com/item?id={hit.get('objectID')}"),
                    "published": published,
                    "points":    hit.get("points", 0),
                })
            logger.debug("HackerNews: %d results", len(results))
            return results
        except Exception as e:
            logger.warning("HackerNews search failed: %s", e)
            return []

    def _search_devto(self, topic: str, max_results: int = 3) -> list[dict]:
        """Search Dev.to public API."""
        try:
            response = requests.get(
                DEVTO_API,
                params={"tag": topic.lower().replace(" ", ""), "per_page": max_results * 2},
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            articles = response.json()
            results = []
            for article in articles[:max_results]:
                results.append({
                    "title":     article.get("title", ""),
                    "snippet":   article.get("description", "")[:300],
                    "source":    "Dev.to",
                    "url":       article.get("url", ""),
                    "published": article.get("published_at", "")[:10],
                    "points":    article.get("positive_reactions_count", 0),
                })
            logger.debug("Dev.to: %d results", len(results))
            return results
        except Exception as e:
            logger.warning("Dev.to search failed: %s", e)
            return []

    def _search_rss(self, feed_url: str, topic: str, source: str, max_results: int = 2) -> list[dict]:
        """
        Search an RSS feed by fetching it and filtering for topic keywords.
        No XML library needed — simple string matching on the raw XML.
        """
        try:
            response = requests.get(feed_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            content = response.text

            # Parse items from RSS XML manually
            # Extract <item> blocks and pull title + description + link
            import re
            items   = re.findall(r"<item>(.*?)</item>", content, re.DOTALL)
            results = []
            keywords = topic.lower().split()

            for item in items:
                title_match = re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>|<title>(.*?)</title>", item)
                desc_match  = re.search(r"<description><!\[CDATA\[(.*?)\]\]></description>|<description>(.*?)</description>", item, re.DOTALL)
                link_match  = re.search(r"<link>(.*?)</link>", item)

                title = (title_match.group(1) or title_match.group(2) or "").strip() if title_match else ""
                desc  = (desc_match.group(1)  or desc_match.group(2)  or "").strip() if desc_match  else ""
                url   = link_match.group(1).strip() if link_match else ""

                # Filter by keyword relevance
                text = (title + " " + desc).lower()
                if any(kw in text for kw in keywords):
                    results.append({
                        "title":     title[:120],
                        "snippet":   re.sub(r"<[^>]+>", "", desc)[:300],  # strip HTML tags
                        "source":    source,
                        "url":       url,
                        "published": "",
                        "points":    0,
                    })

                if len(results) >= max_results:
                    break

            logger.debug("%s: %d results", source, len(results))
            return results

        except Exception as e:
            logger.warning("%s RSS search failed: %s", source, e)
            return []

    def format_for_prompt(self, results: list[dict]) -> str:
        """
        Format search results as a text block for the LLM prompt.

        Args:
            results: List of result dicts from search()

        Returns:
            Formatted string ready to inject into the prompt as industry context
        """
        if not results:
            return "No industry context found — using knowledge base only."

        lines = ["CURRENT INDUSTRY CONTEXT (live sources):\n"]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r['title']} [{r['source']}]")
            if r.get("snippet"):
                lines.append(f"   {r['snippet'][:200]}")
            if r.get("url"):
                lines.append(f"   {r['url']}")
            lines.append("")

        return "\n".join(lines)

    def format_for_display(self, results: list[dict]) -> str:
        """
        Format results for display in the Gradio UI.

        Args:
            results: List of result dicts from search()

        Returns:
            Human-readable string for the Gradio textbox
        """
        if not results:
            return "No results found — will use knowledge base only."

        lines = []
        for i, r in enumerate(results, 1):
            pts = f" · {r['points']} pts" if r.get("points") else ""
            pub = f" · {r['published']}" if r.get("published") else ""
            lines.append(f"{i}. [{r['source']}{pts}{pub}]")
            lines.append(f"   {r['title']}")
            if r.get("snippet"):
                lines.append(f"   {r['snippet'][:150]}...")
            lines.append("")

        return "\n".join(lines)


# ── Quick smoke test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")

    researcher = WebResearcher()
    topic      = "AI governance engineering teams"

    print(f"\nSearching for: '{topic}'\n")
    start   = time.time()
    results = researcher.search(topic, max_results=5)
    elapsed = time.time() - start

    print(f"Found {len(results)} results in {elapsed:.1f}s\n")
    print(researcher.format_for_display(results))
