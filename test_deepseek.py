import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("DEEPSEEK_API_KEY")

print("使用 KEY:", key)

resp = requests.post(
    "https://api.deepseek.com/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "hello"}]
    }
)

print("状态码:", resp.status_code)
print("返回:", resp.text)