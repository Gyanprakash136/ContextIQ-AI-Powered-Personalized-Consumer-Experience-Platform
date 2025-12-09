
# ContextIQ Backend

ContextIQ is an intelligent, context-aware shopping assistant powered by Google Gemini 2.5 Pro, ChromaDB, and FastAPI. It features Agentic RAG, multimodal understanding (text, image, links), and predictive insights.

## Features
- **Agentic RAG**: Retrieves relevant products from the catalog based on user query and context.
- **Multimodal Input**: Understands text, image uploads, and external links (via scraping).
- **Predictive Engine**: Anticipates future user needs based on current purchases.
- **Persistent Memory**: Maintains user session history and context.

## Prerequisites
- Python 3.10+
- Google Cloud API Key (with access to Gemini 2.5 Pro)

## Setup
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: valid requirements are in `requirements.txt` - ensure google-adk is removed if not available using the cleaned version)*

   Actually, use:
   ```bash
   pip install fastapi uvicorn python-dotenv pandas chromadb google-generativeai pydantic python-multipart requests beautifulsoup4 pillow
   ```

2. **Environment Variables**:
   Create a `.env` file:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```

3. **Ingest Data**:
   Populate the vector database with the product catalog:
   ```bash
   python tools/ingest.py
   ```

## Running the Server
Start the production server:
```bash
bash run.sh
```
The API will be available at `http://localhost:8002/agent/chat` (Check run.sh for port).

## API Endpoint
**POST** `/agent/chat`
- `user_id` (string): Unique user identifier.
- `message` (string): User's text query.
- `context_link` (string): Optional URL to analyze.
- `image` (file): Optional image file for visual context.

## Architecture
- **Core**: `core/shim.py` (Agent Logic), `core/agent_builder.py`
- **Tools**: `tools/scraper.py`, `tools/vector_db.py`, `tools/predictor.py`
- **Memory**: `sessions/` (Pickle-based history), `chroma_data/` (Vector Store)

## License
Hackathon usage.
