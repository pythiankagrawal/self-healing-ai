from llm.ollama_client import call_ollama
from llm.prompt_builder import build_parser_prompt
from core.normalizer import normalize_components
from core.normalizer import clean_output
from core.normalizer import fallback_parser


def parser_agent(user_input):
    print("🤖 Parser Agent starting...")

    prompt = build_parser_prompt(user_input)

    raw = call_ollama(prompt)

    print("\n🔍 RAW OUTPUT:\n", raw)

    parsed = clean_output(raw)

    if not parsed:
        print("⚠️ LLM failed → fallback")
        return fallback_parser(user_input)

    parsed = normalize_components(parsed)

    return parsed





def sanitize_component(c):
    return {
        "name": c.get("name") or c.get("endpointName") or "unknown",
        "type": normalize_type(c.get("type", "")),
        "region": extract_region(c.get("region", "global"))
    }


def normalize_type(t):
    t = t.lower()

    if "storage" in t or "gcs" in t:
        return "Object Storage"
    if "pubsub" in t or "queue" in t:
        return "Streaming Queue"
    if "bigquery" in t:
        return "Data Warehouse"
    if "api" in t or "integration" in t:
        return "API Layer"

    return "Unknown"
