"""
Main application entry point — AI Content Creator (Week 1 MVP).

Interactive CLI that lets you choose a content type, provide inputs,
and generate unique content grounded in Ioanna's knowledge base.

Week 1 content types:
  1. LinkedIn post
  2. Executive bio
  3. AI news commentary
  4. Leadership signature content

Run with:
    python main.py
"""
import sys
import logging
from content_pipeline import ContentPipeline


def configure_logging():
    """Set up logging: INFO to console, DEBUG to file."""
    log_format  = "%(asctime)s | %(levelname)-8s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers.clear()

    formatter = logging.Formatter(log_format, datefmt=date_format)

    # Console: INFO+ — clean progress for the user
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    root.addHandler(console)

    # File: DEBUG+ — full audit trail
    file_handler = logging.FileHandler("content_creator.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)


def menu_linkedin(pipeline: ContentPipeline):
    """Handle LinkedIn post generation flow."""
    print("\n--- LinkedIn Post Generator ---")
    topic = input("Topic or angle for the post: ").strip()
    if not topic:
        topic = "Engineering measurement: why making invisible problems visible is the highest-leverage leadership act"
        print(f"Using default topic: {topic}")

    print("\nTone options: thought_leadership / personal_story / industry_observation")
    tone = input("Tone [thought_leadership]: ").strip() or "thought leadership"

    print("\nGenerating LinkedIn post...")
    result = pipeline.generate_linkedin_post(topic=topic, tone=tone)

    print(f"\n{'='*70}")
    print("GENERATED LINKEDIN POST")
    print(f"{'='*70}")
    print(result["content"])
    print(f"{'='*70}")

    save = input("\nSave to file? (y/n): ").strip().lower()
    if save == "y":
        path = pipeline.save_result(result)
        print(f"Saved to: {path}")


def menu_bio(pipeline: ContentPipeline):
    """Handle executive bio generation flow."""
    print("\n--- Executive Bio Generator ---")
    print("Length options: short / medium / long")
    length = input("Length [medium]: ").strip() or "medium"

    print("Purpose options: general / speaking / board / job_application")
    purpose = input("Purpose [general]: ").strip() or "general"

    print("\nGenerating executive bio...")
    result = pipeline.generate_executive_bio(length=length, purpose=purpose)

    print(f"\n{'='*70}")
    print(f"GENERATED BIO ({length.upper()}, {purpose.upper()})")
    print(f"{'='*70}")
    print(result["content"])
    print(f"{'='*70}")

    save = input("\nSave to file? (y/n): ").strip().lower()
    if save == "y":
        path = pipeline.save_result(result)
        print(f"Saved to: {path}")


def menu_ai_commentary(pipeline: ContentPipeline):
    """Handle AI news commentary generation flow."""
    print("\n--- AI News Commentary Generator ---")
    print("Paste the news headline or summary (press Enter twice when done):")

    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    news_item = "\n".join(lines).strip()

    if not news_item:
        news_item = "OpenAI releases new model with improved reasoning capabilities and lower costs"
        print(f"Using example: {news_item}")

    source = input("Source name (e.g. Hacker News, TechCrunch) [optional]: ").strip()

    print("\nGenerating commentary...")
    result = pipeline.generate_ai_commentary(news_item=news_item, source=source)

    print(f"\n{'='*70}")
    print("GENERATED AI COMMENTARY")
    print(f"{'='*70}")
    print(result["content"])
    print(f"{'='*70}")

    save = input("\nSave to file? (y/n): ").strip().lower()
    if save == "y":
        path = pipeline.save_result(result)
        print(f"Saved to: {path}")


def menu_leadership(pipeline: ContentPipeline):
    """Handle leadership signature content generation flow."""
    print("\n--- Leadership Signature Content ---")
    print("Available frameworks: QMI / Engineering Manifesto / 60/40 model / Pre-emptive Scaling")
    framework = input("Framework name: ").strip() or "QMI"

    print("Format options: explanation / linkedin_post / speaking_abstract")
    format_type = input("Format [linkedin_post]: ").strip() or "linkedin_post"

    print(f"\nGenerating {format_type} for {framework}...")
    result = pipeline.generate_leadership_signature(
        framework=framework, format_type=format_type
    )

    print(f"\n{'='*70}")
    print(f"GENERATED: {framework} — {format_type.upper()}")
    print(f"{'='*70}")
    print(result["content"])
    print(f"{'='*70}")

    save = input("\nSave to file? (y/n): ").strip().lower()
    if save == "y":
        path = pipeline.save_result(result)
        print(f"Saved to: {path}")


def main():
    """Entry point: show menu, run selections, print cost summary."""
    configure_logging()

    print("=" * 70)
    print("AI CONTENT CREATOR — Ioanna Renta Personal Brand Engine")
    print("Week 1 MVP — Knowledge Base + LLM Pipeline")
    print("=" * 70)

    pipeline = ContentPipeline()

    while True:
        print("\n--- CONTENT TYPE MENU ---")
        print("1. LinkedIn thought leadership post")
        print("2. Executive bio")
        print("3. AI news commentary")
        print("4. Leadership signature content (QMI, Manifesto, etc.)")
        print("5. Show cost summary")
        print("0. Exit")

        choice = input("\nChoose [0-5]: ").strip()

        try:
            if choice == "1":
                menu_linkedin(pipeline)
            elif choice == "2":
                menu_bio(pipeline)
            elif choice == "3":
                menu_ai_commentary(pipeline)
            elif choice == "4":
                menu_leadership(pipeline)
            elif choice == "5":
                pipeline.print_cost_summary()
            elif choice == "0":
                pipeline.print_cost_summary()
                print("\nGoodbye!")
                break
            else:
                print("Invalid choice — enter 0-5")

        except KeyboardInterrupt:
            print("\n\nCancelled.")
            break
        except Exception as e:
            logging.error("Error: %s", e)
            print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()
