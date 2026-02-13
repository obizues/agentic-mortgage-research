# System Architecture Documentation

## Overview

This document provides detailed technical architecture documentation for the Agentic Mortgage Research system. It covers system design decisions, component interactions, data flows, and production deployment considerations.

**Target Audience**: Technical leads, architects, senior engineers reviewing the codebase

---

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Component Deep Dive](#component-deep-dive)
3. [Data Flow Patterns](#data-flow-patterns)
4. [Multi-Agent System Design](#multi-agent-system-design)
5. [LLM Integration Strategy](#llm-integration-strategy)
6. [State Management](#state-management)
7. [Caching Strategy](#caching-strategy)
8. [Error Handling & Resilience](#error-handling--resilience)
9. [Security Architecture](#security-architecture)
10. [Performance Considerations](#performance-considerations)
11. [Production Deployment](#production-deployment)
12. [Observability & Monitoring](#observability--monitoring)
13. [Testing Strategy](#testing-strategy)
14. [Scalability & Future Enhancements](#scalability--future-enhancements)

---

## High-Level Architecture

### System Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Streamlit UI (dashboard.py)                          │  │
│  │  - Multi-agent perspective cards                      │  │
│  │  - Real-time status widgets                           │  │
│  │  - Data visualizations (Altair)                       │  │
│  │  - Agent log viewer with filtering                    │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Agent Orchestration (AgenticMortgageResearchAgent)   │  │
│  │  - Action planning & execution                        │  │
│  │  - Knowledge base management                          │  │
│  │  - Multi-agent role coordination                      │  │
│  │  - Decision logging & callbacks                       │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                   Integration Layer                          │
│  ┌─────────────────────┐      ┌──────────────────────────┐ │
│  │  LLM Integration    │      │  Data Integration        │ │
│  │  - Claude API       │      │  - FRED API              │ │
│  │  - Prompt templates │      │  - HTTP client (requests)│ │
│  │  - Response parsing │      │  - Data transformation   │ │
│  └─────────────────────┘      └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                   Configuration Layer                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Config Management (config.py)                        │  │
│  │  - API keys & secrets                                 │  │
│  │  - Feature flags                                      │  │
│  │  - Cache settings                                     │  │
│  │  - Threshold configurations                           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Deep Dive

### 1. AgenticMortgageResearchAgent

**Responsibilities:**
- Orchestrate actions based on LLM planning or heuristics
- Maintain in-memory knowledge base
- Execute data fetching, analysis, and insight generation
- Coordinate multi-agent role perspectives
- Provide logging callbacks for UI updates

**Key Methods:**

| Method | Purpose | LLM Usage |
|--------|---------|-----------|
| `agentic_plan()` | Orchestrate full workflow | ✅ Planning |
| `fetch_mortgage_rates()` | Get FRED mortgage data | ❌ |
| `analyze_rates()` | Compute statistics | ❌ |
| `fetch_home_prices()` | Get FRED housing data | ❌ |
| `compare_with_home_prices()` | Correlate datasets | ❌ |
| `summarize_insights()` | Generate summary | ✅ Insights |
| `generate_role_perspectives()` | Multi-agent analysis | ✅ 3x Roles |
| `_llm_based_plan()` | LLM action selection | ✅ Planning |
| `_llm_role_insights()` | Generate role perspectives | ✅ Insights |
| `_simple_plan()` | Heuristic fallback | ❌ |

**State Management:**
```python
self.knowledge = {
    "mortgage_rates": DataFrame,        # FRED data
    "home_prices": DataFrame,           # FRED data
    "rate_insights": Dict,              # Computed stats
    "comparison": str,                  # Correlation text
    "summary": str,                     # LLM-generated summary
    "role_insights": Dict[str, str],   # Multi-agent perspectives
    "fetch_timestamps": Dict[str, datetime],  # Cache tracking
}
```

### 2. Dashboard (dashboard.py)

**Responsibilities:**
- Render Streamlit UI
- Handle user interactions
- Display multi-agent perspectives with HTML/CSS
- Stream real-time agent execution logs
- Manage session state

**UI Components:**

```
Sidebar:
├── Tech Stack (collapsible)
├── System Design Notes (collapsible)
├── Agent Controls (collapsible)
│   ├── Force Refresh checkbox
│   ├── Agentic Plan button
│   ├── Regenerate Summary button
│   └── Regenerate Perspectives button
└── Agent Logs (collapsible)
    └── 3-way filter (All / LLM / Roles)

Main Area:
├── Executive Summary
├── Multi-Agent Perspectives (3-column cards)
├── Mortgage Rates Chart (Altair)
├── Home Prices Chart (Altair)
└── Normalized Comparison Chart (Altair)
```

**Key UI Patterns:**
- **Real-time updates**: Callback system updates `st.session_state` during agent execution
- **Status widget**: Shows progressive role execution with emoji tags
- **Markdown-to-HTML**: Converts LLM markdown output for proper rendering
- **Color-coded cards**: Blue (Planner), Green (Analyst), Red (Risk Officer)

### 3. Configuration (config.py)

**Secrets Management:**
```python
# Priority order:
1. Streamlit secrets (.streamlit/secrets.toml)  # Local dev
2. Environment variables (.env)                  # CI/CD
3. System environment variables                  # Production

# Graceful degradation if secrets missing
if not ANTHROPIC_API_KEY:
    ENABLE_LLM_PLANNING = False
```

**Key Settings:**

| Setting | Default | Purpose |
|---------|---------|---------|
| `CACHE_VALIDITY_HOURS` | 24 | Data freshness threshold |
| `RATE_CHANGE_THRESHOLD` | 0.25 | Trigger for home price fetch |
| `MODEL_NAME` | claude-3-haiku-20240307 | LLM model selection |
| `ENABLE_LLM_PLANNING` | Auto | Feature flag for LLM vs heuristics |

---

## Data Flow Patterns

### Pattern 1: First Run (Cold Start)

```
User opens dashboard
    ↓
st.session_state.first_run = True
    ↓
Auto-trigger agentic_plan()
    ↓
LLM Planning: "No data exists, fetch everything"
    ↓
fetch_mortgage_rates() → FRED API
    ↓
analyze_rates() → compute statistics
    ↓
fetch_home_prices() → FRED API
    ↓
compare_with_home_prices() → correlation
    ↓
summarize_insights() → LLM summary
    ↓
_llm_role_insights() → 3x LLM calls (Planner, Analyst, Risk)
    ↓
Update UI with all perspectives
```

**LLM Calls**: 5 total (1 planning + 1 summary + 3 roles)  
**FRED API Calls**: 2 total (rates + prices)  
**Total Time**: ~8-12 seconds  

### Pattern 2: Refresh with Stale Data

```
User clicks "Agentic Plan" (force_refresh = False)
    ↓
Check timestamps: rates fetched 25 hours ago
    ↓
LLM Planning: "Rates stale, prices fresh"
    ↓
fetch_mortgage_rates() → FRED API
    ↓
analyze_rates() → new statistics
    ↓
Check rate change: 0.3% delta (> 0.25% threshold)
    ↓
fetch_home_prices() → FRED API (refetch for correlation)
    ↓
compare_with_home_prices() → updated correlation
    ↓
summarize_insights() → new LLM summary
    ↓
(Perspectives not regenerated unless forced)
    ↓
Update UI
```

**LLM Calls**: 2 total (1 planning + 1 summary)  
**FRED API Calls**: 2 total  
**Total Time**: ~4-6 seconds  

### Pattern 3: Regenerate Perspectives Only

```
User clicks "Regenerate Perspectives"
    ↓
generate_role_perspectives(force=True)
    ↓
Check LLM client availability
    ↓
_llm_role_insights()
    ↓
For each role (Planner, Analyst, Risk):
    Build context from knowledge base
    Send prompt to Claude
    Parse response
    Store in knowledge["role_insights"]
    ↓
Update UI cards
```

**LLM Calls**: 3 total (3 roles)  
**FRED API Calls**: 0  
**Total Time**: ~3-5 seconds  

---

## Multi-Agent System Design

### Architecture Philosophy

The multi-agent system demonstrates **diversity of thought** pattern:
- Single source of truth (shared knowledge base)
- Multiple specialized perspectives on the same data
- No agent-to-agent communication (simpler, more deterministic)
- Each role has distinct prompts and objectives

### Role Definitions

#### 📊 Planner Role
**Focus**: Action selection and sequencing  
**Prompt Strategy**:
```
"You are an agent planner. Focus on action selection and sequencing.

Context: [shared context]

Provide 2-3 concise bullet points for your perspective."
```

**Typical Output**:
- "Prioritize rate data refresh over home price data"
- "Current correlation suggests no urgent action needed"
- "Next optimal action: wait 6 hours before re-analysis"

#### 📉 Market Analyst Role
**Focus**: Data interpretation and trend analysis  
**Prompt Strategy**:
```
"You are a mortgage market analyst. Focus on data interpretation.

Context: [shared context]

Provide 2-3 concise bullet points for your perspective."
```

**Typical Output**:
- "Rates elevated 8% above 12-month average"
- "Upward trend suggests continued pressure on affordability"
- "Home prices rising despite rate increases (unusual pattern)"

#### 🛡️ Risk Officer Role
**Focus**: Risk signals and guardrails  
**Prompt Strategy**:
```
"You are a risk officer. Focus on risk signals and guardrails.

Context: [shared context]

Provide 2-3 concise bullet points for your perspective."
```

**Typical Output**:
- "High rate volatility increases forecasting uncertainty"
- "Recommend establishing circuit breakers at 8.5% threshold"
- "Price-rate decoupling suggests potential market instability"

### Implementation Pattern

```python
def _llm_role_insights(self):
    role_outputs = {}
    
    for role_name, role_prompt in role_prompts.items():
        # Log execution for UI tracking
        self.log(f"{emoji} {role_name}: Analyzing data...")
        
        # Build context from knowledge base
        context = self._build_context()
        
        # Send to LLM
        response = self.llm_client.messages.create(
            model=config.MODEL_NAME,
            max_tokens=250,  # Keep outputs concise
            messages=[{
                "role": "user",
                "content": f"{role_prompt}\n\nContext:\n{context}"
            }]
        )
        
        # Store result
        role_outputs[role_name] = response.content[0].text.strip()
    
    self.knowledge["role_insights"] = role_outputs
```

**Benefits of This Design**:
- ✅ Parallel execution possible (currently sequential)
- ✅ Easy to add new roles without refactoring
- ✅ Each role is independently testable
- ✅ Clear separation of concerns
- ✅ Deterministic (no agent debates/negotiations)

---

## LLM Integration Strategy

### Prompt Engineering

**Planning Prompt Template**:
```python
f"""You are an AI agent planner for mortgage research.

Current Knowledge State:
- Mortgage rates last fetched: {timestamp}
- Home prices last fetched: {timestamp}
- Rate insights available: {bool}
- Summary available: {bool}

User Action: {action_name}
Force Refresh: {force}

Available Actions:
- fetch_mortgage_rates: Get latest 30-year fixed rates from FRED
- analyze_rates: Compute statistics and trends
- fetch_home_prices: Get home price index
- compare_with_home_prices: Correlate rates with housing
- summarize_insights: Generate executive summary

Decide which actions to run in sequence. Return JSON:
{{"actions": ["action1", "action2"], "reasoning": "explanation"}}
"""
```

**Insights Prompt Template**:
```python
f"""You are a mortgage market analyst. Analyze:

Current Data:
- 30-year rate: {latest_rate}%
- 12-month average: {avg_rate}%
- Trend: {trend_signal}
- Home prices: {price_trend}
- Correlation: {comparison}

Provide:
1. Assessment of current market
2. Implications for homebuyers
3. One key insight
"""
```

### Token Optimization

| Call Type | Max Tokens | Rationale |
|-----------|------------|-----------|
| Planning | 300 | JSON response, reasoning |
| Summary | 500 | Comprehensive analysis |
| Role Perspectives | 250 each | Concise bullet points |

**Estimated Cost per Action** (Claude 3.5 Haiku pricing):
- Planning: ~$0.002
- Summary: ~$0.003
- Perspectives (3): ~$0.006
- **Total per full run**: ~$0.011

### Error Handling

```python
try:
    response = self.llm_client.messages.create(...)
except anthropic.APIError as e:
    self.log(f"LLM API error: {e}")
    return self._simple_plan()  # Fallback to heuristics
except Exception as e:
    self.log(f"Unexpected error: {e}")
    raise
```

---

## State Management

### Session State (Streamlit)

```python
st.session_state = {
    "agent": AgenticMortgageResearchAgent(),  # Singleton per session
    "logs_text": List[str],                   # All log messages
    "role_logs": List[str],                   # Filtered role logs
    "first_run": bool,                        # Auto-run flag
    "status_placeholder": st.empty(),         # Real-time updates
}
```

### Knowledge Base (Agent)

```python
self.knowledge = {
    # Data
    "mortgage_rates": pd.DataFrame,
    "home_prices": pd.DataFrame,
    
    # Analysis
    "rate_insights": {
        "latest_rate": float,
        "12_month_avg": float,
        "trend_signal": str,
        "volatility": float,
    },
    
    # Comparisons
    "comparison": str,
    
    # Summaries
    "summary": str,
    
    # Multi-agent
    "role_insights": {
        "Planner": str,
        "Market Analyst": str,
        "Risk Officer": str,
    },
    
    # Metadata
    "fetch_timestamps": {
        "mortgage_rates": datetime,
        "home_prices": datetime,
    },
}
```

### Cache Invalidation

```python
def _is_data_fresh(self, key: str) -> bool:
    if key not in self.knowledge.get("fetch_timestamps", {}):
        return False
    
    last_fetch = self.knowledge["fetch_timestamps"][key]
    age_hours = (datetime.now() - last_fetch).total_seconds() / 3600
    
    return age_hours < config.CACHE_VALIDITY_HOURS

# Usage
if force or not self._is_data_fresh("mortgage_rates"):
    self.fetch_mortgage_rates()
```

---

## Caching Strategy

### L1: In-Memory Cache (Knowledge Base)
- **Scope**: Per-session (Streamlit session_state)
- **Duration**: Session lifetime
- **Pros**: Zero latency, simple implementation
- **Cons**: Not shared across users, lost on page refresh

### L2: FRED API Caching (Implicit)
- **Scope**: FRED's servers
- **Duration**: ~1 day (FRED update frequency)
- **Pros**: Free, maintained by FRED
- **Cons**: No control, potential staleness

### Future: L3: Redis Cache (Production)
```python
# Proposed production caching
def fetch_mortgage_rates(self, force=False):
    cache_key = "mortgage_rates:latest"
    
    if not force:
        cached = redis_client.get(cache_key)
        if cached:
            return pd.read_json(cached)
    
    # Fetch from FRED
    data = self._fetch_from_fred()
    
    # Cache for 6 hours
    redis_client.setex(
        cache_key,
        timedelta(hours=6),
        data.to_json()
    )
    
    return data
```

---

## Error Handling & Resilience

### Layered Error Handling

```
┌─────────────────────────────────────┐
│  UI Layer (dashboard.py)            │
│  - Try/except around button actions │
│  - Display user-friendly errors     │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│  Agent Layer (run_action)           │
│  - Validate action exists           │
│  - Log all errors                   │
│  - Re-raise for UI handling         │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│  Action Layer (each method)         │
│  - Specific exceptions              │
│  - Retry logic (future)             │
│  - Fallback strategies              │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│  Integration Layer                  │
│  - LLM: APIError → heuristics       │
│  - FRED: HTTPError → cached data    │
└─────────────────────────────────────┘
```

### Graceful Degradation Examples

**LLM Unavailable**:
```python
if self.llm_client is None:
    return self._simple_plan()  # Heuristic fallback
```

**FRED API Down**:
```python
if "mortgage_rates" not in self.knowledge:
    return "Unable to fetch rates. Using cached analysis."
```

**Partial Data**:
```python
if "home_prices" not in self.knowledge:
    summary = "Rate analysis only (home price data unavailable)"
```

---

## Security Architecture

### API Key Management

```
Development:
  .streamlit/secrets.toml (gitignored)
  
CI/CD:
  GitHub Secrets → Environment Variables
  
Production:
  HashiCorp Vault / AWS Secrets Manager
  ↓
  Environment Variables (injected at runtime)
  ↓
  config.py (read-only access)
```

### Security Best Practices Implemented

✅ **Secrets Never Committed**
- `.streamlit/secrets.toml` in `.gitignore`
- `.env` in `.gitignore`
- `secrets.toml.example` provided as template

✅ **Least Privilege**
- FRED API: Read-only public data
- Anthropic API: User-scoped key

✅ **Input Validation**
- User actions validated against whitelist
- No user-provided data passed to LLM (future consideration)

✅ **HTTPS Only**
- All external API calls use HTTPS
- Requests library validates certificates

### Security Enhancements (Production)

🔜 **Input Sanitization**: If user input added, sanitize before LLM prompts  
🔜 **Rate Limiting**: Per-user limits to prevent abuse  
🔜 **Audit Logging**: Track all sensitive operations  
🔜 **Secret Rotation**: Automated key rotation schedule  
🔜 **Dependency Scanning**: Snyk/Dependabot for vulnerability monitoring  

---

## Performance Considerations

### Current Performance Profile

| Operation | Latency | Bottleneck |
|-----------|---------|------------|
| FRED API call | 500-1000ms | Network |
| Claude API (planning) | 1-2s | LLM inference |
| Claude API (insights) | 1-3s | LLM inference |
| Data processing | <100ms | CPU (pandas) |
| UI rendering | <100ms | Streamlit |

**Full Agentic Plan (Cold Start)**: 8-12 seconds  
**Regenerate Perspectives**: 3-5 seconds  

### Optimization Opportunities

**1. Parallel LLM Calls**
```python
# Current: Sequential
for role in roles:
    response = await llm_call(role)  # 1s each = 3s total

# Future: Parallel
tasks = [llm_call(role) for role in roles]
responses = await asyncio.gather(*tasks)  # ~1s total
```
**Impact**: 2-3s reduction per perspective generation

**2. Streaming Responses**
```python
# Future: Stream tokens to UI
with self.llm_client.messages.stream(...) as stream:
    for text in stream.text_stream:
        self.status_placeholder.text(accumulated_text + text)
```
**Impact**: Better perceived performance, <1s to first token

**3. Background Refresh**
```python
# Future: Proactive cache warming
@st.cache_data(ttl=3600)
def prefetch_latest_data():
    # Fetch in background before user requests
    pass
```
**Impact**: Instant results for cached queries

---

## Production Deployment

### Containerization

**Dockerfile**:
```dockerfile
FROM python:3.14-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  dashboard:
    build: .
    ports:
      - "8501:8501"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - FRED_API_KEY=${FRED_API_KEY}
    env_file:
      - .env
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mortgage-research-dashboard
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mortgage-dashboard
  template:
    metadata:
      labels:
        app: mortgage-dashboard
    spec:
      containers:
      - name: dashboard
        image: your-registry/mortgage-dashboard:v1.2.0
        ports:
        - containerPort: 8501
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: anthropic-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## Observability & Monitoring

### Logging Strategy

**Current Implementation**:
```python
# Agent logging with callback
def log(self, message: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    self.logs.append(log_message)
    if self.log_callback:
        self.log_callback(log_message)
```

**Production Enhancement**:
```python
import structlog

logger = structlog.get_logger()

def log(self, message: str, level="info", **context):
    log_func = getattr(logger, level)
    log_func(
        message,
        agent_id=self.agent_id,
        session_id=self.session_id,
        **context
    )
```

### Metrics to Track

**Business Metrics**:
- User sessions per day
- Actions executed per session
- LLM calls per user
- Cost per session (LLM + API)

**Technical Metrics**:
- Response time per action
- LLM latency (p50, p95, p99)
- FRED API success rate
- Cache hit rate
- Error rate by type

**Proposed Stack**:
```
Application → Prometheus Client
    ↓
Prometheus Server (metrics storage)
    ↓
Grafana (visualization)
    ↓
Alertmanager (PagerDuty integration)
```

---

## Testing Strategy

### Test Pyramid

```
        /\
       /  \     E2E Tests (5%)
      /────\    UI automation, full workflow
     /      \   
    /────────\  Integration Tests (15%)
   /          \ API mocking, component integration
  /────────────\
 /              \ Unit Tests (80%)
/________________\ Pure functions, logic, edge cases
```

### Proposed Test Structure

```
tests/
├── unit/
│   ├── test_agent_core.py
│   ├── test_data_processing.py
│   ├── test_prompt_templates.py
│   └── test_caching.py
├── integration/
│   ├── test_fred_api.py
│   ├── test_llm_integration.py
│   └── test_agent_workflows.py
├── e2e/
│   ├── test_dashboard_flows.py
│   └── test_multi_agent_scenarios.py
├── fixtures/
│   ├── fred_responses.json
│   ├── llm_responses.json
│   └── sample_data.csv
└── conftest.py
```

### Example Unit Test

```python
import pytest
from unittest.mock import Mock, patch
from AgenticMortgageResearchAgent import AgenticMortgageResearchAgent

def test_data_freshness_check():
    agent = AgenticMortgageResearchAgent()
    
    # Test: Fresh data
    agent.knowledge["fetch_timestamps"] = {
        "mortgage_rates": datetime.now() - timedelta(hours=12)
    }
    assert agent._is_data_fresh("mortgage_rates") == True
    
    # Test: Stale data
    agent.knowledge["fetch_timestamps"] = {
        "mortgage_rates": datetime.now() - timedelta(hours=25)
    }
    assert agent._is_data_fresh("mortgage_rates") == False
    
    # Test: Missing data
    agent.knowledge["fetch_timestamps"] = {}
    assert agent._is_data_fresh("mortgage_rates") == False

@patch('anthropic.Anthropic')
def test_llm_planning_with_mock(mock_client):
    # Mock LLM response
    mock_client.messages.create.return_value = Mock(
        content=[Mock(text='{"actions": ["fetch_mortgage_rates"], "reasoning": "test"}')]
    )
    
    agent = AgenticMortgageResearchAgent(llm_client=mock_client)
    actions = agent._llm_based_plan()
    
    assert "fetch_mortgage_rates" in actions
    assert mock_client.messages.create.called
```

---

## Scalability & Future Enhancements

### Vertical Scaling (Single Instance)

**Current Bottleneck**: LLM API calls (3-5s per role)

**Solutions**:
1. Async/await for parallel LLM calls (-60% latency)
2. Streaming responses (better UX, no latency improvement)
3. Reduce max_tokens where possible (-20% latency)
4. Use Claude Haiku vs Sonnet (-50% latency, -75% cost)

### Horizontal Scaling (Multiple Instances)

**Current Challenge**: Streamlit session state is per-instance

**Solutions**:
1. **Redis Session Store**: Shared state across instances
2. **Stateless Agent**: Knowledge base in Redis, not memory
3. **Load Balancer**: Sticky sessions during active work
4. **Message Queue**: Celery for async background jobs

**Architecture**:
```
Load Balancer
    ↓
┌─────────┬─────────┬─────────┐
│ App 1   │ App 2   │ App 3   │
└────┬────┴────┬────┴────┬────┘
     └─────────┴─────────┘
              ↓
         Redis Cache
         (shared state)
              ↓
    ┌─────────────────┐
    │  Celery Workers │
    │  (async jobs)   │
    └─────────────────┘
```

### Future Features Roadmap

**Phase 1: Production Readiness** (2-4 weeks)
- [ ] Full test coverage (pytest)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Docker containerization
- [ ] Observability (Prometheus + Grafana)
- [ ] Cost tracking dashboard

**Phase 2: Performance** (2-3 weeks)
- [ ] Async LLM calls (asyncio)
- [ ] Redis caching layer
- [ ] Streaming responses
- [ ] Background data refresh

**Phase 3: Intelligence** (3-4 weeks)
- [ ] Agent debate/consensus mechanism
- [ ] Historical trend analysis
- [ ] Predictive modeling
- [ ] User preference learning

**Phase 4: Enterprise** (4-6 weeks)
- [ ] Multi-tenancy
- [ ] Role-based access control
- [ ] Audit logging
- [ ] SOC2 compliance

---

## Architectural Decision Records (ADRs)

### ADR-001: Why In-Memory Knowledge Base?

**Context**: Need to store agent state between actions

**Decision**: Use in-memory dictionary instead of database

**Rationale**:
- POC/demo scope - session-based data sufficient
- Minimal dependencies
- Fast access (no network latency)
- Simple implementation

**Consequences**:
- ✅ Zero infrastructure overhead
- ✅ Instant access
- ❌ Data lost on page refresh
- ❌ Not shareable across users
- ❌ No persistence

**Future**: Migrate to Redis for production

---

### ADR-002: Why Claude Haiku for Perspectives?

**Context**: Need LLM for multi-agent role generation

**Decision**: Use Claude 3.5 Haiku instead of Sonnet

**Rationale**:
- Perspectives are short (2-3 bullets)
- Haiku is 75% cheaper
- Haiku is 50% faster
- Quality difference negligible for concise outputs

**Consequences**:
- ✅ Lower cost per run
- ✅ Faster response times
- ✅ Same quality for this use case
- ❌ Less nuanced for complex analysis (acceptable trade-off)

---

### ADR-003: Why Sequential Role Execution?

**Context**: Generate 3 role perspectives (Planner, Analyst, Risk)

**Decision**: Execute sequentially instead of parallel

**Rationale**:
- Simpler implementation (no async complexity)
- POC scope - 3-5s latency acceptable
- Easier debugging
- Anthropic SDK doesn't require async

**Consequences**:
- ✅ Simple code
- ✅ Deterministic execution order
- ❌ 3x slower than parallel (3s vs 1s)

**Future**: Migrate to async/await for production

---

### ADR-004: Why No Agent-to-Agent Communication?

**Context**: Multi-agent system design choices

**Decision**: Roles don't communicate, only share read-only context

**Rationale**:
- Simplicity: No message passing complexity
- Determinism: No emergent behaviors
- Cost: 3 LLM calls vs potentially 10+ with debates
- Understandability: Clear input → output per role

**Consequences**:
- ✅ Predictable behavior
- ✅ Lower LLM costs
- ✅ Easier to test
- ❌ No consensus mechanism
- ❌ No cross-role learning

**Future**: Consider debate mechanism if value proven

---

## Summary

This architecture demonstrates:

✅ **Production-aware thinking** despite POC scope  
✅ **Scalability considerations** with clear migration paths  
✅ **Strong separation of concerns** enabling testability  
✅ **Graceful degradation** at every layer  
✅ **Cost-conscious LLM usage** with appropriate model selection  
✅ **Security by default** with proper secrets management  

**The system is production-ready with these additions:**
- Test suite (pytest)
- CI/CD (GitHub Actions)
- Containerization (Docker)
- Observability (Prometheus/Grafana)
- Async multi-agent execution
- Redis caching layer

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-02-12  
**Author**: Chris Obermeier  
**Contact**: chris.obermeier@gmail.com
