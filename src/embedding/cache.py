import hashlib
import json
import logging

import redis
from langchain_community.utils.math import cosine_similarity
from langchain_huggingface import HuggingFaceEmbeddings
from langfuse import observe

from config.settings import SETTINGS

logger = logging.getLogger(__name__)


class SemanticCache:
    """
    Redis-backed semantic cache placed before the retrieval step.

    Flow:
        query → embed → search cache (cosine similarity) → HIT: return cached result
                                                          → MISS: retrieve → store in cache
    """

    KEY_PREFIX = "rag:retrieval:"
    DEFAULT_TTL = 60 * 60 * 24  # 24 hours

    def __init__(
        self,
        embeddings: HuggingFaceEmbeddings,
        threshold: float = SETTINGS.REDIS_CACHE_THRESHOLD,
        key_prefix: str = "rag:retrieval:",
    ):
        self.embeddings = embeddings
        self.threshold = threshold
        self.KEY_PREFIX = key_prefix
        self._client = redis.Redis(
            host=SETTINGS.REDIS_HOST,
            port=SETTINGS.REDIS_PORT,
            password=SETTINGS.REDIS_PASSWORD.get_secret_value() if SETTINGS.REDIS_PASSWORD else None,
            decode_responses=True,
        )
        self._ping()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ping(self) -> None:
        try:
            self._client.ping()
            logger.info("Redis connection established (%s:%s)", SETTINGS.REDIS_HOST, SETTINGS.REDIS_PORT)
        except redis.ConnectionError as exc:
            logger.warning("Cannot connect to Redis – cache will be skipped: %s", exc)

    def _embed(self, text: str) -> list[float]:
        return self.embeddings.embed_query(text)

    def _build_key(self, query: str) -> str:
        digest = hashlib.md5(query.encode()).hexdigest()
        return f"{self.KEY_PREFIX}{digest}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @observe(name="SemanticCache.get")
    def get(self, query: str) -> str | None:
        """
        Search cache using semantic similarity.
        Returns the cached result if score >= threshold, otherwise None.
        """
        try:
            query_vector = self._embed(query)
            best_score = 0
            best_response = ""
            best_query = ""
            for key in self._client.scan_iter(match=f"{self.KEY_PREFIX}*"):
                embedding_cache = json.loads(self._client.hget(key, "embedding"))
                similarity_scores = cosine_similarity([query_vector], [embedding_cache])[0][0]
                if similarity_scores > best_score:
                    best_score = similarity_scores
                    best_response = self._client.hget(key, "result")
                    best_query = self._client.hget(key, "query")
            print(f"best query: {best_query}")
            print(f"best score: {best_score}")
            if best_score >= self.threshold:
                logger.info(f"Cache HIT (score={best_score}, threshold={self.threshold})")
                return best_response

            logger.info(f"Cache MISS (score={best_score}, threshold={self.threshold})")
            return None

        except Exception as exc:
            logger.warning("Cache lookup failed – falling through to retriever: %s", exc)
            return None

    @observe(name="SemanticCache.set")
    def set(self, query: str, result: str) -> None:
        """Store a retrieval result in cache."""
        try:
            print(f"DEBUG query type: {type(query)}")
            print(f"DEBUG query value: {repr(query)}")
            vector = self._embed(query)
            key = self._build_key(query)
            pipe = self._client.pipeline(transaction=False)
            pipe.hset(
                key,
                mapping={
                    "query": query,
                    "embedding": json.dumps(vector, ensure_ascii=False),
                    "result": result,
                },
            )
            pipe.expire(key, self.DEFAULT_TTL)
            pipe.execute()
            logger.info("Cached retrieval result for query: %r", query[:60])
        except Exception as exc:
            logger.warning("Cache write failed: %s", exc)

    def invalidate_all(self) -> int:
        """Delete all retrieval cache keys. Call when S3 / vector store is updated."""
        keys = list(self._client.scan_iter(match=f"{self.KEY_PREFIX}*"))
        if keys:
            self._client.delete(*keys)
        logger.info("Cache invalidated: %d key(s) removed", len(keys))
        return len(keys)
