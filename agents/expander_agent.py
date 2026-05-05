# -------------------------------------------
# SAFE GETTER
# -------------------------------------------
def safe_get(comp, key, default=""):
    return comp.get(key, default) or default


# -------------------------------------------
# DEDUPLICATION
# -------------------------------------------
def deduplicate(components):
    seen = set()
    unique = []

    for c in components:
        name = c.get("name", "").strip().lower()
        ctype = c.get("type", "").strip().lower()

        key = (name, ctype)

        if key not in seen:
            seen.add(key)
            unique.append(c)

    return unique


# -------------------------------------------
# MAIN EXPANDER AGENT (INTENT-AWARE)
# -------------------------------------------
def expander_agent(components, user_input="", intent=None):

    print("\n🤖 Agent 2.5 (Expander) starting...")

    expanded = list(components)

    intent_type = intent.get("intent") if intent else "UNKNOWN"

    # -------------------------------------------
    # DETECT EXISTING COMPONENTS
    # -------------------------------------------
    has_storage = any(c.get("type") == "Object Storage" for c in components)
    has_bq = any(c.get("type") == "Data Warehouse" for c in components)
    has_stream = any(c.get("type") == "Streaming Queue" for c in components)
    has_compute = any(c.get("type") == "Compute" for c in components)

    region = components[0].get("region", "global") if components else "global"

    # -------------------------------------------
    # INTENT-BASED EXPANSION (CORE FIX)
    # -------------------------------------------

    # 🚫 LOGGING → DO NOT expand
    if intent_type == "LOGGING":
        print("⚡ Logging intent → no expansion needed")
        return components

    # 📦 STORAGE → minimal
    if intent_type == "STORAGE":
        print("⚡ Storage intent → no expansion")
        return components

    # 🔄 ETL PIPELINE
    if intent_type == "ETL":
        print("⚡ ETL intent detected")

        if has_storage and has_bq and not has_stream:
            expanded.append({
                "name": "pubsub-event-stream",
                "type": "Streaming Queue",
                "region": region
            })

        if not has_compute:
            expanded.append({
                "name": "dataflow-processor",
                "type": "Compute",
                "region": region
            })

    # ⚡ STREAMING PIPELINE
    elif intent_type == "STREAMING":
        print("⚡ Streaming intent detected")

        if not has_stream:
            expanded.append({
                "name": "pubsub-event-stream",
                "type": "Streaming Queue",
                "region": region
            })

        if not has_compute:
            expanded.append({
                "name": "dataflow-processor",
                "type": "Compute",
                "region": region
            })

    # 🔗 API INTENT
    elif intent_type == "API":
        print("⚡ API intent detected")

        expanded.append({
            "name": "api-gateway",
            "type": "API Layer",
            "region": region
        })

    # ❓ UNKNOWN → fallback to light inference
    else:
        print("⚠️ Unknown intent → using safe fallback")

        if has_storage and has_bq and not has_stream:
            expanded.append({
                "name": "pubsub-event-stream",
                "type": "Streaming Queue",
                "region": region
            })

    # -------------------------------------------
    # FINAL CLEANUP
    # -------------------------------------------
    expanded = deduplicate(expanded)

    print("✅ Final Expanded Components:", expanded)

    return expanded
