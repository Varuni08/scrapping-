from DrissionPage import ChromiumPage, ChromiumOptions
from agent.bypasser import CloudflareBypasser
import time

def get_page_content(url):
    co = ChromiumOptions()
    co.auto_port()
    co.headless(False) 
    
    page = ChromiumPage(co)
    
    try:
        print(f"🕵️ Accessing: {url}")
        page.get(url)
        
        bypasser = CloudflareBypasser(page)
        if not bypasser.is_bypassed():
            bypasser.bypass()
        
        # --- NEW: Scroll Logic ---
        print("   -> Scrolling to load dynamic content...")
        # Scroll down in chunks to trigger lazy loading
        for _ in range(6): 
            page.scroll.down(800)
            time.sleep(0.5)
        
        # Ensure we are at the very bottom
        page.scroll.to_bottom()
        time.sleep(2) 
        # -------------------------

        html = page.html
        return html
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None
    finally:
        try:
            page.quit()
        except:
            pass