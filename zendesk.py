import logging

import requests

logger = logging.getLogger(__name__)


class ZendeskClient:
    MAX_PER_PAGE = 100

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        logger.info("Initialized ZendeskClient for %s", self.base_url)

    def get_all_articles(self) -> list[dict]:
        articles = []
        url = f"{self.base_url}/api/v2/help_center/articles.json"
        params = {"per_page": self.MAX_PER_PAGE}

        while url:
            logger.debug("Fetching articles: %s", url)
            resp = self.session.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            articles.extend(data["articles"])
            page = data.get("page", "?")
            page_count = data.get("page_count", "?")
            logger.debug(
                "Got page %s/%s (%d articles so far)",
                page, page_count, len(articles),
            )
            url = data.get("next_page")
            params = {}

        logger.info("Fetched %d articles total", len(articles))
        return articles
