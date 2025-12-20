from tools.crawlee_service import scrape_url_dynamic
from curl_cffi import requests
from bs4 import BeautifulSoup

def scrape_url(url: str):
    """
    Scrapes the text content from a given URL using Crawlee (Playwright) for JS support.
    """
    try:
        print(f"🕷️ Scraping with Crawlee: {url}")
        content = scrape_url_dynamic(url)
        
        # Post-processing to clean up whitespace
        lines = (line.strip() for line in content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Limit length
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

