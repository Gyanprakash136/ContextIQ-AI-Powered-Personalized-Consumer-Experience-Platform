from tools.search_tool import search_web

def test_search():
    query = "latest noise cancelling headphones 2025"
    print(f"Testing search with query: {query}")
    result = search_web(query)
    print("Search Result:\n", result)
    
if __name__ == "__main__":
    test_search()
