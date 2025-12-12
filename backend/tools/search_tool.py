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
            # General search without region constraint to avoid ip blocking issues
            # formerly 'news' or others
            ddgs_gen = ddgs.text(query, max_results=10)
            for r in ddgs_gen:
                results.append(f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body']}\n")
    except Exception as e:
        print(f"❌ Search Error (DDG): {e}")
        # Return a helpful error message to the agent so it knows what happened
        return f"Error searching web: {e}. Try asking the user for more specific details."

    if not results:
        return "No results found."
    
    return "\n---\n".join(results)
