import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Try to get API key from Streamlit secrets first (for deployed apps),
# then fall back to environment variables (for local development).
try:
    import streamlit as st
    from streamlit.errors import StreamlitSecretNotFoundError

    try:
        secrets_value = st.secrets.get("ANTHROPIC_API_KEY")
    except StreamlitSecretNotFoundError:
        secrets_value = None

    ANTHROPIC_API_KEY = secrets_value or os.getenv("ANTHROPIC_API_KEY")

    try:
        fred_secrets_value = st.secrets.get("FRED_API_KEY")
    except StreamlitSecretNotFoundError:
        fred_secrets_value = None

    FRED_API_KEY = fred_secrets_value or os.getenv("FRED_API_KEY")
except (ImportError, AttributeError):
    # If not in Streamlit context, just use environment variables.
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    FRED_API_KEY = os.getenv("FRED_API_KEY")

MODEL_NAME = "claude-3-haiku-20240307"

# Agent Configuration
CACHE_VALIDITY_HOURS = 24
RATE_CHANGE_THRESHOLD = 0.25  # percentage point

# Local cost guardrails
RUNNING_IN_CLOUD = os.getenv("STREAMLIT_CLOUD", "").lower() == "true"
ALLOW_LLM_LOCAL = os.getenv("ALLOW_LLM_LOCAL", "0") == "1"
ENABLE_LLM_PLANNING = bool(ANTHROPIC_API_KEY) and (RUNNING_IN_CLOUD or ALLOW_LLM_LOCAL)

# LLM usage limits (per session)
LLM_MAX_CALLS_PER_SESSION = int(os.getenv("LLM_MAX_CALLS_PER_SESSION", "8"))
LLM_COOLDOWN_SECONDS = int(os.getenv("LLM_COOLDOWN_SECONDS", "45"))

# Streamlit Configuration
STREAMLIT_PAGE_TITLE = "Agentic Mortgage Research"
STREAMLIT_LAYOUT = "wide"
