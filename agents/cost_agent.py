from core.unified_cost_engine import MultiCloudCostEngine


# -------------------------------------------
# OPTIMIZATION ENGINE (RULE-BASED FINOPS)
# -------------------------------------------
def optimize_architecture(components, breakdown, total_cost):
    print("\n🧠 Optimization Engine starting...")

    suggestions = []

    if not components:
        return suggestions

    types = [c.get("type", "") for c in components]

    # ---------------------------------------
    # RULE 1: Streaming unnecessary detection
    # ---------------------------------------
    if "Streaming Queue" in types and "Data Warehouse" in types:
        suggestions.append({
            "issue": "Streaming layer may be unnecessary",
            "recommendation": "If data is not real-time, replace Pub/Sub with batch GCS → BigQuery load",
            "impact": "20–40% cost reduction"
        })

    # ---------------------------------------
    # RULE 2: Storage-heavy workload
    # ---------------------------------------
    storage_cost = sum(
        b["cost"] for b in breakdown
        if "Storage" in b["type"]
    )

    if total_cost > 0 and storage_cost / total_cost > 0.5:
        suggestions.append({
            "issue": "Storage dominates total cost",
            "recommendation": "Enable lifecycle policies (Coldline/Archive tiers)",
            "impact": "30–70% storage cost reduction"
        })

    # ---------------------------------------
    # RULE 3: Over-engineered pipeline
    # ---------------------------------------
    if len(components) >= 4 and "Streaming Queue" not in types:
        suggestions.append({
            "issue": "Over-engineered batch pipeline",
            "recommendation": "Simplify architecture (remove unnecessary compute hops)",
            "impact": "15–30% infra reduction"
        })

    return suggestions


# -------------------------------------------
# COST AGENT (MAIN ENTRY)
# -------------------------------------------
def cost_agent(components, user_context=""):
    print("\n💰 Agent 3 (Cost + Optimization) starting...")

    engine = MultiCloudCostEngine()

    total_cost = 0
    breakdown = []

    # ---------------------------------------
    # COST CALCULATION
    # ---------------------------------------
    for comp in components:
        cost = engine.get_cost(comp)

        total_cost += cost

        breakdown.append({
            "name": comp.get("name"),
            "type": comp.get("type"),
            "region": comp.get("region", "global"),
            "cost": round(cost, 4)
        })

    # ---------------------------------------
    # OPTIMIZATION
    # ---------------------------------------
    optimizations = optimize_architecture(
        components,
        breakdown,
        total_cost
    )

    # ---------------------------------------
    # FINAL OUTPUT
    # ---------------------------------------
    result = {
        "total_cost": round(total_cost, 4),
        "breakdown": breakdown,
        "optimizations": optimizations
    }

    print("✅ Cost Agent finished.")
    return result
