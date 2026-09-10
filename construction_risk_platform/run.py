import os
import sys
import uvicorn
import webbrowser
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.seed_data import seed_database

def main():
    print("=" * 70)
    print(" 🏗️  AGENTIC CONSTRUCTION RISK INTELLIGENCE PLATFORM & HUB")
    print("=" * 70)
    print("Initializing Database & Seeding 15 Domain Entities...")
    seed_database()

    port = 8000
    host = "127.0.0.1"
    url = f"http://{host}:{port}"

    print(f"\n🚀 Server starting on: {url}")
    print("Press Ctrl+C to stop the server.\n")

    # Automatically open web browser
    try:
        webbrowser.open(url)
    except Exception:
        pass

    # Run FastAPI app via Uvicorn
    uvicorn.run("backend.main:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    main()
