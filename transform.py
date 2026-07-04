import html2text

from zendesk import Article

_converter = html2text.HTML2Text()
_converter.body_width = 0
_converter.ignore_links = False
_converter.ignore_images = False
_converter.ignore_emphasis = False
_converter.protect_links = True
_converter.mark_code = True


def html_to_markdown(html: str) -> str:
    return _converter.handle(html).strip()


def slugify(article: Article) -> str:
    # Zendesk article IDs are already unique and stable — no need to derive
    # a slug from the title (which can be non-ASCII, duplicated, or empty).
    return str(article.id)


def convert_article(article: Article) -> Article:
    article.body = html_to_markdown(article.body)
    return article
