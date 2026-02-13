import streamlit as st
import importlib
import pandas as pd
import altair as alt
import AgenticMortgageResearchAgent
import config

# --- Fintech Style Header & Personal Branding ---
st.set_page_config(page_title=config.STREAMLIT_PAGE_TITLE, page_icon="🏦", layout=config.STREAMLIT_LAYOUT)

st.markdown(
    """
    <style>
        .stButton > button {
            font-size: 0.8rem;
            line-height: 1.1;
            padding: 0.25rem 0.6rem;
            white-space: nowrap;
            overflow: hidden;
            width: 100%;
            min-height: 2.2rem;
        }
        .fintech-header {
            background: linear-gradient(90deg, #0a74da 0%, #00c48c 100%);
            color: white;
            padding: 24px 16px;
            border-radius: 8px;
            margin-bottom: 0;
            font-size: 2rem;
            font-weight: 700;
            box-shadow: 0 2px 8px rgba(10, 116, 218, 0.15);
        }
        .fintech-footer {
            margin-top: 0;
            padding: 12px 16px;
            background: #f5f5f5;
            border-radius: 8px;
            font-size: 1.1rem;
            color: #0a74da;
            text-align: center;
        }
        .brand-block {
            margin-bottom: 16px;
            padding: 16px;
            background: #eafaf1;
            border-radius: 8px;
            color: #0a74da;
            font-size: 1.15rem;
        }
    </style>
    <div class="fintech-header">
        🏦 Agentic Mortgage Research Dashboard
    </div>
    """,
    unsafe_allow_html=True
)

# --- Prominent User Info ---
st.markdown(
    """
    <div class="fintech-footer">
        Built by <b>Chris Obermeier</b> | Head of Engineering | SVP Engineering | AI Leader
        <p>
        <a href="https://www.linkedin.com/in/chris-obermeier" target="_blank">LinkedIn</a> | <a href="https://github.com/obizues" target="_blank">GitHub</a> | <a href="mailto:chris.obermeier@gmail.com">Email</a>
    </div>
    """,
    unsafe_allow_html=True
)
st.sidebar.info("App version: v1.2.0 - Multi-Agent Perspectives")
with st.sidebar.expander("Tech Stack", expanded=False):
    st.markdown(
        """
        **Tech Stack**
        - Python 3.14 (virtual environment)
        - Anthropic Claude 3.5 (claude-3-haiku-20240307)
        - FRED API, pandas, requests
        - Streamlit 1.54 + Altair 6.0
        - HTML/CSS for styled UI components

        **Agentic AI Features**
        - Multi-agent role system (3 specialized perspectives)
        - Claude-driven planning & insights
        - Real-time role execution tracking
        - Emoji-based log filtering
        - Orchestrated action chains
        """
    )

with st.sidebar.expander("System Design Notes", expanded=False):
    st.markdown(
        """
        - **Multi-Agent Architecture**: Three specialized roles (Planner, Market Analyst, Risk Officer) provide diverse analytical perspectives on the same data.
        - **Orchestration**: LLM selects actions from current knowledge state and runs them in order. Force refresh applies only to Agentic Plan.
        - **Real-Time Feedback**: Emoji-tagged logs stream role execution progress to the UI via callbacks and session state.
        - **Dynamic Rendering**: Markdown-to-HTML conversion handles LLM-generated formatting (bold, lists) in color-coded perspective cards.
        - **Caching**: Fetch timestamps prevent unnecessary API calls unless forced.
        - **Resilience**: Heuristic planner runs if LLM is unavailable.
        - **Observability**: Decision trace is logged with 3-way filtering (All/LLM/Roles).
        - **Security**: API keys managed via local secrets.toml or environment variables, gitignored for safety.
        """
    )

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

# ---------- Session State ----------

if "agent" not in st.session_state:
    def ui_log_callback(msg):
        if "logs_text" not in st.session_state:
            st.session_state.logs_text = []
        st.session_state.logs_text.append(msg)
        # Update status placeholder if it exists
        if "status_placeholder" in st.session_state and st.session_state.status_placeholder is not None:
            # Collect role-specific logs (with emojis)
            if any(keyword in msg for keyword in ["📊", "📈", "🔍", "⚖️", "💡", "🧠", "🛡️", "📉"]):
                if "role_logs" not in st.session_state:
                    st.session_state.role_logs = []
                st.session_state.role_logs.append(msg)
                # Update placeholder with all role logs
                st.session_state.status_placeholder.text("\n".join(st.session_state.role_logs))

    st.session_state.agent = AgenticMortgageResearchAgent(log_callback=ui_log_callback, llm_client=llm_client)
    st.session_state.logs_text = []
    st.session_state.first_run = True
    st.session_state.status_placeholder = None
    st.session_state.role_logs = []
else:
    st.session_state.first_run = False

agent = st.session_state.agent

