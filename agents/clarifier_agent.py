from llm.ollama_client import call_ollama
import json
import re


# =========================================================
# SAFE JSON EXTRACTION
# =========================================================
def extract_json(raw):

    if not raw:
        return None

    try:
        # extract JSON array
        match = re.search(r"\[.*\]", raw, re.DOTALL)

        if not match:
            return None

        json_str = match.group()

        # cleanup
        json_str = json_str.replace("\n", " ")
        json_str = json_str.replace("\t", " ")
        json_str = json_str.replace("'", '"')

        # remove trailing commas
        json_str = re.sub(r",\s*]", "]", json_str)
        json_str = re.sub(r",\s*}", "}", json_str)

        return json.loads(json_str)

    except Exception as e:
        print("⚠️ JSON parse failed:", e)

    return None


# =========================================================
# NORMALIZE QUESTIONS
# =========================================================
def normalize_questions(questions):

    normalized = []

    seen_fields = set()

    for q in questions:

        if not isinstance(q, dict):
            continue

        field = str(q.get("field", "")).strip()
        question = str(q.get("question", "")).strip()

        if not field or not question:
            continue

        # dedup
        if field in seen_fields:
            continue

        seen_fields.add(field)

        normalized.append({
            "field": field,
            "question": question
        })

    return normalized


# =========================================================
# FILTER QUESTIONS
# =========================================================
def filter_known_questions(
    questions,
    components,
    intent,
    user_input
):

    known_fields = set()

    # -----------------------------------------
    # Existing component fields
    # -----------------------------------------
    for comp in components:
        for k, v in comp.items():

            if v not in [None, "", "unknown"]:
                known_fields.add(k)

    # -----------------------------------------
    # Intent signals
    # -----------------------------------------
    signals = intent.get("signals", {})

    for k, v in signals.items():
        if v not in [None, "", False]:
            known_fields.add(k)

    # -----------------------------------------
    # Remove known questions
    # -----------------------------------------
    filtered = []

    for q in questions:

        field = q["field"]

        if field not in known_fields:
            filtered.append(q)

    return filtered


# =========================================================
# BUILD WORKLOAD PROFILE
# =========================================================
def build_workload_profile(components):

    profile = {
        "storage_services": [],
        "compute_services": [],
        "streaming_services": [],
        "database_services": [],
        "warehouse_services": []
    }

    for c in components:

        ctype = c.get("type", "")

        if ctype == "Object Storage":
            profile["storage_services"].append(c["name"])

        elif ctype == "Compute":
            profile["compute_services"].append(c["name"])

        elif ctype in ["Streaming", "Streaming Queue"]:
            profile["streaming_services"].append(c["name"])

        elif ctype == "Database":
            profile["database_services"].append(c["name"])

        elif ctype == "Data Warehouse":
            profile["warehouse_services"].append(c["name"])

    return profile


# =========================================================
# MAIN CLARIFIER AGENT
# =========================================================
def clarifier_agent(
    components,
    user_input,
    intent
):

    print("\n🤖 Intelligent Clarifier Agent starting...")

    workload_profile = build_workload_profile(
        components
    )

    # =====================================================
    # MASTER PROMPT
    # =====================================================
    prompt = f"""
You are a principal FinOps architect.

Your task is to identify ONLY the MOST IMPORTANT
missing workload metadata required for accurate
cloud cost estimation.

IMPORTANT:
You are NOT a chatbot.

You are building a workload specification
for a cloud pricing engine.

=================================================
GOAL
=================================================

Your questions must help estimate:

- storage cost
- compute cost
- streaming cost
- API cost
- query cost
- network cost
- retention cost

=================================================
CRITICAL THINKING
=================================================

You must reason deeply about:

1. workload pattern
2. traffic characteristics
3. scaling behavior
4. storage growth
5. data processing frequency
6. streaming throughput
7. query volume
8. retention requirements
9. compute runtime
10. autoscaling behavior

=================================================
USER INPUT
=================================================

{user_input}

=================================================
INTENT ANALYSIS
=================================================

{json.dumps(intent, indent=2)}

=================================================
ARCHITECTURE COMPONENTS
=================================================

{json.dumps(components, indent=2)}

=================================================
WORKLOAD PROFILE
=================================================

{json.dumps(workload_profile, indent=2)}

=================================================
STRICT RULES
=================================================

- Return ONLY JSON array
- No markdown
- No explanation
- Maximum 7 questions
- Ask ONLY cost-critical questions
- DO NOT ask already known info
- DO NOT ask generic questions
- DO NOT ask architecture design questions
- Questions must be highly specific
- Questions must be workload-aware

=================================================
ALLOWED FIELDS
=================================================

data_size_per_day
monthly_storage
retention_days
requests_per_second
events_per_second
throughput_mb_per_sec
compute_hours_per_day
avg_query_tb_per_day
concurrent_users
api_requests_per_day
peak_traffic_multiplier
streaming_enabled
batch_window_minutes
replication_factor
backup_enabled
storage_class
machine_type
worker_count
autoscaling_enabled
network_egress_gb
daily_growth_rate

=================================================
GOOD QUESTIONS
=================================================

[
  {{
    "field": "data_size_per_day",
    "question": "How much data is processed per day (GB/TB)?"
  }},
  {{
    "field": "retention_days",
    "question": "How long should logs/data be retained?"
  }},
  {{
    "field": "events_per_second",
    "question": "Approximate streaming events per second?"
  }}
]

=================================================
BAD QUESTIONS
=================================================

- "What is your use case?"
- "Which cloud provider?"
- "What architecture do you want?"
- "Do you need scaling?"
- "Any other requirements?"

=================================================
RETURN FORMAT
=================================================

[
  {{
    "field": "",
    "question": ""
  }}
]
"""

    raw = call_ollama(prompt)

    print("\n🔍 RAW CLARIFIER OUTPUT:")
    print(raw)

    questions = extract_json(raw)

    if not questions:
        raise Exception(
            "Clarifier Agent failed: Invalid JSON response"
        )

    # =====================================================
    # NORMALIZATION
    # =====================================================
    questions = normalize_questions(
        questions
    )

    # =====================================================
    # REMOVE KNOWN QUESTIONS
    # =====================================================
    questions = filter_known_questions(
        questions,
        components,
        intent,
        user_input
    )

    # =====================================================
    # FAIL FAST
    # =====================================================
    if not questions:

        print(
            "\n✅ No additional workload metadata needed."
        )

        return components

    # =====================================================
    # ASK QUESTIONS
    # =====================================================
    print("\n🧠 Intelligent Workload Questions:\n")

    answers = {}

    for q in questions:

        field = q["field"]
        question = q["question"]

        value = input(f"→ {question}: ").strip()

        if value:
            answers[field] = value

    # =====================================================
    # ENRICH COMPONENTS
    # =====================================================
    enriched_components = []

    for comp in components:

        updated = comp.copy()

        # attach workload metadata
        updated["workload_profile"] = answers

        enriched_components.append(updated)

    # =====================================================
    # FINAL OUTPUT
    # =====================================================
    print("\n✅ ENRICHED WORKLOAD PROFILE")
    print(json.dumps(enriched_components, indent=2))

    return enriched_components
