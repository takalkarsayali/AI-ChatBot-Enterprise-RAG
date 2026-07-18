import streamlit as st
import requests
import uuid

# --- CONFIGURATION ---
API_BASE_URL = "http://localhost:8000"
ALLOWED_EXTENSIONS = ["pdf", "docx", "txt", "md", "csv", "pptx"]
MAX_FILE_SIZE_MB = 50

st.set_page_config(page_title="AI-ChatBot RAG", page_icon="🤖", layout="wide")

# --- SESSION STATE ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR: SETTINGS & DOCUMENT MANAGEMENT ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    llm_provider = st.selectbox(
        "LLM Provider",
        options=["Gemini 2.x", "NVIDIA NIM"],
        help="Switching requires the respective API key in the backend .env"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        top_k = st.number_input("Retrieval Top-K", min_value=1, max_value=10, value=5)
    with col2:
        temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)

    st.divider()

    st.header("📄 Document Management")
    
    # Upload Module
    uploaded_files = st.file_uploader(
        "Upload Files", 
        type=ALLOWED_EXTENSIONS, 
        accept_multiple_files=True,
        help=f"Max size: {MAX_FILE_SIZE_MB}MB per file."
    )
    
    if st.button("Upload Documents", type="primary", use_container_width=True) and uploaded_files:
        with st.spinner("Uploading and processing..."):
            for uploaded_file in uploaded_files:
                # Validate size
                if uploaded_file.size > (MAX_FILE_SIZE_MB * 1024 * 1024):
                    st.error(f"{uploaded_file.name} exceeds {MAX_FILE_SIZE_MB}MB limit.")
                    continue
                    
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                try:
                    res = requests.post(f"{API_BASE_URL}/documents/upload", files=files)
                    if res.status_code == 200:
                        st.success(f"Uploaded: {uploaded_file.name}")
                    else:
                        st.error(f"Failed to upload {uploaded_file.name}: {res.text}")
                except Exception as e:
                    st.error(f"Upload error: {e}")

    # View and Delete Module
    with st.expander("Manage Uploaded Files"):
        if st.button("🔄 Refresh List"):
            try:
                res = requests.get(f"{API_BASE_URL}/documents")
                if res.status_code == 200:
                    docs = res.json()
                    if not docs:
                        st.info("No documents found.")
                    for doc in docs:
                        c1, c2 = st.columns([3, 1])
                        c1.text(doc.get("filename", "Unknown"))
                        if c2.button("🗑️", key=f"del_{doc.get('id')}"):
                            del_res = requests.delete(f"{API_BASE_URL}/documents/{doc.get('id')}")
                            if del_res.status_code == 200:
                                st.toast(f"Deleted {doc.get('filename')}")
                                st.rerun()
                else:
                    st.error("Could not fetch documents.")
            except Exception as e:
                st.error("Backend not reachable for documents API.")

    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# --- MAIN STAGE: CHAT INTERFACE ---
st.title("🤖 AI-ChatBot (Enterprise RAG)")
st.markdown("Retrieval-Augmented Generation powered by LangGraph & Pinecone.")

# Render History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("🔍 View Citations"):
                for idx, source in enumerate(message["sources"]):
                    st.markdown(f"**{idx+1}. {source.get('document_name', 'Unknown')}** (Score: {source.get('relevance_score', 0):.2f})")
                    st.caption(f"Section: {source.get('section', 'N/A')} | Page: {source.get('page_number', 'N/A')}")

# Chat Input
if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    payload = {
        "question": prompt,
        "session_id": st.session_state.session_id,
        "top_k": top_k,
        "temperature": temperature,
        "llm_provider": llm_provider.split(" ")[0].lower() # Sends 'gemini' or 'nvidia'
    }

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Analyzing documents and generating response..."):
            try:
                response = requests.post(f"{API_BASE_URL}/chat/query", json=payload)
                response.raise_for_status()
                data = response.json()
                
                answer = data.get("answer", "No answer generated.")
                sources = data.get("sources", [])
                
                message_placeholder.markdown(answer)
                
                if sources:
                    with st.expander("🔍 View Citations"):
                        for idx, source in enumerate(sources):
                            st.markdown(f"**{idx+1}. {source.get('document_name', 'Unknown')}** (Score: {source.get('relevance_score', 0):.2f})")
                            st.caption(f"Section: {source.get('section', 'N/A')} | Page: {source.get('page_number', 'N/A')}")
                            
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
                
            except requests.exceptions.ConnectionError:
                message_placeholder.error("Error: Could not connect to the backend. Is FastAPI running?")
            except requests.exceptions.RequestException as e:
                message_placeholder.error(f"API Error: {e}")