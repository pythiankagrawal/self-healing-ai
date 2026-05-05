from agents.parser_agent import parser_agent
from agents.clarifier_agent import clarifier_agent
from agents.expander_agent import expander_agent
from agents.cost_agent import cost_agent
from agents.report_agent import report_agent

def run_pipeline(user_input):

    components = parser_agent(user_input)
    components = clarifier_agent(components)
    components = expander_agent(components, user_input)

    result = cost_agent(components, user_input)
    report_agent(components, result)

    print("\n====================================")
    print("💰 FINAL FINOPS REPORT")
    print("====================================")

    print("\nTOTAL COST:", result["total_cost"])

    print("\nBREAKDOWN:")
    for b in result["breakdown"]:
        print(b)

    print("\n🧠 OPTIMIZATIONS:")
    for o in result["optimizations"]:
        print("-", o["recommendation"])


if __name__ == "__main__":
    print("🚀 Intelligent FinOps Advisor")
    print("----------------------------------")
    print("Paste your architecture (press ENTER twice to finish):\n")

    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)

    user_input = "\n".join(lines)

    run_pipeline(user_input)
