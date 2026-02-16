import pandas as pd
import config
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from io import StringIO
from datetime import datetime, timedelta
import json
from typing import Optional
try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

class AgenticMortgageResearchAgent:
    import config
    def __init__(self, log_callback=None, llm_client: Optional['Anthropic'] = None, debate_db=None):
        self.goal = "Understand current US mortgage rate trends and risks"
        self.knowledge = {}
        self.logs = []
        self.log_callback = log_callback
        self.last_fetch_dates = {}  # track when data was fetched
        self.llm_client = llm_client  # Optional Claude client for LLM-based reasoning
        self.debate_db = debate_db  # Database for storing/retrieving debate patterns
        self.session_cost = 0.0  # Track estimated LLM API costs
        # Initialize fetch_timestamps in knowledge for dashboard status display
        self.knowledge["fetch_timestamps"] = {}
        
        # Set up resilient HTTP session with retries
        self.session = self._create_resilient_session()
    
    def _create_resilient_session(self):
        """Create a requests session with retry logic for API calls."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    # ---------- Logging ----------
    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.logs.append(log_message)
        if self.log_callback:
            self.log_callback(log_message)

    def get_logs(self):
        return "\n".join(self.logs)

    # ---------- Action dispatcher ----------
    def run_action(self, action_name: str, force: bool = False):
        if not hasattr(self, action_name):
            self.log(f"Attempted unknown action: {action_name}")
            raise ValueError(f"Unknown action: {action_name}")
        self.log(f"Running action: {action_name} (force={force})")
        method = getattr(self, action_name)
        try:
            result = method(force=force)
            self.log(result)
        except Exception as e:
            self.log(f"ERROR in {action_name}: {str(e)}")
            raise
        return result

    # ---------- Agentic planner ----------
    def agentic_plan(self, force=False):
        """Automatically decide which actions to run based on current knowledge."""
        self.log("🤖 Agentic planning started...")
        self.log("📊 Planner: Evaluating system state and data freshness...")
        
        # Use LLM-based planning if available, otherwise fall back to heuristics
        if self.llm_client:
            return self._llm_based_plan(force)
        else:
            return self._heuristic_plan(force)
    
    def _llm_based_plan(self, force=False):
        """Use Claude to decide which actions should be executed."""
        try:
            # Log Anthropic SDK version
            try:
                import anthropic
                sdk_version = getattr(anthropic, '__version__', 'unknown')
                self.log(f"Anthropic SDK version: {sdk_version}")
            except Exception as sdk_e:
                self.log(f"Could not determine Anthropic SDK version: {sdk_e}")
            # Build context about current knowledge state
            state_summary = self._get_knowledge_state_summary()
            self.log("LLM planning: state summary prepared.")
            
            prompt = f"""You are an intelligent mortgage research agent. Based on the current knowledge state, decide which actions to run:

Current Knowledge State:
{state_summary}

Current Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Force Refresh: {force}

Available actions:
- fetch_mortgage_rates: Get latest 30-year mortgage rates from FRED
- analyze_rates: Compute statistics on mortgage rates
- fetch_home_prices: Get latest US home price index from FRED
- compare_with_home_prices: Correlate rates with home prices
- summarize_insights: Generate insights from all data

Based on the state above, return a JSON object with:
{{"actions": ["action1", "action2", ...], "reasoning": "brief explanation"}}

