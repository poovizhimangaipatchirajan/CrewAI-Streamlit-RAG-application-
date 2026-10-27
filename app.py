import streamlit as st
import os
import glob
from rag_engine import get_uploaded_files_metadata, save_and_index_file, FAISS_DIR
from crew_setup import run_knowly_crew

st.set_page_config(
    page_title="Knowly - Your Documents. Our Intelligence.",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling matching the screenshot
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background-color: #F8FAFC;
    }
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    .user-bubble {
        background-color: #EEF2FF;
        border-radius: 14px 14px 2px 14px;
        padding: 14px 18px;
        color: #1E293B;
        font-size: 14px;
        line-height: 1.5;
        margin-bottom: 12px;
        float: right;
        clear: both;
        max-width: 85%;
        border: 1px solid #E0E7FF;
    }
    .bot-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 16px;
        clear: both;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .section-title {
        font-size: 14px;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .badge-ready {
        display: inline-flex;
        align-items: center;
        background-color: #ECFDF5;
        color: #059669;
        font-size: 12px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 9999px;
    }
    .badge-ready::before {
        content: "";
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #10B981;
        margin-right: 6px;
    }
    .file-row {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 0;
        border-bottom: 1px solid #F1F5F9;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "current_page" not in st.session_state:
    st.session_state.current_page = "Chat"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "preset_query" not in st.session_state:
    st.session_state.preset_query = ""

# ----------------- LEFT SIDEBAR NAVIGATION -----------------
with st.sidebar:
    st.markdown("### 📖 **Knowly**")
    st.caption("Your Documents. Our Intelligence.")
    st.markdown("---")
    
    st.markdown("**Navigation**")
    if st.button("💬 Chat", use_container_width=True):
        st.session_state.current_page = "Chat"
    if st.button("🗄️ Knowledge Base", use_container_width=True):
        st.session_state.current_page = "Knowledge Base"
    if st.button("☁️ Upload Documents", use_container_width=True):
        st.session_state.current_page = "Upload Documents"
    if st.button("🕒 Chat History", use_container_width=True):
        st.session_state.current_page = "Chat History"
    if st.button("⚙️ Settings", use_container_width=True):
        st.session_state.current_page = "Settings"

    st.markdown("---")
    st.markdown("**Recent Logs**")
    log_files = sorted(glob.glob("outputs/*.txt"), reverse=True)[:5]
    if log_files:
        for log in log_files:
            fname = os.path.basename(log)
            st.caption(f"📄 {fname}")
    else:
        st.caption("No logs recorded yet.")

# ----------------- MAIN LAYOUT -----------------
col_center, col_right = st.columns([2.3, 1], gap="large")

with col_center:
    # 1. PAGE: CHAT
    if st.session_state.current_page == "Chat":
        header_col1, header_col2 = st.columns([3, 1])
        with header_col1:
            st.markdown("## **Hello there! 👋**")
            st.markdown("<p style='color:#64748B;'>I'm your RAG assistant. Ask me anything about your documents, or perform live web research.</p>", unsafe_allow_html=True)
        with header_col2:
            rag_status = "RAG Ready" if os.path.exists(FAISS_DIR) else "RAG Unindexed"
            st.markdown(f"<div style='text-align: right; padding-top: 15px;'><span class='badge-ready'>{rag_status}</span></div>", unsafe_allow_html=True)

        # Quick action triggers directly above chat
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("📄 Summarize docs", use_container_width=True):
            st.session_state.preset_query = "Provide a structured summary of the documents in the knowledge base."
        if c2.button("🔍 Key takeaways", use_container_width=True):
            st.session_state.preset_query = "Extract all critical takeaways and actionable items from the documents."
        if c3.button("⚖️ Compare policies", use_container_width=True):
            st.session_state.preset_query = "Compare the key policies and differences mentioned across the uploaded files."
        if c4.button("📋 Next steps", use_container_width=True):
            st.session_state.preset_query = "What are the recommended step-by-step guidance instructions?"

        # Display Chat History
        for msg in st.session_state.messages:
            st.markdown(f"<div class='user-bubble'><b>User Query:</b><br>{msg['query']}</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='bot-card'>
                <div class='section-title'>🤖 Assistant (FAISS RAG) Answer</div>
                <div>{msg['assistant']}</div>
                <hr style='border:0; border-top:1px solid #E2E8F0; margin:16px 0;'>
                <div class='section-title'>🌐 Web Search Answer</div>
                <div>{msg['web_search']}</div>
            </div>
            """, unsafe_allow_html=True)

        # Handle Chat Input (or Preset Query)
        input_query = st.chat_input("Type your question here...")
        active_query = input_query or st.session_state.preset_query

        if active_query:
            st.session_state.preset_query = ""
            st.markdown(f"<div class='user-bubble'><b>User Query:</b><br>{active_query}</div>", unsafe_allow_html=True)
            
            with st.spinner("Crew executing sequentially (Assistant ➔ Web Search ➔ Entry Agent Logger)..."):
                result = run_knowly_crew(active_query)
            
            # Save complete interaction to session state
            st.session_state.messages.append({
                "query": active_query,
                "assistant": result["assistant_answer"],
                "web_search": result["search_answer"]
            })
            
            st.markdown(f"""
            <div class='bot-card'>
                <div class='section-title'>🤖 Assistant (FAISS RAG) Answer</div>
                <div>{result['assistant_answer']}</div>
                <hr style='border:0; border-top:1px solid #E2E8F0; margin:16px 0;'>
                <div class='section-title'>🌐 Web Search Answer</div>
                <div>{result['search_answer']}</div>
                <div style='margin-top: 14px; font-size: 12px; color: #10B981;'>
                    ✔ Interaction (Query + Both Answers) written to disk by Entry Agent
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 2. PAGE: UPLOAD DOCUMENTS
    elif st.session_state.current_page == "Upload Documents":
        st.markdown("## **Upload Documents**")
        st.write("Upload PDF, TXT, DOCX, or CSV files to index into your local FAISS vector store.")
        uploaded_files = st.file_uploader("Select files", accept_multiple_files=True, type=["pdf", "docx", "txt", "csv"])
        
        if uploaded_files:
            if st.button("Process & Save to Vector Store"):
                for uploaded_file in uploaded_files:
                    with st.spinner(f"Indexing {uploaded_file.name}..."):
                        success, message = save_and_index_file(uploaded_file)
                        if success:
                            st.success(f"{uploaded_file.name}: {message}")
                        else:
                            st.error(f"{uploaded_file.name}: {message}")
                st.rerun()

    # 3. PAGE: KNOWLEDGE BASE
    elif st.session_state.current_page == "Knowledge Base":
        st.markdown("## **Knowledge Base Management**")
        files_meta = get_uploaded_files_metadata()
        if not files_meta:
            st.info("Your knowledge base is empty. Upload documents to generate FAISS vectors.")
        else:
            st.write(f"Total documents indexed: **{len(files_meta)}**")
            for f in files_meta:
                col_info, col_del = st.columns([4, 1])
                with col_info:
                    st.markdown(f"**{f['name']}** — {f['size']} (Added {f['date']})")
                with col_del:
                    if st.button("Delete", key=f"del_{f['name']}"):
                        os.remove(f['path'])
                        st.warning(f"Removed {f['name']}. Re-index documents to update vector search.")
                        st.rerun()

    # 4. PAGE: CHAT HISTORY
    elif st.session_state.current_page == "Chat History":
        st.markdown("## **Logged Interactions**")
        logs = sorted(glob.glob("outputs/*.txt"), reverse=True)
        if not logs:
            st.info("No recorded logs found in `outputs/`.")
        else:
            for log_file in logs:
                with st.expander(f"📁 {os.path.basename(log_file)}"):
                    with open(log_file, "r", encoding="utf-8") as lf:
                        st.code(lf.read(), language="text")

    # 5. PAGE: SETTINGS
    elif st.session_state.current_page == "Settings":
        st.markdown("## **System Configuration**")
        st.write("Configured Environment Keys:")
        st.text(f"OpenAI API Key: {'Configured' if os.getenv('OPENAI_API_KEY') else 'Missing'}")
        st.text(f"Serper API Key: {'Configured' if os.getenv('SERPER_API_KEY') else 'Missing'}")
        st.text(f"Storage Directory: {os.path.abspath('uploaded_docs')}")
        st.text(f"FAISS Vector DB: {os.path.abspath(FAISS_DIR)}")

# ----------------- RIGHT COLUMN (DYNAMIC KNOWLEDGE BASE & QUICK ACTIONS) -----------------
with col_right:
    st.markdown("#### ⚡ Quick Actions")
    if st.button("📄 Summarize a document →", use_container_width=True):
        st.session_state.current_page = "Chat"
        st.session_state.preset_query = "Summarize the most recently uploaded document."
        st.rerun()
    if st.button("🔍 Ask about specific topic →", use_container_width=True):
        st.session_state.current_page = "Chat"
        st.session_state.preset_query = "What are the core technical specifications detailed in the documents?"
        st.rerun()
    if st.button("⚖️ Compare two files →", use_container_width=True):
        st.session_state.current_page = "Chat"
        st.session_state.preset_query = "Compare the content and terms of the indexed documents."
        st.rerun()
    if st.button("📑 Generate a report →", use_container_width=True):
        st.session_state.current_page = "Chat"
        st.session_state.preset_query = "Generate an executive report based on knowledge base findings."
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🗄️ Your Knowledge Base")
    
    # Read files dynamically from the storage directory
    current_files = get_uploaded_files_metadata()
    if current_files:
        for doc in current_files:
            icon = "📕" if doc["ext"] == ".pdf" else "📘"
            st.markdown(f"""
            <div class='file-row'>
                <div style='font-size: 20px;'>{icon}</div>
                <div>
                    <div style='font-weight: 600; font-size: 13px; color: #1E293B;'>{doc['name']}</div>
                    <div style='font-size: 12px; color: #64748B;'>{doc['size']} • {doc['date']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No files uploaded yet. Navigate to 'Upload Documents' to add files.")

    st.markdown("---")
    st.markdown("""
    <div style='background-color: #EEF2FF; border-radius: 12px; padding: 16px; text-align: center; border: 1px solid #E0E7FF;'>
        <p style='font-size: 13px; font-weight: 600; color: #1E293B; margin: 0;'>Better answers.</p>
        <p style='font-size: 12px; color: #64748B; margin: 0;'>Powered by your multi-agent crew.</p>
    </div>
    """, unsafe_allow_html=True)