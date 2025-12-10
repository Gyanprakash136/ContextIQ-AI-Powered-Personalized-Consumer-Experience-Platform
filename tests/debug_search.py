from tools.search_tool import search_web

def test_search_output():
    query = "provide me the basketball shoe of nike brand under 5k inr"
    print(f"🔎 Testing Search Query: {query}")
    results = search_web(query, max_results=10)
    print("\n--- RAW RESULTS ---\n")
    print(results)
    
    if "http" not in results:
        print("❌ CRITICAL: No links found in search results!")
    else:
        print("✅ Links present in raw output.")
        
        # Test Scraping on the first link
        first_link = results.split("Link: ")[1].split("\n")[0]
        print(f"\n🔎 Testing Scraping on: {first_link}")
        
        from tools.scraper import scrape_url
        content = scrape_url(first_link)
        print(f"Content Length: {len(content)}")
        
        if "[LINK:" in content:
            print("✅ Extracted Internal Links found in content!")
            print("Sample:", content[:500])
            import re
            links = re.findall(r'\[LINK: (.*?)\]', content)
            print(f"Found {len(links)} product links.")
            if links:
                print(f"Example Link: {links[0]}")
        else:
            print("❌ No internal links extracted from page content.")

if __name__ == "__main__":
    test_search_output()
