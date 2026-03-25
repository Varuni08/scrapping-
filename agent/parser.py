from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

def clean_html(html_content):
    """
    Aggressively cleans HTML but captures ALL visible text to ensure list items aren't missed.
    """
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'lxml')
    
    # 1. Remove non-visible/irrelevant tags
    # Removed 'div' from this list to avoid deleting content, only removing structure wrappers
    for element in soup(["script", "style", "nav", "footer", "iframe", "svg", "noscript", "aside", "form", "input"]):
        element.extract()

    # 2. Get text with specific separator to distinguish items
    # We use a special separator likely not in normal text
    text = soup.get_text(separator="\n")
    
    # 3. Clean up the text
    lines = []
    for line in text.splitlines():
        clean_line = line.strip()
        # Filter out very short lines (often menu items or icon text) unless they look like numbers
        if len(clean_line) > 2:
            lines.append(clean_line)
            
    cleaned_text = "\n".join(lines)
    
    # Limit to ~40k chars (Groq Llama 3 has 8k token context which is roughly 32k-40k chars)
    return cleaned_text[:40000]

def extract_links(html_content, base_url):
    soup = BeautifulSoup(html_content, 'lxml')
    links = set()
    
    main_area = soup.find('body')
    if not main_area: return []

    for a in main_area.find_all('a', href=True):
        href = a['href']
        if href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
            continue
        full_url = urljoin(base_url, href)
        if full_url.startswith('http'):
            links.add(full_url)
            
    return list(links)