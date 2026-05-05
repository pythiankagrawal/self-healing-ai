import requests
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3"


def call_ollama(prompt, retries=2):
    for i in range(retries):
        try:
            res = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=180
            )
            return res.json().get("response", "")
        except Exception as e:
            print(f"⚠️ Retry {i+1} failed:", e)
            time.sleep(2 * (i+1))

    return None
