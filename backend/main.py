import truststore
truststore.inject_into_ssl()

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from app.routers import documents, chat

# Locate the .env file at the parent workspace root
root_dir = Path(__file__).resolve().parent.parent
env_path = root_dir / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded environment variables from: {env_path}")
else:
    print(f"Warning: .env file not found at {env_path}")

app = FastAPI(title="AI-ChatBot API", docs_url="/api/docs", openapi_url="/openapi.json")

# Include Modular Routers
app.include_router(documents.router)
app.include_router(chat.router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}