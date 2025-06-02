import os
import arxiv
from datetime import datetime
from typing import List, Dict, TypedDict, Annotated
import operator

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI # Changed for Azure
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

# --- 1. Load Environment Variables (for Azure OpenAI) --- 
load_dotenv()

# Below Datastructure is used in order to capture all details of one ARXIV paper
class Paper(TypedDict):
    title: str
    authors: List[str]
    published_date: str
    summary: str  # This is the abstract
    pdf_url: str
    arxiv_id: str

class SummarizedPaper(Paper):
    layman_summary: str

# --- 2. Define State for the Graph ---
class AgentState(TypedDict):
    query_categories: List[str]
    num_papers: int
    fetched_papers: List[Paper]
    summarized_papers: List[SummarizedPaper]
    final_report: str
    error_message: str | None

# --- 3. Initialize Azure OpenAI LLM ---
# Ensure your .env file has AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT,
# AZURE_OPENAI_API_VERSION, and AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
# I have set the varibales like AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT in my environment variables setting .. Alternatively dot env could also be used here
try:
    llm = AzureChatOpenAI(
        azure_deployment="gpt-4o-mini",  # or your deployment, you can also use "os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")"
        api_version="2024-12-01-preview",  # or your api version
        temperature=0.2,
        max_tokens=250, # Max tokens for summary
    )
except Exception as e:
    print(f"Error initializing AzureChatOpenAI: {e}")
    print("Please ensure Azure OpenAI environment variables are set correctly in your .env file.")
    exit()

# --- 4. Define Node Functions (Agents) ---

# Node 1: Fetch papers from ArXiv
def fetch_arxiv_papers_node(state: AgentState) -> Dict:
    print("---FETCHING PAPERS FROM ARXIV---")
    query_categories = state.get("query_categories", ["cs.AI", "cs.LG", "stat.ML"])
    num_papers = state.get("num_papers", 10)
    
    search_query = " OR ".join([f"cat:{cat}" for cat in query_categories])
    
    try:
        search = arxiv.Search(
            query=search_query,
            max_results=num_papers,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        results = list(search.results())
        
        if not results:
            return {"fetched_papers": [], "error_message": "No papers found for the given categories."}

        fetched_papers_data: List[Paper] = []
        for result in results:
            fetched_papers_data.append({
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "published_date": result.published.strftime("%Y-%m-%d"),
                "summary": result.summary.replace("\n", " "),
                "pdf_url": result.pdf_url,
                "arxiv_id": result.entry_id.split('/')[-1]
            })
        
        print(f"Fetched {len(fetched_papers_data)} papers.")
        print(f"Fetched data is {fetched_papers_data}")
        return {"fetched_papers": fetched_papers_data, "error_message": None}
    except Exception as e:
        print(f"Error fetching from ArXiv: {e}")
        return {"fetched_papers": [], "error_message": f"ArXiv API error: {str(e)}"}


summarization_prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert science communicator. Your task is to summarize the following research paper abstract in simple, layman's terms. Avoid all jargon and complex technical details. Explain the core idea, what problem it tries to solve, and its potential impact, as if you were explaining it to a 10-year-old or someone completely new to AI. The summary should be concise, ideally 2-4 sentences. Focus on clarity and simplicity above all else."),
    ("human", "Please summarize this abstract:\n\nTitle: {title}\n\nAbstract: {abstract}")
])

summarization_chain = summarization_prompt_template | llm | StrOutputParser()

# Node 2: Summarize papers using Azure OpenAI LLM
def summarize_papers_node(state: AgentState) -> Dict:
    try:
            
        print("---SUMMARIZING PAPERS---")
        fetched_papers = state.get("fetched_papers", [])
        if not fetched_papers:
            return {"summarized_papers": [], "error_message": "No papers to summarize."}

        summarized_papers_data: List[SummarizedPaper] = []
        for i, paper in enumerate(fetched_papers):
            print(f"Summarizing paper {i+1}/{len(fetched_papers)}: {paper['title'][:50]}...")
            layman_summary = summarization_chain.invoke({
                    "title": paper["title"],
                    "abstract": paper["summary"] 
                })
            summarized_paper_entry: SummarizedPaper = {**paper, "layman_summary": layman_summary} # type: ignore
            summarized_papers_data.append(summarized_paper_entry)
        print(f"Summarised papers data from LLM {summarized_papers_data}")
        return {"summarized_papers": summarized_papers_data, "error_message": state.get("error_message")}
    except Exception:
        import traceback; traceback.print_exc();

# Node 3: Compile the final report
def compile_report_node(state: AgentState) -> Dict:
    print("---COMPILING REPORT---")
    summarized_papers = state.get("summarized_papers", [])
    
    if not summarized_papers:
        error_msg = state.get("error_message", "No summaries available to compile report.")
        return {"final_report": f"Report Generation Failed: {error_msg}"}

    report_parts = [f"AI Research Update - {datetime.now().strftime('%Y-%m-%d')}\n" + "="*40 + "\n"]
    
    for i, paper in enumerate(summarized_papers):
        report_parts.append(f"📄 Paper {i+1}: {paper['title']}")
        report_parts.append(f"   Authors: {', '.join(paper['authors'])}")
        report_parts.append(f"   Published: {paper['published_date']}")
        report_parts.append(f"   ArXiv ID: {paper['arxiv_id']} (Link: http://arxiv.org/abs/{paper['arxiv_id']})")
        report_parts.append(f"   PDF: {paper['pdf_url']}")
        report_parts.append(f"\n   🧠 Layman's Summary:\n   {paper['layman_summary']}\n")
        report_parts.append("-" * 30)

    return {"final_report": "\n".join(report_parts)}

# --- 5. Build the LangGraph Workflow ---
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("fetch_arxiv", fetch_arxiv_papers_node)
workflow.add_node("summarize_papers", summarize_papers_node)
workflow.add_node("compile_report", compile_report_node)

# Define edges (the flow of work)
workflow.set_entry_point("fetch_arxiv")
workflow.add_edge("fetch_arxiv", "summarize_papers")
workflow.add_edge("summarize_papers", "compile_report")
workflow.add_edge("compile_report", END) # END signifies the workflow completion

# Compile the graph
app = workflow.compile()

# --- 6. Run the Workflow ---
def runAgents(num_papers:int):
    # Define initial inputs for the workflow
    initial_input = {
        "query_categories": ["cs.AI", "cs.LG", "stat.ML", "cs.CV", "cs.CL"], 
        "num_papers": num_papers
    }

    print("🚀 Starting AI Research Update Agent System...")



    # Invoke the graph to get the final result
    final_state = app.invoke(initial_input)

    print("\n\n🎉 --- FINAL REPORT --- 🎉\n")
    if final_state.get("error_message") and not final_state.get("final_report"): # Only show if no report
        print(f"An error occurred during the process: {final_state['error_message']}")
    
    if final_state.get("final_report"):
        print(final_state["final_report"])
    else:
        print("No report generated. Check for earlier error messages.")
    return final_state

if __name__ == "__main__":
    runAgents(5)
