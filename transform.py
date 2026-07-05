import re
from dataclasses import dataclass
from datetime import datetime
from logging import getLogger
from nt import remove
from typing import NamedTuple

import html2text

from zendesk import ZendeskArticle

logger = getLogger(__name__)


_converter = html2text.HTML2Text()
_converter.body_width = 0
_converter.ignore_links = False
_converter.ignore_images = False
_converter.ignore_emphasis = False
_converter.protect_links = True
_converter.mark_code = True


@dataclass
class MarkdownDocument:
    id: int
    title: str
    url: str
    locale: str
    body: str
    created_at: datetime
    updated_at: datetime


BASE64_IMAGE_PATTERN = re.compile(r"!\[.*?\]\(data:image\/[^)]*\)")


class MarkdownConversionResult(NamedTuple):
    body: str
    removed_base64_images_count: int


def html_to_markdown(html: str) -> MarkdownConversionResult:
    # strip base64 images from results
    # RAG doesn't work well on these.
    md = _converter.handle(html).strip()
    cleaned, count = BASE64_IMAGE_PATTERN.subn("", md)
    return MarkdownConversionResult(body=cleaned, removed_base64_images_count=count)


def slugify(article: ZendeskArticle | MarkdownDocument) -> str:
    return str(article.id)


def convert_article(article: ZendeskArticle) -> MarkdownDocument:
    body, removed_base64_images_count = html_to_markdown(article.body)
    if removed_base64_images_count > 0:
        logger.warning(
            "Removed %d base64 image(s) from document %s",
            removed_base64_images_count,
            article.id,
        )
    return MarkdownDocument(
        id=article.id,
        title=article.title,
        url=article.html_url,
        locale=article.locale,
        body=body,
        created_at=article.created_at,
        updated_at=article.updated_at,
    )
