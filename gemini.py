import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai.types import CustomMetadataDict, Document
from pydantic import BaseModel

from transform import MarkdownDocument

logger = logging.getLogger(__name__)


class DocumentMetadata(BaseModel):
    id: int
    url: str
    locale: str
    updated_at: datetime

    @classmethod
    def from_document(cls, data: Document) -> "DocumentMetadata":
        if not data.custom_metadata:
            raise ValueError("Document missing custom metadata")
        meta = {
            m.key: (m.string_value if m.string_value is not None else m.numeric_value)
            for m in data.custom_metadata
        }
        return cls.model_validate(meta)

    def to_list(self) -> list[CustomMetadataDict]:
        return [
            CustomMetadataDict(key="id", string_value=str(self.id)),
            CustomMetadataDict(key="url", string_value=self.url),
            CustomMetadataDict(key="locale", string_value=self.locale),
            CustomMetadataDict(key="updated_at", string_value=str(self.updated_at)),
        ]


@dataclass
class SyncResult:
    created: int
    updated: int
    deleted: int


class GeminiClient:
    def __init__(self, store_name: str, documents_dir: str):
        self.client = genai.Client()
        self.store_name = store_name
        self.documents_dir = documents_dir

    def _list_existing(self) -> list[Document] | None:
        try:
            result = list(
                self.client.file_search_stores.documents.list(parent=self.store_name)
            )
            logger.debug("Found %d existing documents in store", len(result))
            return result
        except Exception:
            logger.exception("Failed to list existing documents", exc_info=True)
            return None

    def _upload_document(
        self,
        doc: MarkdownDocument,
    ) -> bool:
        file_path = Path(self.documents_dir) / f"{doc.id}.md"
        if not file_path.exists():
            logger.error("File not found: %s", file_path)
            return False

        meta = DocumentMetadata(
            id=doc.id,
            url=doc.url,
            locale=doc.locale,
            updated_at=doc.updated_at,
        )

        try:
            self.client.file_search_stores.upload_to_file_search_store(
                file=str(file_path),
                file_search_store_name=self.store_name,
                config={
                    "display_name": doc.title,
                    "custom_metadata": meta.to_list(),
                },
            )
            logger.debug("Uploaded %s — %s", doc.id, doc.title)
            return True
        except Exception:
            logger.exception(
                "Failed to upload %s — %s", doc.id, doc.title, exc_info=True
            )
            return False

    def _delete_document(self, resource_name: str) -> bool:
        try:
            self.client.file_search_stores.documents.delete(
                name=resource_name, config={"force": True}
            )
            return True
        except Exception:
            logger.exception("Failed to delete document", exc_info=True)
            return False

    def _update_document(
        self,
        doc: MarkdownDocument,
        resource_name: str,
    ) -> bool:
        # Delete-then-upload is intentional: uploading a duplicate
        # results in both files in the store (undocumented but observed).
        return self._delete_document(resource_name) and self._upload_document(doc)

    def sync(
        self,
        documents: list[MarkdownDocument],
    ) -> SyncResult:
        existing_docs = self._list_existing()
        if existing_docs is None:
            return SyncResult(0, 0, 0)

        existing = {
            DocumentMetadata.from_document(d).id: d for d in existing_docs if d.name
        }
        local_ids = {d.id for d in documents}

        created = 0
        updated = 0

        for doc in documents:
            existing_doc = existing.get(doc.id)
            if existing_doc is None:
                if self._upload_document(doc):
                    created += 1
            else:
                existing_meta = DocumentMetadata.from_document(existing_doc)
                if existing_meta.updated_at < doc.updated_at:
                    assert existing_doc.name is not None
                    if self._update_document(doc, existing_doc.name):
                        updated += 1

        deleted = 0
        for existing_doc in existing_docs:
            if existing_doc.name:
                meta = DocumentMetadata.from_document(existing_doc)
                if meta.id not in local_ids:
                    if self._delete_document(existing_doc.name):
                        deleted += 1

        return SyncResult(created=created, updated=updated, deleted=deleted)
