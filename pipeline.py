from agents.parser_agent import parser_agent
from agents.clarifier_agent import clarifier_agent
from agents.expander_agent import expander_agent
from agents.cost_agent import cost_agent
from agents.report_agent import report_agent
from agents.intent_agent import intent_agent


# =========================================================
# MAIN PIPELINE
# =========================================================
def run_pipeline(user_input):

    # =====================================================
    # 1. PARSER
    # =====================================================
    components = parser_agent(user_input)

    # =====================================================
    # 2. INTENT DETECTION
    # =====================================================
    intent = intent_agent(
        user_input,
        components
    )

    # =====================================================
    # 3. EXPANDER
    # =====================================================
    components = expander_agent(
        components,
        user_input,
        intent
    )

    # =====================================================
    # 4. CLARIFIER
    # =====================================================
    components = clarifier_agent(
        components,
        user_input,
        intent
    )

    print("\n📦 FINAL COMPONENTS:")
    print(components)

    # =====================================================
    # 5. COST ESTIMATION
    # =====================================================
    result = cost_agent(
        components,
        user_input,
        intent
    )

    # =====================================================
    # 6. REPORT GENERATION
    # =====================================================
    report_agent(
        components,
        result,
        intent
    )

    # =====================================================
    # 7. FINAL TERMINAL REPORT
    # =====================================================
    print("\n====================================")
    print("💰 FINAL FINOPS REPORT")
    print("====================================")

    # -----------------------------------------------------
    # TOTAL COST
    # -----------------------------------------------------
    print(
        "\nTOTAL COST:",
        result.get("total_cost", 0),
        result.get("currency", "USD")
    )

    # -----------------------------------------------------
    # BREAKDOWN
    # -----------------------------------------------------
    print("\nBREAKDOWN:")

    breakdown = result.get("breakdown", [])

    if breakdown:

        for b in breakdown:

            print(
                f"- {b.get('name', 'unknown')} "
                f"({b.get('type', 'unknown')}) "
                f"→ ${b.get('monthly_cost', 0)}"
            )

            if b.get("reason"):
                print(f"  Reason: {b['reason']}")

    else:
        print("- No breakdown available")

    # -----------------------------------------------------
    # ASSUMPTIONS
    # -----------------------------------------------------
    assumptions = result.get(
        "assumptions",
        []
    )

    print("\n📘 ASSUMPTIONS:")

    if assumptions:

        for a in assumptions:
            print("-", a)

    else:
        print("- None")

    # -----------------------------------------------------
    # OPTIMIZATIONS
    # -----------------------------------------------------
    print("\n🧠 OPTIMIZATIONS:")

    optimizations = result.get(
        "optimizations",
        result.get(
            "optimization_recommendations",
            []
        )
    )

    if optimizations:

        for o in optimizations:

            # dict format
            if isinstance(o, dict):

                print(
                    "-",
                    o.get(
                        "recommendation",
                        str(o)
                    )
                )

            # string format
            else:
                print("-", o)

    else:
        print("- No optimizations")

    print("\n====================================")


# =========================================================
# ENTRYPOINT
# =========================================================
if __name__ == "__main__":

    print("🚀 Intelligent FinOps Advisor")
    print("----------------------------------")
    print(
        "Paste your architecture "
        "(press ENTER twice to finish):\n"
    )

    lines = []

    while True:

        line = input()

        if line.strip() == "":
            break

        lines.append(line)

    user_input = "\n".join(lines)

    run_pipeline(user_input)
