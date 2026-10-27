# CrewAI-Streamlit-RAG-application-
A modular, multi-agent AI system built using CrewAI, Streamlit, and LangChain. The platform implements a sequential multi-agent workflow featuring short-term, long-term, and entity memory, an embedded FAISS vector store for document question-answering, and real-time web search verification.
Knowly — Multi-Agent RAG & Web Research Intelligence Platform
A modular, multi-agent AI system built using CrewAI, Streamlit, and LangChain. The platform implements a sequential multi-agent workflow featuring short-term, long-term, and entity memory, an embedded FAISS vector store for document question-answering, and real-time web search verification.
🌟 Key Features
•	Sequential Multi-Agent Architecture:
o	Assistant Agent (RAG Specialist): Inspects and retrieves context from the local FAISS vector store to ground answers in uploaded documents.
o	Web Search Agent: Gathers up-to-date facts from the live internet using the Serper API.
o	Entry Agent (Logger & Coordinator): Consolidates the original query and both generated answers, writing a timestamped record to persistent disk storage.
•	Persistent Agent Memory: Configured with memory=True and OpenAI embeddings to enable short-term, long-term, and entity memory across conversational turns.
•	Dynamic Knowledge Base: Upload documents directly via the UI; documents are parsed, chunked, and indexed incrementally into a local FAISS database.
•	Multi-Format Ingestion: Supports .pdf, .docx, .txt, and .csv files.
•	Three-Column Dashboard: Fully dynamic Streamlit UI mimicking modern document workspace layouts, including dynamic metadata cards, active sidebar routing, and one-click quick actions.
📁 Project Directory Structure
Plaintext
knowly-crew/
│
├── uploaded_docs/        # Ingested user documents
├── faiss_index/          # Local FAISS vector index files
├── outputs/              # Timestamped query & answer logs saved by Entry Agent
├── .env                  # Environment configuration (API keys)
├── requirements.txt      # Python dependencies
├── rag_engine.py         # Document parsing, chunking, and FAISS indexing
├── crew_setup.py         # CrewAI sequential workflow, LLM configuration, and agents
└── app.py                # Streamlit user interface and application routing
🚀 Getting Started
1. Prerequisites
•	Python 3.10+ (Python 3.11 recommended)
•	OpenAI API key (for gpt-4o-mini and text embeddings)
•	Serper API key (for live web search)
2. Installation
Clone or create the project folder, then set up a virtual environment:
Bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
3. Environment Variables Configuration
Create a .env file in the root directory:
Ini, TOML
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here
Security Note: Never commit your .env file to version control. Add .env to your .gitignore.
4. Running the Application
Launch the Streamlit web dashboard:
Bash
streamlit run app.py
🖥️ Using the Application
1.	Upload Documents:
o	Click Upload Documents in the left sidebar.
o	Upload any .pdf, .docx, .txt, or .csv files.
o	Click Process & Save to Vector Store to chunk and embed documents into FAISS.
2.	Review Knowledge Base:
o	Navigate to Knowledge Base or inspect the right-hand panel to view indexed files, file sizes, and ingestion timestamps.
3.	Execute Queries:
o	Switch to the Chat tab or click any of the Quick Actions.
o	Submit your prompt in the chat input box.
o	The sequential crew will run:
1.	The Assistant Agent queries the FAISS index.
2.	The Web Search Agent searches the live web via Serper.
3.	The Entry Agent structures and writes the complete log to outputs/query_log_<timestamp>.txt.
4.	View Outputs:
o	The conversation view displays the user query alongside separated cards for both the Assistant (FAISS RAG) answer and the Web Search answer.
o	Prior logs can be inspected inside the Chat History tab.
🛠️ Tech Stack
•	Orchestration: CrewAI (Sequential Process, Memory enabled)
•	LLM Engine: gpt-4o-mini via OpenAI API
•	Vector Store: FAISS (faiss-cpu) via LangChain Community
•	Embeddings: text-embedding-3-small (OpenAI)
•	Frontend: Streamlit
•	Live Web Retrieval: Serper API (SerperDevTool)

