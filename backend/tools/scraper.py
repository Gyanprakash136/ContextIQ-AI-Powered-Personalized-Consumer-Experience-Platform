from curl_cffi import requests
from bs4 import BeautifulSoup

def scrape_url(url: str):
    """
    Scrapes the text content from a given URL.
    Use this tool when the user provides a link to a product page, review, or article.
    """
    try:
        # Use impersonate="chrome" to mimic a real browser perfectly
        # This helps bypass bot detection on Amazon/Flipkart
        session = requests.Session(impersonate="chrome")
        
        # Amazon often requires cookies or returns 503 to headless requests
        # We increase timeout and allow redirects
        response = session.get(url, timeout=15, allow_redirects=True)
        # response.raise_for_status() # Relaxed check
        
        if response.status_code not in [200, 404, 500]: # Allow 500 as it might still have content
             return f"Error: Status code {response.status_code}"

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()

        # Transform <a> tags to explicit text: "Link Text [URL: href]"
        # This allows the LLM to see which text corresponds to which link
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if text and href and len(text) > 3: # Skip empty/tiny links
                if href.startswith('/'):
                     # Resolve relative URL using the base URL from the response (handling redirects)
                     from urllib.parse import urljoin
                     href = urljoin(response.url, href)

                # Check if it's a product link pattern (optional helpful heuristic)
                if "/dp/" in href or "/p/" in href or "product" in href or "pd" in href:
                    new_string = f" {text} [LINK: {href}] "
                else:
                    new_string = f" {text} "
                
                a.replace_with(new_string)

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

        if len(clean_text) < 500:
             # Might be empty but let's return what we have in case of partial success
             pass

        # Limit length to avoid context window issues
        # Reduced to 15k to avoid overwhelming the model
        return clean_text[:15000] + ("..." if len(clean_text) > 15000 else "")
        
    except Exception as e:
        return f"Error scraping URL: {str(e)}"

def fetch_meta_image(url: str) -> str | None:
    """
    Fetches the Open Graph image (og:image) from a given URL.
    Returns None if no image is found or an error occurs.
    """
    try:
        session = requests.Session(impersonate="chrome")
        response = session.get(url, timeout=10, allow_redirects=True)
        
        # Warn but proceed on non-200
        if response.status_code != 200:
            print(f"⚠️ Scraper warning for {url}: Status {response.status_code}")
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try og:image first
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image["content"]
            
        # Try twitter:image
        twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
        if twitter_image and twitter_image.get("content"):
            return twitter_image["content"]

        # Fallback for Amazon
        if "amazon" in url:
            # Look for landingImage
            img = soup.find("img", id="landingImage")
            if img: return img.get('src')
            
            img = soup.find("img", id="imgBlkFront")
            if img: return img.get('src')

        # Fallback for Flipkart
        if "flipkart" in url:
             # Look for images with 'loading="eager"' which main images often have
             images = soup.find_all("img", attrs={"loading": "eager"})
             for img in images:
                 src = img.get("src")
                 if src and "image" in src and "128/128" not in src:
                      return src.replace("/128/128/", "/832/832/")

        # Try finding the first large image
        images = soup.find_all("img", src=True)
        for img in images:
             src = img.get("src", "")
             if "icon" not in src.lower() and "logo" not in src.lower():
                 from urllib.parse import urljoin
                 return urljoin(response.url, src)

        return None
    except Exception as e:
        print(f"Scraper error: {e}")
        return None
