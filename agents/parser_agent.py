from llm.ollama_client import call_ollama

import json
import re


# =========================================================
# CLOUD SERVICE ONTOLOGY
# =========================================================

SERVICE_ONTOLOGY = {
    "gcs": {
        "type": "Object Storage",
        "provider": "gcp"
    },
    "bigquery": {
        "type": "Data Warehouse",
        "provider": "gcp"
    },
    "pubsub": {
        "type": "Streaming Queue",
        "provider": "gcp"
    },
    "datastream": {
        "type": "CDC/Streaming",
        "provider": "gcp"
    },
    "dataflow": {
        "type": "Compute",
        "provider": "gcp"
    },
    "cloud sql": {
        "type": "Database",
        "provider": "gcp"
    },
    "cloud run": {
        "type": "Compute",
        "provider": "gcp"
    },
    "kafka": {
        "type": "Streaming Queue",
        "provider": "apache"
    },
    "s3": {
        "type": "Object Storage",
        "provider": "aws"
    },
    "redshift": {
        "type": "Data Warehouse",
        "provider": "aws"
    }
}


# =========================================================
# SAFE JSON EXTRACTION
# =========================================================

def safe_json_extract(raw):

    if not raw:
        return None

    try:

        # extract first json array
        match = re.search(r"\[.*?\]", raw, re.DOTALL)

        if not match:
            return None

        json_str = match.group()

        data = json.loads(json_str)

        if isinstance(data, list):
            return data

    except Exception as e:
        print("⚠️ JSON parse failed:", e)

    return None


# =========================================================
# EXTRACT REGION
# =========================================================

def extract_region(user_input):

    text = (user_input or "").lower()

    patterns = [
        r"(us[- ]east[- ]1)",
        r"(us[- ]west[- ]1)",
        r"(us[- ]central1)",
        r"(asia[- ]south1)",
        r"(europe[- ]west1)"
    ]

    for p in patterns:

        match = re.search(p, text)

        if match:
            return (
                match.group(1)
                .replace(" ", "")
                .lower()
            )

    return "global"


# =========================================================
# NORMALIZE SERVICES
# =========================================================

def normalize_services(service_names, region):

    components = []

    for s in service_names:

        s = str(s).strip().lower()

        if s not in SERVICE_ONTOLOGY:
            continue

        meta = SERVICE_ONTOLOGY[s]

        components.append({
            "name": s,
            "type": meta["type"],
            "provider": meta["provider"],
            "region": region
        })

    return components


# =========================================================
# PARSER PROMPT
# =========================================================

def build_parser_prompt(user_input):

    services = list(SERVICE_ONTOLOGY.keys())

    return f"""
You are a cloud architecture parser.

TASK:
Extract ONLY cloud service names explicitly mentioned.

STRICT RULES:
- Return ONLY JSON array
- No explanation
- No markdown
- No reasoning
- No extra text
- No comments
- No hallucinations
- Do NOT infer services
- ONLY extract services present in text

ALLOWED SERVICES:
{json.dumps(services)}

USER INPUT:
{user_input}

GOOD OUTPUT:
["gcs", "bigquery", "datastream"]

BAD OUTPUT:
- explanations
- prose
- inferred services
- invalid json

RETURN ONLY JSON ARRAY.
"""


# =========================================================
# MAIN PARSER AGENT
# =========================================================

def parser_agent(user_input):

    print("\n🤖 Intelligent Parser Agent starting...")

    region = extract_region(user_input)

    prompt = build_parser_prompt(user_input)

    raw = call_ollama(prompt)

    print("\n🔍 RAW PARSER OUTPUT:")
    print(raw)

    services = safe_json_extract(raw)

    if not services:
        raise Exception(
            "Parser Agent failed: Invalid JSON response"
        )

    print("\n🧠 EXTRACTED SERVICES:")
    print(services)

    components = normalize_services(
        services,
        region
    )

    print("\n✅ FINAL PARSED COMPONENTS")
    print(json.dumps(components, indent=2))

    return components
