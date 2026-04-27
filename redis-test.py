import redis
from langchain_community.utils.math import cosine_similarity
from langchain_huggingface import HuggingFaceEmbeddings
import json
import hashlib

query = "Do cơn mưa lớn sáng nay, tôi đã đến công ty trễ"


model_name = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_name)

# 2. Tạo embedding cho 2 câu

embedding_s2 = embeddings.embed_query(query)
response = "OK"
r = redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=True  # trả về string thay vì bytes
    )
def save_to_cache(query: str, vector: list, response: str):
    pipe = r.pipeline(transaction=False)
    key = hashlib.md5(query.encode()).hexdigest()
    full_key = f"semantic_search:{key}"
    pipe.hset(full_key,mapping = {
        "query": query,
        "embedding": json.dumps(vector),
        "response": response
    })
    pipe.expire(full_key,60 * 60 * 24 * 30 * 6)
    pipe.execute()

save_to_cache(query, embedding_s2, response)

query = "Sáng nay trời mưa rất to nên tôi đi làm muộn"

input_vector = embeddings.embed_query(query)


def find_in_cache(query_vector: list, threshold: float = 0.8):
    best_score = 0
    best_response = ""
    for key in r.scan_iter(match="semantic_search:*"):
        embedding_cache = json.loads(r.hget(key, "embedding"))
        similarity_scores = cosine_similarity([query_vector], [embedding_cache])[0][0]
        if similarity_scores > best_score:
            best_score = similarity_scores
            best_response = r.hget(key, "response")
    if best_score > threshold:
        return best_response
    return None

