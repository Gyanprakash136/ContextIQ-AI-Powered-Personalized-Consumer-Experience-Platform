try:
    from googlesearch import search
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠️ 'googlesearch-python' not found. Falling back to DuckDuckGo.")

try:
    from duckduckgo_search import DDGS
    DDG_AVAILABLE = True
except ImportError:
    DDG_AVAILABLE = False

def search_web(query: str, max_results: int = 5) -> str:
    """
    Searches the web using Google (primary) or DuckDuckGo (fallback).
    Results are formatted for LLM ingestion.
    """
    print(f"🔎 Searching for: {query}")
    results = []
    
    # 1. Try Google Search
    if GOOGLE_AVAILABLE:
        try:
            # advanced=True yields enriched results
            google_results = search(query, num_results=max_results, advanced=True)
            for r in google_results:
                results.append(f"Title: {r.title}\nLink: {r.url}\nSnippet: {r.description}\n")
            return "\n---\n".join(results)
        except Exception as e:
            print(f"❌ Google Search failed: {e}")
            # Fall through to DDG
            
    # 2. Try DuckDuckGo
    if DDG_AVAILABLE:
        try:
            with DDGS() as ddgs:
                ddg_results = [r for r in ddgs.text(query, max_results=max_results)]
                for r in ddg_results:
                     results.append(f"Title: {r.get('title')}\nLink: {r.get('href')}\nSnippet: {r.get('body')}\n")
            return "\n---\n".join(results)
        except Exception as e:
            print(f"❌ DDG Search failed: {e}")
            
    # 3. Last Resort
    if not results:
        return "Search unavailable. SYSTEM INSTRUCTION: Answer using internal knowledge."
    
    return "\n---\n".join(results)
