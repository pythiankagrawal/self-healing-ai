from llm.ollama_client import call_ollama
import json
import re
import time


# =========================================================
# SERVICE PRICING HEURISTICS (BASELINE)
# =========================================================
SERVICE_BASELINES = {
    "gcs": {
        "type": "Object Storage",
        "base_monthly": 5
    },
    "bigquery": {
        "type": "Data Warehouse",
        "base_monthly": 20
    },
    "pubsub": {
        "type": "Streaming Queue",
        "base_monthly": 15
    },
    "datastream": {
        "type": "CDC/Streaming",
        "base_monthly": 25
    },
    "dataflow": {
        "type": "Compute",
        "base_monthly": 40
    },
    "cloudrun": {
        "type": "Compute",
        "base_monthly": 10
    },
    "cloudsql": {
        "type": "Database",
        "base_monthly": 50
    }
}


# =========================================================
# SAFE JSON EXTRACTION
# =========================================================
def extract_json(raw):

    if not raw:
        return None

    try:
        raw = raw.replace("```json", "")
        raw = raw.replace("```", "")

        match = re.search(r"\{.*\}", raw, re.DOTALL)

        if not match:
            return None

        json_str = match.group()

        return json.loads(json_str)

    except Exception as e:
        print("⚠️ Cost JSON parse failed:", e)

    return None


# =========================================================
# SAFE LLM CALL
# =========================================================
def safe_llm_call(prompt, retries=3):

    for i in range(retries):

        try:
            raw = call_ollama(prompt)

            if raw:
                return raw

        except Exception as e:
            print(f"⚠️ Retry {i+1} failed:", e)

            time.sleep(2 * (i + 1))

    return None


# =========================================================
# BUILD PRICING CONTEXT
# =========================================================
def build_pricing_context(components):

    pricing_context = []

    for c in components:

        name = c["name"].lower()

        if name in SERVICE_BASELINES:

            pricing_context.append({
                "service": name,
                "type": SERVICE_BASELINES[name]["type"],
                "baseline_monthly_usd":
                    SERVICE_BASELINES[name]["base_monthly"]
            })

    return pricing_context


# =========================================================
# NORMALIZE COST RESPONSE
# =========================================================
def normalize_cost_response(data):

    if not data:
        return None

    total = (
        data.get("total_cost")
        or data.get("total_cost_monthly")
        or 0
    )

    breakdown = data.get("breakdown", [])

    assumptions = (
        data.get("assumptions")
        or []
    )

    optimizations = (
        data.get("optimizations")
        or data.get("optimization_recommendations")
        or data.get("optimization")
        or []
    )

    # normalize breakdown schema
    normalized_breakdown = []

    for item in breakdown:

        normalized_breakdown.append({
            "name": item.get("name", "unknown"),
            "type": item.get("type", "Unknown"),
            "monthly_cost": float(
                item.get("monthly_cost")
                or item.get("estimated_monthly_cost")
                or 0
            ),
            "reason": item.get("reason", "")
        })

    return {
        "total_cost": round(float(total), 2),
        "currency": data.get("currency", "USD"),
        "breakdown": normalized_breakdown,
        "assumptions": assumptions,
        "optimizations": optimizations
    }


# =========================================================
# VALIDATE COST RESPONSE
# =========================================================
def validate_cost_response(data, components):

    if not data:
        return False

    required_keys = [
        "total_cost",
        "currency",
        "breakdown",
        "assumptions",
        "optimizations"
    ]

    for key in required_keys:

        if key not in data:
            print(f"⚠️ Missing key: {key}")
            return False

    if not isinstance(data["breakdown"], list):
        return False

    # validate breakdown entries
    for item in data["breakdown"]:

        if "name" not in item:
            return False

        if "monthly_cost" not in item:
            return False

    return True


# =========================================================
# FALLBACK COST ESTIMATION
# =========================================================
def fallback_cost_estimation(components):

    breakdown = []

    total = 0

    for c in components:

        name = c["name"].lower()

        if name in SERVICE_BASELINES:

            base = SERVICE_BASELINES[name]["base_monthly"]

            breakdown.append({
                "name": name,
                "type": SERVICE_BASELINES[name]["type"],
                "monthly_cost": base,
                "reason": "Baseline heuristic pricing"
            })

            total += base

    return {
        "total_cost": round(total, 2),
        "currency": "USD",
        "breakdown": breakdown,
        "assumptions": [
            "Fallback baseline pricing used due to LLM failure"
        ],
        "optimizations": [
            "Provide workload metrics for more accurate pricing"
        ]
    }


# =========================================================
# MAIN COST AGENT
# =========================================================
def cost_agent(components, user_input, intent):

    print("\n💰 Intelligent Cost Agent starting...")

    pricing_context = build_pricing_context(
        components
    )

    prompt = f"""
You are a senior FinOps cloud cost engineer.

TASK:
Estimate realistic monthly cloud cost.

USER INPUT:
{user_input}

INTENT:
{json.dumps(intent, indent=2)}

COMPONENTS:
{json.dumps(components, indent=2)}

PRICING BASELINES:
{json.dumps(pricing_context, indent=2)}

STRICT RULES:
- Return ONLY valid JSON
- Do NOT explain outside JSON
- Do NOT hallucinate services
- Use ONLY listed components
- Estimate conservative GCP pricing
- Include storage + streaming + compute
- Keep estimates realistic
- total_cost must equal sum of breakdown

OUTPUT FORMAT:
{{
  "total_cost": 0.0,
  "currency": "USD",
  "breakdown": [
    {{
      "name": "gcs",
      "type": "Object Storage",
      "monthly_cost": 0.0,
      "reason": "Short explanation"
    }}
  ],
  "assumptions": [
    ""
  ],
  "optimizations": [
    ""
  ]
}}

Return ONLY JSON.
"""

    # =====================================================
    # SAFE LLM CALL
    # =====================================================
    raw = safe_llm_call(prompt)

    print("\n🔍 RAW COST OUTPUT:")
    print(raw)

    # =====================================================
    # JSON EXTRACTION
    # =====================================================
    parsed = extract_json(raw)

    # =====================================================
    # FALLBACK IF LLM FAILS
    # =====================================================
    if not parsed:

        print("⚠️ Cost agent failed → using fallback pricing")

        fallback = fallback_cost_estimation(
            components
        )

        print("\n💰 FALLBACK COST REPORT")
        print(json.dumps(fallback, indent=2))

        return fallback

    # =====================================================
    # NORMALIZE RESPONSE
    # =====================================================
    normalized = normalize_cost_response(
        parsed
    )

    # =====================================================
    # VALIDATE RESPONSE
    # =====================================================
    valid = validate_cost_response(
        normalized,
        components
    )

    if not valid:

        print("⚠️ Invalid cost schema → using fallback")

        fallback = fallback_cost_estimation(
            components
        )

        print("\n💰 FALLBACK COST REPORT")
        print(json.dumps(fallback, indent=2))

        return fallback

    print("\n💰 FINAL COST REPORT")
    print(json.dumps(normalized, indent=2))

    return normalized
