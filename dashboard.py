import streamlit as st
import importlib
import pandas as pd
import altair as alt
import AgenticMortgageResearchAgent
import config
st.sidebar.info("App version: v1.1.0")

# Initialize LLM client if API key is available
llm_client = None
if config.ENABLE_LLM_PLANNING:
    try:
        from anthropic import Anthropic
        llm_client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    except Exception as e:
        st.warning(f"Could not initialize LLM: {e}. Using heuristic-based planning.")

# Reload agent code
importlib.reload(AgenticMortgageResearchAgent)
from AgenticMortgageResearchAgent import AgenticMortgageResearchAgent

# ---------- Page Config ----------
st.set_page_config(page_title=config.STREAMLIT_PAGE_TITLE, layout=config.STREAMLIT_LAYOUT)
st.title("🏠 Agentic Mortgage Research Agent Dashboard")

# ---------- Session State ----------
if "agent" not in st.session_state:
    def ui_log_callback(msg):
        if "logs_text" not in st.session_state:
            st.session_state.logs_text = []
        st.session_state.logs_text.append(msg)
        # Update placeholder for logs if it has been created
        if st.session_state.get("logs_area") is not None:
            st.session_state.logs_area.text("\n".join(st.session_state.logs_text))

    st.session_state.agent = AgenticMortgageResearchAgent(log_callback=ui_log_callback, llm_client=llm_client)
    st.session_state.logs_text = []
    st.session_state.first_run = True
else:
    st.session_state.first_run = False

agent = st.session_state.agent

# Initialize logs_area as None (will be created before it's needed for display)
if "logs_area" not in st.session_state:
    st.session_state.logs_area = None

# Run agentic plan on first load
if st.session_state.first_run:
    with st.spinner("🤖 Agent is analyzing mortgage market..."):
        try:
            agent.run_action("agentic_plan", force=False)
        except Exception as e:
            st.error(f"Error running agentic plan: {e}")
    st.session_state.first_run = False

# ---------- Sidebar ----------
st.sidebar.title("Agent Actions")
force_refresh = st.sidebar.checkbox("Force refresh", value=False)

def run_action_ui(action_name, use_spinner=True):
    try:
        if use_spinner:
            with st.spinner(f"Running {action_name}..."):
                agent.run_action(action_name, force=force_refresh)
        else:
            agent.run_action(action_name, force=force_refresh)
    except Exception as e:
        st.error(f"Error running {action_name}: {e}")

# Core actions
if st.sidebar.button("Fetch Mortgage Rates"):
    run_action_ui("fetch_mortgage_rates")
if st.sidebar.button("Analyze Rates"):
    run_action_ui("analyze_rates")
if st.sidebar.button("Fetch Home Prices"):
    run_action_ui("fetch_home_prices")
if st.sidebar.button("Compare with Home Prices"):
    run_action_ui("compare_with_home_prices")
if st.sidebar.button("Summarize Insights"):
    run_action_ui("summarize_insights")
if st.sidebar.button("Agentic Plan"):
    run_action_ui("agentic_plan")

# Clear logs
if st.sidebar.button("Clear Logs"):
    agent.logs.clear()
    st.session_state.logs_text = []
    st.session_state.logs_area.text("")

# ---------- Executive Summary ----------
st.subheader("📊 Executive Summary")
st.write(agent.knowledge.get("summary", "No summary available."))

# ---------- Visualizations ----------
st.subheader("📈 Data Visualizations")

# Mortgage Rates Chart
if "mortgage_rates" in agent.knowledge and not agent.knowledge["mortgage_rates"].empty:
    df_rates = agent.knowledge["mortgage_rates"]
    st.altair_chart(
        alt.Chart(df_rates).mark_line(color='blue').encode(
            x='date:T',
            y='rate:Q',
            tooltip=['date:T', 'rate:Q']
        ).properties(title='30-Year Fixed Mortgage Rates', height=300),
        use_container_width=True
    )

# Home Prices Chart
if "home_prices" in agent.knowledge and not agent.knowledge["home_prices"].empty:
    df_prices = agent.knowledge["home_prices"]
    st.altair_chart(
        alt.Chart(df_prices).mark_line(color='green').encode(
            x='date:T',
            y='price:Q',
            tooltip=['date:T', 'price:Q']
        ).properties(title='US Home Prices Index', height=300),
        use_container_width=True
    )

# Combined normalized chart
if all(k in agent.knowledge for k in ["mortgage_rates", "home_prices"]):
    df_rates = agent.knowledge["mortgage_rates"]
    df_prices = agent.knowledge["home_prices"]
    df_combined = pd.merge_asof(
        df_rates.sort_values("date"),
        df_prices.sort_values("date"),
        on="date"
    )
    df_combined['rate_norm'] = df_combined['rate'] / df_combined['rate'].max()
    df_combined['price_norm'] = df_combined['price'] / df_combined['price'].max()

    chart_combined = alt.Chart(df_combined).transform_fold(
        ['rate_norm', 'price_norm'],
        as_=['Metric', 'Value']
    ).mark_line().encode(
        x='date:T',
        y='Value:Q',
        color='Metric:N',
        tooltip=['date:T', 'Metric:N', 'Value:Q']
    ).properties(title='Normalized Mortgage Rates vs Home Prices', height=300)
    st.altair_chart(chart_combined, use_container_width=True)

# ---------- Agent Logs ----------
st.subheader("📝 Agent Logs")

# Create logs placeholder (will be used for real-time updates on button clicks)
if st.session_state.logs_area is None:
    st.session_state.logs_area = st.empty()

st.session_state.logs_area.text("\n".join(agent.logs))
