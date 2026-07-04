from dataclasses import dataclass

import html2text

from zendesk import ZendeskArticle

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
    created_at: str
    updated_at: str


def html_to_markdown(html: str) -> str:
    return _converter.handle(html).strip()


def slugify(article: ZendeskArticle | MarkdownDocument) -> str:
    return str(article.id)


def convert_article(article: ZendeskArticle) -> MarkdownDocument:
    return MarkdownDocument(
        id=article.id,
        title=article.title,
        url=article.html_url,
        locale=article.locale,
        body=html_to_markdown(article.body),
        created_at=article.created_at,
        updated_at=article.updated_at,
    )
