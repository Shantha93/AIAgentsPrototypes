# AIAgentsPrototypes
# 🚀 AI arXiv Paper Summarizer 📄✨

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Deployed-brightgreen.svg)](https://streamlit.io)
[![LangChain/LangGraph](https://img.shields.io/badge/LangChain-LangGraph-orange.svg)](https://www.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<!-- Add other relevant badges if you have them, e.g., for specific LLMs used, arXiv API version, etc. -->

Stay ahead of the curve in AI research! This agent fetches the latest papers from the AI categories on arXiv (cs.AI, cs.LG, cs.CL, etc.) and provides concise, AI-generated summaries, all through a user-friendly Streamlit interface. Powered by a LangGraph agent for robust and extensible workflow management.

---

## 🌟 Features

*   **Latest AI Papers:** Automatically fetches the most recent pre-prints from arXiv's AI-related categories.
*   **AI-Powered Summaries:** Leverages Large Language Models (LLMs) via LangChain to generate insightful summaries of paper abstracts.
*   **Interactive UI:** Built with Streamlit for an intuitive and easy-to-use web interface.
*   **LangGraph Agent:** Utilizes LangGraph for a clear, stateful, and extensible agentic workflow, managing fetching, processing, and summarization steps.
*   **Customizable:** (Potentially - Run this on any Model and extend the prototype, by adding more features to the flow. )
*   Specify the number of papers to fetch.
*   **Easy to Run:** Simple setup and execution.

---

## 📸 Demo / Screenshot

![App Screenshot](https://github.com/Shantha93/AIAgentsPrototypes/blob/main/Arxiv.PNG)

---

## 🧠 How It Works (The Agentic Flow)

The core of this application is a LangGraph agent defined in `main.py`. This agent orchestrates the following steps:

1.  **Fetch Papers Agent:**
    *   The agent connects to the arXiv API.
    *   It queries for the latest papers in specified AI categories (e.g., "cs.AI", "cs.LG", "stat.ML").
    *   It retrieves metadata for these papers, including titles, authors, and abstracts.
2.  **Summarize Papers Agent:**
    *   For each paper's abstract, the agent uses a LangChain LLM (e.g., OpenAI's GPT in this case) to generate a concise summary.
    *   This involves a carefully crafted prompt to ensure the summary is focused and informative and understandable even by a Layman 
4.  **Complie Report Agent:**
    * Complies final report from all the papers summarised by previous agent and produces the final output in consolidated manner so it could be well presented.
5.  **Streamlit UI**
    *   The `ui.py` script uses Streamlit to:
        *   Provide an interface to trigger the agent.
        *   Display the fetched papers along with their AI-generated summaries in a readable format.
        *   Show links to the original arXiv papers.

The LangGraph structure allows for clear separation of these concerns, error handling, and potential for future expansion (e.g., adding a paper analysis node, a knowledge graph creation node, etc.).

---

## 🛠️ Tech Stack

*   **Python:** Core programming language.
*   **Streamlit:** For building the interactive web UI (`ui.py`).
*   **LangGraph (LangChain):** For defining and running the AI agent workflow (`main.py`).
*   **LangChain:** For LLM integrations, prompt management, and other AI building blocks.
*   **arXiv API Client:** (e.g., the `arxiv` Python library) For fetching paper data.
*   **LLM Provider:** We have used OpenAI here, however this project could be model agnostic with minimal changes
*   **Dotenv:** (Recommended) For managing API keys.

---

## ⚙️ Setup & Installation

Follow these steps to get the AI arXiv Paper Summarizer running locally:

1.  **Prerequisites:**
    *   Python 3.8 or higher.
    *   Git.
    *   An API key for your chosen LLM provider (e.g., OpenAI API Key).

2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Shantha93/AIAgentsPrototypes.git
    cd YOUR_REPOSITORY_NAME
    ```

3.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set Up API Keys:**
    *   You'll need an API key from your chosen LLM provider (e.g., OpenAI).
    *   Update the keys in the `.env` file present the root directory of the project:
          
    *   Add your API key(s) to the `.env` file. For example, if using OpenAI:
        ```env
        # .env
        OPENAI_API_KEY="your_openai_api_key_here"
        # LANGCHAIN_TRACING_V2="true" # Optional: for LangSmith tracing
        # LANGCHAIN_API_KEY="your_langsmith_api_key" # Optional: for LangSmith tracing
        ```
        *Note: `main.py` or your LangChain setup should be configured to load these environment variables (e.g., using `python-dotenv`).*

---

## 🚀 Running the Application

Once the setup is complete, you can run the Streamlit application:

```bash
streamlit run ui.py
