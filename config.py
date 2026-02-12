import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL_NAME = "claude-3-5-sonnet-20241022"

# Agent Configuration
CACHE_VALIDITY_HOURS = 24
RATE_CHANGE_THRESHOLD = 0.25  # percentage point
ENABLE_LLM_PLANNING = bool(ANTHROPIC_API_KEY)  # Only enable if API key is set

# Streamlit Configuration
STREAMLIT_PAGE_TITLE = "Agentic Mortgage Research"
STREAMLIT_LAYOUT = "wide"
