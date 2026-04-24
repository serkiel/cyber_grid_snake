import sys
import subprocess
import os

print("=== Cyber Arcade Analytics Setup ===")
print("1. Installing required data science libraries (this may take a moment)...")

# Force uses the exact Python interpreter VS Code is currently using
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

print("\n2. Generating mock telemetry data...")
# Import and run the mock data generator directly
try:
    import generate_mock_data
    generate_mock_data.generate_data()
except Exception as e:
    print(f"Mock data generation issue: {e}")

print("\n3. Launching Streamlit Dashboard! Your browser should open shortly...")
print("To stop the server later, just click the Stop/Trash icon in your IDE terminal.")

# Launch Streamlit from within Python so we bypass Windows PATH issues
from streamlit.web import cli as stcli
target_script = os.path.join(os.path.dirname(__file__), "dashboard.py")
sys.argv = ["streamlit", "run", target_script]

sys.exit(stcli.main())
