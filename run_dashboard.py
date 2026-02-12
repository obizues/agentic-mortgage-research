import subprocess
import sys

# Always use current Python to run Streamlit
subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
