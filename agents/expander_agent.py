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
    "cloudsql": {
        "type": "Database",
        "provider": "gcp"
    },
    "cloudrun": {
        "type": "Compute",
        "provider": "gcp"
    },
    "apigateway": {
        "type": "API Layer",
        "provider": "gcp"
    }
}


# =========================================================
# SAFE JSON EXTRACTION
# =========================================================
def extract_json(raw):

    if not raw:
        return []

    try:

        # -------------------------------------------------
        # REMOVE MARKDOWN
        # -------------------------------------------------
        raw = raw.replace("```json", "")
        raw = raw.replace("```", "")
        raw = raw.strip()

        # -------------------------------------------------
        # DIRECT EMPTY ARRAY
        # -------------------------------------------------
        if raw == "[]":
            return []

        # -------------------------------------------------
        # EXTRACT JSON ARRAY
        # -------------------------------------------------
        match = re.search(r"\[[\s\S]*\]", raw)

        if not match:
            return []

        json_str = match.group(0).strip()

        if json_str == "[]":
            return []

        parsed = json.loads(json_str)

        if isinstance(parsed, list):
            return parsed

        return []

    except Exception as e:

        print("⚠️ JSON parse failed:", e)

        return []


# =========================================================
# NORMALIZE SERVICE NAME
# =========================================================
def normalize_service_name(name):

    if not name:
        return None

    name = str(name).strip().lower()

    aliases = {
        "google cloud storage": "gcs",
        "cloud storage": "gcs",
        "storage": "gcs",
        "bq": "bigquery",
        "google bigquery": "bigquery",
        "pub/sub": "pubsub",
        "data stream": "datastream"
    }

    return aliases.get(name, name)


# =========================================================
# VALIDATE COMPONENTS
# =========================================================
def validate_expanded_components(
    comps,
    existing_components
):

    validated = []

    existing_names = {
        c["name"].lower()
        for c in existing_components
    }

    for c in comps:

        if not isinstance(c, dict):
            continue

        name = normalize_service_name(
            c.get("name")
        )

        if not name:
            continue

        # -------------------------------------------------
        # ONLY ALLOWED SERVICES
        # -------------------------------------------------
        if name not in SERVICE_ONTOLOGY:
            continue

        # -------------------------------------------------
        # SKIP DUPLICATES
        # -------------------------------------------------
        if name in existing_names:
            continue

        meta = SERVICE_ONTOLOGY[name]

        validated.append({
            "name": name,
            "type": meta["type"],
            "provider": meta["provider"],
            "region": c.get("region", "global")
        })

    return validated


# =========================================================
# DEDUPLICATE COMPONENTS
# =========================================================
def deduplicate(components):

    unique = []
    seen = set()

    for c in components:

        key = (
            c.get("name", "").lower(),
            c.get("type", "").lower(),
            c.get("provider", "").lower(),
            c.get("region", "").lower()
        )

        if key not in seen:

            seen.add(key)

            unique.append(c)

    return unique


# =========================================================
# ARCHITECTURE GUARDRAILS
# =========================================================
def should_expand(user_input, intent):

    text = (
        user_input + " " +
        json.dumps(intent)
    ).lower()

    realtime_keywords = [
        "stream",
        "real-time",
        "realtime",
        "event",
        "pubsub",
        "queue",
        "kafka",
        "cdc",
        "ingestion pipeline"
    ]

    return any(
        keyword in text
        for keyword in realtime_keywords
    )


# =========================================================
# RULE-BASED MINIMAL EXPANSION
# =========================================================
def minimal_rule_expansion(
    components,
    user_input
):

    existing = {
        c["name"].lower()
        for c in components
    }

    additions = []

    text = user_input.lower()

    # -----------------------------------------------------
    # REALTIME LOG INGESTION
    # -----------------------------------------------------
    if (
        "gcs" in existing and
        (
            "stream" in text or
            "real-time" in text or
            "realtime" in text or
            "event" in text
        )
    ):

        if "pubsub" not in existing:

            additions.append({
                "name": "pubsub",
                "type": "Streaming Queue",
                "provider": "gcp",
                "region": "global"
            })

    return additions


# =========================================================
# MAIN EXPANDER AGENT
# =========================================================
def expander_agent(
    components,
    user_input,
    intent
):

    print("\n🤖 Intelligent Expander Agent starting...")

    # =====================================================
    # SKIP EXPANSION FOR SIMPLE WORKLOADS
    # =====================================================
    if not should_expand(user_input, intent):

        print("\nℹ️ No expansion required")

        return deduplicate(components)

    existing_services = [
        c["name"]
        for c in components
    ]

    ontology_services = list(
        SERVICE_ONTOLOGY.keys()
    )

    prompt = f"""
You are a principal cloud architect.

TASK:
Infer ONLY infrastructure components that are STRICTLY REQUIRED
for the architecture to function.

IMPORTANT:
- If the workload can operate with existing services, return []
- Do NOT add optional services
- Do NOT add best-practice services
- Do NOT add monitoring/security unless explicitly requested
- Do NOT add streaming systems unless real-time ingestion is required
- Prefer minimal architecture
- Return ONLY missing services
- Use ONLY allowed services

STRICT RULES:
- Return ONLY JSON array
- Do NOT explain
- Do NOT invent services
- Do NOT create processors/managers/helpers

ALLOWED SERVICES:
{ontology_services}

EXISTING SERVICES:
{json.dumps(existing_services, indent=2)}

USER INPUT:
{user_input}

INTENT:
{json.dumps(intent, indent=2)}

OUTPUT FORMAT:
[
  {{
    "name": "pubsub",
    "region": "us-east1"
  }}
]

Return ONLY JSON array.
"""

    raw = call_ollama(prompt)

    print("\n🔍 RAW EXPANDER OUTPUT:")
    print(raw)

    # =====================================================
    # SAFE EXTRACTION
    # =====================================================
    parsed = extract_json(raw)

    # =====================================================
    # VALIDATE
    # =====================================================
    validated = validate_expanded_components(
        parsed,
        components
    )

    # =====================================================
    # RULE-BASED FALLBACK
    # =====================================================
    if not validated:

        validated = minimal_rule_expansion(
            components,
            user_input
        )

    # =====================================================
    # FINAL COMPONENTS
    # =====================================================
    final_components = (
        components + validated
    )

    final_components = deduplicate(
        final_components
    )

    print("\n✅ FINAL EXPANDED ARCHITECTURE")
    print(json.dumps(final_components, indent=2))

    return final_components
