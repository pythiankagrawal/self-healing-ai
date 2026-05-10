import json


# =========================================================
# COMPONENT TYPE ORDERING
# =========================================================
COMPONENT_ORDER = {
    "Client": 1,
    "CDN": 2,
    "Load Balancer": 3,
    "API Layer": 4,
    "Security": 5,
    "Streaming Queue": 6,
    "CDC/Streaming": 7,
    "Messaging": 8,
    "Compute": 9,
    "Container Platform": 10,
    "Cache": 11,
    "Database": 12,
    "Object Storage": 13,
    "Data Warehouse": 14,
    "Analytics": 15,
    "ML Platform": 16,
    "Monitoring": 17
}


# =========================================================
# DEDUPLICATE COMPONENTS
# =========================================================
def deduplicate_components(components):

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
# SORT COMPONENTS
# =========================================================
def sort_components(components):

    return sorted(
        components,
        key=lambda x: COMPONENT_ORDER.get(
            x.get("type"),
            999
        )
    )


# =========================================================
# BUILD DAG
# =========================================================
def build_dag(components):

    dag = []

    ordered = sort_components(components)

    for i in range(len(ordered) - 1):

        source = ordered[i]
        target = ordered[i + 1]

        dag.append({
            "from": source["name"],
            "to": target["name"]
        })

    return dag


# =========================================================
# GENERATE MERMAID DIAGRAM
# =========================================================
def generate_mermaid(components):

    ordered = sort_components(components)

    lines = ["graph LR"]

    created_nodes = set()

    # -----------------------------------------------------
    # CREATE NODES
    # -----------------------------------------------------
    for component in ordered:

        name = component["name"]
        ctype = component["type"]

        safe_name = (
            name.replace("-", "_")
            .replace(" ", "_")
            .lower()
        )

        if safe_name in created_nodes:
            continue

        created_nodes.add(safe_name)

        label = f"{name}<br/>{ctype}"

        lines.append(
            f'{safe_name}["{label}"]'
        )

    # -----------------------------------------------------
    # CREATE EDGES
    # -----------------------------------------------------
    created_edges = set()

    for i in range(len(ordered) - 1):

        a = (
            ordered[i]["name"]
            .replace("-", "_")
            .replace(" ", "_")
            .lower()
        )

        b = (
            ordered[i + 1]["name"]
            .replace("-", "_")
            .replace(" ", "_")
            .lower()
        )

        edge = (a, b)

        if edge in created_edges:
            continue

        created_edges.add(edge)

        lines.append(f"{a} --> {b}")

    return "\n".join(lines)


# =========================================================
# GENERATE ARCHITECTURE SUMMARY
# =========================================================
def generate_architecture_summary(
    components,
    intent
):

    distribution = {}

    for c in components:

        ctype = c.get("type", "Unknown")

        distribution[ctype] = (
            distribution.get(ctype, 0) + 1
        )

    return {
        "primary_intent": (
            intent.get("primary_intent")
            if intent else "UNKNOWN"
        ),
        "architecture_pattern": (
            intent.get("architecture_pattern")
            if intent else "UNKNOWN"
        ),
        "total_components": len(components),
        "component_distribution": distribution
    }


# =========================================================
# GENERATE EXECUTIVE SUMMARY
# =========================================================
def generate_executive_summary(
    intent,
    cost_result,
    components
):

    primary_intent = (
        intent.get("primary_intent", "UNKNOWN")
        if intent else "UNKNOWN"
    )

    architecture_pattern = (
        intent.get("architecture_pattern", "UNKNOWN")
        if intent else "UNKNOWN"
    )

    total_cost = cost_result.get(
        "total_cost",
        0
    )

    summary = (
        f"This architecture represents a "
        f"{primary_intent} workload using "
        f"{len(components)} cloud services "
        f"following a {architecture_pattern} "
        f"design with an estimated monthly "
        f"cost of ${total_cost}."
    )

    return summary


# =========================================================
# RISK ANALYSIS
# =========================================================
def generate_risk_analysis(
    components,
    cost_result
):

    risks = []

    total_cost = cost_result.get(
        "total_cost",
        0
    )

    component_types = [
        c.get("type")
        for c in components
    ]

    component_names = [
        c.get("name", "").lower()
        for c in components
    ]

    # -----------------------------------------------------
    # COST RISK
    # -----------------------------------------------------
    if total_cost > 5000:

        risks.append(
            "High projected monthly cloud spend"
        )

    # -----------------------------------------------------
    # DATABASE WITHOUT BACKUP
    # -----------------------------------------------------
    if (
        "Database" in component_types and
        "gcs" not in component_names
    ):

        risks.append(
            "Database workload without backup/archive storage"
        )

    # -----------------------------------------------------
    # STREAMING WITHOUT MONITORING
    # -----------------------------------------------------
    if (
        "Streaming Queue" in component_types or
        "CDC/Streaming" in component_types
    ):

        if "Monitoring" not in component_types:

            risks.append(
                "Streaming workloads should include monitoring/alerting"
            )

    # -----------------------------------------------------
    # API WITHOUT SECURITY
    # -----------------------------------------------------
    if (
        "API Layer" in component_types and
        "Security" not in component_types
    ):

        risks.append(
            "API infrastructure missing security layer"
        )

    return risks


