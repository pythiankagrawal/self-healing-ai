def build_dag(components):
    """
    Very basic DAG builder based on common patterns
    """

    order = {
        "Object Storage": 1,
        "Streaming Queue": 2,
        "Compute": 3,
        "Data Warehouse": 4,
        "Database": 5,
        "API Layer": 6
    }

    return sorted(components, key=lambda x: order.get(x["type"], 99))


def generate_mermaid(dag):
    """
    Generate Mermaid diagram
    """

    lines = ["graph LR"]

    for i in range(len(dag) - 1):
        a = dag[i]["name"]
        b = dag[i + 1]["name"]
        lines.append(f"{a} --> {b}")

    return "\n".join(lines)


def generate_cost_summary(breakdown):
    total = sum(x["cost"] for x in breakdown)

    summary = []
    for b in breakdown:
        percent = (b["cost"] / total) * 100 if total else 0
        summary.append({
            "name": b["name"],
            "type": b["type"],
            "cost": b["cost"],
            "percent": round(percent, 2)
        })

    return summary


def generate_insights(summary):
    insights = []

    if not summary:
        return insights

    max_comp = max(summary, key=lambda x: x["cost"])

    insights.append(
        f"Highest cost component is {max_comp['name']} ({max_comp['type']}) contributing {max_comp['percent']}%"
    )

    if max_comp["type"] == "Compute":
        insights.append("Consider autoscaling or smaller instance sizes")

    if max_comp["type"] == "Data Warehouse":
        insights.append("Consider partitioning or clustering to reduce cost")

    return insights


def report_agent(components, cost_result):
    print("\n📊 Agent 4 (Report + DAG) starting...")

    dag = build_dag(components)

    mermaid = generate_mermaid(dag)

    summary = generate_cost_summary(cost_result["breakdown"])

    insights = generate_insights(summary)

    print("\n🧩 ARCHITECTURE DAG:")
    for c in dag:
        print(f"{c['type']} → {c['name']}")

    print("\n📈 MERMAID DIAGRAM:")
    print(mermaid)

    print("\n💰 COST SUMMARY:")
    for s in summary:
        print(f"{s['name']} ({s['type']}): ${s['cost']} ({s['percent']}%)")

    print("\n🧠 INSIGHTS:")
    for i in insights:
        print("-", i)

    return {
        "dag": dag,
        "diagram": mermaid,
        "summary": summary,
        "insights": insights
    }
