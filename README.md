# Enterprise RAG Chatbot 🤖

A production-ready, containerized Retrieval-Augmented Generation (RAG) application. This system allows users to upload documents and query them securely, utilizing a graph-based state machine to guarantee hallucination-free answers with exact source citations.

## 🏗️ Architecture & Tech Stack

This project is decoupled into microservices and orchestrated via **Docker Compose**:

*   **Frontend (Streamlit):** A dynamic UI for document uploads, chat interactions, and real-time LLM provider switching.
*   **Backend API (FastAPI):** An asynchronous REST gateway handling file streaming, chunking, and routing.
*   **AI Orchestration (LangGraph):** A 9-node state machine that manages query validation, dynamic API routing, fallback mechanisms, and citation formatting.
*   **Memory & State (SQLite & ChromaDB):** Persistent local conversational memory and vector storage, mapped to Docker volumes to survive container restarts.
*   **Infrastructure (Docker):** Fully containerized environments ensuring seamless deployment across any OS.

## 🚀 Key Engineering Features

*   **Hot-Swappable LLMs:** Implements a Factory pattern to switch dynamically between Google Gemini and NVIDIA NIM without system reboots.
*   **Enterprise Network Resilience:** Engineered to function behind strict corporate firewalls by overriding SSL certificate injections using native Python `truststore` integrations.
*   **Infrastructure as Code:** A single `docker-compose.yml` manages private internal networking, port mapping, and volume persistence for both the frontend and backend containers.

## 💻 How to Run (Docker)

1. Clone the repository.
2. Create a `.env` file in the root directory:
   ```env
   LLM_PROVIDER=gemini
   
   GEMINI_API_KEY=your_key_here
   GEMINI_MODEL=gemini-2.0-flash

   NVIDIA_API_KEY=your_key_here

    PINECONE_API_KEY=your_key_here
    PINECONE_INDEX=chatbot-rag-index
    PINECONE_ENV=us-east-1
    PINECONE_NAMESPACE=default

    REDIS_URL=redis://localhost:6379

    MAX_UPLOAD_SIZE_MB=50
    RETRIEVAL_TOP_K=5
    CHUNK_SIZE=1000
    CHUNK_OVERLAP=150
    LLM_TEMPERATURE=0.3
    BACKEND_URL=http://localhost:8000
