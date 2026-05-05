from llm.ollama_client import call_ollama
import json


# -------------------------------------------
# INTENT KEYWORDS (WEIGHTED)
# -------------------------------------------
INTENT_KEYWORDS = {
    "LOGGING": ["log", "logging", "monitoring"],
    "ETL": ["etl", "pipeline", "batch", "ingestion", "transform", "load"],
    "STREAMING": ["stream", "real-time", "event", "kafka", "pubsub"],
    "STORAGE": ["store", "storage", "archive", "backup"],
    "API": ["api", "endpoint", "integration", "service"]
}


# -------------------------------------------
# NORMALIZE INTENT (CRITICAL)
# -------------------------------------------
def normalize_intent(intent):
    if not intent:
        return "UNKNOWN"

    intent = intent.strip().upper()

    if intent in INTENT_KEYWORDS:
        return intent

    return "UNKNOWN"


# -------------------------------------------
# SCORE-BASED RULE CLASSIFIER (IMPROVED)
# -------------------------------------------
def rule_based_intent(text):
    text = (text or "").lower()

    scores = {intent: 0 for intent in INTENT_KEYWORDS}

    for intent, keywords in INTENT_KEYWORDS.items():
        for k in keywords:
            if k in text:
                scores[intent] += 1

    # get best intent
    best_intent = max(scores, key=scores.get)
    best_score = scores[best_intent]

    if best_score == 0:
        return None, 0.0

    # confidence = normalized score
    total_hits = sum(scores.values())
    confidence = round(best_score / total_hits, 2) if total_hits else 0.0

    return best_intent, confidence


# -------------------------------------------
# LLM CLASSIFIER
# -------------------------------------------
def llm_classify_intent(user_input):
    prompt = f"""
You are a cloud architecture expert.

Classify the intent into ONE:

STORAGE
ETL
STREAMING
LOGGING
API
UNKNOWN

RULES:
- Return ONLY JSON
- No explanation

Input:
{user_input}

Output:
{{"intent": "ETL", "confidence": 0.9}}
"""

    raw = call_ollama(prompt)

    if not raw:
        return {"intent": "UNKNOWN", "confidence": 0.0}

    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        data = json.loads(raw[start:end])

        intent = normalize_intent(data.get("intent"))
        confidence = float(data.get("confidence", 0.5))

        return {
            "intent": intent,
            "confidence": confidence
        }

    except Exception as e:
        print("⚠️ LLM intent parse failed:", e)

    return {"intent": "UNKNOWN", "confidence": 0.0}


# -------------------------------------------
# MAIN INTENT AGENT (FINAL)
# -------------------------------------------
def intent_agent(user_input):
    print("\n🧠 Intent Agent starting...")

    # ---------------------------------------
    # 1. Rule-based (fast + reliable)
    # ---------------------------------------
    intent, confidence = rule_based_intent(user_input)

    if intent and confidence >= 0.6:
        print(f"⚡ Rule-based intent: {intent} ({confidence})")
        return {
            "intent": intent,
            "confidence": confidence,
            "source": "rule"
        }

    # ---------------------------------------
    # 2. LLM fallback (only if needed)
    # ---------------------------------------
    print("🤖 Using LLM for intent classification...")
    result = llm_classify_intent(user_input)

    print(f"✅ LLM intent: {result}")

    result["source"] = "llm"

    return result
