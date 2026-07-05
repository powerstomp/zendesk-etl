import logging
import os
import sys

from google import genai

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-3.1-flash-lite"

SYSTEM_PROMPT = """You are OptiBot, the customer-support bot for OptiSigns.com.
• Tone: helpful, factual, concise.
• Only answer using the uploaded docs.
• Max 5 bullet points; else link to the doc.
• Cite up to 3 "Article URL:" lines per reply."""


def main() -> None:
    if len(sys.argv) < 2:
        logger.error("Usage: uv run python query.py <question>")
        sys.exit(1)

    question = sys.argv[1]
    store_name = os.getenv("GOOGLE_STORE_RESOURCE_NAME")
    if not store_name:
        logger.error("GOOGLE_STORE_RESOURCE_NAME not set")
        sys.exit(1)

    client = genai.Client()
    interaction = client.interactions.create(
        model=MODEL_NAME,
        input=question,
        system_instruction=SYSTEM_PROMPT,
        tools=[
            {
                "type": "file_search",
                "file_search_store_names": [store_name],
            }
        ],
    )

    for step in interaction.steps or []:
        if step.type == "model_output":
            for content_block in step.content or []:
                if content_block.type == "text":
                    print(content_block.text)
                    if content_block.annotations:
                        print("\nSources:")
                        for annotation in content_block.annotations:
                            if annotation.type == "file_citation":
                                print(
                                    f"  - {annotation.file_name}: {annotation.source}"
                                )


if __name__ == "__main__":
    main()
