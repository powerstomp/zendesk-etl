import logging

from zendesk import ZendeskClient

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)


def main() -> None:
    client = ZendeskClient("https://support.optisigns.com")
    articles = client.get_all_articles()
    logger.info("Done — %d articles retrieved", len(articles))


if __name__ == "__main__":
    main()
