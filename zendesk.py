from datetime import datetime
from logging import getLogger

import requests
from pydantic import BaseModel

logger = getLogger(__name__)


class ZendeskArticle(BaseModel):
    id: int
    title: str
    html_url: str
    body: str
    locale: str
    created_at: datetime
    updated_at: datetime


class ZendeskClient:
    MAX_PER_PAGE = 100

    def __init__(self, base_url: str, locale: str = "en-us"):
        self.base_url = base_url.rstrip("/")
        self.locale = locale
        self.session = requests.Session()
        logger.info("Initialized ZendeskClient for %s (%s)", self.base_url, self.locale)

    def get_all_articles(self) -> list[ZendeskArticle]:
        articles: list[ZendeskArticle] = []
        url = f"{self.base_url}/api/v2/help_center/{self.locale}/articles.json"
        params = {"per_page": self.MAX_PER_PAGE}

        while url:
            logger.debug("Fetching articles: %s", url)
            resp = self.session.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            articles.extend(ZendeskArticle.model_validate(a) for a in data["articles"])
            page = data.get("page", "?")
            page_count = data.get("page_count", "?")
            logger.debug(
                "Got page %s/%s (%d articles so far)",
                page,
                page_count,
                len(articles),
            )
            url = data.get("next_page")
            params = {}

        logger.info("Fetched %d articles total", len(articles))
        return articles
