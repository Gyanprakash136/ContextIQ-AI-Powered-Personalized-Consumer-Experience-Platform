import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.scraper import scrape_url

def test():
    # This URL loads content via AJAX/JS, perfect for testing Crawlee vs Requests
    url = "https://www.scrapethissite.com/pages/ajax-javascript/"
    print(f"🧪 Testing scraper on: {url}")
    
    result = scrape_url(url)
    
    print("\n--- RESULT SNIPPET ---\n")
    print(result[:1000])
    print("\n----------------------\n")
    
    if "Oscar" in result:
        print("✅ SUCCESS: Found content loaded via JavaScript (Oscars data).")
    else:
        print("❌ FAILURE: Did not find JS-loaded content.")

if __name__ == "__main__":
    test()
