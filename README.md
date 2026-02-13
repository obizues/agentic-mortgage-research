# 🏠 Agentic Mortgage Research Agent

A hands-on AI project demonstrating **intelligent agent reasoning** with real LLM integration. This agent autonomously researches US mortgage rates and home prices, uses Claude AI to make intelligent decisions about data fetching, and generates insightful analysis.

## ✅ Tech Stack (Recruiter Friendly)

- **Language**: Python 3.x
- **LLM**: Anthropic Claude (planning + insights)
- **Data**: FRED API, pandas, requests
- **Visualization/UI**: Streamlit, Altair
- **Agent Orchestration**: Custom agent planner + knowledge base
- **Config/Security**: python-dotenv, Streamlit secrets

## 🤖 Agentic AI Highlights

- **Multi-Agent Architecture**: Three specialized roles (Planner, Market Analyst, Risk Officer) provide diverse perspectives on market data
- **LLM-Driven Planning**: Claude decides which actions to execute based on knowledge state
- **Real-Time Visualization**: Color-coded perspective cards with markdown rendering
- **Orchestration**: Selects actions from knowledge state and runs them in sequence
- **Decision Transparency**: Complete decision trace logged in UI with emoji-based filtering
- **Graceful Fallback**: Heuristics when LLM unavailable

## 🎯 What This Demonstrates

### ✅ Hands-On AI Capabilities
- **LLM-Based Reasoning**: Uses Claude 3.5 Sonnet to decide which actions to execute based on current knowledge state
- **Real Data Integration**: Fetches live economic data from Federal Reserve (FRED API)
- **Intelligent Planning**: Agent determines if data needs refreshing, correlates market signals, and chains dependent actions
- **Production-Grade Architecture**: Clean separation of concerns, configuration management, error handling

### 🧠 Agent Behavior

The agent follows a intelligent decision flow:

1. **Plan (LLM-Driven)**: Analyzes current knowledge state and decides:
   - Should mortgage rates be refreshed? (checks recency and force flag)
   - Should rates be analyzed? (only if data is new)
   - Should home prices be fetched? (only if rates changed significantly)
   - How should insights be generated?

2. **Execute**: Runs planned actions in sequence
3. **Analyze**: Generates insights using Claude to interpret data
4. **Inform**: Updates the dashboard with findings

### Key Features
- **LLM Planning**: Claude decides what data to fetch based on knowledge state
- **Multi-Agent Perspectives**: Three specialized roles analyze the same data:
  - **📊 Planner**: Focuses on action selection and sequencing
  - **📉 Market Analyst**: Interprets data and identifies trends
  - **🛡️ Risk Officer**: Evaluates risks and establishes guardrails
