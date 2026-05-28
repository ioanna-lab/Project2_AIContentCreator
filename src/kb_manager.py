"""
KB Manager — Knowledge Base read/write operations.

Handles all KB file management: reading, browsing, and appending new entries.
Designed so that any addition is immediately available to the next generation
(document_processor reads files fresh on every pipeline call — no restart needed).

Categories map to specific KB files:
  Primary KB  → bio.md, case_studies.md, leadership_philosophy.md, positioning.md
  Secondary KB → ai_trends.md, cto_market.md
"""
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("kb_manager")

KB_ROOT = Path(__file__).parent.parent / "knowledge_base"

# ── Constants (imported by gradio_app.py for dropdowns) ──────────────────────

PRIMARY_FILES = ["bio", "case_studies", "leadership_philosophy", "positioning"]
SECONDARY_FILES = ["ai_trends", "cto_market"]

CATEGORIES = [
    "Case Study",
    "Achievement / Metric",
    "Philosophy / Framework",
    "Bio / Positioning",
    "Industry Observation",
    "Market / CTO Insight",
]

# Maps each category to (kb_type, filename)
CATEGORY_TO_FILE: dict[str, tuple[str, str]] = {
    "Case Study":             ("primary",   "case_studies"),
    "Achievement / Metric":   ("primary",   "case_studies"),
    "Philosophy / Framework": ("primary",   "leadership_philosophy"),
    "Bio / Positioning":      ("primary",   "bio"),
    "Industry Observation":   ("secondary", "ai_trends"),
    "Market / CTO Insight":   ("secondary", "cto_market"),
}

# Default category suggestion per content tab
TAB_DEFAULT_CATEGORY: dict[str, str] = {
    "linkedin":    "Philosophy / Framework",
    "bio":         "Bio / Positioning",
    "commentary":  "Industry Observation",
    "leadership":  "Philosophy / Framework",
}


# ── Read operations ───────────────────────────────────────────────────────────

def get_kb_file_path(kb_type: str, filename: str) -> Path:
    """Return the absolute path for a KB file."""
    return KB_ROOT / kb_type / f"{filename}.md"


def read_kb_file(kb_type: str, filename: str) -> str:
    """
    Read and return the content of a KB file.

    Args:
        kb_type:  "primary" or "secondary"
        filename: File stem without .md extension

    Returns:
        File content as string, or an error message.
    """
    path = get_kb_file_path(kb_type, filename)
    try:
        content = path.read_text(encoding="utf-8")
        logger.debug("Read %s (%d chars)", path.name, len(content))
        return content
    except FileNotFoundError:
        return f"[File not found: {path}]\n\nThis file does not exist yet in the knowledge base."
    except Exception as e:
        return f"[Error reading {path.name}: {e}]"


def list_all_kb_files() -> dict[str, list[str]]:
    """
    Return all existing KB files grouped by kb_type.

    Returns:
        {"primary": ["bio", "case_studies", ...], "secondary": ["ai_trends", ...]}
    """
    result: dict[str, list[str]] = {}
    for kb_type in ["primary", "secondary"]:
        kb_dir = KB_ROOT / kb_type
        if kb_dir.exists():
            result[kb_type] = [f.stem for f in sorted(kb_dir.glob("*.md"))]
        else:
            result[kb_type] = []
    return result


# ── Write operations ──────────────────────────────────────────────────────────

def append_to_kb(
    kb_type: str,
    filename: str,
    content: str,
    category: str = "",
    source_tab: str = "",
) -> tuple[bool, str]:
    """
    Append a new entry to an existing KB file.

    The entry is wrapped in a timestamped comment block so it is clearly
    marked as a later addition and can be found/removed easily.

    Args:
        kb_type:    "primary" or "secondary"
        filename:   File stem (e.g. "case_studies" — no .md)
        content:    The text to append
        category:   Optional category label for the header comment
        source_tab: Which app tab triggered the save (for traceability)

    Returns:
        (success: bool, message: str)
    """
    if not content.strip():
        return False, "Nothing to save — content is empty."

    path = get_kb_file_path(kb_type, filename)

    if not path.parent.exists():
        return False, (
            f"KB directory not found: {path.parent}\n"
            f"Create the folder or check your KB_ROOT path."
        )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    meta_parts = [f"Added: {timestamp}"]
    if category:
        meta_parts.append(f"Category: {category}")
    if source_tab:
        meta_parts.append(f"Source: {source_tab}")

    divider = "\n\n---\n\n"
    header  = f"<!-- {' | '.join(meta_parts)} -->\n\n"
    entry   = divider + header + content.strip() + "\n"

    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(entry)
        char_count = len(content.strip())
        logger.info(
            "Appended %d chars to %s/%s.md (category: %s)",
            char_count, kb_type, filename, category
        )
        return True, (
            f"✓ Saved to knowledge_base/{kb_type}/{filename}.md  "
            f"({char_count} chars) — available in next generation."
        )
    except PermissionError:
        return False, f"Permission denied writing to {path.name}."
    except Exception as e:
        logger.error("Failed to write to %s: %s", path, e)
        return False, f"Error saving: {e}"


def append_to_kb_by_category(
    content: str,
    category: str,
    source_tab: str = "",
) -> tuple[bool, str]:
    """
    Convenience wrapper: look up the right file from CATEGORY_TO_FILE
    and append the content.

    Args:
        content:    Text to save
        category:   One of the CATEGORIES strings
        source_tab: Optional tab name for traceability

    Returns:
        (success: bool, message: str)
    """
    if category not in CATEGORY_TO_FILE:
        return False, (
            f"Unknown category: '{category}'. "
            f"Choose from: {', '.join(CATEGORY_TO_FILE.keys())}"
        )

    kb_type, filename = CATEGORY_TO_FILE[category]
    return append_to_kb(
        kb_type=kb_type,
        filename=filename,
        content=content,
        category=category,
        source_tab=source_tab,
    )


# ── Quick smoke test ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s | %(levelname)-8s | %(message)s")

    print("KB files found:")
    for kb_type, files in list_all_kb_files().items():
        print(f"  {kb_type}: {files}")

    print("\nCategory → file mapping:")
    for cat, (kbt, fn) in CATEGORY_TO_FILE.items():
        path = get_kb_file_path(kbt, fn)
        exists = "✓" if path.exists() else "✗ (not found)"
        print(f"  {cat:30s} → {kbt}/{fn}.md  {exists}")
