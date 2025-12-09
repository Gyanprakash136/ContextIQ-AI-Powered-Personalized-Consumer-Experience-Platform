import pandas as pd
import google.generativeai as genai
import chromadb
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def ingest_data(csv_path="products.csv"):
    client = chromadb.PersistentClient(path="./chroma_data")
    collection = client.get_or_create_collection("hackathon_catalog")
    
    df = pd.read_csv(csv_path)
    print(f"🔄 Ingesting {len(df)} products...")

    for i, row in df.iterrows():
        # Create a rich description for the vector
        content = f"Product: {row['Product Name']}. Category: {row['Category']}. Price: {row['Price']}. Description: {row['Description']}"
        
        # Embed
        emb = genai.embed_content(
            model="models/text-embedding-004",
            content=content,
            task_type="retrieval_document"
        )['embedding']

        # Save
        collection.add(
            ids=[str(i)],
            documents=[content],
            embeddings=[emb],
            metadatas=[row.to_dict()]
        )
    print("✅ Ingestion Complete!")

if __name__ == "__main__":
    ingest_data()