Only include actions that should be run. Skip actions if data is recent and unchanged."""

            try:
                message = self.llm_client.messages.create(
                    model=config.MODEL_NAME,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                self.session_cost += 0.002  # Approximate cost for planning call
            except Exception as conn_e:
                self.log(f"LLM connection error: {conn_e}")
                raise
            
            response_text = message.content[0].text
            # Extract JSON from response
            try:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    plan = json.loads(json_match.group())
                    actions = plan.get("actions", [])
                    reasoning = plan.get("reasoning", "")
                    self.log(f"LLM Decision: {reasoning}")
                    self.log(f"LLM Actions: {', '.join(actions) if actions else 'none'}")
                else:
                    self.log("Could not parse LLM response, falling back to heuristics")
                    return self._heuristic_plan(force)
            except json.JSONDecodeError:
                self.log("Failed to parse LLM JSON, falling back to heuristics")
                return self._heuristic_plan(force)
            
            # Execute the planned actions
            for action in actions:
                if hasattr(self, action):
                    self.run_action(action, force=force)
                else:
                    self.log(f"Skipping unknown action: {action}")
            
            # Always summarize at the end
            if "summarize_insights" not in actions:
                self.log("LLM Plan: appending summarize_insights")
                self.run_action("summarize_insights", force=force)
            
            # Auto-run Round 1 debate (initial positions) for display
            if self.llm_client and "debate_round_1" not in self.knowledge:
                self.log("🎯 Auto-generating Round 1 debate positions...")
                self._debate_round_1_initial_positions()
            
            self.log("🤖 LLM-based planning finished.")
            return "LLM agentic plan executed."
            
        except Exception as e:
            self.log(f"LLM planning failed: {str(e)}. Falling back to heuristics.")
            return self._heuristic_plan(force)
    
    def _get_knowledge_state_summary(self):
        """Summarize what knowledge the agent currently has."""
        summary = []
        if "mortgage_rates" in self.knowledge:
            df = self.knowledge["mortgage_rates"]
            summary.append(f"- Mortgage rates: {len(df)} data points, latest: {df.iloc[-1]['rate']:.2f}%")
            last_fetch = self.last_fetch_dates.get("mortgage_rates", "never")
            summary.append(f"  Last fetched: {last_fetch}")
        else:
            summary.append("- Mortgage rates: NOT LOADED")
        
        if "rate_insights" in self.knowledge:
            insights = self.knowledge["rate_insights"]
            summary.append(f"- Rate insights: {insights.get('trend_signal')} (12mo avg: {insights.get('12_month_avg')}%)")
        else:
            summary.append("- Rate insights: NOT ANALYZED")
        
        if "home_prices" in self.knowledge:
            df = self.knowledge["home_prices"]
            summary.append(f"- Home prices: {len(df)} data points, latest: {df.iloc[-1]['price']:.1f}")
            last_fetch = self.last_fetch_dates.get("home_prices", "never")
            summary.append(f"  Last fetched: {last_fetch}")
        else:
            summary.append("- Home prices: NOT LOADED")
        
        if "comparison" in self.knowledge:
            summary.append(f"- Comparison: {self.knowledge['comparison']}")
        else:
            summary.append("- Comparison: NOT DONE")
        
        return "\n".join(summary)
    
    def _heuristic_plan(self, force=False):
        """Original heuristic-based planning logic."""

        # 1️⃣ Mortgage rates
        fetch_rates = False
        if "mortgage_rates" not in self.knowledge:
            fetch_rates = True
            self.log("Mortgage rates missing → will fetch.")
        elif force:
            fetch_rates = True
            self.log("Force refresh → fetching mortgage rates.")
        else:
            last_fetch = self.last_fetch_dates.get("mortgage_rates", datetime.min)
            if datetime.now() - last_fetch > timedelta(days=1):
                fetch_rates = True
                self.log("Mortgage rates >1 day old → will fetch.")
            else:
                self.log("Mortgage rates up-to-date → skipping fetch.")

        if fetch_rates:
            self.run_action("fetch_mortgage_rates", force=force)
            self.last_fetch_dates["mortgage_rates"] = datetime.now()

        # 2️⃣ Analyze rates
        analyze = False
        if "rate_insights" not in self.knowledge:
            analyze = True
        elif force:
            analyze = True
        elif fetch_rates:
            analyze = True  # only analyze if rates updated
        if analyze:
            self.run_action("analyze_rates", force=force)
        else:
            self.log("Rates already analyzed → skipping.")

        # 3️⃣ Home prices
        fetch_prices = False
        if "home_prices" not in self.knowledge:
            fetch_prices = True
            self.log("Home prices missing → will fetch.")
        elif force:
            fetch_prices = True
            self.log("Force refresh → fetching home prices.")
        elif fetch_rates:
            # Only fetch if rates changed significantly
            latest = self.knowledge.get("rate_insights", {}).get("latest_rate", None)
            prior = self.knowledge.get("rate_insights", {}).get("prior_rate", None)
            if latest is not None and prior is not None and abs(latest - prior) > 0.25:
                fetch_prices = True
                self.log("Mortgage rate changed >0.25% → fetching home prices.")
        if fetch_prices:
            self.run_action("fetch_home_prices", force=force)
            self.last_fetch_dates["home_prices"] = datetime.now()
        else:
            self.log("Home prices up-to-date → skipping fetch.")

        # 4️⃣ Compare with home prices
        compare = False
        if "comparison" not in self.knowledge:
            compare = True
        elif force:
            compare = True
        elif fetch_prices or fetch_rates:
            compare = True
        if compare:
            self.run_action("compare_with_home_prices", force=force)
        else:
            self.log("Comparison already done → skipping.")

        # 5️⃣ Summarize
        self.run_action("summarize_insights", force=force)

        self.log("🤖 Agentic planning finished.")
        return "Agentic plan executed."

    # ---------- Core actions ----------
    def fetch_mortgage_rates(self, force=False):
        if "mortgage_rates" in self.knowledge and not force:
            return "Mortgage rates already loaded."
        self.log("⚙️ System: Fetching mortgage rates from FRED API...")
        try:
            url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
            df.columns = df.columns.str.strip()
            df = df.rename(columns={"observation_date": "date", "MORTGAGE30US": "rate"})
            df["date"] = pd.to_datetime(df["date"])
            df["rate"] = pd.to_numeric(df["rate"], errors="coerce")
            self.knowledge["mortgage_rates"] = df.dropna()
            # Track fetch timestamp
            if "fetch_timestamps" not in self.knowledge:
                self.knowledge["fetch_timestamps"] = {}
            self.knowledge["fetch_timestamps"]["mortgage_rates"] = pd.Timestamp.now()
            return "Mortgage rates fetched."
        except Exception as e:
            self.log(f"⚠️ Failed to fetch mortgage rates: {e}")
            # Return cached data if available, otherwise use empty dataframe
            if "mortgage_rates" not in self.knowledge:
                self.knowledge["mortgage_rates"] = pd.DataFrame(columns=["date", "rate"])
            return f"Failed to fetch rates (using cache): {str(e)}"

    def analyze_rates(self, force=False):
        if "mortgage_rates" not in self.knowledge or force:
            self.fetch_mortgage_rates(force=force)
        self.log("⚙️ System: Analyzing mortgage rate trends...")
        df = self.knowledge["mortgage_rates"].sort_values("date")
        
        # Check if we have enough data
        if df.empty or len(df) < 2:
            self.log("⚠️ Insufficient mortgage rate data. Using placeholder insights.")
            self.knowledge["rate_insights"] = {
                "latest_rate": 6.5,
                "prior_rate": 6.5,
                "12_month_avg": 6.5,
                "trend_signal": "Insufficient Data",
            }
            return "Mortgage rates analyzed (insufficient data)."
        
        latest = df.iloc[-1]
        prior = df.iloc[-2]
        avg_12 = df.tail(52)["rate"].mean()
        insights = {
            "latest_rate": round(latest["rate"], 2),
            "prior_rate": round(prior["rate"], 2),
            "12_month_avg": round(avg_12, 2),
            "trend_signal": "Rates Elevated" if latest["rate"] > avg_12 else "Rates Cooling",
        }
        self.knowledge["rate_insights"] = insights
        return "Mortgage rates analyzed."

    def fetch_home_prices(self, force=False):
        if "home_prices" in self.knowledge and not force:
            return "Home prices already loaded."
        self.log("⚙️ System: Fetching home price data from FRED API...")
        try:
            url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CSUSHPINSA"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
            df.columns = df.columns.str.strip()
            df = df.rename(columns={df.columns[0]: "date", df.columns[1]: "price"})
            df["date"] = pd.to_datetime(df["date"])
            df["price"] = pd.to_numeric(df["price"], errors="coerce")
            self.knowledge["home_prices"] = df.dropna()
            # Track fetch timestamp
            if "fetch_timestamps" not in self.knowledge:
                self.knowledge["fetch_timestamps"] = {}
            self.knowledge["fetch_timestamps"]["home_prices"] = pd.Timestamp.now()
            return "Home prices fetched."
        except Exception as e:
            self.log(f"⚠️ Failed to fetch home prices: {e}")
            # Return cached data if available, otherwise use empty dataframe
            if "home_prices" not in self.knowledge:
                self.knowledge["home_prices"] = pd.DataFrame(columns=["date", "price"])
            return f"Failed to fetch prices (using cache): {str(e)}"

    def compare_with_home_prices(self, force=False):
        if "mortgage_rates" not in self.knowledge or force:
            self.fetch_mortgage_rates(force=force)
        if "home_prices" not in self.knowledge or force:
            self.fetch_home_prices(force=force)
        self.log("⚙️ System: Correlating rates with home price trends...")
        m = self.knowledge["mortgage_rates"].sort_values("date")
        h = self.knowledge["home_prices"].sort_values("date")
        
        # Check if we have enough data
        if m.empty or h.empty:
            self.log("⚠️ Insufficient data for price correlation. Using placeholder.")
            self.knowledge["comparison"] = "Home prices data unavailable."
            return "Compared mortgage rates with home prices (insufficient data)."
        
        merged = pd.merge_asof(m, h, on="date")
        if merged.empty:
            self.log("⚠️ No matching dates for correlation. Using placeholder.")
            self.knowledge["comparison"] = "Home prices data unavailable."
            return "Compared mortgage rates with home prices (no matching data)."
        
        latest = merged.iloc[-1]
        year_ago_date = latest['date'] - pd.DateOffset(years=1)
        year_ago = merged.iloc[(merged['date'] - year_ago_date).abs().argsort()[0]]
        trend = "rising" if latest["price"] > year_ago["price"] else "falling"
        self.knowledge["comparison"] = (
            f"Home prices are {trend} year-over-year "
            f"(latest index: {round(latest['price'], 1)})."
        )
        return "Compared mortgage rates with home prices."

    def summarize_insights(self, force=False):
        if "rate_insights" not in self.knowledge or force:
            self.analyze_rates(force=force)
        if "comparison" not in self.knowledge or force:
            self.compare_with_home_prices(force=force)
        
        # Use LLM for insights if available, otherwise use simple summary
        if self.llm_client:
            summary = self._llm_based_insights()
        else:
            summary = self._simple_summary()

        if "role_insights" not in self.knowledge or force:
            if self.llm_client:
                self._llm_role_insights()
            else:
                self._simple_role_insights()

        return summary
    
    def _simple_summary(self):
        """Generate basic summary from data."""
        i = self.knowledge["rate_insights"]
        summary = (
            f"Current 30Y rate: {i['latest_rate']}% "
            f"(12-mo avg: {i['12_month_avg']}%).\n"
            f"Trend: {i['trend_signal']}.\n\n"
            f"{self.knowledge['comparison']}"
        )
        self.knowledge["summary"] = summary
        self.log("Insights summarized.")
        return summary
    
    def _llm_based_insights(self):
        """Use Claude to generate sophisticated insights from mortgage and housing data."""
        self.log("⚙️ System: Generating market insights with Claude...")
        try:
            # Gather all available data for analysis
            rate_insights = self.knowledge.get("rate_insights", {})
            comparison = self.knowledge.get("comparison", "No price comparison available")
            
            # Get recent rate trends
            if "mortgage_rates" in self.knowledge:
                df_rates = self.knowledge["mortgage_rates"].sort_values("date")
                recent_rates = df_rates.tail(10)
                rate_trend = "stable" if recent_rates["rate"].std() < 0.1 else "volatile"
                rate_direction = "rising" if df_rates.iloc[-1]["rate"] > df_rates.iloc[-10]["rate"] else "falling"
            else:
                rate_trend = "unknown"
                rate_direction = "unknown"
            
            prompt = f"""You are a mortgage market analyst. Analyze the following data and provide actionable insights:

