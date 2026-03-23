# Store AI Agent Cum Chatbot

A RAG (Retrieval-Augmented Generation) chatbot that helps customers find products from a CSV file using natural language queries.

## Quick Start

1. **Create .env file:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENROUTER_API_KEY
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare data:**
   - Place your `products.csv` in `app/data/raw/`
   - CSV must have columns: `id`, `price`, `quantity`, `rating`
   - Optional columns: `name`, `description`, `category`, etc.

4. **Ingest data:**
   ```bash
   python ingest.py
   ```

5. **Run chatbot:**
   ```bash
   python main.py
   ```

## Architecture

See `../Task2_Store_bot.md` for detailed architecture and implementation guide.

### Core Components:
- **Retrieval**: CSV loading + semantic search via embeddings
- **Query Engine**: LLM-powered product filtering and ranking
- **Confidence Scoring**: Evaluates result quality
- **Clarification Loop**: Asks follow-up questions when needed

## Example Queries

- "Show me products under $100"
- "Find all highly-rated products"
- "What products have 5-star ratings?"
- "Show products in stock with good ratings"
- "Find expensive items"

## Configuration

All settings are in `app/config/settings.py`, loaded from `.env`:
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `OPENROUTER_MODEL`: Model to use (default: gpt-4o)
- `EMBEDDING_MODEL`: Embedding model (default: sentence-transformers/all-MiniLM-L6-v2)
- `CSV_FILE_PATH`: Path to products.csv
- `TOP_K`: Number of products to retrieve (default: 5)

## Data Format

### products.csv
```
id,price,quantity,rating
1,50.00,10,4.5
2,75.00,5,4.8
3,25.00,20,3.9
```

Additional columns (optional): name, description, category, etc.

## Dependencies

- `sentence-transformers`: For semantic embeddings
- `requests`: HTTP client for OpenRouter API
- `pandas`: CSV handling
- `numpy`: Numerical operations
- `python-dotenv`: Environment variable loading

## Testing

Run test queries to verify the agent is working:
1. Ingest sample data: `python ingest.py`
2. Start chatbot: `python main.py`
3. Enter test queries and verify responses

## Troubleshooting

- **"OPENROUTER_API_KEY is not set"**: Create .env file with valid API key
- **"CSV file not found"**: Place products.csv in app/data/raw/
- **"No vectors found"**: Run `python ingest.py` first

## Reference

Based on AutomotiveRAGFlow architecture adapted for product queries.