# Helper function to convert markdown to HTML for perspectives
def markdown_to_html(text):
    """Convert basic markdown to HTML for role perspectives."""
    import re
    # Convert **bold** to <strong>bold</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Convert newlines to <br>
    text = text.replace('\n', '<br>')
    return text

# Helper function to run actions with UI feedback
def run_action_ui(action_name, force=False, use_spinner=True):
    try:
        if use_spinner:
            with st.spinner(f"Running {action_name}..."):
                agent.run_action(action_name, force=force)
        else:
            agent.run_action(action_name, force=force)
    except Exception as e:
        st.error(f"Error running {action_name}: {e}")

# ---------- Sidebar ----------

with st.sidebar.expander("Agent Controls", expanded=False):
    force_refresh = st.checkbox("Force refresh (Agentic Plan only)", value=False)

    # Streamlined actions
    if st.button("Agentic Plan"):
        run_action_ui("agentic_plan", force=force_refresh)
    if st.button("Regenerate Summary", help="Generate fresh summary from current data"):
        run_action_ui("summarize_insights", force=True)
    if st.button("Regenerate Perspectives", help="Generate fresh multi-agent perspectives"):
        run_action_ui("generate_role_perspectives", force=True)
    if st.button("Clear Logs"):
        agent.logs.clear()
        st.session_state.logs_text = []

# Run agentic plan on first load
if st.session_state.first_run:
    with st.status("🤖 Multi-Agent System Initializing...", expanded=True) as status:
        try:
            # Reset role logs for this run
            st.session_state.role_logs = []
            
            # Create placeholder for real-time status updates
            status_container = st.container()
            with status_container:
                st.session_state.status_placeholder = st.empty()
                st.session_state.status_placeholder.text("📊 Planner: Evaluating system state...")
            
            # Run the agentic plan (logs will update the placeholder via callback)
            agent.run_action("agentic_plan", force=False)
            
            # Clear the placeholder reference
            st.session_state.status_placeholder = None
            
            status.update(label="✅ Multi-Agent Analysis Complete", state="complete", expanded=False)
        except Exception as e:
            st.session_state.status_placeholder = None
            status.update(label="❌ Analysis Failed", state="error", expanded=True)
            st.error(f"Error running agentic plan: {e}")
    st.session_state.first_run = False


# ---------- Executive Summary ----------
st.subheader("📊 Executive Summary")
st.write(agent.knowledge.get("summary", "No summary available."))

st.subheader("🧠 Multi-Agent Perspectives")
role_insights = agent.knowledge.get("role_insights", {})
if role_insights:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown("##### 📊 Planner")
            st.markdown(
                f"""<div style='padding: 12px; background: #f0f8ff; border-left: 4px solid #0a74da; border-radius: 4px;'>
                {markdown_to_html(role_insights.get("Planner", "No planner perspective."))}
                </div>""",
                unsafe_allow_html=True
            )
    
    with col2:
        with st.container():
            st.markdown("##### 📉 Market Analyst")
            st.markdown(
                f"""<div style='padding: 12px; background: #f0fff4; border-left: 4px solid #00c48c; border-radius: 4px;'>
                {markdown_to_html(role_insights.get("Market Analyst", "No analyst perspective."))}
                </div>""",
                unsafe_allow_html=True
            )
    
    with col3:
        with st.container():
            st.markdown("##### 🛡️ Risk Officer")
            st.markdown(
                f"""<div style='padding: 12px; background: #fff5f5; border-left: 4px solid #e53e3e; border-radius: 4px;'>
                {markdown_to_html(role_insights.get("Risk Officer", "No risk perspective."))}
                </div>""",
                unsafe_allow_html=True
            )
else:
    st.info("Run Agentic Plan or Summarize to generate multi-agent perspectives.")

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

# Move logs to sidebar expander
with st.sidebar.expander("📝 Agent Logs", expanded=False):
    st.caption("Decision trace (most recent entries)")
    log_filter = st.radio(
        "Filter logs:",
        ["All logs", "LLM decisions only", "Role outputs only"],
        index=0,
        horizontal=True
    )
    
    if log_filter == "LLM decisions only":
        filtered_logs = [log for log in agent.logs if "LLM" in log]
        recent_logs = filtered_logs[-100:]
        st.text("\n".join(recent_logs) or "No LLM decisions yet.")
    elif log_filter == "Role outputs only":
        # Filter for role-specific logs (with emojis)
        filtered_logs = [log for log in agent.logs if any(keyword in log for keyword in ["📊", "📈", "🔍", "⚖️", "💡", "🧠", "🛡️", "📉"])]
        recent_logs = filtered_logs[-100:]
        st.text("\n".join(recent_logs) or "No role outputs yet.")
    else:
        recent_logs = agent.logs[-200:]
        st.text("\n".join(recent_logs) or "No agent decisions yet.")
