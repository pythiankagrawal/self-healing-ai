from llm.ollama_client import call_ollama
import json
import re


# =========================================================
# STRICT JSON EXTRACTION (NO FIXES, NO GUESSING)
# =========================================================
def extract_json(raw):

    if not raw:
        return None

    raw = raw.replace("```json", "").replace("```", "").strip()

    start = raw.find("{")
    end = raw.rfind("}")

    if start == -1 or end == -1:
        return None

    try:
        return json.loads(raw[start:end + 1])
    except Exception:
        return None


# =========================================================
# INTENT AGENT (PURE LLM)
# =========================================================
def intent_agent(user_input, components=None):

    print("\n🧠 LLM-Only Intent Agent starting...")

    prompt = f"""
You are a senior cloud architect and FinOps intelligence system.

Your job is to deeply understand cloud architecture intent.

You MUST behave like a reasoning model.

Do NOT guess blindly.
Do NOT ignore details like frequency or services.
Do NOT normalize or simplify user intent.

==================================================
INPUT
==================================================

USER REQUEST:
{user_input}

PARSED COMPONENTS:
{json.dumps(components or [], indent=2)}

==================================================
TASK
==================================================

Infer a FULL structured understanding of:

1. primary_intent
2. secondary_intents
3. architecture_pattern
4. workload_characteristics
5. signals (VERY IMPORTANT)
6. components_detected
7. missing_information
8. confidence

==================================================
CRITICAL RULES
==================================================

- If user says "every 30 mins" → MUST output exactly "every_30_mins"
- If user says "realtime" → must reflect realtime=true
- DO NOT override user-specified frequency
- DO NOT generalize (no "daily" unless user says daily)
- DO NOT hallucinate services not in input
- If unsure → use UNKNOWN, not guess

==================================================
OUTPUT FORMAT (STRICT JSON ONLY)
==================================================

{{
  "primary_intent": "",
  "secondary_intents": [],
  "architecture_pattern": "",
  "workload_characteristics": {{
    "stateful": false,
    "event_driven": false,
    "latency_sensitive": false,
    "compute_intensive": false,
    "storage_intensive": false
  }},
  "signals": {{
    "frequency": "",
    "realtime": false,
    "batch": false,
    "cloud_provider": "",
    "region": ""
  }},
  "components_detected": [],
  "missing_information": [],
  "confidence": 0.0
}}
"""

    raw = call_ollama(prompt)

    print("\n🔍 RAW INTENT OUTPUT:\n", raw)

    data = extract_json(raw)

    if not data:
        raise Exception("Intent Agent failed: Invalid JSON from LLM")

    data["source"] = "llm"

    print("\n✅ FINAL INTENT ANALYSIS")
    print(json.dumps(data, indent=2))

    return data
