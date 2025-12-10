
import requests
from bs4 import BeautifulSoup

def scrape_url(url: str):
    """
    Scrapes the text content from a given URL.
    Use this tool when the user provides a link to a product page, review, or article.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        # Amazon often requires cookies or returns 503 to headless requests
        # We increase timeout and allow redirects
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Heuristic: Skip noisy headers if possible
        if "Skip to main content" in clean_text:
            try:
                clean_text = clean_text.split("Skip to main content")[1]
            except IndexError:
                pass

        # Limit length to avoid context window issues
        # Increased to 25k to capture product grids on Amazon
        return clean_text[:25000] + ("..." if len(clean_text) > 25000 else "")
        
    except Exception as e:
        return f"Error scraping URL: {str(e)}"
