"""
Document Processor — Markdown ingestion and parsing.

Reads all markdown files from the knowledge base directories and returns
structured content ready for use in LLM prompts.

This is the entry point of the content pipeline: every content generation
request starts here, loading the context that makes outputs unique.
"""
import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("document_processor")

# Root of the knowledge base, relative to this file's location
KB_ROOT = Path(__file__).parent.parent / "knowledge_base"


def load_markdown_file(file_path: Path) -> Optional[str]:
    """
    Read a single markdown file and return its content as a string.

    Args:
        file_path: Path to the markdown file

    Returns:
        File content as string, or None if the file cannot be read
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        logger.debug("Loaded: %s (%d chars)", file_path.name, len(content))
        return content
    except FileNotFoundError:
        logger.error("File not found: %s", file_path)
        return None
    except Exception as e:
        logger.error("Could not read %s: %s", file_path, e)
        return None


def load_knowledge_base(kb_type: str = "primary") -> dict[str, str]:
    """
    Load all markdown files from a knowledge base directory.

    Args:
        kb_type: "primary" (company/personal docs) or "secondary" (research)

    Returns:
        Dict mapping filename (without extension) to file content.
        Empty dict if directory not found or no markdown files present.
    """
    kb_dir = KB_ROOT / kb_type

    if not kb_dir.exists():
        logger.error("Knowledge base directory not found: %s", kb_dir)
        return {}

    documents = {}
    md_files = list(kb_dir.glob("*.md"))

    if not md_files:
        logger.warning("No markdown files found in %s", kb_dir)
        return {}

    for file_path in sorted(md_files):
        content = load_markdown_file(file_path)
        if content:
            # Use filename without extension as the key
            key = file_path.stem
            documents[key] = content

    logger.info(
        "Loaded %d documents from %s knowledge base: %s",
        len(documents), kb_type, list(documents.keys())
    )
    return documents


def load_all_documents() -> dict[str, dict[str, str]]:
    """
    Load both primary and secondary knowledge bases.

    Returns:
        Dict with keys "primary" and "secondary", each containing
        a dict of filename -> content.
    """
    return {
        "primary":   load_knowledge_base("primary"),
        "secondary": load_knowledge_base("secondary"),
    }


def get_context_for_content_type(content_type: str) -> str:
    """
    Assemble the most relevant knowledge base context for a given content type.

    Different content types need different combinations of documents:
    - LinkedIn posts: bio + philosophy + positioning
    - AI commentary: bio + philosophy + AI trends
    - Executive bio: bio + case_studies + positioning
    - Leadership signature: philosophy + case_studies

    Args:
        content_type: One of "linkedin", "bio", "ai_commentary", "leadership"

    Returns:
        Concatenated markdown string with all relevant context,
        with clear section headers for the LLM to navigate.
    """
    all_docs = load_all_documents()
    primary   = all_docs.get("primary",   {})
    secondary = all_docs.get("secondary", {})

    # Define which documents are most relevant for each content type
    # Order matters — most important documents come first
    content_map = {
        "linkedin": {
            "primary":   ["bio", "leadership_philosophy", "positioning"],
            "secondary": ["ai_trends", "cto_market"],
        },
        "bio": {
            "primary":   ["bio", "case_studies", "positioning"],
            "secondary": [],
        },
        "ai_commentary": {
            "primary":   ["bio", "leadership_philosophy", "positioning"],
            "secondary": ["ai_trends"],
        },
        "leadership": {
            "primary":   ["leadership_philosophy", "case_studies", "bio"],
            "secondary": ["ai_trends"],
        },
    }

    # Default: use everything if content type is not recognised
    selected = content_map.get(content_type, {
        "primary":   list(primary.keys()),
        "secondary": list(secondary.keys()),
    })

    sections = []

    # Add primary documents
    for doc_key in selected.get("primary", []):
        if doc_key in primary:
            sections.append(f"## PRIMARY KNOWLEDGE BASE: {doc_key.upper()}\n\n{primary[doc_key]}")

    # Add secondary documents
    for doc_key in selected.get("secondary", []):
        if doc_key in secondary:
            sections.append(f"## SECONDARY RESEARCH: {doc_key.upper()}\n\n{secondary[doc_key]}")

    if not sections:
        logger.warning("No documents found for content type '%s'", content_type)
        return ""

    context = "\n\n---\n\n".join(sections)
    logger.info(
        "Assembled context for '%s': %d sections, %d total chars",
        content_type, len(sections), len(context)
    )
    return context


# ── Quick smoke test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s | %(levelname)-8s | %(message)s")

    print("Loading all knowledge base documents...\n")
    all_docs = load_all_documents()

    for kb_type, docs in all_docs.items():
        print(f"{kb_type.upper()} knowledge base ({len(docs)} documents):")
        for name, content in docs.items():
            print(f"  - {name}: {len(content)} chars")

    print("\nTesting context assembly for 'linkedin':")
    ctx = get_context_for_content_type("linkedin")
    print(f"  Total context: {len(ctx)} chars")
    print(f"  Preview: {ctx[:200]}...")
