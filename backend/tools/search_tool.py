from duckduckgo_search import DDGS

def search_web(query: str, max_results: int = 5) -> str:
    """
    Searches the web using DuckDuckGo.
    Optimizes query for Shopping if intent is detected.
    """
    print(f"🔎 Searching web for: {query}")
    
    # Shopping Optimization: Force search on Marketplaces if query implies buying
    buy_keywords = ["buy", "price", "shop", "cost", "cheap", "best", "shoe", "laptop", "phone"]
    # if any(k in query.lower() for k in buy_keywords):
        # Append site filters for Indian Context
        # We explicitly look for product pages on major e-commerce sites
        # query += " (site:amazon.in OR site:flipkart.com OR site:myntra.com OR site:ajio.com)"
    
    results = []
    try:
        with DDGS() as ddgs:
            # We use 'text' search (formerly 'news' or others)
            # region='in-en' optimizes for India (English)
            # region='in-en' optimizes for India (English)
            # Limit to 10 results to give agent more real link options
            ddgs_gen = ddgs.text(query, region="in-en", max_results=10)
            for r in ddgs_gen:
                results.append(f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body']}\n")
    except Exception as e:
        print(f"❌ Search Error: {e}")
        return f"Error searching web: {e}"

    if not results:
        return "No results found."
    
    return "\n---\n".join(results)
