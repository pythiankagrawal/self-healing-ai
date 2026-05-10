import streamlit as st
import json

from agents.parser_agent import parser_agent
from agents.intent_agent import intent_agent
from agents.expander_agent import expander_agent
from agents.clarifier_agent import clarifier_agent
from agents.cost_agent import cost_agent

st.set_page_config(
    page_title="Intelligent FinOps Advisor",
    layout="wide"
)

st.title("🚀 Intelligent FinOps Advisor")

user_input = st.text_area(
    "Describe your cloud architecture",
    height=150
)

if st.button("Analyze Architecture"):

    if not user_input.strip():
        st.warning("Please enter architecture description")
        st.stop()

    # ---------------------------------------
    # Parser
    # ---------------------------------------
    with st.spinner("Running Parser Agent..."):
        components = parser_agent(user_input)

    st.subheader("📦 Parsed Components")
    st.json(components)

    # ---------------------------------------
    # Intent
    # ---------------------------------------
    with st.spinner("Running Intent Agent..."):
        intent = intent_agent(user_input, components)

    st.subheader("🧠 Intent Analysis")
    st.json(intent)

    # ---------------------------------------
    # Expander
    # ---------------------------------------
    with st.spinner("Running Expander Agent..."):
        components = expander_agent(
            components,
            user_input,
            intent
        )

    st.subheader("⚙️ Expanded Architecture")
    st.json(components)

    # ---------------------------------------
    # Clarifier
    # ---------------------------------------
    with st.spinner("Running Clarifier Agent..."):
        components = clarifier_agent(
            components,
            user_input,
            intent
        )

    st.subheader("❓ Enriched Workload")
    st.json(components)

    # ---------------------------------------
    # Cost
    # ---------------------------------------
    with st.spinner("Running Cost Agent..."):
        result = cost_agent(
            components,
            user_input,
            intent
        )

    st.subheader("💰 Cost Report")
    st.json(result)

    # ---------------------------------------
    # Breakdown Table
    # ---------------------------------------
    st.subheader("📊 Cost Breakdown")

    for item in result.get("breakdown", []):

        st.metric(
            label=item["name"],
            value=f"${item['monthly_cost']}"
        )

        st.caption(item["reason"])

    # ---------------------------------------
    # Optimizations
    # ---------------------------------------
    st.subheader("🧠 Optimizations")

    for opt in result.get("optimizations", []):
        st.success(opt)
