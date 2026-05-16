import httpx
r = httpx.get("https://cloud.langfuse.com/api/public/health")
print(r.status_code)  