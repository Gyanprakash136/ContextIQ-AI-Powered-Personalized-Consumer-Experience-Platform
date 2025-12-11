
from curl_cffi import requests
from bs4 import BeautifulSoup

def fetch_meta_image(url: str):
    print(f"Testing URL: {url}")
    try:
        # Use impersonate="chrome" to mimic a real browser perfectly
        session = requests.Session(impersonate="chrome")
        
        response = session.get(url, timeout=15, allow_redirects=True)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Warning: Status Code {response.status_code}. Proceeding with parsing anyway...")
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try og:image first
        og_image = soup.find("meta", property="og:image")
        if og_image:
            print(f"Found og:image: {og_image.get('content')}")
            return og_image.get('content')

        # Try twitter:image
        twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
        if twitter_image:
             print(f"Found twitter:image: {twitter_image.get('content')}")
             return twitter_image.get('content')

        # Fallback for Amazon
        if "amazon" in url:
            print("Trying Amazon fallbacks...")
            # Look for landingImage
            img = soup.find("img", id="landingImage")
            if img:
                 print(f"Found Amazon landingImage: {img.get('src')}")
                 return img.get('src')
            
            img = soup.find("img", id="imgBlkFront")
            if img:
                 print(f"Found Amazon imgBlkFront: {img.get('src')}")
                 return img.get('src')

        # Fallback for Flipkart
        if "flipkart" in url:
             print("Trying Flipkart fallbacks...")
             # Flipkart is tricky, classes are randomized. Look for largest image?
             # Often og:image works but if 500, maybe not.
             # Look for images with 'loading="eager"' which main images often have
             images = soup.find_all("img", attrs={"loading": "eager"})
             for img in images:
                 src = img.get("src")
                 if src and "image" in src and "128/128" not in src: # Avoid small thumbnails
                      # Flipkart often resizes in URL like /128/128/. We want larger.
                      # URL pattern: .../image/128/128/phone/x/y/z/...
                      # We can replace /128/128/ with /832/832/
                      high_res = src.replace("/128/128/", "/832/832/")
                      print(f"Found Flipkart High Res: {high_res}")
                      return high_res


        # Dump title to see if we got blocked
        print(f"Page Title: {soup.title.string if soup.title else 'No Title'}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("--- Testing Flipkart ---")
    test_url_flipkart = "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac648551528c" 
    fetch_meta_image(test_url_flipkart)
    
    print("\n--- Testing Amazon ---")
    test_url_amazon = "https://www.amazon.in/Apple-iPhone-15-128-GB/dp/B0CHX1W1XY"
    fetch_meta_image(test_url_amazon)
