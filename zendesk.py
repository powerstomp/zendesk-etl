from dataclasses import dataclass
from logging import getLogger
from typing import Any

import requests

logger = getLogger(__name__)


@dataclass
class Article:
    id: int
    title: str
    html_url: str
    body: str
    locale: str
    section_id: int
    author_id: int
    draft: bool
    promoted: bool
    position: int
    vote_sum: int
    vote_count: int
    comments_disabled: bool
    created_at: str
    updated_at: str
    label_names: list[str]
    content_tag_ids: list[int]

    @classmethod
    def from_api_dict(cls, data: dict[str, Any]) -> "Article":
        return cls(
            id=data["id"],
            title=data["title"],
            html_url=data["html_url"],
            body=data["body"],
            locale=data["locale"],
            section_id=data["section_id"],
            author_id=data["author_id"],
            draft=data["draft"],
            promoted=data["promoted"],
            position=data["position"],
            vote_sum=data["vote_sum"],
            vote_count=data["vote_count"],
            comments_disabled=data["comments_disabled"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            label_names=data["label_names"],
            content_tag_ids=data["content_tag_ids"],
        )


class ZendeskClient:
    MAX_PER_PAGE = 100

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        logger.info("Initialized ZendeskClient for %s", self.base_url)

    def get_all_articles(self) -> list[Article]:
        articles: list[Article] = []
        url = f"{self.base_url}/api/v2/help_center/articles.json"
        params = {"per_page": self.MAX_PER_PAGE}

        while url:
            logger.debug("Fetching articles: %s", url)
            resp = self.session.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            articles.extend(Article.from_api_dict(a) for a in data["articles"])
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
