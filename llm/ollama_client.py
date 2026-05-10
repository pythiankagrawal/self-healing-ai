import requests
import time
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5"

# =========================================================
# SAFE OLLAMA CALLER (ROBUST VERSION)
# =========================================================
def call_ollama(prompt, retries=3, timeout=180):

    session = requests.Session()

    for i in range(retries):

        try:
            response = session.post(
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2
                    }
                },
                timeout=timeout
            )

            # -------------------------------
            # HTTP ERROR HANDLING
            # -------------------------------
            if response.status_code != 200:
                print(f"⚠️ HTTP Error {response.status_code}")
                time.sleep(2 * (i + 1))
                continue

            # -------------------------------
            # JSON SAFETY CHECK
            # -------------------------------
            try:
                data = response.json()
            except Exception:
                print("⚠️ Invalid JSON response from Ollama")
                time.sleep(2 * (i + 1))
                continue

            # -------------------------------
            # VALID RESPONSE CHECK
            # -------------------------------
            if not data or "response" not in data:
                print("⚠️ Empty response from Ollama")
                time.sleep(2 * (i + 1))
                continue

            return data["response"]

        except requests.exceptions.Timeout:
            print(f"⚠️ Retry {i+1} failed: Timeout")
            time.sleep(2 * (i + 1))

        except requests.exceptions.ConnectionError:
            print(f"⚠️ Retry {i+1} failed: Connection error")
            time.sleep(2 * (i + 1))

        except Exception as e:
            print(f"⚠️ Retry {i+1} failed: {e}")
            time.sleep(2 * (i + 1))

    return None
