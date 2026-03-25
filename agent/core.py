import multiprocessing
import json
from agent.scraper import get_page_content
from agent.parser import clean_html, extract_links
from agent.llm import query_groq

def scrape_worker(url):
    try:
        html = get_page_content(url)
        if html:
            return clean_html(html)
    except:
        pass
    return ""

class WebAgent:
    def process_query(self, start_url, query):
        print(f"1. Scraping Main Page: {start_url}")
        raw_html = get_page_content(start_url)
        if not raw_html:
            return "Failed to access the website."
        
        main_text = clean_html(raw_html)
        
        # --- FIRST PASS: DIRECT EXTRACTION ATTEMPT ---
        print("2. Attempting direct extraction...")
        
        # We give the LLM a specialized prompt for lists
        extraction_prompt = """
        You are a data extraction engine.
        The user wants a list of items (e.g., schools, companies, products).
        
        Task:
        1. Read the page text below.
        2. Extract the SPECIFIC items requested by the user.
        3. Do NOT summarize ("Here are the schools..."). List them one by one.
        4. If you find the answer, format it as a clean list.
        5. If the text seems cut off or you can't find the requested number (e.g., user asked for 25, you only see 5), return EXACTLY the string: "NEED_MORE_LINKS".
        """
        
        user_input = f"""
        User Query: {query}
        
        --- PAGE CONTENT START ---
        {main_text}
        --- PAGE CONTENT END ---
        """
        
        initial_response = query_groq(extraction_prompt, user_input)
        
        # If the LLM is satisfied, return the result
        if "NEED_MORE_LINKS" not in initial_response and len(initial_response) > 50:
            return initial_response

        # --- SECOND PASS: PAGINATION / SUB-LINKS ---
        print("3. List incomplete or not found. Looking for pagination or detail links...")
        
        all_links = extract_links(raw_html, start_url)
        
        # Ask LLM which links might contain the rest of the list (e.g., "Page 2", "Next", or specific school profiles)
        decision_prompt = """
        The user asked for a list, but the main page didn't have enough information.
        Analyze the links below.
        Select up to 3 links that are likely:
        1. Pagination links (e.g., "Page 2", "Next", "View All")
        2. Or sub-category links that might contain the list.
        
        Return STRICT JSON: {"links": ["url1", "url2"]}
        """
        
        decision_response = query_groq(decision_prompt, f"Query: {query}\nLinks: {all_links[:60]}", json_mode=True)
        try:
            links_to_visit = json.loads(decision_response).get("links", [])
        except:
            links_to_visit = []

        if not links_to_visit:
            return "I extracted what I could from the main page:\n" + initial_response

        print(f"   -> Visiting: {links_to_visit}")
        with multiprocessing.Pool(processes=min(len(links_to_visit), 3)) as pool:
            sub_contents = pool.map(scrape_worker, links_to_visit)

        # Final Synthesis
        combined = main_text + "\n" + "\n".join([c for c in sub_contents if c])
        
        final_prompt = "Combine the data extracted below to produce the final full list requested by the user. Number the list."
        return query_groq(final_prompt, f"Query: {query}\nData: {combined[:60000]}")