import subprocess
import sys
import os
import time

def main():
    print("🤖 Starting AI-ChatBot Enterprise RAG...")

    # Automatically apply the HuggingFace corporate proxy bypass
    env = os.environ.copy()
    env["HF_HUB_OFFLINE"] = "1"

    try:
        # 1. Start the FastAPI Backend
        print("⏳ Booting Backend (FastAPI)...")
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--reload"], 
            cwd="backend", 
            env=env
        )

        # Give the backend a 3-second head start to boot up
        time.sleep(3)

        # 2. Start the Streamlit Frontend
        print("⏳ Booting Frontend (Streamlit)...")
        frontend_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "frontend\\app.py"]
        )

        # Keep the script running and listening to both processes
        backend_process.wait()
        frontend_process.wait()

    except KeyboardInterrupt:
        # If you press CTRL+C, it gracefully shuts down both servers at once
        print("\n🛑 Shutting down AI-ChatBot services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Shutdown complete.")

if __name__ == "__main__":
    main()