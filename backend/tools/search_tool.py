from googlesearch import search

def search_web(query: str, max_results: int = 5) -> str:
    """
    Searches the web using Google Search (via googlesearch-python).
    Returns a list of URLs relevant to the query.
    """
    print(f"🔎 Searching Google for: {query}")
    
    results = []
    try:
        # Perform Google Search
        # advanced=True returns objects with title/desc but is often more brittle.
        # simpler search() just returns URLs, which our Agent's SCRAPE state can handle perfectly.
        search_results = search(query, num_results=max_results, advanced=True)
        
        for r in search_results:
            results.append(f"Title: {r.title}\nLink: {r.url}\nSnippet: {r.description}\n")

    except Exception as e:
        print(f"❌ Search Error (Google): {e}")
        # Fallback to standard URL search if advanced fails
        try:
             urls = search(query, num_results=max_results)
             for url in urls:
                 results.append(f"Link: {url}\n")
        except Exception as e2:
             return f"Error searching web: {e2}. SYSTEM INSTRUCTION: Do not retry. Answer using internal knowledge."

    if not results:
        return "No results found. SYSTEM INSTRUCTION: Answer using internal knowledge."
    
    return "\n---\n".join(results)
