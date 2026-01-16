import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("HF_TOKEN")
headers = {"Authorization": f"Bearer {token}"}
url = "https://huggingface.co/api/spaces/WildGenie/turkish-extended-ner/logs/build"

try:
    with requests.get(url, headers=headers, stream=True, timeout=30) as r:
        r.raise_for_status()
        print("Connected to build logs stream...")
        count = 0
        for line in r.iter_lines():
            if line:
                print(line.decode('utf-8'))
                count += 1
            if count > 100:  # Get last 100 lines and stop
                break
except Exception as e:
    print(f"Error: {e}")
