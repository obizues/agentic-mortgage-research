# 🏠 Agentic Mortgage Research Agent

A hands-on AI project demonstrating **intelligent agent reasoning** with real LLM integration. This agent autonomously researches US mortgage rates and home prices, uses Claude AI to make intelligent decisions about data fetching, and generates insightful analysis.

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
- **LLM Insights**: Claude analyzes data and generates actionable insights
- **Graceful Fallback**: If LLM unavailable, uses heuristic-based planning
- **Real-Time Logging**: Transparent decision-making visible in UI
- **Interactive Dashboard**: Streamlit UI with force refresh, real-time visualizations

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
    - **Streamlit secrets** (local): edit `.streamlit/secrets.toml` and set:
       ```toml
       ANTHROPIC_API_KEY = "sk-ant-xxx..."
       ```
    - **Environment file**: copy `.env.example` to `.env` and set:
       ```
       ANTHROPIC_API_KEY=sk-ant-xxx...
       ```

4. **Run the dashboard**:
   ```bash
   python run_dashboard.py
   ```
   
   The dashboard opens at `http://localhost:8501`

---

## 📊 Architecture

### Components

**AgenticMortgageResearchAgent** (`AgenticMortgageResearchAgent.py`)
- Core agent with knowledge base and action methods
- LLM-based planning: `_llm_based_plan()` - Claude decides what to do
- LLM-based analysis: `_llm_based_insights()` - Claude generates insights
- Heuristic fallback: Works without LLM using rule-based logic

**Dashboard** (`dashboard.py`)
- Streamlit UI with real-time updates
- Data visualizations (mortgage rates, home prices, normalized comparison)
- Agent logs showing decision-making process
- Interactive controls for manual actions

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
- 📊 Live data visualizations
- 📝 Agent logs with timestamps showing:
  - What the LLM decided
  - Which actions were executed
  - Why decisions were made
- ⚠️ Error messages with fallback behavior

Example log output:
```
[14:23:45] 🤖 Agentic planning started...
[14:23:45] LLM Decision: Mortgage rates >24h old and home prices need refresh
[14:23:47] Running action: fetch_mortgage_rates (force=False)
[14:23:48] Mortgage rates fetched.
[14:23:49] Running action: analyze_rates (force=False)
[14:23:50] LLM-based insights generated.
[14:23:50] 🤖 LLM-based planning finished.
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
1. **Multi-Step Agent Orchestration**: Planning → Execution → Analysis → UI
2. **LLM Integration Patterns**: Prompting for structured decisions + JSON parsing
3. **Graceful Degradation**: Full functionality with or without LLM
4. **Real Data Pipelines**: API integration, caching, error handling
5. **Intelligent Reasoning**: Agent makes decisions, humans don't hardcode them

### Future Enhancements
- [ ] Persistence layer (save/load agent state)
- [ ] Multi-turn LLM conversations for complex analysis
- [ ] Async action execution for faster processing
- [ ] More data sources (unemployment, inflation, etc.)
- [ ] Risk modeling with LLM-based scenario analysis
- [ ] Unit tests with mocked FRED API responses
- [ ] Docker containerization
- [ ] CI/CD pipeline

---

## 📚 Tech Stack

- **LLM**: Anthropic Claude 3.5 Sonnet
- **Data**: pandas, FRED Economic Data API
- **Visualization**: Streamlit, Altair
- **Language**: Python 3.8+

### Pinned Dependencies

The exact installed dependency set is captured in [requirements.txt](requirements.txt) to ensure reproducible runs.

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
