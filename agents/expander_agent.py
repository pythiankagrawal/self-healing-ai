from llm.ollama_client import call_ollama
import json

# -------------------------------------------
# PIPELINE KNOWLEDGE BASE (SMARTER)
# -------------------------------------------
PIPELINE_PATTERNS = [
    {
        "keywords": ["data transfer", "etl", "ingestion", "pipeline"],
        "components": [
            {"name": "gcs", "type": "Object Storage"},
            {"name": "bigquery", "type": "Data Warehouse"}
        ]
    },
    {
        "keywords": ["streaming", "real-time", "event"],
        "components": [
            {"name": "pubsub", "type": "Streaming Queue"},
            {"name": "dataflow", "type": "Compute"},
            {"name": "bigquery", "type": "Data Warehouse"}
        ]
    },
    {
        "keywords": ["api", "integration"],
        "components": [
            {"name": "api-gateway", "type": "API"},
            {"name": "cloud-functions", "type": "Compute"}
        ]
    }
]

# -------------------------------------------
# SAFE GETTERS
# -------------------------------------------
def safe_get(comp, key, default=""):
    return comp.get(key, default) or default


# -------------------------------------------
# RULE-BASED EXPANSION (IMPROVED)
# -------------------------------------------
def rule_based_expand(component, full_context=""):
    text = (safe_get(component, "name") + " " + full_context).lower()

    for pattern in PIPELINE_PATTERNS:
        if any(k in text for k in pattern["keywords"]):
            print(f"⚡ Rule match: {pattern['keywords']}")
            return pattern["components"]

    return None


# -------------------------------------------
# LLM EXPANSION (ROBUST)
# -------------------------------------------
def llm_expand(component):
    prompt = f"""
You are a cloud architecture expert.

Expand this component into real cloud services.

RULES:
- Return ONLY valid JSON list
- No explanation
- No markdown
- Each item must have name + type

Component:
{json.dumps(component)}

Output:
"""

    raw = call_ollama(prompt)

    if not raw:
        return []

    try:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        data = json.loads(raw[start:end])

        if isinstance(data, list):
            return data

    except Exception as e:
        print("⚠️ LLM parse failed:", e)

    return []


# -------------------------------------------
# DEDUPLICATION ENGINE
# -------------------------------------------
def deduplicate(components):
    seen = set()
    unique = []

    for c in components:
        key = (c.get("name", ""), c.get("type", ""))
        if key not in seen:
            seen.add(key)
            unique.append(c)

    return unique


# -------------------------------------------
# MAIN EXPANDER AGENT (FINAL)
# -------------------------------------------

def expander_agent(components, user_input=""):

    expanded = []

    for c in components:

        expanded.append(c)

        t = c["type"].lower()

        # only ADD, never replace

        if "storage" in t:
            expanded.append({
                "name": "pubsub-event-stream",
                "type": "Streaming Queue",
                "region": c.get("region")
            })

        if "streaming" in t:
            expanded.append({
                "name": "dataflow-processor",
                "type": "Compute",
                "region": c.get("region")
            })

    return expanded


# def expander_agent(components, user_input=""):
#     print("\n🤖 Agent 2.5 (Expander) starting...")
# 
#     expanded = []
# 
#     for comp in components:
#         name = safe_get(comp, "name")
#         ctype = safe_get(comp, "type", "Unknown")
# 
#         # ---------------------------------------
#         # 1. Skip already detailed components
#         # ---------------------------------------
#         if ctype != "Unknown" and len(name) < 5:
#             expanded.append(comp)
#             continue
# 
#         # ---------------------------------------
#         # 2. RULE-BASED EXPANSION
#         # ---------------------------------------
#         rule_result = rule_based_expand(comp, user_input)
# 
#         if rule_result:
#             expanded.extend(rule_result)
#             continue
# 
#         # ---------------------------------------
#         # 3. LLM EXPANSION
#         # ---------------------------------------
#         print(f"🤖 Expanding via LLM: {name}")
#         llm_result = llm_expand(comp)
# 
#         if llm_result:
#             expanded.extend(llm_result)
#         else:
#             print("⚠️ Keeping original (no expansion)")
#             expanded.append(comp)
# 
#     # -------------------------------------------
#     # 4. CLEAN OUTPUT
#     # -------------------------------------------
#     expanded = deduplicate(expanded)
# 
#     print("✅ Final Expanded Components:", expanded)
# 
#     return expanded
