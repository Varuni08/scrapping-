# app.py
import streamlit as st
from agent.core import WebAgent

st.set_page_config(page_title="Agentic Web Scraper", layout="wide")

st.title("🤖 AI Agent with Cloudflare Bypass")
st.markdown("""
This agent can:
1. **Bypass Cloudflare** using custom DrissionPage logic.
2. **Read** a website.
3. **Decide** to click links (visit new tabs) if the answer isn't found immediately.
""")

# Input
col1, col2 = st.columns([2, 1])
with col1:
    url = st.text_input("Target Website URL", "https://nowsecure.nl") # Good for testing CF
with col2:
    query = st.text_input("What do you want to find?", "What is the challenge on this page?")

if st.button("Run Agent", type="primary"):
    if not url or not query:
        st.error("Please provide both URL and Query.")
    else:
        agent = WebAgent()
        
        with st.status("Agent is running...", expanded=True) as status:
            st.write("Initializing Browser Engine...")
            
            try:
                # Run the agent
                result = agent.process_query(url, query)
                
                status.update(label="Scraping Complete!", state="complete", expanded=False)
                
                st.subheader("💡 Answer:")
                st.success(result)
                
            except Exception as e:
                st.error(f"An error occurred: {e}")