- **LLM Insights**: Claude analyzes data and generates actionable insights
- **Dynamic UI**: Color-coded perspective cards with HTML/CSS styling and markdown rendering
- **Graceful Fallback**: If LLM unavailable, uses heuristic-based planning
- **Real-Time Logging**: Transparent decision-making with emoji-filtered role execution tracking
- **Interactive Dashboard**: Streamlit UI with granular controls (Agentic Plan, Regenerate Summary, Regenerate Perspectives)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Anthropic API key (get one at https://console.anthropic.com)

### Setup

1. **Clone/setup the project**:
   ```bash
   cd PyCharmMiscProject
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   The requirements file is pinned to the exact package versions used in the current environment.

3. **Configure API key** (choose one):
    - **Streamlit secrets** (local): create `.streamlit/secrets.toml` and set:
       ```toml
       ANTHROPIC_API_KEY = "sk-ant-xxx..."
       ```
      This file is ignored by git and must be created on each local machine.
    - **Environment file**: copy `.env.example` to `.env` and set:
       ```
       ANTHROPIC_API_KEY=sk-ant-xxx...
       ```

4. **Run the dashboard**:
   ```bash
   python run_dashboard.py
   ```
   
   The dashboard opens at `http://localhost:8501`

### Local Secrets Quickstart

After you pull the repo on a new machine, copy the template secrets file and add your key:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Then edit `.streamlit/secrets.toml` and set:

```toml
ANTHROPIC_API_KEY = "sk-ant-xxx..."
```

### First Run Checklist

- Create `.streamlit/secrets.toml` (from the example) or set `.env` with `ANTHROPIC_API_KEY`.
- Install dependencies with `pip install -r requirements.txt`.
- Start the app with `python run_dashboard.py`.

---

## 📊 Architecture

### Components

**AgenticMortgageResearchAgent** (`AgenticMortgageResearchAgent.py`)
- Core agent with knowledge base and action methods
- LLM-based planning: `_llm_based_plan()` - Claude decides what to do
- LLM-based analysis: `_llm_based_insights()` - Claude generates insights
- Heuristic fallback: Works without LLM using rule-based logic

**Dashboard** (`dashboard.py`)
- Streamlit UI with real-time updates and status widget
- Multi-agent perspectives displayed in color-coded cards (blue/green/red themes)
- Markdown-to-HTML conversion for proper formatting of LLM outputs
- Data visualizations (mortgage rates, home prices, normalized comparison)
- Agent logs with 3-way filtering (All logs / LLM decisions / Role outputs)
- Interactive controls:
  - **Agentic Plan**: Full orchestration (respects force refresh checkbox)
  - **Regenerate Summary**: Always creates fresh summary
  - **Regenerate Perspectives**: Always generates new role perspectives
  - **Clear Logs**: Resets decision trace
- Collapsible sidebar sections (Tech Stack, System Design, Agent Controls, Logs)

**Configuration** (`config.py`)
- Centralized settings (API keys, cache windows, thresholds)
- Environment variable support
- Feature flags for LLM vs heuristic mode

### Data Flow

```
User Action
    ↓
agentic_plan() [calls LLM to decide]
    ↓
LLM Response: ["fetch_mortgage_rates", "analyze_rates", ...]
    ↓
Execute Actions in Sequence
    ├─ fetch_mortgage_rates() → FRED API → cache
    ├─ analyze_rates() → compute statistics
    ├─ fetch_home_prices() → FRED API → cache
    ├─ compare_with_home_prices() → merge & correlate
    └─ summarize_insights() [calls LLM for analysis] → UI
```

---

## 🤖 LLM Integration Details

### Planning Phase
The agent sends Claude its current knowledge state and receives a JSON response:
```json
{
  "actions": ["fetch_mortgage_rates", "analyze_rates", "summarize_insights"],
  "reasoning": "Rates are stale (>24h), new fetch needed. Home prices up-to-date."
}
```

Claude considers:
- Data recency (when was it last fetched?)
- Whether force refresh is requested
- Data dependencies (don't analyze rates until they're fetched)
- Correlation signals (if rates changed >0.25%, fetch home prices too)

### Insights Phase
Claude analyzes the data context and generates actionable insights:
```
You are a mortgage market analyst. Analyze the following data:
- Current rate: 7.45%
- 12-month average: 6.89%
- Trend: Rates Elevated
- Home prices: rising year-over-year

Provide assessment, implications for homebuyers, and key insight.
```

### Multi-Agent Perspectives

The system generates three specialized perspectives on the same data:

**📊 Planner**
- Analyzes action selection and sequencing decisions
- Evaluates system state and workflow optimization
- Focuses on orchestration strategy

**📉 Market Analyst**
- Interprets mortgage rate trends and economic signals
- Identifies market patterns and correlations
- Provides data-driven market insights

**🛡️ Risk Officer**
- Assesses risk signals and market volatility
- Establishes guardrails and safety thresholds
- Highlights potential concerns for stakeholders

Each role receives the same context (summary, rates, trends, home prices) but responds from their professional perspective with 2-3 concise bullet points. This demonstrates a sophisticated multi-agent architecture where diverse viewpoints enhance analysis quality.

---

## 📈 How the Agent Reasons

### Example: Intelligent Fetching

**Scenario 1: First Run**
```
LLM Decision: "All data missing, fetch everything"
→ Actions: [fetch_mortgage_rates, analyze_rates, fetch_home_prices, compare, summarize]
```

**Scenario 2: Daily Check**
```
LLM Decision: "Rates are 6 hours old (fresh), rates haven't changed, skip fetch"
→ Actions: [summarize_insights]  # Fast path
```

**Scenario 3: Rate Spike**
```
LLM Decision: "Rates changed 0.35%, correlation broken, refetch home prices"
→ Actions: [fetch_home_prices, compare_with_home_prices, summarize_insights]
```

The LLM does this reasoning, not hardcoded rules!

---

## 🛠️ Configuration

Edit `config.py` to customize:

```python
# Cache validity
CACHE_VALIDITY_HOURS = 24

# Market sensitivity
RATE_CHANGE_THRESHOLD = 0.25  # percentage points

# LLM Settings
ENABLE_LLM_PLANNING = bool(ANTHROPIC_API_KEY)
MODEL_NAME = "claude-3-5-sonnet-20241022"
```

---

## 🔍 Monitoring & Logs

The dashboard displays:
- 📊 Live data visualizations (rates, prices, normalized comparison)
- 🧠 Multi-agent perspectives in color-coded cards
- 📝 Agent logs with timestamps and 3-way filtering:
  - **All logs**: Complete decision trace
  - **LLM decisions only**: Claude's planning and reasoning
  - **Role outputs only**: Emoji-tagged role execution (📊📉🛡️📈🔍💡🧠)
- 🚨 Real-time status widget during agent execution
- ⚠️ Error messages with fallback behavior

Example log output:
```
[14:23:45] 📊 Planner: Evaluating system state and data freshness...
[14:23:46] 📈 Data Collector: Fetching mortgage rates from FRED...
[14:23:47] Running action: fetch_mortgage_rates (force=False)
[14:23:48] Mortgage rates fetched.
[14:23:49] 🔍 Market Analyst: Analyzing mortgage rate trends...
[14:23:50] 📊 Planner: Analyzing data and generating perspective...
[14:23:51] 📉 Market Analyst: Analyzing data and generating perspective...
[14:23:52] 🛡️ Risk Officer: Analyzing data and generating perspective...
[14:23:53] Multi-agent perspectives generated successfully.
```

---

## 🧪 Testing LLM Integration

### Without API Key
If `ANTHROPIC_API_KEY` is not set, the agent automatically falls back to heuristic-based planning. You can still use the dashboard; it just won't use Claude for decisions.

### With API Key
Set your key in `.env` and the LLM features activate automatically.

### Forcing Heuristic Mode (for comparison)
Edit the `config.py` and set `ENABLE_LLM_PLANNING = False` to test heuristic vs LLM behavior.

---

## 🎓 Learning & Extension Points

### What I Built
1. **Multi-Agent Architecture**: Three specialized roles providing diverse analytical perspectives
2. **Multi-Step Agent Orchestration**: Planning → Execution → Analysis → UI
3. **LLM Integration Patterns**: Prompting for structured decisions + insights generation
4. **Real-Time UI Feedback**: Emoji-based role tracking with status widgets and callbacks
5. **Dynamic Content Rendering**: Markdown-to-HTML conversion for formatted LLM outputs
6. **Graceful Degradation**: Full functionality with or without LLM
7. **Real Data Pipelines**: API integration, caching, error handling
8. **Intelligent Reasoning**: Agent makes decisions, humans don't hardcode them

### Future Enhancements
- [ ] Add more specialized roles (Technical Analyst, Economic Forecaster)
- [ ] Implement role debate/consensus mechanisms
- [ ] Persistence layer (save/load agent state)
- [ ] Multi-turn LLM conversations for complex analysis
- [ ] Async action execution for faster processing
- [ ] More data sources (unemployment, inflation, consumer sentiment)
- [ ] Risk modeling with LLM-based scenario analysis
- [ ] Historical perspective comparisons (track how analysis changes over time)
- [ ] Unit tests with mocked FRED API responses
- [ ] Docker containerization
- [ ] CI/CD pipeline

---

## 📚 Tech Stack Details

- **Language**: Python 3.14+ (virtual environment)
- **LLM**: Anthropic Claude 3.5 (claude-3-haiku-20240307 for perspectives)
- **Data**: pandas 2.3.3, FRED Economic Data API, requests 2.32.5
- **Visualization/UI**: Streamlit 1.54.0, Altair 6.0.0
- **Agent Orchestration**: Custom multi-agent planner with role-based perspectives
- **UI Rendering**: HTML/CSS for dynamic styled components
- **Config/Security**: python-dotenv 1.2.1, Streamlit secrets (.gitignored)

### Pinned Dependencies

The exact installed dependency set (51 packages) is captured in [requirements.txt](requirements.txt) to ensure reproducible runs across environments.

---

## 🔐 Security Notes

- API keys stored in `.env` (never committed to git)
- No sensitive data logged
- API calls use HTTPS
- Fallback behavior if API fails

---

## 📄 License

This is a portfolio project for demonstrating AI/ML capabilities.

---

**Built as a hands-on AI demonstration for VP/SVP/Head of Engineering roles.**
