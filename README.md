# 🏠 Agentic Mortgage Research Agent

A hands-on AI project demonstrating **intelligent agent reasoning** with real LLM integration. This agent autonomously researches US mortgage rates and home prices, uses Claude AI to make intelligent decisions about data fetching, and generates insightful analysis.

## 📖 Table of Contents

- [Tech Stack](#-tech-stack-recruiter-friendly)
- [Agentic AI Highlights](#-agentic-ai-highlights)
- [What This Demonstrates](#-what-this-demonstrates)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture) ⭐ **Includes 5 Mermaid Diagrams** | [Deep Dive →](ARCHITECTURE.md)
  - [System Architecture Diagram](#system-architecture-diagram)
  - [Multi-Agent Execution Flow](#multi-agent-execution-flow)
  - [Data Flow Architecture](#data-flow-architecture)
  - [Component Dependencies](#component-interaction--dependencies)
  - [Deployment Architecture](#deployment-architecture-production-ready)
- [LLM Integration Details](#-llm-integration-details)
- [Configuration](#️-configuration)
- [Monitoring & Logs](#-monitoring--logs)
- [Learning & Extension](#-learning--extension-points)
- [Tech Stack Details](#-tech-stack-details)
- [Security](#-security-notes)
- [License](#-license)

---

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

> 📘 **For detailed technical documentation**, see [ARCHITECTURE.md](ARCHITECTURE.md)  
> Includes: System layers, component deep dive, ADRs, deployment strategies, testing approaches, and scalability plans.

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

### System Architecture Diagram

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[Streamlit Dashboard<br/>dashboard.py]
        Cards[Color-Coded<br/>Perspective Cards]
        Viz[Data Visualizations<br/>Altair Charts]
        Logs[Agent Logs<br/>3-Way Filter]
    end
    
    subgraph "Agent Orchestration Layer"
        Agent[AgenticMortgageResearchAgent<br/>Core Logic]
        Planner[LLM-Based Planner<br/>Claude 3.5]
        Actions[Action Methods<br/>fetch/analyze/compare]
        KB[Knowledge Base<br/>In-Memory Cache]
    end
    
    subgraph "Multi-Agent System"
        RolePlanner[📊 Planner Role<br/>Action Sequencing]
        RoleAnalyst[📉 Market Analyst<br/>Data Interpretation]
        RoleRisk[🛡️ Risk Officer<br/>Risk Assessment]
    end
    
    subgraph "External Services"
        Claude[Anthropic Claude API<br/>LLM Planning & Insights]
        FRED[FRED Economic Data API<br/>Mortgage Rates & Housing]
    end
    
    subgraph "Configuration"
        Config[config.py<br/>Settings & Secrets]
        Secrets[.streamlit/secrets.toml<br/>API Keys]
        Env[.env<br/>Environment Variables]
    end
    
    UI --> Agent
    Agent --> KB
    Agent --> Planner
    Planner --> Claude
    Agent --> Actions
    Actions --> FRED
    Actions --> KB
    
    Agent --> RolePlanner
    Agent --> RoleAnalyst
    Agent --> RoleRisk
    RolePlanner --> Claude
    RoleAnalyst --> Claude
    RoleRisk --> Claude
    
    KB --> Cards
    KB --> Viz
    Agent --> Logs
    
    Config --> Agent
    Secrets --> Config
    Env --> Config
    
    style UI fill:#e3f2fd
    style Agent fill:#fff3e0
    style Claude fill:#f3e5f5
    style FRED fill:#e8f5e9
    style KB fill:#fff9c4
```

### Multi-Agent Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant Dashboard
    participant Agent
    participant Planner as 📊 Planner Role
    participant Analyst as 📉 Market Analyst
    participant Risk as 🛡️ Risk Officer
    participant Claude as Claude API
    participant FRED as FRED API
    participant KB as Knowledge Base
    
    User->>Dashboard: Click "Agentic Plan"
    Dashboard->>Agent: agentic_plan()
    
    Agent->>Planner: Evaluate system state
    Planner->>Claude: "What actions needed?"
    Claude-->>Planner: ["fetch_rates", "analyze", "generate_perspectives"]
    
    Agent->>FRED: fetch_mortgage_rates()
    FRED-->>KB: Store rates data
    
    Agent->>KB: analyze_rates()
    KB-->>KB: Compute statistics
    
    Agent->>Planner: Generate perspective
    Planner->>Claude: "Plan next actions..."
    Claude-->>Planner: Planner insights
    
    Agent->>Analyst: Generate perspective
    Analyst->>Claude: "Analyze market trends..."
    Claude-->>Analyst: Analyst insights
    
    Agent->>Risk: Generate perspective
    Risk->>Claude: "Evaluate risks..."
    Claude-->>Risk: Risk insights
    
    KB-->>Dashboard: Update perspectives cards
    Dashboard-->>User: Display multi-agent insights
```

### Data Flow Architecture

```mermaid
flowchart LR
    subgraph Input
        User[User Action<br/>Button Click]
        Force[Force Refresh<br/>Checkbox]
    end
    
    subgraph Planning
        Check{Data Fresh?}
        LLM[Claude LLM<br/>Planning]
        Heuristic[Heuristic<br/>Fallback]
    end
    
    subgraph Execution
        FetchRates[Fetch Mortgage<br/>Rates FRED API]
        FetchPrices[Fetch Home<br/>Prices FRED API]
        Analyze[Analyze &<br/>Correlate]
        Summary[Generate<br/>Summary]
        Perspectives[Generate<br/>Perspectives]
    end
    
    subgraph Storage
        Cache[(Knowledge Base<br/>In-Memory Cache)]
        Timestamp[Timestamp<br/>Tracking]
    end
    
    subgraph Output
        UI[Streamlit UI<br/>Update]
        Cards[Multi-Agent<br/>Perspective Cards]
        Charts[Data<br/>Visualizations]
    end
    
    User --> Check
    Force --> Check
    Check -->|Stale| LLM
    Check -->|Fresh| Summary
    LLM --> FetchRates
    LLM -.Fallback.-> Heuristic
    Heuristic --> FetchRates
    
    FetchRates --> Cache
    FetchPrices --> Cache
    Cache --> Timestamp
    Cache --> Analyze
    Analyze --> Summary
    Summary --> Perspectives
    
    Perspectives --> Cards
    Cache --> Charts
    Summary --> UI
    Cards --> UI
    Charts --> UI
    
    style LLM fill:#f3e5f5
    style Cache fill:#fff9c4
    style Cards fill:#e3f2fd
    style UI fill:#e8f5e9
```

### Component Interaction & Dependencies

```mermaid
graph LR
    subgraph "Frontend"
        ST[Streamlit<br/>v1.54.0]
        AL[Altair<br/>v6.0.0]
    end
    
    subgraph "Agent Core"
        PY[Python 3.14<br/>Core Logic]
        PD[pandas 2.3.3<br/>Data Processing]
    end
    
    subgraph "LLM Layer"
        AN[Anthropic SDK<br/>v0.79.0]
        CL[Claude 3.5 Haiku<br/>claude-3-haiku-20240307]
    end
    
    subgraph "Data Sources"
        FR[FRED API<br/>Economic Data]
        RE[requests 2.32.5<br/>HTTP Client]
    end
    
    subgraph "Configuration"
        DT[python-dotenv<br/>v1.2.1]
        SE[Streamlit Secrets<br/>.toml]
    end
    
    ST --> PY
    AL --> ST
    PY --> PD
    PY --> AN
    AN --> CL
    PY --> RE
    RE --> FR
    DT --> SE
    SE --> PY
    
    style ST fill:#e3f2fd
    style PY fill:#fff3e0
    style CL fill:#f3e5f5
    style FR fill:#e8f5e9
```

### Deployment Architecture (Production Ready)

```mermaid
graph TB
    subgraph "Local Development"
        Dev[Developer Machine<br/>Python venv]
        Local[localhost:8501<br/>Streamlit Dev Server]
        DevSecrets[.streamlit/secrets.toml<br/>Local API Keys]
    end
    
    subgraph "Production Deployment"
        LB[Load Balancer<br/>HTTPS/TLS]
        App1[Streamlit App<br/>Container 1]
        App2[Streamlit App<br/>Container 2]
        AppN[Streamlit App<br/>Container N]
    end
    
    subgraph "State Management"
        Redis[(Redis Cache<br/>Session State)]
        Metrics[Prometheus<br/>Metrics]
    end
    
    subgraph "External APIs"
        Claude2[Anthropic Claude<br/>Rate Limited]
        FRED2[FRED API<br/>Public Data]
    end
    
    subgraph "Secrets & Config"
        Vault[HashiCorp Vault<br/>or AWS Secrets Manager]
        EnvVars[Environment Variables<br/>Injected at Runtime]
    end
    
    subgraph "Monitoring"
        Logs[Centralized Logging<br/>ELK Stack]
        Alerts[PagerDuty<br/>Alert Management]
        Dash[Grafana Dashboards<br/>Performance Metrics]
    end
    
    Dev --> Local
    DevSecrets --> Local
    
    LB --> App1
    LB --> App2
    LB --> AppN
    
    App1 --> Redis
    App2 --> Redis
    AppN --> Redis
    
    App1 --> Claude2
    App1 --> FRED2
    App2 --> Claude2
    App2 --> FRED2
    
    Vault --> EnvVars
    EnvVars --> App1
    EnvVars --> App2
    
    App1 --> Metrics
    App2 --> Metrics
    Metrics --> Dash
    
    App1 --> Logs
    App2 --> Logs
    Logs --> Alerts
    
    style LB fill:#e8f5e9
    style Redis fill:#fff9c4
    style Claude2 fill:#f3e5f5
    style Vault fill:#ffebee
    style Dash fill:#e3f2fd
```

**Key Architecture Decisions:**

1. **Stateless Application**: Agent knowledge stored per-session for horizontal scaling
2. **LLM Caching**: 24-hour cache validity reduces API costs and latency
3. **Graceful Degradation**: Heuristic fallback when Claude API unavailable
4. **Async-Ready**: Current implementation synchronous, easily adaptable to async/await
5. **Security by Default**: API keys never committed, secrets.toml gitignored
6. **Real-Time Feedback**: Callback-based logging enables streaming updates to UI
7. **Modular Design**: Clean separation allows easy testing and mocking

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
