import streamlit as st
import importlib
import pandas as pd
import altair as alt
import AgenticMortgageResearchAgent
import config
from database import DebateDatabase

# --- Fintech Style Header & Personal Branding ---
st.set_page_config(
    page_title=config.STREAMLIT_PAGE_TITLE, 
    page_icon="🏦", 
    layout=config.STREAMLIT_LAYOUT,
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
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
        <a href="https://www.linkedin.com/in/chris-obermeier" target="_blank">LinkedIn</a> | 
        <a href="https://github.com/obizues" target="_blank">GitHub</a> | 
        <a href="mailto:chris.obermeier@gmail.com">Email</a>
        <p style="margin-top: 12px; font-size: 0.95rem;">
        ⭐ <a href="https://github.com/obizues/agentic-mortgage-research" target="_blank">Star on GitHub</a> | 
        📖 <a href="https://github.com/obizues/agentic-mortgage-research#readme" target="_blank">Read Documentation</a> | 
        🎓 <a href="https://github.com/obizues/agentic-mortgage-research/blob/main/ARCHITECTURE.md" target="_blank">View Architecture</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.info("App version: v1.3.0 - Multi-Round Debate & Learning")

st.sidebar.markdown(
    """
    <div style='text-align: center; margin: 4px 0 8px 0; padding: 8px; background: #f0f8ff; border-radius: 6px;'>
        <div style='margin: 4px;'><span class='status-indicator status-online'></span><strong>Multi-Agent System</strong></div>
        <div style='font-size: 0.85rem; margin: 2px;'>📊 3 Specialized Perspectives</div>
        <div style='font-size: 0.85rem; margin: 2px;'>🤖 Claude 3.5 Powered</div>
        <div style='font-size: 0.85rem; margin: 2px;'>⚡ Live Execution Tracking</div>
    </div>
    """,
    unsafe_allow_html=True
)

with st.sidebar.expander("ℹ️ About This Project", expanded=False):
    st.markdown(
        """
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
        - Compact, optimized spacing throughout
        """
    )

with st.sidebar.expander("System Design Notes", expanded=False):
    st.markdown(
        """
        - **Multi-Round Debate System**: Agents engage in 3-round debates (Initial → Cross-Examination → Consensus) with automatic Round 1 on plan execution. Button appears to continue to Rounds 2 & 3.
        - **Unified 3-Column Interface**: All debate rounds displayed side-by-side with agent-specific color themes (📊 Planner=Blue, 📉 Market Analyst=Green, 🛡️ Risk Officer=Red) for easy comparison throughout all stages.
        - **Round Selection**: Button-based navigation (Round 1/2/3) allows switching between debate stages while maintaining consistent 3-column agent layout.
        - **Multi-Agent Architecture**: Three specialized roles (Planner, Market Analyst, Risk Officer) provide diverse analytical perspectives with confidence levels.
        - **Historical Learning**: SQLite database stores all debates with outcome validation against actual market movements for accuracy tracking.
        - **Progressive Disclosure**: Round 1 positions display immediately after Agentic Plan. "Continue" button triggers Rounds 2 & 3 on demand for full debate with consensus.
        - **Orchestration**: LLM selects actions from current knowledge state and auto-generates Round 1 positions. Continue button generates Rounds 2 & 3 seamlessly within same view.
        - **Real-Time Feedback**: Emoji-tagged logs stream role execution progress to the UI via callbacks and session state.
        - **Dynamic Rendering**: Markdown-to-HTML conversion handles LLM-generated formatting (bold, lists) in color-coded debate cards with 0.9rem font for optimal fit.
        - **Compact Layout**: Optimized spacing throughout UI removes unnecessary dividers and white space for cleaner presentation.
        - **Cost Tracking**: Real-time session cost monitoring (~$0.002-0.003 per LLM call) displayed in system metrics.
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
    # Initialize debate database
    st.session_state.debate_db = DebateDatabase()
else:
    st.session_state.first_run = False

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

    # Main actions
    if st.button("🤖 Agentic Plan", help="Fetch data, analyze, and generate Round 1 positions"):
        run_action_ui("agentic_plan", force=force_refresh)
    
    if st.button("📝 Regenerate Summary", help="Generate fresh executive summary"):
        run_action_ui("summarize_insights", force=True)
    
    st.divider()
    st.caption("**Debate Controls**")
    
    if st.button("🔄 Regenerate Round 1", help="Refresh initial agent positions"):
        with st.spinner("Regenerating Round 1 positions..."):
            if agent.llm_client:
                agent._debate_round_1_initial_positions()
                st.success("✅ Round 1 positions regenerated!")
                st.rerun()
            else:
                st.error("LLM client required")
    
    if st.button("🔥 Run Full Debate", help="Run all 3 rounds from scratch"):
        with st.spinner("Running full 3-round debate..."):
            result = agent.run_agent_debate(force=True)
            agent.save_debate_to_database(debate_db)
            st.success(result)
            st.rerun()
    
    st.divider()
    if st.button("Clear Logs"):
        agent.logs.clear()
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

# Show debate interface if Round 1 exists
if round_1_positions:
    # Show final recommendation banner if debate is complete
    if debate_complete:
        debate_results = agent.knowledge["debate_results"]
        st.markdown(
            f"""<div style='padding: 20px; background: linear-gradient(90deg, #0a74da 0%, #00c48c 100%); 
            color: white; border-radius: 8px; text-align: center; margin-bottom: 16px;'>
            <h2 style='margin: 0;'>Final Recommendation: {debate_results['final_recommendation']}</h2>
            <p style='margin-top: 8px; font-size: 1.1rem;'>
            Vote Breakdown: {debate_results['vote_breakdown']} | 
            Avg Confidence: {debate_results['avg_confidence']:.0f}%
            </p>
            </div>""",
            unsafe_allow_html=True
        )
    
    # If debate not complete, show "Continue" button
    if not debate_complete:
        # Initialize debate running state
        if 'debate_running' not in st.session_state:
            st.session_state.debate_running = False
        
        st.markdown("### 🔥 Ready to see the agents debate?")
        st.info("Each agent has analyzed the market and staked a position. Continue to watch them challenge each other and build consensus.")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            # Only show button if not currently running
            if not st.session_state.debate_running:
                if st.button("🔥 Continue to Full Debate (Rounds 2 & 3)", use_container_width=True, type="primary", key="continue_debate_btn"):
                    st.session_state.debate_running = True
                    st.rerun()
            else:
                # Show spinner and run debate
                with st.spinner("🎯 Running cross-examination and consensus rounds..."):
                    result = agent.continue_debate(force=True)
                    # Save to database
                    agent.save_debate_to_database(debate_db)
                    st.session_state.debate_running = False
                    st.rerun()
        st.divider()
    
    # Three-column debate layout with round selection (shown for both complete and incomplete debates)
    st.markdown("### 📋 Complete Debate Transcript")
    
    # Round selector buttons
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        if st.button("📋 Round 1: Initial Positions", use_container_width=True, key="round_1_btn"):
            st.session_state.selected_round = 1
    with col_btn2:
        if st.button("🔍 Round 2: Cross-Examination", use_container_width=True, key="round_2_btn"):
            st.session_state.selected_round = 2
    with col_btn3:
        if st.button("🤝 Round 3: Final Votes", use_container_width=True, key="round_3_btn"):
            st.session_state.selected_round = 3
    
    # Initialize default round
    if 'selected_round' not in st.session_state:
        st.session_state.selected_round = 1
    
    # Show currently selected round
    round_names = {
        1: "📋 Round 1: Initial Positions",
        2: "🔍 Round 2: Cross-Examination", 
        3: "🤝 Round 3: Final Votes"
    }
    st.caption(f"**Viewing:** {round_names[st.session_state.selected_round]}")
    
    # Get debate data
    round_1 = agent.knowledge.get("debate_round_1", {})
    round_2 = agent.knowledge.get("debate_round_2", {})
    round_3 = agent.knowledge.get("debate_round_3", {})
    
    # Get agent names in order
    agent_names = ["Planner", "Market Analyst", "Risk Officer"]
    
    # Agent-specific colors and emojis
    agent_styles = {
        "Planner": {"color": "#0a74da", "bg": "#f0f8ff", "emoji": "📊"},
        "Market Analyst": {"color": "#00c48c", "bg": "#f0fff4", "emoji": "📉"},
        "Risk Officer": {"color": "#e53e3e", "bg": "#fff5f5", "emoji": "🛡️"}
    }
    
    # Display selected round in 3 columns
    col1, col2, col3 = st.columns(3)
    
    for col, agent_name in zip([col1, col2, col3], agent_names):
        with col:
            r1_data = round_1.get(agent_name, {})
            r2_data = round_2.get(agent_name, {})
            r3_data = round_3.get(agent_name, {})
            
            style = agent_styles[agent_name]
            
            # Agent header
            st.markdown(f"### {style['emoji']} {agent_name}")
            
            # Display content based on selected round
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
                    st.info("Round 2 not yet available. Click 'Continue to Full Debate' above.")
                    
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
                    st.info("Round 3 not yet available. Click 'Continue to Full Debate' above.")

elif not round_1_positions:
    st.info("Run Agentic Plan to generate initial agent positions and start the debate.")

# ---------- Historical Debates Section ----------
if round_1_positions:
    # Historical Debates Section
    st.divider()
    with st.expander("📊 Historical Debates & Learning System", expanded=False):
        st.info("""
        This section tracks all past debates stored in the database. Each debate includes:
        - **Consensus Score**: How aligned the agents were
        - **Validation Status**: Whether predictions were accurate (compared against actual market movements)
        - **Accuracy Rate**: Overall system performance over time
        
        Use the 'Outcome Validation' sidebar to validate past debates by comparing their predictions to current market data.
        """)
        
        # Get recent debates from database
        recent_debates = debate_db.get_recent_debates(limit=10)
        
        if recent_debates:
            # Validation stats
            val_stats = debate_db.get_validation_stats()
            if val_stats['total_validated'] > 0:
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Validated", val_stats['total_validated'])
                col2.metric("Accuracy Rate", f"{val_stats['accuracy_rate']}%")
                col3.metric("Avg Accuracy", f"{val_stats['avg_accuracy']:.1f}%")
                st.divider()
            
            # Display recent debates
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
    st.caption(f"Decision trace - {len(agent.logs)} total entries")
    st.info("💡 Logs persist across actions. Expand this section after running debates to see all agent reasoning.")
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

# ---------- Outcome Validation ----------
with st.sidebar.expander("📊 Outcome Validation", expanded=False):
    st.markdown("**Validate Past Debates**")
    st.info("""**What this does:**
    
Compares a past debate's prediction (BULLISH/BEARISH/NEUTRAL) against actual market movements.
    
- **BEARISH** = Predicted rates would rise → Checks if rates actually went up
- **BULLISH** = Predicted rates would fall → Checks if rates actually went down  
- **NEUTRAL** = Predicted stable rates → Checks if change was <5%
    
Accuracy score increases based on how much the market moved in the predicted direction.
    """)
    
    recent_debates = debate_db.get_recent_debates(limit=5)
    unvalidated = [d for d in recent_debates if d['validation_status'] is None]
    
    if unvalidated:
        st.info(f"{len(unvalidated)} debates pending validation")
        
        debate_to_validate = st.selectbox(
            "Select debate to validate:",
            options=[d['id'] for d in unvalidated],
            format_func=lambda x: f"Debate #{x} - {next(d['timestamp'][:10] for d in unvalidated if d['id'] == x)}"
        )
        
        if st.button("Validate Selected Debate") and debate_to_validate:
            # Get current rate for validation
            if "mortgage_rates" in agent.knowledge and len(agent.knowledge["mortgage_rates"]) > 0:
                current_rate = float(agent.knowledge["mortgage_rates"].iloc[-1]['rate'])
                result = debate_db.validate_debate_outcome(int(debate_to_validate), current_rate)
                
                status_emoji = "✅" if result['status'] == 'correct' else "❌"
                st.success(f"{status_emoji} Validation complete!")
                st.metric("Accuracy", f"{result['accuracy']:.1f}%")
                st.metric("Rate Change", f"{result['rate_change_pct']:+.2f}%")
            else:
                st.warning("Fetch current data first to validate")
    else:
        st.success("All recent debates validated!")
        val_stats = debate_db.get_validation_stats()
        if val_stats['total_validated'] > 0:
            st.metric("Overall Accuracy", f"{val_stats['accuracy_rate']}%")
            st.metric("Correct Predictions", f"{val_stats['correct_count']}/{val_stats['total_validated']}")

