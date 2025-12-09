import chromadb
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
# Ensure API key is set
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class CatalogDB:
    def __init__(self):
        # Persistent storage so you don't lose data on restart
        self.client = chromadb.PersistentClient(path="./chroma_data")
        self.collection = self.client.get_or_create_collection("hackathon_catalog")

    def search(self, query: str, n_results=3):
        """
        Converts query to vector -> Finds matching products
        """
        try:
            # 1. Embed the query using Google's model
            embedding = genai.embed_content(
                model="models/text-embedding-004",
                content=query,
                task_type="retrieval_query"
            )['embedding']

            # 2. Search ChromaDB
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=n_results
            )

            # 3. Format for the Agent
            if not results['documents'] or not results['documents'][0]:
                return "No matching products found in our catalog."
            
            # Combine metadata and document content for context
            formatted_results = []
            for i in range(len(results['documents'][0])):
                doc = results['documents'][0][i]
                meta = results['metadatas'][0][i] if results['metadatas'] else {}
                formatted_results.append(f"Product {i+1}: {doc}\nMetadata: {meta}")

            return "\n---\n".join(formatted_results)
            
        except Exception as e:
            return f"Error searching catalog: {str(e)}"

# Singleton instance
db = CatalogDB()

# Wrapper function for the Agent Tool
def search_internal_catalog(search_query: str):
    """
    Use this tool to find products in our inventory. 
    Input: A specific product name or feature (e.g., 'noise cancelling headphones').
    """
    return db.search(search_query)