import json
import redis
# scan_iter giúp duyệt qua các key từ từ mà không làm đơ Server
r = redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=True  # trả về string thay vì bytes
    )


for key in r.scan_iter("rag:*"):
    response_text = r.hgetall(key)
    print(f"Key: {key}, Query: {response_text['query']}")