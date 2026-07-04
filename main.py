import logging
import os
from pathlib import Path

from transform import convert_article
from zendesk import ZendeskClient

ZENDESK_BASE_URL = os.getenv("ZENDESK_BASE_URL", "https://support.optisigns.com")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "articles")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)


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


if __name__ == "__main__":
    main()
