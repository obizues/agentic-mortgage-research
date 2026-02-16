import streamlit as st
import importlib
import pandas as pd
import altair as alt
import AgenticMortgageResearchAgent
import config
from database import DebateDatabase
import sys
import platform
import os
import time

# --- Fintech Style Header & Personal Branding ---
st.set_page_config(
    page_title=config.STREAMLIT_PAGE_TITLE, 
    page_icon="🏦", 
    layout=config.STREAMLIT_LAYOUT,
    initial_sidebar_state="expanded"
)

# Force light color scheme in all browsers + iOS Chrome
st.markdown(
    """
    <meta name="color-scheme" content="light only">
    <meta name="apple-mobile-web-app-status-bar-style" content="light-content">
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
        /* Force light color scheme globally */
                st.markdown(
                    "Agents learn from past debates. When current market conditions match a learned pattern, agents use it to help guide their next recommendation. "
                    "The agent combines the current market signal with the most accurate matching pattern, but the market always has the most influence."
                )
        }
        
        /* Ensure links are visible */
        a {
            color: #0a74da !important;
        }
        
        /* Button text must be white on color backgrounds */
        .stButton > button:enabled {
            color: white !important;
        }

        /* Make disabled buttons visibly greyed out */
        button:disabled,
        button[disabled],
        .stButton > button:disabled,
        .stButton > button[disabled],
        .stButton > button:disabled:hover {
            background-color: #e5e7eb !important;
            color: #6b7280 !important;
            border: 1px solid #d1d5db !important;
            opacity: 0.6 !important;
            filter: grayscale(100%) !important;
            cursor: not-allowed !important;
            box-shadow: none !important;
        }
        
        /* Sidebar text must be dark */
        section[data-testid="stSidebar"] {
            color-scheme: light !important;
        }
        
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div {
            color: #262730 !important;
        }
        
        /* Input/text area text */
        input, textarea, select {
            color: #262730 !important;
        }
        
        /* Headers must be dark (except styled headers) */
        h1:not(.fintech-header), h2:not(.fintech-header), h3, h4, h5, h6 {
            color: #262730 !important;
        }
        
        /* PRESERVE styled components - these override the above */
        .fintech-header {
            color: white !important;
        }
        
        .fintech-footer, .brand-block, .stats-badge {
            color: #0a74da !important;
        }
        
        /* Remove top white space */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
        /* Hide specific header elements but keep sidebar toggle */
        header[data-testid="stHeader"] {
            background: transparent;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        /* Ensure sidebar is visible */
        section[data-testid="stSidebar"] {
            display: block !important;
        }
        /* Reduce sidebar top padding */
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 1rem;
        }
        /* Collapsed sidebar control button (when sidebar is hidden) - this is the main toggle on mobile */
        button[data-testid="collapsedControl"] {
            background: linear-gradient(135deg, #0a74da 0%, #00c48c 100%) !important;
            border-radius: 8px !important;
            padding: 14px !important;
            box-shadow: 0 3px 15px rgba(10, 116, 218, 0.6) !important;
            border: 2px solid rgba(255, 255, 255, 0.3) !important;
        }
        button[data-testid="collapsedControl"]:hover {
            box-shadow: 0 5px 20px rgba(10, 116, 218, 0.8) !important;
            transform: scale(1.15);
        }
        /* Mobile-specific enhancements */
        @media (max-width: 768px) {
            button[data-testid="collapsedControl"] {
                padding: 18px !important;
                box-shadow: 0 5px 20px rgba(10, 116, 218, 0.8) !important;
                border-width: 3px !important;
            }
        }
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
        .stats-badge {
            display: inline-block;
            padding: 8px 16px;
            margin: 4px;
            background: #e3f2fd;
            border-left: 3px solid #0a74da;
            border-radius: 4px;
            font-size: 0.9rem;
            font-weight: 600;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 6px;
        }
        .status-online { background: #00c48c; }
        .status-offline { background: #ff6b6b; }
    </style>
    <div class="fintech-header">
        🏦 Multi-Agent Mortgage Analysis System
    </div>
    """,
    unsafe_allow_html=True
)

