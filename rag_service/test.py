import os
from dotenv import load_dotenv

# 1. Ép nạp file .env vào bộ nhớ
load_dotenv() 

# 2. Lấy giá trị từ bộ nhớ ra
public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
host = os.getenv("LANGFUSE_HOST")

print(public_key)
print(host)