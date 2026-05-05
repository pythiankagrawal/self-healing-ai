rom llm.ollama_client import call_ollama
import json
import re


# -------------------------------------------
# CONSTANTS
# -------------------------------------------
VALID_FIELDS = {
    "data_size",
    "compute_hours",
    "frequency",
    "throughput",
    "requests_per_sec",
    "storage_size"
}


# -------------------------------------------
# EXTRACT SIGNALS FROM INPUT
# -------------------------------------------
def extract_signals(user_input):
    text = (user_input or "").lower()

    signals = {}

    if "daily" in text:
        signals["frequency"] = "daily"
    elif "hourly" in text:
        signals["frequency"] = "hourly"
    elif "real-time" in text or "stream" in text:
        signals["frequency"] = "real-time"

    return signals


# -------------------------------------------
# SAFE JSON EXTRACTION
# -------------------------------------------
def safe_json_extract(raw):
    if not raw:
        return None

    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        return None

    json_str = match.group()

    json_str = json_str.replace("\n", " ")
    json_str = json_str.replace("'", '"')

    json_str = re.sub(r'"question"\s+"', '"question": "', json_str)
    json_str = re.sub(r'"field"\s+"', '"field": "', json_str)

    try:
        return json.loads(json_str)
    except Exception as e:
        print("⚠️ JSON still invalid:", e)
        return None


# -------------------------------------------
# LLM: GENERATE QUESTIONS
# -------------------------------------------
def llm_generate_questions(components, user_input, signals, intent):

    prompt = f"""
You are a FinOps expert.

Task:
Generate MOST IMPORTANT cost-related questions.

INTENT: {intent}

STRICT RULES:
- Return STRICT JSON list
- Max 3 items
- Each item MUST have:
  - "field"
  - "question"
- No explanation

Allowed fields:
data_size, compute_hours, frequency, throughput, requests_per_sec, storage_size

User Input:
{user_input}

Signals:
{signals}

Components:
{json.dumps(components)}

Example:
[
  {{"field": "data_size", "question": "How much data is processed per day (GB/TB)?"}}
]
"""

    raw = call_ollama(prompt)
    data = safe_json_extract(raw)

    if isinstance(data, list):
        return data

    return []


# -------------------------------------------
# FILTER QUESTIONS BY INTENT (CRITICAL)
# -------------------------------------------
def filter_by_intent(questions, intent):

    if intent == "LOGGING":
        allowed = {"storage_size", "data_size"}

    elif intent == "ETL":
        allowed = {"data_size", "compute_hours", "frequency"}

    elif intent == "STREAMING":
        allowed = {"throughput", "requests_per_sec", "compute_hours"}

    else:
        return questions

    return [q for q in questions if q.get("field") in allowed]


# -------------------------------------------
# SKIP ALREADY KNOWN SIGNALS
# -------------------------------------------
def filter_known_fields(questions, signals):
    return [q for q in questions if q.get("field") not in signals]


# -------------------------------------------
# VALIDATE QUESTIONS
# -------------------------------------------
def validate_questions(questions):
    valid = []

    for q in questions:
        field = q.get("field")
        question = q.get("question")

        if (
            field and
            isinstance(field, str) and
            field in VALID_FIELDS and
            question
        ):
            valid.append(q)
        else:
            print(f"⚠️ Skipping invalid question: {q}")

    return valid


# -------------------------------------------
# FALLBACK QUESTIONS
# -------------------------------------------
def fallback_questions(components, signals, intent):

    questions = []

    if intent == "ETL":
        if "frequency" not in signals:
            questions.append({
                "field": "frequency",
                "question": "How often does this run (daily/hourly)?"
            })

        questions.append({
            "field": "data_size",
            "question": "How much data is processed per run (GB/TB)?"
        })

        questions.append({
            "field": "compute_hours",
            "question": "Approx compute hours per run?"
        })

    elif intent == "LOGGING":
        questions.append({
            "field": "storage_size",
            "question": "How much data is stored (GB/TB)?"
        })

    elif intent == "STREAMING":
        questions.append({
            "field": "throughput",
            "question": "Events per second?"
        })

    else:
        questions.append({
            "field": "data_size",
            "question": "Estimated data size (GB/TB)?"
        })

    return questions[:2]


# -------------------------------------------
# APPLY USER ANSWERS
# -------------------------------------------
def apply_answers(components, answers):
    for comp in components:
        for k, v in answers.items():
            if k:
                comp[k] = v
    return components


# -------------------------------------------
# FINAL CLARIFIER AGENT
# -------------------------------------------
def clarifier_agent(components, user_input="", intent=None):
    print("🤖 Clarifier Agent (LLM + Intent) starting...")

    # Step 1: extract signals
    signals = extract_signals(user_input)

    # Step 2: LLM questions
    questions = llm_generate_questions(
        components,
        user_input,
        signals,
        intent
    )

    # Step 3: validation + filtering pipeline
    questions = validate_questions(questions)
    questions = filter_by_intent(questions, intent)
    questions = filter_known_fields(questions, signals)

    # Step 4: fallback if nothing left
    if not questions:
        print("⚠️ Using fallback questions")
        questions = fallback_questions(components, signals, intent)

    # Step 5: LIMIT QUESTIONS (VERY IMPORTANT)
    questions = questions[:2]

    print("\n🧠 Smart Questions:")

    answers = {}

    for q in questions:
        field = q["field"]
        question = q["question"]

        val = input(f"→ {question} ").strip()

        if val:
            answers[field] = val

    # Step 6: apply answers
    components = apply_answers(components, answers)

    return components