# --- Prominent User Info ---
st.markdown(
    """
    <div class="fintech-footer">
        <b>Chris Obermeier</b> | VP Engineering
        <br>
        <span style="font-size: 0.85rem; opacity: 0.8;">Enterprise & PE-Backed Platform Modernization | AI & Data-Driven Transformation</span>
        <p style="margin: 4px 0 2px 0; font-size: 0.9rem; line-height: 1.2;">
        <a href="https://www.linkedin.com/in/chris-obermeier" target="_blank">LinkedIn</a> | 
        <a href="https://github.com/obizues" target="_blank">GitHub</a> | 
        <a href="mailto:chris.obermeier@gmail.com">Email</a>
        </p>
        <p style="margin: 2px 0 2px 0; font-size: 0.9rem; line-height: 1.2;">
        ⭐ <a href="https://github.com/obizues/agentic-mortgage-research" target="_blank">Star on GitHub</a> | 
        📖 <a href="https://github.com/obizues/agentic-mortgage-research#readme" target="_blank">Read Documentation</a> | 
        🎓 <a href="https://github.com/obizues/agentic-mortgage-research/blob/main/ARCHITECTURE.md" target="_blank">View Architecture</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.info("📱 App version: v1.3.5 - Learning Enabled")

st.sidebar.markdown(
    """
    <div style='text-align: center; margin: 4px 0 8px 0; padding: 8px; background: #f0f8ff; border-radius: 6px;'>
        <div style='margin: 4px;'><span class='status-indicator status-online'></span><strong>3-Agent Debate System</strong></div>
        <div style='font-size: 0.85rem; margin: 2px;'>📊 Planner | 📉 Market Analyst | 🛡️ Risk Officer</div>
        <div style='font-size: 0.85rem; margin: 2px;'>🤖 Claude 3.5 Powered</div>
        <div style='font-size: 0.85rem; margin: 2px;'>⚡ Live Execution Tracking</div>
    </div>
    """,
    unsafe_allow_html=True
)

with st.sidebar.expander("ℹ️ About This Project", expanded=False):
    st.markdown(
        """
        **Built By**
        
        [github.com/obizues](https://github.com/obizues)
        
        VP Engineering | Enterprise & PE-Backed Platform Modernization | AI & Data-Driven Transformation | Scaling High-Performance Teams
        
        ---
        
        **Portfolio Project**
        
        This is a demonstration of **agentic AI architecture** built to showcase:
        - Multi-agent LLM orchestration
        - Multi-round debate system with consensus building
        - Historical learning with outcome validation
        - Real-time UI with streaming updates
        - Production-grade patterns
        - System design thinking
        
        **Target Audience**: Recruiters, CTOs, hiring managers evaluating VP/Head of Engineering candidates.
        
        **What This Demonstrates**:
        - Deep LLM integration (Claude 3.5)
        - Multi-agent role systems with debate dynamics
        - Unified 3-column debate visualization
        - Clean architecture & documentation
        - Technical leadership capabilities
        """
    )

with st.sidebar.expander("📂 Project Documentation", expanded=False):
    st.markdown(
        """
        **GitHub Repository**
        🔗 [github.com/obizues/agentic-mortgage-research](https://github.com/obizues/agentic-mortgage-research)
        
        **Documentation**
        - 📖 [README.md](https://github.com/obizues/agentic-mortgage-research#readme) - Project overview, quick start, features
        - 🏗️ [ARCHITECTURE.md](https://github.com/obizues/agentic-mortgage-research/blob/main/ARCHITECTURE.md) - Deep technical documentation
        - 📊 [System Diagrams](https://github.com/obizues/agentic-mortgage-research#-architecture) - 5 Mermaid diagrams
        
        **Key Sections**:
        - Multi-agent system design
        - LLM integration strategy
        - Production deployment guide
        - Architectural decision records
        """
    )

with st.sidebar.expander("🛠️ Tech Stack", expanded=False):
    st.markdown(
        """
        **Tech Stack**
        - Python 3.14 (virtual environment)
        - Anthropic Claude 3.5 (claude-3-haiku-20240307)
        - FRED API, pandas, requests
        - Streamlit 1.54 + Altair 6.0
        - HTML/CSS with mobile-optimized styling
        - GitHub Actions (automated keep-alive)

        **Agentic AI Features**
        - Multi-round debate system (3 rounds with cross-examination)
        - Unified 3-column layout with round selection buttons
        - Agent-specific color themes (📊 Blue, 📉 Green, 🛡️ Red)
        - Auto-generated Round 1 positions on plan execution
        - Progressive disclosure (Rounds 2 & 3 on-demand)
        - Claude-driven planning & insights
        - Historical learning with outcome validation
        - Real-time role execution tracking
        - Emoji-based log filtering
        - Cost tracking per session
        - Mobile-responsive UI with enhanced touch targets
        """
    )

with st.sidebar.expander("📋 System Design Notes", expanded=False):
    st.markdown(
        """
        - **Multi-Round Debate System**: Agents engage in 3-round debates (Initial → Cross-Examination → Consensus) with automatic Round 1 on plan execution. Button appears to continue to Rounds 2 & 3.
        - **Unified 3-Column Interface**: All debate rounds displayed side-by-side with agent-specific color themes (📊 Planner=Blue, 📉 Market Analyst=Green, 🛡️ Risk Officer=Red) for easy comparison throughout all stages.
        - **Round Selection**: Button-based navigation (Round 1/2/3) allows switching between debate stages while maintaining consistent 3-column agent layout.
        - **Multi-Agent Architecture**: Three specialized roles (Planner, Market Analyst, Risk Officer) provide diverse analytical perspectives. Each agent's confidence level reflects certainty in their own analysis, not agreement—agents can have high confidence while reaching different conclusions.
        - **Historical Learning**: SQLite database stores all debates with outcome validation against actual market movements for accuracy tracking.
        - **Progressive Disclosure**: Round 1 positions display immediately after Agentic Plan. "Start Debate" button triggers Rounds 2 & 3 on demand with clear process flow caption and tooltips.
        - **Session Persistence**: Helpful messages guide users when debate data unavailable (e.g., after app redeploys). Inline error messaging replaces blocking cooldown screens.
        - **Mobile Optimized**: Enhanced sidebar toggle visibility with gradient styling, larger touch targets (18px on mobile), and device-independent emoji rendering (⚙️ for system operations).
        - **Orchestration**: LLM selects actions from current knowledge state and auto-generates Round 1 positions. Continue button generates Rounds 2 & 3 seamlessly within same view.
        - **Real-Time Feedback**: Emoji-tagged logs stream role execution progress to the UI via callbacks and session state.
        - **Dynamic Rendering**: Markdown-to-HTML conversion handles LLM-generated formatting (bold, lists) in color-coded debate cards with 0.9rem font for optimal fit.
        - **Cost Tracking**: Real-time session cost monitoring (~$0.002-0.003 per LLM call) displayed in system metrics.
        - **Infrastructure**: GitHub Actions workflow pings app every 5 minutes to prevent sleep on free tier, ensuring instant availability for visitors.
        - **Resilience**: Heuristic planner runs if LLM is unavailable. Graceful degradation throughout.
        - **Observability**: Decision trace is logged with 3-way filtering (All/LLM/Roles).
        - **Security**: API keys managed via local secrets.toml or environment variables, gitignored for safety.
        """
    )

# Initialize LLM client if API key is available
llm_client = None
llm_init_error = None
if config.ENABLE_LLM_PLANNING:
    try:
        from anthropic import Anthropic
        api_key = config.ANTHROPIC_API_KEY
        if not api_key:
            llm_init_error = "ANTHROPIC_API_KEY is not set"
        else:
            llm_client = Anthropic(api_key=api_key)
    except Exception as e:
        llm_init_error = str(e)

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
            if any(keyword in msg for keyword in ["📊", "⚙️", "🛡️", "📉"]):
                if "role_logs" not in st.session_state:
                    st.session_state.role_logs = []
                st.session_state.role_logs.append(msg)
                # Update placeholder with all role logs
                st.session_state.status_placeholder.text("\n".join(st.session_state.role_logs))

    # Initialize debate database
    st.session_state.debate_db = DebateDatabase()
    st.session_state.agent = AgenticMortgageResearchAgent(log_callback=ui_log_callback, llm_client=llm_client, debate_db=st.session_state.debate_db)
    st.session_state.logs_text = []
    st.session_state.first_run = True
    st.session_state.status_placeholder = None
    st.session_state.role_logs = []
    st.session_state.llm_calls = 0
    st.session_state.last_llm_call_at = 0.0
else:
    st.session_state.first_run = False

if "llm_calls" not in st.session_state:
    st.session_state.llm_calls = 0
if "last_llm_call_at" not in st.session_state:
    st.session_state.last_llm_call_at = 0.0

if st.session_state.first_run:
    st.session_state.llm_calls = 0
    st.session_state.last_llm_call_at = 0.0

agent = st.session_state.agent
debate_db = st.session_state.debate_db

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
def can_run_llm_action(action_label, requires_llm=False):
    if not config.ENABLE_LLM_PLANNING:
        if requires_llm:
            return False, "LLM is disabled for this session."
        return True, None

    if not requires_llm:
        return True, None

    max_calls = getattr(config, 'LLM_MAX_CALLS_PER_SESSION', 8)
    cooldown = getattr(config, 'LLM_COOLDOWN_SECONDS', 45)
    now = time.time()

    if st.session_state.llm_calls >= max_calls:
        msg = f"LLM usage limit reached for this session ({max_calls} actions). Please refresh later or use cached results."
        return False, msg

    wait_time = cooldown - (now - st.session_state.last_llm_call_at)
    if wait_time > 0:
        msg = f"⏳ Please wait {int(wait_time)}s before running another LLM action."
        return False, msg

    return True, None


def mark_llm_action_success(requires_llm=False):
    if not requires_llm:
        return

    st.session_state.last_llm_call_at = time.time()
    st.session_state.llm_calls += 1


def run_action_ui(action_name, force=False, use_spinner=True, requires_llm=False):
    can_run, error_msg = can_run_llm_action(action_name, requires_llm=requires_llm)
    if not can_run:
        if error_msg:
            st.warning(error_msg)
        return
    try:
        if use_spinner:
            with st.spinner(f"Running {action_name}..."):
                agent.run_action(action_name, force=force)
        else:
            agent.run_action(action_name, force=force)
        mark_llm_action_success(requires_llm=requires_llm)
    except Exception as e:
        st.error(f"Error running {action_name}: {e}")

# ---------- Sidebar ----------

with st.sidebar.expander("⚙️ Agent Controls", expanded=False):
    force_refresh = st.checkbox("Force refresh (Agentic Plan only)", value=False)

    # Main actions
    if st.button("🤖 Agentic Plan", help="Fetch data, analyze, and generate Round 1 positions"):
        run_action_ui("agentic_plan", force=force_refresh, requires_llm=False)
    
    if st.button("📝 Regenerate Summary", help="Generate fresh executive summary"):
        run_action_ui("summarize_insights", force=True, requires_llm=False)
    
    st.divider()
    st.caption("**Debate Controls**")
    
    if st.button("🔄 Regenerate Round 1", help="Refresh initial agent positions"):
        with st.spinner("Regenerating Round 1 positions..."):
            if not agent.llm_client:
                st.error("LLM client required")
            else:
                can_run, error_msg = can_run_llm_action("regenerate_round_1", requires_llm=True)
                if can_run:
                    agent._debate_round_1_initial_positions()
                    mark_llm_action_success(requires_llm=True)
                    st.success("✅ Round 1 positions regenerated!")
                    st.rerun()
                elif error_msg:
                    st.warning(error_msg)
    
    if st.button("🔥 Run Full Debate", help="Run all 3 rounds from scratch"):
        with st.spinner("Running full 3-round debate..."):
            can_run, error_msg = can_run_llm_action("run_full_debate", requires_llm=True)
            if can_run:
                result = agent.run_agent_debate(force=True)
                mark_llm_action_success(requires_llm=True)
                debate_id = agent.save_debate_to_database(debate_db)
                
                # Auto-validate immediately using current rates
                if debate_id:
                    try:
                        current_rate = None
                        rate_series = agent.knowledge.get("mortgage_rates")
                        if rate_series is not None and len(rate_series) > 0:
                            current_rate = float(rate_series.iloc[-1]['rate'])
                        else:
                            rate_insights = agent.knowledge.get("rate_insights", {})
                            if rate_insights.get("latest_rate") is not None:
                                current_rate = float(rate_insights.get("latest_rate"))

                        if current_rate is not None:
                            validation_result = debate_db.validate_debate_outcome(debate_id, current_rate)
                            st.info(f"[Learning] Debate #{debate_id} auto-validated: {validation_result['status'].upper()}")
                        else:
                            st.warning(f"[Learning] Debate #{debate_id} saved but could not auto-validate (no rate data)")
                    except Exception as e:
                        st.warning(f"[Learning] Debate #{debate_id} saved but validation error: {str(e)}")
                
                st.success(result)
                st.rerun()
            elif error_msg:
                st.warning(error_msg)
    
    st.divider()
    if st.button("Clear Logs"):
        agent.logs.clear()
        agent.logs.clear()
        st.session_state.logs_text = []

# Run agentic plan on first load or if no debate data exists
round_1_positions = agent.knowledge.get("debate_round_1", {})
should_auto_run = st.session_state.first_run or not round_1_positions
st.session_state.initializing = False

if should_auto_run:
    st.session_state.initializing = True
    with st.status("🤖 Multi-Agent System Initializing...", expanded=True) as status:
        try:
            if config.ENABLE_LLM_PLANNING:
                can_run, error_msg = can_run_llm_action("auto_agentic_plan", requires_llm=False)
                if not can_run:
                    agent.llm_client = None
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
        finally:
            if config.ENABLE_LLM_PLANNING and agent.llm_client is None:
                try:
                    from anthropic import Anthropic
                    agent.llm_client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
                except Exception:
                    agent.llm_client = None
            st.session_state.initializing = False
    st.session_state.first_run = False

# Auto-validate any pending debates (catch-all in case auto-validation missed any)
current_rate = None
rate_series = agent.knowledge.get("mortgage_rates")
if rate_series is not None and len(rate_series) > 0:
    current_rate = float(rate_series.iloc[-1]['rate'])
else:
    rate_insights = agent.knowledge.get("rate_insights", {})
    if rate_insights.get("latest_rate") is not None:
        current_rate = float(rate_insights.get("latest_rate"))

if current_rate is not None:
    try:
        recent_debates = debate_db.get_recent_debates(limit=50)
        pending = [d for d in recent_debates if d['validation_status'] is None]
        
        if pending:
            with st.status(f"🤖 Auto-validating {len(pending)} pending debate(s)...", expanded=False) as validation_status:
                for debate in pending:
                    try:
                        result = debate_db.validate_debate_outcome(debate['id'], current_rate)
                        st.write(f"✓ Debate #{debate['id']}: {result['status'].upper()}")
                    except Exception as e:
                        st.write(f"✗ Debate #{debate['id']}: {str(e)}")
                validation_status.update(label="✅ Auto-validation complete", state="complete", expanded=False)
    except Exception:
        pass  # Silent fail - don't interrupt page load



# ---------- System Status & Metrics ----------
col_status1, col_status2, col_status3, col_status4 = st.columns(4)

with col_status1:
    llm_icon = "🟢" if config.ENABLE_LLM_PLANNING else "🔴"
    llm_text = "LLM Active" if config.ENABLE_LLM_PLANNING else "Heuristic"
    st.metric(label="🤖 LLM Status", value=llm_text, delta=None)

with col_status2:
    timestamps = agent.knowledge.get("fetch_timestamps", {})
    if timestamps:
        latest_ts = max(timestamps.values())
        age_hours = (pd.Timestamp.now() - latest_ts).total_seconds() / 3600
        data_status = f"{age_hours:.1f}h ago"
        data_label = "Fresh" if age_hours < 24 else "Stale"
    else:
        data_status = "None"
        data_label = ""
    st.metric(label="📊 Data Status", value=data_status, delta=data_label if data_label else None)

with col_status3:
    log_count = len(agent.logs)
    st.metric(label="📝 Log Entries", value=log_count)

with col_status4:
    session_cost = agent.session_cost if hasattr(agent, 'session_cost') else 0.0
    st.metric(label="💵 Session Cost", value=f"${session_cost:.4f}")

# ---------- Agent Debate System ----------
round_1_positions = agent.knowledge.get("debate_round_1", {})
debate_complete = "debate_results" in agent.knowledge

# If Round 1 exists but no results yet, clear stale Round 2/3 data.
if round_1_positions and not debate_complete:
    if "debate_round_2" in agent.knowledge:
        del agent.knowledge["debate_round_2"]
    if "debate_round_3" in agent.knowledge:
        del agent.knowledge["debate_round_3"]

# Show debate interface if Round 1 exists
if round_1_positions:
    # Get debate data
    round_1 = agent.knowledge.get("debate_round_1", {})
    round_2 = agent.knowledge.get("debate_round_2", {})
    round_3 = agent.knowledge.get("debate_round_3", {})
    
    # Initialize default round
    if 'selected_round' not in st.session_state:
        st.session_state.selected_round = 1
    
    # Get agent names in order
    agent_names = ["Planner", "Market Analyst", "Risk Officer"]
    
    # Agent-specific colors and emojis
    agent_styles = {
        "Planner": {"color": "#0a74da", "bg": "#f0f8ff", "emoji": "📊"},
        "Market Analyst": {"color": "#00c48c", "bg": "#f0fff4", "emoji": "📉"},
        "Risk Officer": {"color": "#e53e3e", "bg": "#fff5f5", "emoji": "🛡️"}
    }
    
    # ===== MAIN DEBATE SECTION HEADER =====
    st.markdown("### 🎬 Multi-Agent Debate & Analysis")
    
    # ===== SECTION 1: CONTINUE TO DEBATE PROMPT (at top, only on Round 1 if not complete) =====
    if st.session_state.get("initializing", False):
        st.info("🤖 Initializing multi-agent analysis...")
    elif not debate_complete and round_1:
        st.info(
            "**Three Unique AI Agents Ready to Debate**\n\n"
            "Each AI brings its own specialized perspective (see their initial positions below):\n\n"
            "📊 **Planner AI** sees opportunities & strategy | "
            "📉 **Market Analyst AI** sees trends & patterns | "
            "🛡️ **Risk Officer AI** sees risks & concerns"
        )
        
        if "debate_in_progress" not in st.session_state:
            st.session_state.debate_in_progress = False
        if "pending_debate" not in st.session_state:
            st.session_state.pending_debate = False

        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            # Show spinner early if debate is already in progress from previous cycle
            if st.session_state.debate_in_progress:
                st.spinner("🎯 Running cross-examination and consensus rounds...")
            
            if st.session_state.pending_debate or st.session_state.debate_in_progress:
                # Run the debate from the pending state and hide the button while running
                st.session_state.pending_debate = False
                st.session_state.debate_in_progress = True
                # First verify LLM client is available
                if llm_client is None:
                    st.error(f"❌ LLM not available: {llm_init_error}")
                    st.session_state.debate_in_progress = False
                elif agent.llm_client is None:
                    st.error("❌ Agent LLM client is None. This shouldn't happen – please refresh the page.")
                    st.session_state.debate_in_progress = False
                else:
                    can_run, error_msg = can_run_llm_action("continue_debate", requires_llm=True)
                    if error_msg:
                        st.warning(error_msg)
                        st.session_state.debate_in_progress = False
                    else:
                        try:
                            with st.spinner("🎯 Running cross-examination and consensus rounds..."):
                                result = agent.continue_debate(force=True)
                                if "debate_results" in agent.knowledge:
                                    mark_llm_action_success(requires_llm=True)
                                    debate_id = agent.save_debate_to_database(debate_db)
                                    
                                    # Auto-validate immediately using current rates
                                    if debate_id:
                                        try:
                                            current_rate = None
                                            rate_series = agent.knowledge.get("mortgage_rates")
                                            if rate_series is not None and len(rate_series) > 0:
                                                current_rate = float(rate_series.iloc[-1]['rate'])
                                            else:
                                                rate_insights = agent.knowledge.get("rate_insights", {})
                                                if rate_insights.get("latest_rate") is not None:
                                                    current_rate = float(rate_insights.get("latest_rate"))

                                            if current_rate is not None:
                                                validation_result = debate_db.validate_debate_outcome(debate_id, current_rate)
                                                st.info(f"[Learning] Debate #{debate_id} auto-validated: {validation_result['status'].upper()}")
                                            else:
                                                st.warning(f"[Learning] Debate #{debate_id} saved but could not auto-validate (no rate data)")
                                        except Exception as e:
                                            st.warning(f"[Learning] Debate #{debate_id} saved but validation error: {str(e)}")
                                    
                                    st.session_state.debate_in_progress = False
                                    st.session_state.selected_round = 2  # Auto-advance to Round 2 to show cross-examination
                                    st.rerun()
                                else:
                                    st.error("❌ Debate did not complete properly. Check agent logs below.")
                                    st.session_state.debate_in_progress = False
                        except Exception as e:
                            st.error(f"❌ Error running debate: {e}")
                            st.session_state.debate_in_progress = False
            else:
                # Single button; disabled state prevents duplicate rendering
                if st.button(
                    "🔥 Start Debate",
                    width="stretch",
                    type="primary",
                    key="continue_debate_btn",
                ):
                    st.session_state.pending_debate = True
                    st.rerun()
            
            st.markdown("<p style='text-align: center; font-size: 0.9rem; color: #666;'>Runs Rounds 2 & 3 → Voting Consensus → Summary</p>", unsafe_allow_html=True)
    
    # ===== CONSENSUS SUMMARY AT TOP (when debate complete) =====
    if debate_complete:
        # TEMP DEBUG: Show raw vote data for troubleshooting
        st.expander("🛠️ Debug: Raw Vote Data").write({
            "debate_round_3": agent.knowledge.get("debate_round_3", {}),
            "debate_results": agent.knowledge.get("debate_results", {})
        })
        st.divider()
        debate_results = agent.knowledge["debate_results"]
        final_stance = debate_results.get("majority_vote", "NEUTRAL")
        consensus_score = debate_results.get("consensus_score", 0)
        avg_confidence = debate_results.get("avg_confidence", 0)
        vote_breakdown = debate_results.get("vote_breakdown", {})
        vote_order = ["BULLISH", "BEARISH", "NEUTRAL"]
        vote_parts = [
            f"{vote_breakdown[stance]} {stance.title()}"
            for stance in vote_order
            if stance in vote_breakdown
        ]
        vote_summary = ", ".join(vote_parts) if vote_parts else "No votes recorded"
        
        # Check if this is a true consensus (2+ agents agree) or a complete disagreement (1-1-1 tie)
        is_no_consensus = consensus_score <= 33.5  # No majority: 1 vote (33%)
        is_weak_consensus = 33.5 < consensus_score < 99  # Weak majority: 2 votes (67%)
        is_strong_consensus = consensus_score >= 99  # Strong unanimous: 3 votes (100%)
        
        if is_no_consensus:
            # Complete disagreement: special styling
            bg_gradient = "linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)"
            stance_emoji = "⚪"
            heading = "Agents Fundamentally Disagree"
            action_text = "**What this means:** The agents could not reach agreement. Each took a different stance on the market—this reflects genuine uncertainty in the mortgage market signals. Your decision should prioritize your personal circumstances and risk tolerance."
        elif "BULLISH" in final_stance:
            bg_gradient = "linear-gradient(135deg, #00c48c 0%, #0a74da 100%)"
            stance_emoji = "🟢"
            heading = "Final Consensus: BULLISH"
            action_text = "**What this means:** Market conditions favor homebuyers. Rates are expected to be favorable—consider moving forward with mortgage decisions."
        elif "BEARISH" in final_stance:
            bg_gradient = "linear-gradient(135deg, #e53e3e 0%, #ff6b6b 100%)"
            stance_emoji = "🔴"
            heading = "Final Consensus: BEARISH"
            action_text = "**What this means:** Market conditions suggest caution. Rates may be less favorable—consider waiting or exploring alternatives."
        else:  # NEUTRAL
            bg_gradient = "linear-gradient(135deg, #ffa500 0%, #ffcc00 100%)"
            stance_emoji = "🟡"
            heading = "Final Consensus: NEUTRAL"
            action_text = "**What this means:** Market signals are mixed. No strong direction—evaluate your personal circumstances carefully."
        
        st.markdown(
            f"""<div style='padding: 20px; background: {bg_gradient}; 
            color: white; border-radius: 8px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15);'>
            <h2 style='margin: 0;'>{stance_emoji} {heading}</h2>
            <p style='margin-top: 8px; font-size: 1rem; opacity: 0.95;'>
            Votes: {vote_summary} | Consensus Strength: {consensus_score:.0f}% | Avg Confidence: {avg_confidence:.0f}%
            </p>
            </div>""",
            unsafe_allow_html=True
        )
        
        # Build explanation text dynamically based on consensus type
        if is_no_consensus:
            explanation_text = (
                f"{action_text}\n\n"
                f"**How agents voted:** {vote_summary} — A perfect 1-1-1 split means each agent holds a different view. This isn't weakness in the analysis—it reflects real market uncertainty.\n\n"
                f"**Consensus Strength:** {consensus_score:.0f}% — No majority view; all stances equally weighted.\n\n"
                f"**Average Confidence:** {avg_confidence:.0f}% — Average certainty level across agents."
            )
        else:
            # For 2-1 or 3-0 consensus
            if is_strong_consensus:
                consensus_description = "unanimous agreement"
                strength_description = "Perfect unanimity: all 3 agents aligned"
            else:  # is_weak_consensus (2-1 split)
                consensus_description = "a majority decision"
                strength_description = "Moderate agreement: 2 agents aligned, 1 dissents"
            
            explanation_text = (
                f"{action_text}\n\n"
                f"**How agents voted:** {vote_summary} — {consensus_description}.\n\n"
                f"**Consensus Strength:** {consensus_score:.0f}% — {strength_description}.\n\n"
                f"**Average Confidence:** {avg_confidence:.0f}% — {'Very high' if avg_confidence >= 80 else 'moderate' if avg_confidence >= 60 else 'lower'} certainty across agents."
            )
        
        st.info(explanation_text)
        st.divider()
    
    # ===== SECTION 2: ROUND SELECTOR BUTTONS =====
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        if st.button("📋 Round 1", width="stretch", key="round_1_btn"):
            st.session_state.selected_round = 1
    with col_btn2:
        r2_available = bool(round_2)
        r2_help = None if r2_available else "Click 'Start Debate' above to unlock this round"
        if st.button("🔍 Round 2", width="stretch", key="round_2_btn", disabled=not r2_available, help=r2_help):
            st.session_state.selected_round = 2
    with col_btn3:
        r3_available = bool(round_3)
        r3_help = None if r3_available else "Click 'Start Debate' above to unlock this round"
        if st.button("🤝 Round 3", width="stretch", key="round_3_btn", disabled=not r3_available, help=r3_help):
            st.session_state.selected_round = 3
    
    # ===== SECTION 3: DISPLAY SELECTED ROUND CONTENT =====
    round_names = {
        1: "📋 Round 1: Initial Positions",
        2: "🔍 Round 2: Cross-Examination", 
        3: "🤝 Round 3: Final Votes"
    }
    st.markdown(f"#### {round_names[st.session_state.selected_round]}")
    
    col1, col2, col3 = st.columns(3)
    
    for col, agent_name in zip([col1, col2, col3], agent_names):
        with col:
            r1_data = round_1.get(agent_name, {})
            r2_data = round_2.get(agent_name, {})
            r3_data = round_3.get(agent_name, {})
            style = agent_styles[agent_name]
            
            # Agent header
            st.markdown(f"##### {style['emoji']} {agent_name}")
            
            if st.session_state.selected_round == 1:
                st.markdown("**Initial Position**")
                st.caption(f"Confidence: {r1_data.get('confidence', 'N/A')}%")
                st.markdown(
                    f"""<div style='padding: 12px; background: {style['bg']}; border-left: 4px solid {style['color']}; border-radius: 4px; min-height: 180px; font-size: 0.9rem;'>
                    {markdown_to_html(r1_data.get('position', 'N/A'))}
                    </div>""",
                    unsafe_allow_html=True
                )
                
            elif st.session_state.selected_round == 2:
                st.markdown("**Cross-Examination**")
                if r2_data.get('cross_examination'):
                    st.markdown(
                        f"""<div style='padding: 12px; background: {style['bg']}; border-left: 4px solid {style['color']}; border-radius: 4px; min-height: 180px; font-size: 0.9rem;'>
                        {markdown_to_html(r2_data.get('cross_examination', 'N/A'))}
                        </div>""",
                        unsafe_allow_html=True
                    )
                else:
                    st.info("Round 2 not yet available.")
                    
            elif st.session_state.selected_round == 3:
                st.markdown("**Final Vote**")
                if r3_data.get('stance'):
                    stance = r3_data.get('stance', 'N/A')
                    confidence = r3_data.get('confidence', 0)
                    stance_color = {"BULLISH": "🟢", "BEARISH": "🔴", "NEUTRAL": "🟡"}
                    st.markdown(f"**Vote:** {stance_color.get(stance, '⚪')} **{stance}**")
                    st.caption(f"Confidence: {confidence:.0f}%")
                    st.markdown(
                        f"""<div style='padding: 12px; background: {style['bg']}; border-left: 4px solid {style['color']}; border-radius: 4px; min-height: 180px; font-size: 0.9rem;'>
                        {markdown_to_html(r3_data.get('reasoning', 'N/A'))}
                        </div>""",
                        unsafe_allow_html=True
                    )
                else:
                    st.info("Round 3 not yet available.")

elif not round_1_positions:
    st.info("Run Agentic Plan to generate initial agent positions and start the debate.")

# ---------- Executive Summary & Historical Debates ----------
if round_1_positions:
    # Executive Summary (moved below debate for context) - only show if debate is complete
    if debate_complete:
        st.divider()
        st.subheader("📊 Executive Summary")
        st.caption("Generated after debate consensus")
        
        # Generate post-debate summary incorporating consensus
        if agent.llm_client:
            try:
                summary_prompt = f"""Based on a multi-agent mortgage market debate, provide a 3-paragraph executive summary:

Debate Consensus: {agent.knowledge['debate_results']['final_recommendation']}
Vote Breakdown: {agent.knowledge['debate_results']['vote_breakdown']}

Current mortgage rate: {agent.knowledge.get('rate_insights', {}).get('latest_rate', 'N/A')}%
12-month average: {agent.knowledge.get('rate_insights', {}).get('12_month_avg', 'N/A')}%
Home price trend: {agent.knowledge.get('comparison', 'N/A')}

Provide:
1. Market assessment
2. Implications for homebuyers
3. Key recommendation informed by agent consensus"""
                
                message = agent.llm_client.messages.create(
                    model=config.MODEL_NAME,
                    max_tokens=400,
                    messages=[{"role": "user", "content": summary_prompt}]
                )
                post_debate_summary = message.content[0].text.strip()
                st.write(post_debate_summary)
            except Exception as e:
                st.write(agent.knowledge.get("summary", "No summary available."))
        else:
            st.write(agent.knowledge.get("summary", "No summary available."))
    
    # Historical Debates Section (moved below Executive Summary)
    st.divider()
    with st.expander("📚 Historical Debates & System Learning", expanded=False):
        st.info("💡 **Value**: Learn from past debates using historical multi-agent system's predictions' accuracy.")
        # Get recent debates from database
        recent_debates = debate_db.get_recent_debates(limit=10)


        # ...existing code for validation stats, emerging patterns, etc...

        # Move 'Show Individual Debates' expander to the bottom
        if recent_debates:
            with st.expander("Show Individual Debates", expanded=False):
                for debate in recent_debates:
                    with st.expander(
                        f"Debate #{debate['id']} - {debate['timestamp'][:19]} - {debate['final_recommendation']}", 
                        expanded=False
                    ):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Consensus", f"{debate['consensus_score']:.0f}%")
                        col2.metric("Cost", f"${debate['session_cost']:.4f}")
                        if debate['validation_status']:
                            status_emoji = "✅" if debate['validation_status'] == 'correct' else "❌"
                            col3.metric(
                                "Validation", 
                                f"{status_emoji} {debate['validation_status'].title()}",
                                delta=f"{debate['validation_accuracy']:.0f}% accurate" if debate['validation_accuracy'] else None
                            )
                        else:
                            col3.metric("Validation", "Pending")
                        if st.button(f"View Details", key=f"view_{debate['id']}"):
                            debate_details = debate_db.get_debate_details(debate['id'])
                            st.json(debate_details)
        else:
            st.info("No historical debates yet. Run your first debate to see results here!")

        # Validation stats and emerging patterns at the bottom
        val_stats = debate_db.get_validation_stats()
        if val_stats['total_validated'] > 0:
            st.caption(
                "**Emerging Patterns**"
                )
            learned_patterns = None
            try:
                learned_patterns = debate_db.get_learned_patterns(limit=5, min_times=1)
            except TypeError:
                learned_patterns = debate_db.get_learned_patterns(limit=5)
            if learned_patterns:
                import pandas as pd
                pattern_data = []
                for pattern in learned_patterns:
                    pattern_data.append({
                        "Prediction": pattern['pattern'],
                        "Accuracy": float(pattern['accuracy']),
                        "Frequency": pattern['frequency'],
                        "Condition": pattern['condition']
                    })
                df_patterns = pd.DataFrame(pattern_data)
                st.dataframe(df_patterns, use_container_width=True, hide_index=True)

                st.markdown(
                    "Agents learn from past debates. When current market conditions match a learned pattern, agents use it to help guide their next recommendation. "
                    "The agent combines the current market signal with the most accurate matching pattern, but the market always has the most influence."
                )

                # Short agent recommendation preview with weighted logic
                st.markdown("**Current Recommendation Basis**")
                if 'mortgage_rates' in agent.knowledge and not agent.knowledge['mortgage_rates'].empty:
                    current_rate = agent.knowledge['mortgage_rates'].iloc[-1]['rate']
                    avg_rate = agent.knowledge['mortgage_rates']['rate'].mean()
                    current_condition = 'Market condition: rates decreasing' if current_rate < avg_rate else 'Market condition: rates increasing'
                    matched_patterns = df_patterns[df_patterns['Condition'] == current_condition]
                    if not matched_patterns.empty:
                        # Use the most accurate pattern
                        best_pattern = matched_patterns.iloc[matched_patterns['Accuracy'].astype(float).idxmax()]
                        accuracy = float(best_pattern['Accuracy']) / 100.0
                        wp = accuracy * 0.25
                        wm = 1 - wp
                        # Market signal: +1 for decreasing, -1 for increasing
                        market_signal = 1 if current_condition == 'Market condition: rates decreasing' else -1
                        # Pattern signal: +1 for BULLISH, -1 for BEARISH, 0 for NEUTRAL
                        pred = best_pattern['Prediction'].upper()
                        if 'BULLISH' in pred:
                            pattern_signal = 1
                        elif 'BEARISH' in pred:
                            pattern_signal = -1
                        else:
                            pattern_signal = 0
                        final_score = wm * market_signal + wp * pattern_signal
                        if final_score > 0.1:
                            rec = 'BULLISH'
                        elif final_score < -0.1:
                            rec = 'BEARISH'
                        else:
                            rec = 'NEUTRAL'
                        st.write(f"Pattern: {best_pattern['Prediction']} | Accuracy: {best_pattern['Accuracy']}% | Used for: {best_pattern['Condition']}")
                        st.write(f"**Weighted Recommendation:** {rec}  ")
                        st.caption(f"$w_p$ = {wp:.2f}, $w_m$ = {wm:.2f}, Final Score = {final_score:.2f}")
                        st.write(f"**Formula:**"
                                "$w_p = \\text{accuracy} \\times 0.25$ (pattern weight, max 0.25)  \n"
                                "$w_m = 1 - w_p$ (market weight, always at least 0.75)  \n"
                                "Final Score = $w_m \\times$ market signal $+$ $w_p \\times$ pattern signal."
                        )
                    else:
                        st.info("No learned patterns match current market conditions.")
            else:
                st.info("📕 No patterns learned yet. Run additional debates to build a visible learning trail.")

else:
    # Helpful message when debate data isn't loaded (e.g., after app redeploy)
    if st.session_state.first_run and not st.session_state.get('plan_generated', False):
        st.info(
            "💬 **Multi-Agent Debate System Ready**\n\n"
            "Once you generate the Agentic Plan above, three specialized AI agents will create "
            "their initial market perspectives. Then you can start the full debate to see them "
            "challenge each other's views and reach consensus."
        )

# ---------- Visualizations ----------
with st.expander("📈 Data Visualizations (Market Context)", expanded=False):
    st.caption("Historical mortgage rates and home prices that inform the agents' analysis")
    
    # Mortgage Rates Chart
    if "mortgage_rates" in agent.knowledge and not agent.knowledge["mortgage_rates"].empty:
        df_rates = agent.knowledge["mortgage_rates"]
        st.altair_chart(
            alt.Chart(df_rates).mark_line(color='blue').encode(
                x='date:T',
                y='rate:Q',
                tooltip=['date:T', 'rate:Q']
            ).properties(title='30-Year Fixed Mortgage Rates', height=300),
            width="stretch"
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
            width="stretch"
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
        st.altair_chart(chart_combined, width="stretch")

# ---------- Agent Logs ----------

# Move logs to sidebar expander
with st.sidebar.expander("📝 Agent Activity Log", expanded=False):
    st.caption(f"📚 {len(agent.logs)} total activities tracked")
    st.info("💡 **What you're seeing**: Real-time agent operations and decisions")
    
    log_filter = st.radio(
        "Show me:",
        ["🎯 All Activity", "🤖 AI Decisions", "👥 Agent Actions"],
        index=0,
        horizontal=True
    )
    
    if log_filter == "🤖 AI Decisions":
        filtered_logs = [log for log in agent.logs if "LLM" in log]
        recent_logs = filtered_logs[-50:]
        if recent_logs:
            for log in recent_logs:
                # Clean up log format - remove timestamps and make more readable
                clean_log = log.replace("[LLM]", "🤖 **AI Decision:**")
                st.markdown(clean_log)
        else:
            st.caption("No AI decisions yet - run Agentic Plan to see AI in action")
    elif log_filter == "👥 Agent Actions":
        # Filter for role-specific logs (with emojis)
        filtered_logs = [log for log in agent.logs if any(keyword in log for keyword in ["📊", "⚙️", "🛡️", "📉"])]
        recent_logs = filtered_logs[-50:]
        if recent_logs:
            for log in recent_logs:
                # Format each log entry with better spacing
                if "📊" in log:
                    st.markdown(f"📊 **Planner:** {log.split('📊')[1] if '📊' in log else log}")
                elif "📉" in log:
                    st.markdown(f"📉 **Market Analyst:** {log.split('📉')[1] if '📉' in log else log}")
                elif "🛡️" in log:
                    st.markdown(f"🛡️ **Risk Officer:** {log.split('🛡️')[1] if '🛡️' in log else log}")
                elif "⚙️" in log:
                    st.markdown(f"⚙️ **System:** {log.split('⚙️')[1] if '⚙️' in log else log}")
                else:
                    st.markdown(log)
        else:
            st.caption("No agent actions yet - generate the Agentic Plan to see agents work")
    else:
        recent_logs = agent.logs[-100:]
        if recent_logs:
            st.markdown("**Recent Activity:**")
            for log in recent_logs:
                st.caption(log)
        else:
            st.caption("No activity yet - start by running the Agentic Plan")

# ---------- Outcome Validation ----------

# ---------- Diagnostics (Simplified for v1.3.1) ----------
with st.sidebar.expander("🧪 Diagnostics", expanded=False):
    st.caption("System health and data availability checks")

    try:
        st.markdown("**Environment**")
        st.text(f"Streamlit: {st.__version__} | Python: {sys.version.split()[0]}")
        st.text(f"Platform: {platform.platform()}")
        
        st.markdown("**LLM Configuration**")
        st.text(f"LLM Enabled: {bool(config.ENABLE_LLM_PLANNING)}")
        st.text(f"Calls This Session: {st.session_state.llm_calls} / {getattr(config, 'LLM_MAX_CALLS_PER_SESSION', 8)}")
        st.text(f"Anthropic Key: {'✓ Set' if getattr(config, 'ANTHROPIC_API_KEY', None) else '✗ Missing'}")
        st.text(f"FRED API Key: {'✓ Set' if getattr(config, 'FRED_API_KEY', None) else '✗ Missing'}")

        st.markdown("**Data Status**")
        rates_df = agent.knowledge.get("mortgage_rates")
        prices_df = agent.knowledge.get("home_prices")
        st.text(f"Mortgage Rates: {0 if rates_df is None else len(rates_df)} rows")
        st.text(f"Home Prices: {0 if prices_df is None else len(prices_df)} rows")

        st.markdown("**Debate Status**")
        round_1 = agent.knowledge.get("debate_round_1", {})
        round_2 = agent.knowledge.get("debate_round_2", {})
        round_3 = agent.knowledge.get("debate_round_3", {})
        r1_count = len(round_1) if isinstance(round_1, dict) else 0
        r2_count = len(round_2) if isinstance(round_2, dict) else 0
        r3_count = len(round_3) if isinstance(round_3, dict) else 0
        st.text(f"Round 1: {r1_count} agents | Round 2: {r2_count} | Round 3: {r3_count}")
        
    except Exception as exc:
        st.error("Diagnostics error - see logs")
        st.text(str(exc))

    st.info(
        "💡 **Troubleshooting**: If content is missing, check for ad blockers, VPN/Private Relay, "
        "or network filters blocking Streamlit resources."
    )

