import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

url = "https://api.openai.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Write a short poem about coding"}]
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    print(result["choices"][0]["message"]["content"])
else:
    print("❌ API Error:", response.text)
