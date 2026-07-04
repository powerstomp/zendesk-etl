import logging
import os
from pathlib import Path

from gemini import GeminiClient
from transform import convert_article
from zendesk import ZendeskClient

ZENDESK_BASE_URL = os.getenv("ZENDESK_BASE_URL", "https://support.optisigns.com")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "articles")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
GOOGLE_STORE_RESOURCE_NAME = os.getenv("GOOGLE_STORE_RESOURCE_NAME")

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logging.getLogger("httpx").setLevel(logging.WARNING)


def main() -> None:
    client = ZendeskClient(ZENDESK_BASE_URL)
    articles = client.get_all_articles()
    logger.info("Fetched %d articles", len(articles))

    articles = [convert_article(a) for a in articles]
    logger.info("Transformed %d articles", len(articles))

    output = Path(OUTPUT_DIR)
    output.mkdir(parents=True, exist_ok=True)

    for a in articles:
        path = output / f"{a.id}.md"
        path.write_text(
            f"""Article URL: {a.url}
# {a.title}

{a.body}
""",
            encoding="utf-8",
        )

    logger.info("Wrote %d articles to %s", len(articles), output.resolve())

    if GOOGLE_STORE_RESOURCE_NAME:
        gclient = GeminiClient(GOOGLE_STORE_RESOURCE_NAME, OUTPUT_DIR)
        logger.info("Syncing documents...")
        result = gclient.sync(articles)
        logger.info(
            "Synced: %d created, %d updated, %d deleted",
            result.created,
            result.updated,
            result.deleted,
        )
    else:
        logger.warning("GOOGLE_STORE_RESOURCE_NAME not set, skipping Gemini sync")


if __name__ == "__main__":
    main()
