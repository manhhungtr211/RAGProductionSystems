"""
src/embedding/openai_embedder.py

OpenAI-backed embeddings (text-embedding-3-small / text-embedding-3-large).
Placeholder — requires langchain-openai and OPENAI_API_KEY in .env.

TODO: Uncomment and configure when switching to OpenAI embeddings.
"""
# from langchain_openai import OpenAIEmbeddings
# from config.settings import SETTINGS
#
# def get_openai_embeddings(model: str = "text-embedding-3-small") -> OpenAIEmbeddings:
#     return OpenAIEmbeddings(
#         model=model,
#         openai_api_key=SETTINGS.API_KEY.get_secret_value(),
#     )
