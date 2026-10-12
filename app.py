"""
DataDrishti Platform Entry Point
Run this file with: python app.py
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Backend.app import app

if __name__ == "__main__":
    print("=" * 60)
    print(" 📊 DataDrishti – AI-Powered Analytics Platform")
    print(" 🚀 Server running at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)