## Mortgage Rate Data:
- Current 30-year rate: {rate_insights.get('latest_rate', 'N/A')}%
- 12-month average: {rate_insights.get('12_month_avg', 'N/A')}%
- Trend signal: {rate_insights.get('trend_signal', 'N/A')}
- Recent trend: {rate_direction} ({rate_trend})

## Housing Market Data:
- {comparison}

Based on this data, provide:
1. A brief assessment of the current mortgage market (2-3 sentences)
2. What this means for homebuyers (1-2 sentences)
3. One key insight or recommendation (1-2 sentences)

Keep the response concise and actionable."""

            message = self.llm_client.messages.create(
                model=config.MODEL_NAME,
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )
            self.session_cost += 0.003  # Approximate cost for insights call
            
            summary = message.content[0].text
            self.knowledge["summary"] = summary
            self.log("LLM-based insights generated.")
            return summary
            
        except Exception as e:
            self.log(f"LLM insights generation failed: {str(e)}. Using simple summary.")
            return self._simple_summary()

    def _simple_role_insights(self):
        """Generate basic role-based perspectives without an LLM."""
        rate_insights = self.knowledge.get("rate_insights", {})
        comparison = self.knowledge.get("comparison", "No price comparison available")
        summary = self.knowledge.get("summary", "No summary available")

        roles = {
            "Planner": (
                "Prioritize actions based on data freshness and impact. "
                "Refresh rates if stale; re-check prices if rates moved >0.25%."
            ),
            "Market Analyst": (
                f"Current rate {rate_insights.get('latest_rate', 'N/A')}% vs 12-mo avg "
                f"{rate_insights.get('12_month_avg', 'N/A')}%. {comparison}"
            ),
            "Risk Officer": (
                "Watch for rapid rate shifts and affordability risk. "
                "Validate data recency before decisions."
            ),
        }

        self.knowledge["role_insights"] = roles
        self.log("Role perspectives generated (heuristic).")

    def generate_role_perspectives(self, force=False):
        """Public action to generate multi-agent role perspectives."""
        if not force and "role_insights" in self.knowledge:
            return "Multi-agent perspectives already generated."
        
        if self.llm_client is None:
            return "LLM client not available. Cannot generate role perspectives."
        
        self._llm_role_insights()
        return "Multi-agent perspectives generated successfully."

    def _llm_role_insights(self):
        """Generate role-based perspectives using Claude."""
        self.log("⚙️ System: Generating 3-agent debate perspectives...")
        rate_insights = self.knowledge.get("rate_insights", {})
        comparison = self.knowledge.get("comparison", "No price comparison available")
        summary = self.knowledge.get("summary", "No summary available")

        role_prompts = {
            "Planner": "You are an agent planner. Focus on action selection and sequencing.",
            "Market Analyst": "You are a mortgage market analyst. Focus on data interpretation.",
            "Risk Officer": "You are a risk officer. Focus on risk signals and guardrails.",
        }

        role_emojis = {
            "Planner": "📊",
            "Market Analyst": "📉",
            "Risk Officer": "🛡️"
        }

        role_outputs = {}
        for role, role_prompt in role_prompts.items():
            self.log(f"{role_emojis[role]} {role}: Analyzing data and generating perspective...")
            
            prompt = f"""{role_prompt}