# =========================================================
# RECOMMENDATIONS
# =========================================================
def generate_recommendations(
    components,
    cost_result
):

    recommendations = []

    component_types = {
        c["type"]
        for c in components
    }

    # -----------------------------------------------------
    # STORAGE
    # -----------------------------------------------------
    if "Object Storage" in component_types:

        recommendations.append(
            "Enable lifecycle tiering for object storage"
        )

    # -----------------------------------------------------
    # COMPUTE
    # -----------------------------------------------------
    if "Compute" in component_types:

        recommendations.append(
            "Use autoscaling and spot/preemptible compute where possible"
        )

    # -----------------------------------------------------
    # DATA WAREHOUSE
    # -----------------------------------------------------
    if "Data Warehouse" in component_types:

        recommendations.append(
            "Use partitioning and clustering to reduce BigQuery query cost"
        )

    # -----------------------------------------------------
    # STREAMING
    # -----------------------------------------------------
    if (
        "Streaming Queue" in component_types or
        "CDC/Streaming" in component_types
    ):

        recommendations.append(
            "Tune retention and throughput settings for streaming workloads"
        )

    return list(set(recommendations))


# =========================================================
# FINAL REPORT AGENT
# =========================================================
def report_agent(
    components,
    cost_result,
    intent=None
):

    print("\n📊 Intelligent Report Agent starting...")

    # =====================================================
    # STEP 1: DEDUP
    # =====================================================
    components = deduplicate_components(
        components
    )

    # =====================================================
    # STEP 2: SORT
    # =====================================================
    components = sort_components(
        components
    )

    # =====================================================
    # STEP 3: BUILD DAG
    # =====================================================
    dag = build_dag(
        components
    )

    # =====================================================
    # STEP 4: MERMAID
    # =====================================================
    mermaid = generate_mermaid(
        components
    )

    # =====================================================
    # STEP 5: SUMMARY
    # =====================================================
    architecture_summary = (
        generate_architecture_summary(
            components,
            intent
        )
    )

    # =====================================================
    # STEP 6: EXECUTIVE SUMMARY
    # =====================================================
    executive_summary = (
        generate_executive_summary(
            intent,
            cost_result,
            components
        )
    )

    # =====================================================
    # STEP 7: RISKS
    # =====================================================
    risks = generate_risk_analysis(
        components,
        cost_result
    )

    # =====================================================
    # STEP 8: RECOMMENDATIONS
    # =====================================================
    recommendations = (
        generate_recommendations(
            components,
            cost_result
        )
    )

    # =====================================================
    # STEP 9: FINAL REPORT OBJECT
    # =====================================================
    report = {
        "executive_summary": executive_summary,
        "architecture_summary": architecture_summary,
        "components": components,
        "dag": dag,
        "mermaid_diagram": mermaid,
        "cost_analysis": cost_result,
        "risks": risks,
        "recommendations": recommendations
    }

    # =====================================================
    # STEP 10: PRINT REPORT
    # =====================================================
    print("\n====================================")
    print("📘 FINAL FINOPS ARCHITECTURE REPORT")
    print("====================================")

    print("\n🧠 EXECUTIVE SUMMARY:")
    print(executive_summary)

    print("\n🏗️ ARCHITECTURE COMPONENTS:")

    for c in components:

        print(
            f"- {c['name']} "
            f"({c['type']}) "
            f"[{c.get('region', 'global')}]"
        )

    print("\n📈 MERMAID DIAGRAM:")
    print(mermaid)

    print("\n💰 TOTAL ESTIMATED MONTHLY COST:")
    print(f"${cost_result.get('total_cost', 0)}")

    print("\n📦 COST BREAKDOWN:")

    for item in cost_result.get(
        "breakdown",
        []
    ):

        print(
            f"- {item.get('name')} "
            f"({item.get('type')}) "
            f"→ ${item.get('monthly_cost', 0)}"
        )

    print("\n⚠️ RISKS:")

    if risks:
        for risk in risks:
            print(f"- {risk}")
    else:
        print("- No major risks detected")

    print("\n🧠 RECOMMENDATIONS:")

    if recommendations:
        for r in recommendations:
            print(f"- {r}")
    else:
        print("- No recommendations")

    print("\n====================================")

    return report
