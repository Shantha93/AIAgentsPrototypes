# streamlit_app.py
import streamlit as st

from main import runAgents

# --- Streamlit UI ---
def main():
    st.set_page_config(page_title="AI Research Updater", layout="wide", initial_sidebar_state="expanded")
    
    st.title("🚀 AI Research Trend Updater")
    st.markdown("Get the latest AI/ML research from ArXiv, summarized in easy-to-understand language.")
    st.markdown("---")

    # Sidebar for inputs
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        default_categories = ["cs.AI", "cs.LG", "stat.ML","cs.CV", "cs.CL"]
        st.info(default_categories)
        
        num_papers = st.number_input(
            "Number of papers to fetch:",
            min_value=1,
            max_value=20, # Sensible limit for UI responsiveness and ArXiv courtesy
            value=5,
            step=1,
            help="How many of the latest papers do you want?"
        )

        st.markdown("---")
        if st.button("✨ Get Latest Research Update", type="primary", use_container_width=True):
            
            initial_input = {
                    "query_categories": default_categories,
                    "num_papers": num_papers
                }
            with st.spinner("👩‍🔬 Your AI research assistant is processing papers... This may take a moment."):
                try:
                    
                        # Invoke the LangGraph app
                    final_state = runAgents(num_papers)
                        
                        # Store results in session state for display
                    if final_state and "final_report" in final_state:
                        
                        st.session_state.final_report = final_state["final_report"]
                        
                        # Check for errors, even if a partial report might exist
                        if final_state and "error_message" in final_state and final_state["error_message"]:
                            
                            st.session_state.error_message = final_state["error_message"]
                  
                except Exception as e:
                    
                    st.session_state.error_message = f"An unexpected error occurred while running the AI pipeline: {str(e)}"
                    st.exception(e) # Shows detailed traceback in Streamlit for dev

                
    # Main area for displaying the report or errors
    st.header("📊 Research Digest")

    if "error_message" in st.session_state and st.session_state.error_message:

        is_report_failed_message = "Report Generation Failed" in st.session_state.get("final_report", "")
        
        if not is_report_failed_message: # If error is not already in the report text
            st.error(f"🚨 An issue occurred: {st.session_state.error_message}")
        # If there's also a report (even if it's an error report), display it below
        if "final_report" in st.session_state and st.session_state.final_report:
            st.markdown(st.session_state.final_report, unsafe_allow_html=True) # unsafe_allow_html for Markdown links
        elif not is_report_failed_message : # No report and error is not in report text.
            st.info("No report was generated due to the issue mentioned above.")

    elif "final_report" in st.session_state and st.session_state.final_report:
        st.markdown(st.session_state.final_report, unsafe_allow_html=True)
    else:
        st.info("Configure your preferences in the sidebar and click 'Get Latest Research Update' to begin.")
    
    st.sidebar.markdown("---")
    st.sidebar.caption("Powered by LangGraph and Azure OpenAI.")
    st.sidebar.caption("Ensure `.env` is configured if running locally.")

if __name__ == "__main__":
    main()