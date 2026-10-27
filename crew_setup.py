import os
from datetime import datetime
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task, LLM
from crewai.tools import tool
from crewai_tools import SerperDevTool
from rag_engine import query_vectorstore

load_dotenv()

# 1. Explicitly configure the LLM (gpt-4o-mini)
default_llm = LLM(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.3
)

# 2. Local FAISS Search Tool
@tool("Query Knowledge Base")
def rag_search_tool(query: str) -> str:
    """Searches the local FAISS vector store containing all uploaded documents."""
    return query_vectorstore(query)

web_search_tool = SerperDevTool()

# 3. Define the 3 Agents with the explicit LLM
assistant_agent = Agent(
    role="RAG Knowledge Specialist",
    goal="Answer user inquiries using the FAISS Knowledge Base tool and fallback to general reasoning if unindexed.",
    backstory="You are an expert technical assistant who retrieves and synthesizes documents from the internal vector database.",
    tools=[rag_search_tool],
    llm=default_llm,
    verbose=True
)

search_agent = Agent(
    role="Web Research Specialist",
    goal="Conduct real-time web searches to retrieve external, live facts relevant to the user query.",
    backstory="You are an internet intelligence analyst who finds fresh, accurate information from the live web.",
    tools=[web_search_tool],
    llm=default_llm,
    verbose=True
)

entry_agent = Agent(
    role="Entry & Logging Coordinator",
    goal="Compile the user query and both answers into a structured summary and write it to a .txt file.",
    backstory="You record all interactions and ensure every record contains the query, the assistant's answer, and the web search answer.",
    llm=default_llm,
    verbose=True
)

def run_knowly_crew(user_query: str) -> dict:
    # Task 1: Assistant RAG
    task_assistant = Task(
        description=f"Check the Knowledge Base for context about: '{user_query}' and answer thoroughly.",
        expected_output="An accurate answer based on the knowledge base.",
        agent=assistant_agent
    )

    # Task 2: Live Web Search
    task_search = Task(
        description=f"Search the live web for: '{user_query}'. Highlight up-to-date facts and outside context.",
        expected_output="A structured summary of web search findings.",
        agent=search_agent
    )

    # Task 3: Entry Agent saves everything to disk
    def save_log_callback(output):
        os.makedirs("outputs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outputs/query_log_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(str(output.raw))
        return output

    task_entry = Task(
        description=(
            f"Format and persist the complete interaction for query: '{user_query}'.\n"
            "Format the output strictly as:\n"
            f"=== USER QUERY ===\n{user_query}\n\n"
            "=== ASSISTANT ANSWER ===\n[Assistant Answer Here]\n\n"
            "=== WEB SEARCH ANSWER ===\n[Web Search Answer Here]"
        ),
        expected_output="Complete structured text containing the query and both answers.",
        agent=entry_agent,
        callback=save_log_callback
    )

    # 4. Sequential Crew with MEMORY ENABLED
    crew = Crew(
        agents=[assistant_agent, search_agent, entry_agent],
        tasks=[task_assistant, task_search, task_entry],
        process=Process.sequential,
        memory=True,  # Enables Short-Term, Long-Term, and Entity Memory
        embedder={
            "provider": "openai",
            "config": {
                "model": "text-embedding-3-small"
            }
        },
        verbose=True
    )

    result = crew.kickoff()
    raw_output = str(result.raw)

    # Extract answers for separate UI rendering
    assistant_text = ""
    search_text = ""

    if "=== ASSISTANT ANSWER ===" in raw_output and "=== WEB SEARCH ANSWER ===" in raw_output:
        parts = raw_output.split("=== WEB SEARCH ANSWER ===")
        assistant_text = parts[0].replace(f"=== USER QUERY ===\n{user_query}", "").replace("=== ASSISTANT ANSWER ===", "").strip()
        search_text = parts[1].strip()
    else:
        assistant_text = str(task_assistant.output.raw) if task_assistant.output else "No response generated."
        search_text = str(task_search.output.raw) if task_search.output else "No search response generated."

    return {
        "query": user_query,
        "assistant_answer": assistant_text,
        "search_answer": search_text
    }