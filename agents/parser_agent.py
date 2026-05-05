from llm.ollama_client import call_ollama
from llm.prompt_builder import build_parser_prompt
from core.normalizer import normalize_components, clean_output, fallback_parser

# -------------------------------------------
# CANONICAL SERVICE MAP (CRITICAL)
# -------------------------------------------
CANONICAL_SERVICES = {
    "gcs": {"name": "gcs", "type": "Object Storage"},
    "google cloud storage": {"name": "gcs", "type": "Object Storage"},
    "storage": {"name": "gcs", "type": "Object Storage"},

    "pubsub": {"name": "pubsub", "type": "Streaming Queue"},
    "pub/sub": {"name": "pubsub", "type": "Streaming Queue"},

    "bigquery": {"name": "bigquery", "type": "Data Warehouse"},
    "bq": {"name": "bigquery", "type": "Data Warehouse"},
}

# -------------------------------------------
# RULE-BASED PARSER (FIRST LINE OF DEFENSE)
# -------------------------------------------
def rule_based_parser(text):
    text = text.lower()
    components = []

    for key, value in CANONICAL_SERVICES.items():
        if key in text:
            components.append({
                "name": value["name"],
                "type": value["type"],
                "region": "asia-south1"
            })

    return components


# -------------------------------------------
# MAIN PARSER AGENT (FIXED)
# -------------------------------------------
def parser_agent(user_input):
    print("🤖 Parser Agent starting...")

    # ---------------------------------------
    # 1. RULE-BASED FIRST (IMPORTANT FIX)
    # ---------------------------------------
    rule_components = rule_based_parser(user_input)

    if rule_components:
        print("⚡ Rule-based parsing used:", rule_components)
        return rule_components

    # ---------------------------------------
    # 2. LLM PARSING (FALLBACK)
    # ---------------------------------------
    prompt = build_parser_prompt(user_input)

    raw = call_ollama(prompt)

    print("\n🔍 RAW OUTPUT:\n", raw)

    parsed = clean_output(raw)

    if not parsed:
        print("⚠️ LLM failed → fallback parser")
        return fallback_parser(user_input)

    # ---------------------------------------
    # 3. NORMALIZATION + VALIDATION
    # ---------------------------------------
    parsed = normalize_components(parsed)

    # 🚫 Remove garbage entries
    parsed = [c for c in parsed if c.get("type") != "Unknown"]

    if not parsed:
        print("⚠️ Invalid LLM output → fallback")
        return fallback_parser(user_input)

    return parsed


# -------------------------------------------
# OPTIONAL SANITIZER (KEEP IF NEEDED)
# -------------------------------------------
def sanitize_component(c):
    return {
        "name": c.get("name") or c.get("endpointName") or "unknown",
        "type": normalize_type(c.get("type", "")),
        "region": extract_region(c.get("region", "global"))
    }


def normalize_type(t):
    if isinstance(t, list):
        t = " ".join(t)

    t = str(t).lower()

    if "storage" in t or "gcs" in t:
        return "Object Storage"
    if "pubsub" in t or "queue" in t:
        return "Streaming Queue"
    if "bigquery" in t:
        return "Data Warehouse"
    if "api" in t or "integration" in t:
        return "API Layer"

    return "Unknown"


def extract_region(r):
    if not r:
        return "global"

    r = str(r).lower()

    if "asia-south1" in r:
        return "asia-south1"

    return "global"
