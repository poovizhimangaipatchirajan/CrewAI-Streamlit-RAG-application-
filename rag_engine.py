import os
import glob
from datetime import datetime
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

DOCS_DIR = "uploaded_docs"
FAISS_DIR = "faiss_index"

os.makedirs(DOCS_DIR, exist_ok=True)

def get_uploaded_files_metadata():
    """Returns dynamic metadata for all files currently in the upload directory."""
    files = glob.glob(os.path.join(DOCS_DIR, "*"))
    file_list = []
    for filepath in files:
        if os.path.isfile(filepath):
            size_bytes = os.path.getsize(filepath)
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} KB"
            else:
                size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
            
            mod_time = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%b %d, %Y")
            ext = os.path.splitext(filepath)[1].lower()
            
            file_list.append({
                "name": os.path.basename(filepath),
                "path": filepath,
                "size": size_str,
                "date": mod_time,
                "ext": ext
            })
    return file_list

def save_and_index_file(uploaded_file):
    """Saves an uploaded file and incrementally indexes it into FAISS."""
    file_path = os.path.join(DOCS_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Extract text based on file format
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    elif ext in [".txt", ".csv"]:
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        return False, "Unsupported file format."

    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    splits = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    if os.path.exists(FAISS_DIR):
        vectorstore = FAISS.load_local(FAISS_DIR, embeddings, allow_dangerous_deserialization=True)
        vectorstore.add_documents(splits)
    else:
        vectorstore = FAISS.from_documents(splits, embeddings)
        
    vectorstore.save_local(FAISS_DIR)
    return True, "Indexed successfully."

def query_vectorstore(query: str, k: int = 4) -> str:
    """Retrieves top-k context passages from the local FAISS index."""
    if not os.path.exists(FAISS_DIR):
        return "No documents have been uploaded or indexed into the FAISS Knowledge Base yet."
    
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.load_local(FAISS_DIR, embeddings, allow_dangerous_deserialization=True)
    results = vectorstore.similarity_search(query, k=k)
    
    if not results:
        return "No relevant context found in uploaded documents."
    
    return "\n\n".join([f": {doc.page_content}" for doc in results])