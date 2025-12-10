from ddgs import DDGS

def search_web(query: str):
    """
    Use this tool to search the internet for products, reviews, or general information.
    Use this when a product is NOT found in the internal catalog.
    
    Args:
        query: The search query (e.g., "best 4k drones 2025 review").
    """
    try:
        print(f"🔎 Searching web for: {query}")
        results = list(DDGS().text(query, max_results=5))
        
        if not results:
            return "No results found on the web."
            
        formatted_results = []
        for i, res in enumerate(results):
            title = res.get('title', 'No Title')
            link = res.get('href', 'No Link')
            body = res.get('body', '')
            formatted_results.append(f"Result {i+1}:\nTitle: {title}\nLink: {link}\nSnippet: {body}\n")
            
        return "\n---\n".join(formatted_results)
        
    except Exception as e:
        return f"Error searching web: {str(e)}"
