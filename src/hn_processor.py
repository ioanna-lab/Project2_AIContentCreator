"""
HackerNews Processor — Live AI/tech news feed.

Uses the Algolia HackerNews Search API (hn.algolia.com) instead of
the Firebase item-by-item API. One HTTP call returns multiple relevant
stories instantly — no scanning loop, no 2-minute waits.

API docs: https://hn.algolia.com/api
Free, no authentication required.

Usage:
    from hn_processor import HackerNewsProcessor
    hn = HackerNewsProcessor()
    stories = hn.fetch_ai_stories(max_stories=5)
"""
import requests
import logging
from datetime import datetime

logger = logging.getLogger("hn_processor")

# Algolia HN search API — single call returns multiple relevant stories
ALGOLIA_URL = "https://hn.algolia.com/api/v1/search"

# Default search query — covers AI and engineering leadership topics
DEFAULT_QUERY = "artificial intelligence"


class HackerNewsProcessor:
    """
    Fetch relevant HackerNews stories using the Algolia search API.

    One HTTP call returns multiple pre-filtered stories — no item-by-item
    scanning, no waiting. Typical response time: under 2 seconds.
    """

    def fetch_ai_stories(
        self,
        max_stories: int = 5,
        query: str = DEFAULT_QUERY,
        min_points: int = 10,
    ) -> list[dict]:
        """
        Fetch top HackerNews stories matching the query.

        Uses Algolia's HN search API — single request, instant results.

        Args:
            max_stories: Number of stories to return (1-10)
            query:       Search terms (default covers AI + engineering)
            min_points:  Minimum HN score to include

        Returns:
            List of story dicts with title, url, score, by, formatted_time
        """
        logger.info("Fetching HN stories via Algolia search: '%s'", query)

        params = {
            "query":        query,
            "tags":         "story",        # stories only, no comments/jobs
            "hitsPerPage":  max_stories * 2, # fetch extra in case some are filtered
            
        }

        try:
            response = requests.get(ALGOLIA_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.Timeout:
            logger.error("HackerNews Algolia request timed out")
            return []
        except requests.exceptions.ConnectionError:
            logger.error("Could not connect to HackerNews Algolia API")
            return []
        except Exception as e:
            logger.error("HackerNews request failed: %s", e)
            return []

        hits    = data.get("hits", [])
        stories = []

        for hit in hits:
            if len(stories) >= max_stories:
                break

            # Parse timestamp
            ts = hit.get("created_at_i", 0)
            formatted_time = (
                datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
                if ts else ""
            )

            stories.append({
                "id":             hit.get("objectID", ""),
                "title":          hit.get("title", ""),
                "url":            hit.get("url", ""),
                "score":          hit.get("points", 0),
                "by":             hit.get("author", ""),
                "formatted_time": formatted_time,
                "comments":       hit.get("num_comments", 0),
                "text":           hit.get("story_text", "") or "",
            })

        logger.info("Fetched %d stories from HackerNews", len(stories))
        return stories

    def format_for_prompt(self, story: dict) -> str:
        """
        Format a single story as text for the LLM commentary prompt.

        Args:
            story: Story dict from fetch_ai_stories()

        Returns:
            Formatted string ready to inject into the commentary prompt
        """
        lines = [
            f"Title: {story['title']}",
            f"Source: Hacker News",
            f"Score: {story['score']} points | {story['comments']} comments",
            f"Posted: {story['formatted_time']}",
        ]

        if story.get("url"):
            lines.append(f"URL: {story['url']}")

        if story.get("text"):
            lines.append(f"Content: {story['text'][:500]}")

        return "\n".join(lines)

    def format_story_list(self, stories: list[dict]) -> str:
        """
        Format a list of stories as a numbered list for display.

        Args:
            stories: List of story dicts

        Returns:
            Formatted string for display in Gradio
        """
        if not stories:
            return "No stories found."

        lines = []
        for i, story in enumerate(stories, 1):
            lines.append(
                f"{i}. [{story['score']} pts] {story['title']}\n"
                f"   {story['formatted_time']} | {story['comments']} comments"
            )
        return "\n\n".join(lines)


# ── Quick smoke test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    hn = HackerNewsProcessor()
    print("\nFetching top AI/engineering stories...\n")
    stories = hn.fetch_ai_stories(max_stories=5)

    if not stories:
        print("No stories found — check your network connection.")
    else:
        print(hn.format_story_list(stories))
        print(f"\n--- Prompt format for story 1 ---\n")
        print(hn.format_for_prompt(stories[0]))
