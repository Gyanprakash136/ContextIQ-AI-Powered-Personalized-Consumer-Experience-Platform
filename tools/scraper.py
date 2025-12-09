
import requests
from bs4 import BeautifulSoup

def scrape_url(url: str):
    """
    Scrapes the text content from a given URL.
    Use this tool when the user provides a link to a product page, review, or article.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
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
        
        # Limit length to avoid context window issues
        return clean_text[:5000] + ("..." if len(clean_text) > 5000 else "")
        
    except Exception as e:
        return f"Error scraping URL: {str(e)}"
