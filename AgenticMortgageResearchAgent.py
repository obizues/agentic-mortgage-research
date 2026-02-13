import pandas as pd
import config
import requests
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
    def __init__(self, log_callback=None, llm_client: Optional['Anthropic'] = None):
        self.goal = "Understand current US mortgage rate trends and risks"
        self.knowledge = {}
        self.logs = []
        self.log_callback = log_callback
        self.last_fetch_dates = {}  # track when data was fetched
        self.llm_client = llm_client  # Optional Claude client for LLM-based reasoning

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
        url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        df.columns = df.columns.str.strip()
        df = df.rename(columns={"observation_date": "date", "MORTGAGE30US": "rate"})
        df["date"] = pd.to_datetime(df["date"])
        df["rate"] = pd.to_numeric(df["rate"], errors="coerce")
        self.knowledge["mortgage_rates"] = df.dropna()
        return "Mortgage rates fetched."

    def analyze_rates(self, force=False):
        if "mortgage_rates" not in self.knowledge or force:
            self.fetch_mortgage_rates(force=force)
        df = self.knowledge["mortgage_rates"].sort_values("date")
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
        url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CSUSHPINSA"
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        df.columns = df.columns.str.strip()
        df = df.rename(columns={df.columns[0]: "date", df.columns[1]: "price"})
        df["date"] = pd.to_datetime(df["date"])
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        self.knowledge["home_prices"] = df.dropna()
        return "Home prices fetched."

    def compare_with_home_prices(self, force=False):
        if "mortgage_rates" not in self.knowledge or force:
            self.fetch_mortgage_rates(force=force)
        if "home_prices" not in self.knowledge or force:
            self.fetch_home_prices(force=force)
        m = self.knowledge["mortgage_rates"].sort_values("date")
        h = self.knowledge["home_prices"].sort_values("date")
        merged = pd.merge_asof(m, h, on="date")
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
            return self._llm_based_insights()
        else:
            return self._simple_summary()
    
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
            
            summary = message.content[0].text
            self.knowledge["summary"] = summary
            self.log("LLM-based insights generated.")
            return summary
            
        except Exception as e:
            self.log(f"LLM insights generation failed: {str(e)}. Using simple summary.")
            return self._simple_summary()
