"""
Trello Manager — Automated board setup and card management.

Connects to your existing Trello board and:
1. Creates all workflow columns (lists)
2. Creates all project cards with FR IDs and descriptions
3. Adds WIP limit and Definition of Done to the board
4. Can update card status as work progresses

Board: ACFT0520 - Project 2 - Ioanna
URL: https://trello.com/b/kteKFdzb/treloforleadership

Usage:
    python trello_manager.py setup                              # Full board setup
    python trello_manager.py status                             # Show current board status
    python trello_manager.py move "card name" "list name"       # Move a card
    python trello_manager.py add "list name" "card name" "desc" # Add a new card
"""
import os
import sys
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("trello_manager")

# ── Trello API config ─────────────────────────────────────────────────────────
API_KEY  = os.getenv("TRELLO_API_KEY")
TOKEN    = os.getenv("TRELLO_TOKEN")
BOARD_ID = "kteKFdzb"
BASE_URL = "https://api.trello.com/1"


def _auth() -> dict:
    """Return auth params appended to every request."""
    return {"key": API_KEY, "token": TOKEN}


def _get(endpoint: str, params: dict = {}) -> dict | list | None:
    """Make a GET request to the Trello API."""
    try:
        response = requests.get(
            f"{BASE_URL}/{endpoint}",
            params={**_auth(), **params},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error("Trello API error: %s", e)
        return None
    except Exception as e:
        logger.error("Request failed: %s", e)
        return None


def _post(endpoint: str, data: dict = {}) -> dict | None:
    """Make a POST request to the Trello API."""
    try:
        response = requests.post(
            f"{BASE_URL}/{endpoint}",
            params=_auth(),
            json=data,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error("Trello POST error: %s — %s", e, e.response.text if e.response else "")
        return None
    except Exception as e:
        logger.error("Request failed: %s", e)
        return None


def _put(endpoint: str, data: dict = {}) -> dict | None:
    """Make a PUT request to the Trello API."""
    try:
        response = requests.put(
            f"{BASE_URL}/{endpoint}",
            params=_auth(),
            json=data,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error("Trello PUT error: %s", e)
        return None


# ── Board inspection ──────────────────────────────────────────────────────────

def get_board_lists() -> dict[str, str]:
    """Return all lists on the board as {list_name: list_id}."""
    lists = _get(f"boards/{BOARD_ID}/lists")
    if not lists:
        return {}
    return {lst["name"]: lst["id"] for lst in lists}


def get_list_cards(list_id: str) -> list[dict]:
    """Return all cards in a given list."""
    cards = _get(f"lists/{list_id}/cards")
    return cards or []


# ── Board setup ───────────────────────────────────────────────────────────────

COLUMNS = [
    "Backlog",
    "This Week",
    "In Progress  [WIP: 2]",
    "Review",
    "Done",
]

BACKLOG_CARDS = [
    (
        "[FR-001/002] Knowledge base markdown files",
        "Set up primary and secondary knowledge base markdown files.\n\n"
        "Primary: bio.md, leadership_philosophy.md, case_studies.md, positioning.md\n"
        "Secondary: ai_trends.md, cto_market.md\n\n"
        "Acceptance criteria: all files load successfully via document_processor.py\n"
        "Requirement: FR-001, FR-002"
    ),
    (
        "[FR-003] document_processor.py — context assembly",
        "Build the markdown ingestion module.\n\n"
        "- load_markdown_file()\n"
        "- load_knowledge_base()\n"
        "- get_context_for_content_type()\n\n"
        "Acceptance criteria: given a content_type string, returns relevant "
        "documents concatenated with section headers\n"
        "Requirement: FR-003"
    ),
    (
        "[FR-004] llm_integration.py — OpenAI wrapper",
        "Build the LLM client with cost tracking.\n\n"
        "- LLMClient.generate(system_prompt, user_prompt)\n"
        "- CostTracker.track() and summary()\n"
        "- Rate limiting\n\n"
        "Acceptance criteria: given prompts, returns response string and tracks cost\n"
        "Requirement: FR-004"
    ),
    (
        "[FR-005/006] prompt_templates.py — LinkedIn + bio templates",
        "Build prompt templates for Week 1 content types.\n\n"
        "- IOANNA_SYSTEM_PROMPT (shared voice guidelines)\n"
        "- linkedin_post_template()\n"
        "- executive_bio_template()\n\n"
        "Acceptance criteria: generated content references specific Ioanna data points\n"
        "Requirement: FR-005, FR-006"
    ),
    (
        "[FR-007/008] prompt_templates.py — commentary + leadership templates",
        "Build remaining prompt templates.\n\n"
        "- ai_commentary_template()\n"
        "- leadership_signature_template()\n\n"
        "Acceptance criteria: commentary references at least one Ioanna framework\n"
        "Requirement: FR-007, FR-008"
    ),
    (
        "[FR-009/010] content_pipeline.py — orchestration layer",
        "Build the pipeline connecting all modules.\n\n"
        "- ContentPipeline.generate_linkedin_post()\n"
        "- ContentPipeline.generate_executive_bio()\n"
        "- ContentPipeline.generate_ai_commentary()\n"
        "- ContentPipeline.generate_leadership_signature()\n"
        "- ContentPipeline.save_result()\n\n"
        "Acceptance criteria: end-to-end flow works for all 4 content types\n"
        "Requirement: FR-009, FR-010"
    ),
    (
        "main.py — CLI interface",
        "Build the interactive CLI menu.\n\n"
        "- Menu for all 4 content types\n"
        "- Input prompts per content type\n"
        "- Cost summary on exit\n"
        "- Logging to file\n\n"
        "Acceptance criteria: first-time user generates content within 5 minutes of setup"
    ),
    (
        "Project setup — .env, requirements.txt, .gitignore, README",
        "Environment and documentation setup.\n\n"
        "- .env.example with all required keys\n"
        "- requirements.txt with pinned versions\n"
        "- .gitignore excluding .env and output/\n"
        "- README with setup instructions\n\n"
        "Acceptance criteria: fresh clone + pip install + python main.py works"
    ),
    (
        "[FR-011] HackerNews API integration (Week 2)",
        "Integrate HackerNews API for live AI news feed.\n\n"
        "- Fetch top stories by topic\n"
        "- Filter for AI/engineering relevance\n"
        "- Feed into ai_commentary_template()\n\n"
        "Acceptance criteria: given a topic, system returns top N HN stories "
        "and generates commentary\n"
        "Requirement: FR-011\n"
        "NOTE: Week 2 task — do not start until core pipeline is working"
    ),
    (
        "Uniqueness comparison documentation (Week 2)",
        "Create side-by-side comparison showing system output vs generic ChatGPT.\n\n"
        "- Same prompt, two outputs\n"
        "- Annotate the differences\n"
        "- Add to README and presentation\n\n"
        "Acceptance criteria: comparison clearly shows brand alignment and specificity"
    ),
    (
        "Polish prompts and test all 4 content types (Week 2)",
        "Iterate on prompt templates based on Week 1 output quality.\n\n"
        "- Test each content type 3+ times\n"
        "- Refine system prompt if outputs are too generic\n"
        "- Update prompt tracking log in PROJECT_REQUIREMENTS.md"
    ),
    (
        "Kanban planning screenshot — p2-kanban-planning.png",
        "Take full-board screenshot after initial planning.\n\n"
        "Filename: p2-kanban-planning.png\n"
        "Submit with project deliverables.\n"
        "NOTE: Take this screenshot NOW before moving any cards."
    ),
    (
        "Kanban midpoint screenshot — p2-kanban-midpoint.png",
        "Take full-board screenshot at project midpoint (end of Week 1).\n\n"
        "Filename: p2-kanban-midpoint.png\n"
        "Board should show cards in progress and some in Done."
    ),
    (
        "Kanban final screenshot — p2-kanban-final.png",
        "Take full-board screenshot before final submission.\n\n"
        "Filename: p2-kanban-final.png\n"
        "Most cards should be in Done."
    ),
]

IN_PROGRESS_CARDS = [
    (
        "Trello board setup and API integration",
        "Set up ACFT0520 board with columns, WIP limits, and cards.\n\n"
        "- Create trello_manager.py\n"
        "- Connect via Trello API\n"
        "- Auto-create all cards\n\n"
        "Acceptance criteria: board visible with all cards and correct columns\n"
        "Status: IN PROGRESS"
    ),
]

DONE_CARDS = [
    (
        "PROJECT_REQUIREMENTS.md — initial version",
        "Created project requirements file at repository root.\n\n"
        "Includes: MVP scope, functional requirements, acceptance criteria, "
        "Kanban setup, AI coding-agent rules, prompt tracking log, change log.\n\n"
        "Status: DONE ✓"
    ),
]


def create_list(name: str, pos: str = "bottom") -> str | None:
    """Create a new list on the board and return its ID."""
    result = _post(f"boards/{BOARD_ID}/lists", {"name": name, "pos": pos})
    if result:
        logger.info("Created list: %s", name)
        return result["id"]
    return None


def create_card(list_id: str, name: str, description: str = "") -> dict | None:
    """Create a card in a list and return the card dict."""
    result = _post("cards", {
        "idList": list_id,
        "name":   name,
        "desc":   description,
        "pos":    "bottom",
    })
    if result:
        logger.info("Created card: %s", name[:50])
    return result


def update_board_description() -> None:
    """Add WIP limit and Definition of Done to the board description."""
    description = (
        "ACFT0520 - Project 2 - Ioanna Renta\n\n"
        "AI Content Creator — Personal Brand Engine\n\n"
        "WIP LIMIT: Maximum 2 cards In Progress at any time.\n\n"
        "DEFINITION OF DONE:\n"
        "- Code committed to GitHub\n"
        "- Tested manually (python module.py passes)\n"
        "- Output file generated if applicable\n"
        "- README updated if applicable\n"
        "- Prompt tracking log updated in PROJECT_REQUIREMENTS.md\n\n"
        "WORKFLOW: Backlog → This Week → In Progress [WIP:2] → Review → Done"
    )
    _put(f"boards/{BOARD_ID}", {"desc": description})
    logger.info("Updated board description with WIP limit and DoD")


def setup_board() -> None:
    """
    Full board setup: create all lists and cards.
    Safe to run multiple times — checks for existing lists first.
    """
    print("\n🚀 Setting up ACFT0520 - Project 2 - Ioanna board...")

    existing = get_board_lists()
    print(f"   Existing lists: {list(existing.keys())}")

    list_ids = {}
    for col in COLUMNS:
        if col in existing:
            list_ids[col] = existing[col]
            print(f"   ✓ List already exists: {col}")
        else:
            new_id = create_list(col)
            if new_id:
                list_ids[col] = new_id
                print(f"   ✓ Created list: {col}")

    update_board_description()
    print("   ✓ Board description updated (WIP limit + Definition of Done)")

    backlog_id = list_ids.get("Backlog")
    if backlog_id:
        print(f"\n   Creating {len(BACKLOG_CARDS)} Backlog cards...")
        for name, desc in BACKLOG_CARDS:
            create_card(backlog_id, name, desc)

    in_progress_id = list_ids.get("In Progress  [WIP: 2]")
    if in_progress_id:
        print(f"\n   Creating {len(IN_PROGRESS_CARDS)} In Progress cards...")
        for name, desc in IN_PROGRESS_CARDS:
            create_card(in_progress_id, name, desc)

    done_id = list_ids.get("Done")
    if done_id:
        print(f"\n   Creating {len(DONE_CARDS)} Done cards...")
        for name, desc in DONE_CARDS:
            create_card(done_id, name, desc)

    print("\n✅ Board setup complete!")
    print(f"   View your board: https://trello.com/b/{BOARD_ID}")


def show_status() -> None:
    """Print current board status — lists and card counts."""
    print(f"\n📋 Board status: https://trello.com/b/{BOARD_ID}\n")

    lists = get_board_lists()
    if not lists:
        print("Could not fetch board lists — check your API key and token.")
        return

    for list_name, list_id in lists.items():
        cards = get_list_cards(list_id)
        print(f"  {list_name}: {len(cards)} card(s)")
        for card in cards:
            print(f"    - {card['name'][:70]}")


def move_card(card_name_fragment: str, target_list_name: str) -> None:
    """
    Move a card to a different list by partial name match.

    Args:
        card_name_fragment: Part of the card name to search for
        target_list_name:   Exact name of the target list
    """
    lists = get_board_lists()
    target_id = lists.get(target_list_name)

    if not target_id:
        print(f"List '{target_list_name}' not found. Available: {list(lists.keys())}")
        return

    for list_name, list_id in lists.items():
        cards = get_list_cards(list_id)
        for card in cards:
            if card_name_fragment.lower() in card["name"].lower():
                result = _put(f"cards/{card['id']}", {"idList": target_id})
                if result:
                    print(f"✓ Moved '{card['name'][:60]}' → {target_list_name}")
                return

    print(f"Card containing '{card_name_fragment}' not found.")


def add_card(list_name: str, card_name: str, description: str = "") -> None:
    """
    Add a new card to any list by name.

    Args:
        list_name:   Exact name of the target list
        card_name:   Name of the new card
        description: Optional card description
    """
    lists = get_board_lists()
    list_id = lists.get(list_name)

    if not list_id:
        print(f"List '{list_name}' not found.")
        print(f"Available lists: {list(lists.keys())}")
        return

    result = create_card(list_id, card_name, description)
    if result:
        print(f"✓ Card created: {card_name}")
        print(f"  URL: {result.get('shortUrl', '')}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if not API_KEY or not TOKEN:
        print("❌ TRELLO_API_KEY and TRELLO_TOKEN must be set in your .env file")
        sys.exit(1)

    command = sys.argv[1] if len(sys.argv) > 1 else "setup"

    if command == "setup":
        setup_board()

    elif command == "status":
        show_status()

    elif command == "move" and len(sys.argv) == 4:
        move_card(sys.argv[2], sys.argv[3])

    elif command == "add" and len(sys.argv) >= 4:
        list_name  = sys.argv[2]
        card_name  = sys.argv[3]
        card_desc  = sys.argv[4] if len(sys.argv) > 4 else ""
        add_card(list_name, card_name, card_desc)

    else:
        print("Usage:")
        print("  python3 trello_manager.py setup")
        print("  python3 trello_manager.py status")
        print('  python3 trello_manager.py move "card name" "list name"')
        print('  python3 trello_manager.py add "list name" "card name" "description"')