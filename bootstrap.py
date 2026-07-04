"""Create or find a Gemini file search store, printing its resource name."""

import logging
import sys

from google import genai

logging.basicConfig(level=logging.INFO)


def main() -> None:
    display_name = sys.argv[1]

    client = genai.Client()
    for store in client.file_search_stores.list():
        if store.display_name == display_name and store.name:
            logging.info("Store exists: %s", store.name)
            print(store.name)
            return

    store = client.file_search_stores.create(
        config={
            "display_name": display_name,
            "embedding_model": "models/gemini-embedding-2",
        }
    )
    logging.info("Created store: %s", store.name)
    assert store.name is not None


if __name__ == "__main__":
    main()