Context:
- Summary: {summary}
- Current 30-year rate: {rate_insights.get('latest_rate', 'N/A')}%
- 12-month average: {rate_insights.get('12_month_avg', 'N/A')}%
- Trend signal: {rate_insights.get('trend_signal', 'N/A')}
- Housing: {comparison}

Provide 2-3 concise bullet points for your perspective."""

            message = self.llm_client.messages.create(
                model=config.MODEL_NAME,
                max_tokens=250,
                messages=[{"role": "user", "content": prompt}]
            )
            self.session_cost += 0.002  # Approximate cost per role perspective
            role_outputs[role] = message.content[0].text.strip()

        self.knowledge["role_insights"] = role_outputs

    # ---------- Multi-Round Debate System ----------
    
    def run_agent_debate(self, force=False):
        """
        Execute a full 3-round agent debate with cross-examination and consensus.
        This is the main entry point for the debate system.
        """
        if not force and "debate_results" in self.knowledge:
            return "Agent debate already completed."
        
        if self.llm_client is None:
            return "LLM client not available. Cannot run agent debate."
        
        self.log("🎯 Starting Multi-Round Agent Debate System...")
        
        # Ensure we have data to debate about
        if "rate_insights" not in self.knowledge:
            self.analyze_rates()
        if "comparison" not in self.knowledge:
            self.compare_with_home_prices()
        
        # Round 1: Initial Positions
        self._debate_round_1_initial_positions()
        
        # Round 2: Cross-Examination
        self._debate_round_2_cross_examination()
        
        # Round 3: Consensus Voting
        self._debate_round_3_consensus()
        
        self.log("✅ Multi-round debate completed successfully!")
        return "Agent debate completed with consensus reached."
    
    def continue_debate(self, force=False):
        """
        Continue debate from Round 1 to Rounds 2 & 3.
        Assumes Round 1 is already completed.
        """
        if not force and "debate_results" in self.knowledge:
            return "Agent debate already completed."
        
        if self.llm_client is None:
            return "LLM client not available. Cannot continue debate."
        
        if "debate_round_1" not in self.knowledge:
            self.log("ERROR: Round 1 not found. Run Agentic Plan first.")
            return "Round 1 positions not found. Cannot continue debate."
        
        self.log("🎯 Continuing Agent Debate (Rounds 2 & 3)...")
        
        # Round 2: Cross-Examination
        self._debate_round_2_cross_examination()
        
        # Round 3: Consensus Voting
        self._debate_round_3_consensus()
        
        self.log("✅ Multi-round debate completed successfully!")
        return "Agent debate completed with consensus reached."
    
    def _debate_round_1_initial_positions(self):
        """Round 1: Each agent presents their initial position."""
        self.log("📋 Round 1: Initial Positions")

        # Reset downstream rounds when starting a new debate cycle.
        for key in ("debate_round_2", "debate_round_3", "debate_results"):
            if key in self.knowledge:
                del self.knowledge[key]
        
        rate_insights = self.knowledge.get("rate_insights", {})
        comparison = self.knowledge.get("comparison", "No comparison available")
        summary = self.knowledge.get("summary", "Basic market summary")
        
        # Get learned patterns from previous validated debates
        learned_patterns = ""
        if self.debate_db:
            learned_patterns = self.debate_db.get_patterns_summary_for_agents()
        
        roles = {
            "Planner": {
                "emoji": "📊",
                "prompt": "You are a strategic planner analyzing mortgage market data. Focus on actionable insights and decision-making frameworks."
            },
            "Market Analyst": {
                "emoji": "📉", 
                "prompt": "You are a mortgage market analyst. Focus on trend analysis, historical context, and data interpretation."
            },
            "Risk Officer": {
                "emoji": "🛡️",
                "prompt": "You are a risk management officer. Focus on identifying risks, vulnerabilities, and protective measures."
            }
        }
        
        debate_positions = {}
        
        for role_name, role_config in roles.items():
            self.log(f"{role_config['emoji']} {role_name}: Formulating initial position...")
            
            prompt = f"""{role_config['prompt']}{learned_patterns}

