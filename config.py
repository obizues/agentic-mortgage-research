import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Try to get API key from Streamlit secrets first (for deployed apps)
# then fall back to environment variables (for local development)
try:
    import streamlit as st
    ANTHROPIC_API_KEY = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))
except (ImportError, AttributeError):
    # If not in Streamlit context, just use environment variables
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

MODEL_NAME = "claude-3-haiku-20240307"

# Agent Configuration
CACHE_VALIDITY_HOURS = 24
RATE_CHANGE_THRESHOLD = 0.25  # percentage point
ENABLE_LLM_PLANNING = bool(ANTHROPIC_API_KEY)  # Only enable if API key is set

# Streamlit Configuration
STREAMLIT_PAGE_TITLE = "Agentic Mortgage Research"
STREAMLIT_LAYOUT = "wide"