Market Context:
- Current 30-year mortgage rate: {rate_insights.get('latest_rate', 'N/A')}%
- 12-month average rate: {rate_insights.get('12_month_avg', 'N/A')}%
- Trend signal: {rate_insights.get('trend_signal', 'N/A')}
- Housing market: {comparison}
- Overall summary: {summary}

Task: Provide your initial market position in 3-4 bullet points. Be specific about whether you lean BULLISH (rates will fall), BEARISH (rates will rise/stay high), or NEUTRAL. Include your confidence level (0-100%)."""

            message = self.llm_client.messages.create(
                model=config.MODEL_NAME,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            self.session_cost += 0.003
            
            position_text = message.content[0].text.strip()
            
            # Extract confidence if mentioned (simple parsing)
            confidence = 70.0  # default
            if "confidence" in position_text.lower():
                import re
                conf_match = re.search(r'(\d+)%?\s*confidence', position_text.lower())
                if conf_match:
                    confidence = float(conf_match.group(1))
            
            debate_positions[role_name] = {
                "round": 1,
                "position": position_text,
                "confidence": confidence,
                "emoji": role_config['emoji']
            }
        
        self.knowledge["debate_round_1"] = debate_positions
        self.log("✓ Round 1 complete: All initial positions recorded")
    
    def _debate_round_2_cross_examination(self):
        """Round 2: Each agent reviews others' positions and responds with challenges/support."""
        self.log("🔍 Round 2: Cross-Examination & Challenges")
        
        round_1_positions = self.knowledge.get("debate_round_1", {})
        if not round_1_positions:
            self.log("ERROR: Round 1 not completed. Cannot proceed to Round 2.")
            return
        
        # Get learned patterns from previous validated debates
        learned_patterns = ""
        if self.debate_db:
            learned_patterns = self.debate_db.get_patterns_summary_for_agents()
        
        round_2_responses = {}
        
        for role_name, agent_data in round_1_positions.items():
            # Get the other agents' positions
            other_positions = {k: v for k, v in round_1_positions.items() if k != role_name}
            
            other_positions_text = "\n\n".join([
                f"**{name}** {data['emoji']}:\n{data['position']}"
                for name, data in other_positions.items()
            ])
            
            self.log(f"{agent_data['emoji']} {role_name}: Reviewing peer positions and responding...")
            
            prompt = f"""You are the {role_name}. You previously stated:

YOUR POSITION:
{agent_data['position']}{learned_patterns}

Now you have seen the positions from your peer agents:

PEER POSITIONS:
{other_positions_text}

Task: 
1. Identify ONE specific point from the peer positions that you either:
   - CHALLENGE (provide counter-evidence or alternative interpretation)
   - SUPPORT (reinforce with additional reasoning)

2. After reviewing peer arguments, do you want to revise your stance or confidence level?

Provide 2-3 bullet points. Be specific about which agent you're addressing."""

            message = self.llm_client.messages.create(
                model=config.MODEL_NAME,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            self.session_cost += 0.003
            
            response_text = message.content[0].text.strip()
            
            round_2_responses[role_name] = {
                "round": 2,
                "original_position": agent_data['position'],
                "cross_examination": response_text,
                "emoji": agent_data['emoji']
            }
        
        self.knowledge["debate_round_2"] = round_2_responses
        self.log("✓ Round 2 complete: All cross-examinations recorded")
    
    def _debate_round_3_consensus(self):
        """Round 3: Each agent votes with final confidence and we build consensus."""
        self.log("🤝 Round 3: Consensus Building & Final Vote")
        
        round_1 = self.knowledge.get("debate_round_1", {})
        round_2 = self.knowledge.get("debate_round_2", {})
        
        if not round_1 or not round_2:
            self.log("ERROR: Previous rounds not completed. Cannot proceed to Round 3.")
            return
        
        # Get learned patterns from previous validated debates
        learned_patterns = ""
        if self.debate_db:
            learned_patterns = self.debate_db.get_patterns_summary_for_agents()
        
        final_votes = {}
        vote_stances = []
        
        for role_name in round_1.keys():
            agent_r1 = round_1[role_name]
            agent_r2 = round_2.get(role_name, {})
            
            self.log(f"{agent_r1['emoji']} {role_name}: Casting final vote...")
            
            prompt = f"""You are the {role_name}. Review your debate history:{learned_patterns}

ROUND 1 - Your Initial Position:
{agent_r1['position']}

ROUND 2 - Your Cross-Examination Response:
{agent_r2.get('cross_examination', 'N/A')}

Task: Cast your FINAL VOTE on the mortgage rate outlook:
1. Choose: BULLISH (rates falling), BEARISH (rates rising/high), or NEUTRAL
2. Provide final confidence level (0-100%)
3. Give 1-2 sentences justifying your vote

Format your response as:
VOTE: [BULLISH/BEARISH/NEUTRAL]
CONFIDENCE: [0-100]%
REASONING: [your justification]"""

            message = self.llm_client.messages.create(
                model=config.MODEL_NAME,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            self.session_cost += 0.002
            
            vote_text = message.content[0].text.strip()
            
            # Parse vote
            stance = "NEUTRAL"
            confidence = 50.0
            
            if "BULLISH" in vote_text.upper():
                stance = "BULLISH"
            elif "BEARISH" in vote_text.upper():
                stance = "BEARISH"
            
            import re
            conf_match = re.search(r'CONFIDENCE:\s*(\d+)', vote_text, re.IGNORECASE)
            if conf_match:
                confidence = float(conf_match.group(1))
            
            final_votes[role_name] = {
                "round": 3,
                "stance": stance,
                "confidence": confidence,
                "reasoning": vote_text,
                "emoji": agent_r1['emoji']
            }
            
            vote_stances.append(stance)
        
        # Calculate consensus
        from collections import Counter
        vote_counts = Counter(vote_stances)
        majority_vote = vote_counts.most_common(1)[0][0]
        consensus_score = (vote_counts[majority_vote] / len(vote_stances)) * 100
        
        # Compute average confidence
        avg_confidence = sum(v['confidence'] for v in final_votes.values()) / len(final_votes)
        
        # Generate final recommendation
        final_recommendation = f"{majority_vote} (Consensus: {consensus_score:.0f}%, Avg Confidence: {avg_confidence:.0f}%)"
        
        self.knowledge["debate_round_3"] = final_votes
        self.knowledge["debate_results"] = {
            "final_recommendation": final_recommendation,
            "consensus_score": consensus_score,
            "avg_confidence": avg_confidence,
            "majority_vote": majority_vote,
            "vote_breakdown": dict(vote_counts)
        }
        
        self.log(f"✅ Consensus reached: {final_recommendation}")
        self.log(f"   Vote breakdown: {dict(vote_counts)}")
    
    def save_debate_to_database(self, db):
        """Save the completed debate to the historical database."""
        from database import DebateDatabase
        
        if "debate_results" not in self.knowledge:
            self.log("No debate results to save.")
            return
        
        debate_results = self.knowledge["debate_results"]
        
        # Collect all agent positions across rounds
        agent_positions = []
        
        for round_num in [1, 2, 3]:
            round_key = f"debate_round_{round_num}"
            round_data = self.knowledge.get(round_key, {})
            
            for role_name, data in round_data.items():
                if round_num == 1:
                    position_record = {
                        "agent_role": role_name,
                        "round_number": 1,
                        "position": data.get('position'),
                        "confidence": data.get('confidence'),
                        "reasoning": data.get('position'),
                        "challenges": None,
                        "responses": None
                    }
                elif round_num == 2:
                    position_record = {
                        "agent_role": role_name,
                        "round_number": 2,
                        "position": "Cross-Examination",
                        "confidence": None,
                        "reasoning": data.get('cross_examination'),
                        "challenges": data.get('cross_examination'),
                        "responses": None
                    }
                else:  # round 3
                    position_record = {
                        "agent_role": role_name,
                        "round_number": 3,
                        "position": data.get('stance'),
                        "confidence": data.get('confidence'),
                        "reasoning": data.get('reasoning'),
                        "challenges": None,
                        "responses": None
                    }
                
                agent_positions.append(position_record)
        
        # Collect market snapshot
        rate_insights = self.knowledge.get("rate_insights", {})
        home_prices = self.knowledge.get("home_prices")
        
        latest_price = None
        price_yoy = None
        if home_prices is not None and len(home_prices) > 0:
            latest_price = float(home_prices.iloc[-1]['price'])
            if len(home_prices) > 12:
                year_ago_price = float(home_prices.iloc[-13]['price'])
                price_yoy = ((latest_price - year_ago_price) / year_ago_price) * 100
        
        market_snapshot = {
            "mortgage_rate": rate_insights.get('latest_rate'),
            "home_price_index": latest_price,
            "rate_12mo_avg": rate_insights.get('12_month_avg'),
            "price_yoy_change": price_yoy
        }
        
        # Save to database
        debate_id = db.save_debate(
            final_recommendation=debate_results['final_recommendation'],
            consensus_score=debate_results['consensus_score'],
            session_cost=self.session_cost,
            agent_positions=agent_positions,
            market_snapshot=market_snapshot
        )
        
        self.knowledge["last_saved_debate_id"] = debate_id
        self.log(f"💾 Debate saved to database with ID: {debate_id}")
        
        return debate_id
