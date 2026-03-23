# Task2: Store AI Agent Chatbot (CSV-based Product Query System)

## Overview
A RAG (Retrieval-Augmented Generation) AI agent that answers customer queries about store products using CSV data. Users can ask questions like "Show me products over $50", "What products have 5-star ratings?", or "Find items in stock with the best ratings" and the system retrieves and synthesizes answers.

- **Core Paradigm**: CSV-based product retrieval + LLM synthesis for natural language responses.
- **LLM Backend**: OpenRouter GPT-4o (compatible with AutomotiveRAGFlow).
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 for product description vectorization.
- **Vector Store**: JSON file (`vectors.json`) with product embeddings, metadata (id, price, quantity, rating, description).
- **Data Source**: CSV file with columns: `id`, `price`, `quantity`, `rating`.

## Architecture & Pipeline Flow

```
User Query (main.py interactive loop)
    ↓
1. QueryHandler.process() → normalized_query payload (intent detection)
    ↓
2. Retriever.retrieve() → top-K products via embedding similarity
    - EmbeddingService.embed_text(query)
    - VectorStore.search(embedding, top_k=5)
    ↓
3. ProductQueryEngine.query()
    - build_product_query_prompt(payload, products) → structured JSON prompt
    - LLMClient.generate(prompt) → raw text → parse_json_response()
    - ConfidenceScorer.score(products, response) → 0-1 float
    ↓ Response JSON: {query_summary, filtered_products[], recommendations, confidence}
    ↓
4. ClarificationEngine.evaluate() → needs_clarification?, clarification_question
    ↓
5. ResponseBuilder.build() → formatted final response with product listing
    ↓ Output: response, needs_clarification, query_result, retrieved_products
```

## Key Components

### 1. Orchestrator & Pipeline
- `app/core/orchestrator.py`: Thin wrapper: `pipeline.run(user_query)`.
- `app/core/pipeline.py`: Coordinates all steps, initializes handlers/engines.
- `app/core/state.py`: PipelineState dataclass tracking execution.

### 2. Data Ingestion (app/data/)
- **CSV Structure**: `id`, `price`, `quantity`, `rating` (+ optional: name, description, category)
- `app/data/raw/products.csv`: Source CSV file.
- `app/data/processed/products_chunks.json`: Chunked/formatted product data with enhanced descriptions.
- `app/data/vector_db/vectors.json`: Embeddings for all products (for semantic search).

### 3. Retrieval (app/retrieval/)
- `app/retrieval/csv_loader.py`: Load and parse CSV → product objects.
- `app/retrieval/retriever.py`: Embeds query, searches vector store, returns top-K products.
- Support batch ingestion via `ingest.py`.

### 4. LLM Integration (app/llm/)
- `app/llm/llm_client.py`: OpenRouter `/chat/completions` (reuse from AutomotiveRAGFlow).
- `app/llm/prompt_templates.py`: `build_product_query_prompt()` with JSON schema.
  - Input: user query + top-K retrieved products.
  - Output: { query_summary, filtered_products: [{id, price, quantity, rating, reason}], recommendations, confidence }.

### 5. Query Engine & Scoring (app/query_engine/)
- `app/query_engine/product_query_engine.py`: LLM call + parsing + confidence scoring.
- `app/query_engine/confidence_scorer.py`: Heuristic score (retrieval quality, match relevance).
- Query rewriter + intent detector (reuse templates from AutomotiveRAGFlow).

### 6. Loop & Polish (app/loop/)
- `app/loop/clarification_engine.py`: Ask for clarification if low confidence or ambiguous intent.
- `app/loop/response_builder.py`: Format results into user-friendly text with product table.

### 7. Query Handler (app/query/)
- `app/query/query_handler.py`: Normalize query, detect intent (filter, sort, search, compare).
- `app/query/intent_detector.py`: Classify as price_filter, rating_filter, stock_check, etc.

## Configuration (app/config/settings.py)
- Loaded from `.env`.
- Key vars:
  - `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, `OPENROUTER_MODEL`
  - `EMBEDDING_MODEL` (sentence-transformers/all-MiniLM-L6-v2)
  - `DATA_DIR`, `PROCESSED_DIR`, `VECTOR_DB_DIR`
  - `CSV_FILE_PATH`: Path to products.csv
  - `TOP_K=5`: Number of product results to retrieve
  - `CHUNK_SIZE=500`: For future multi-chunk product descriptions

## Dependencies (requirements.txt)
```
python-dotenv
sentence-transformers
numpy
requests
pandas
```

## File Structure
```
Store_AI_agent_cum_chatbot/
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py            # Configuration from .env
│   │   └── logging_config.py       # Logging setup
│   ├── core/
│   │   ├── __init__.py
│   │   ├── orchestrator.py         # Main entry point
│   │   ├── pipeline.py             # Orchestrates pipeline steps
│   │   └── state.py                # PipelineState dataclass
│   ├── data/
│   │   ├── raw/
│   │   │   └── products.csv        # Source data
│   │   ├── processed/
│   │   │   └── products_chunks.json # Processed chunks
│   │   └── vector_db/
│   │       └── vectors.json        # Embeddings
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── csv_loader.py           # CSV parsing
│   │   ├── retriever.py            # Embedding + similarity search
│   │   └── embedding_service.py    # Embedding generation
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── llm_client.py           # OpenRouter client
│   │   └── prompt_templates.py     # Product query prompts
│   ├── query_engine/
│   │   ├── __init__.py
│   │   ├── product_query_engine.py # Core query logic
│   │   └── confidence_scorer.py    # Scoring
│   ├── query/
│   │   ├── __init__.py
│   │   ├── query_handler.py        # Query preprocessing
│   │   ├── intent_detector.py      # Intent classification
│   │   └── query_rewriter.py       # Query rewriting
│   └── loop/
│       ├── __init__.py
│       ├── clarification_engine.py # Clarification logic
│       └── response_builder.py     # Response formatting
├── .env.example                    # Environment template
├── .env                            # (Set by user)
├── ingest.py                       # Data ingestion script
├── main.py                         # Interactive CLI
└── requirements.txt
```

## Data Pipeline

### Step 1: CSV Ingestion (ingest.py)
```
products.csv (raw)
    ↓
1. CSVLoader.load() → List[Product]
2. EmbeddingService.embed_products() → embeddings for each product
3. VectorStore.save() → products_chunks.json, vectors.json
```

### Step 2: Query Execution (main.py)
```
User Query
    ↓
QueryHandler → Orchestrator.pipeline.run()
    ↓ (retrieval, query engine, scoring, formatting)
Final Response (with product table + reasoning)
```

## Running the Agent

### Setup
1. Create `.env` file:
   ```
   OPENROUTER_API_KEY=your_key
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   OPENROUTER_MODEL=gpt-4o
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   CSV_FILE_PATH=app/data/raw/products.csv
   DATA_DIR=app/data
   PROCESSED_DIR=app/data/processed
   VECTOR_DB_DIR=app/data/vector_db
   TOP_K=5
   ```
2. Place `products.csv` in `app/data/raw/`.

### Execution
```bash
python ingest.py       # Build vectors from CSV
python main.py         # Interactive: Enter query → Get results
```

## Example Interactions

### Query 1: Price Filter
**User**: "Show me products under $100"
```
Retrieved Products: [id:1, price:50, rating:4.5], [id:3, price:75, rating:4.0], ...
LLM Response: Filtered to 3 products matching criteria...
```

### Query 2: Rating Filter
**User**: "Find all products with 5-star ratings"
```
Retrieved Products: [id:5, rating:5.0], [id:7, rating:5.0], ...
LLM Response: Found 2 products with 5-star ratings...
```

### Query 3: Stock + Rating
**User**: "Show highly-rated products that are in stock"
```
Retrieved Products: [id:2, quantity:10, rating:4.8], ...
LLM Response: Found 4 products with good ratings and inventory...
```

## Sample Output Structure
```
--- QUERY RESULT ---
Query: "Find products under $50 with ratings > 4"
Matching Products:
  • Product ID: 2, Price: $45, Rating: 4.5/5, Stock: 15
  • Product ID: 5, Price: $30, Rating: 4.8/5, Stock: 8
Confidence: 0.92

--- RAW JSON ---
{
  "query_summary": "Price filter (< $50) + Rating filter (> 4.0)",
  "filtered_products": [
    {"id": 2, "price": 45, "quantity": 15, "rating": 4.5, "reason": "Matches price and rating criteria"},
    ...
  ],
  "recommendations": "Consider checking reviews for product 2.",
  "confidence": 0.92
}
```

## Testing Checklist
- [ ] CSV loading works correctly
- [ ] Embeddings are generated and stored
- [ ] Retrieval returns sensible results
- [ ] LLM generates valid JSON responses
- [ ] Confidence scoring is reasonable
- [ ] Clarification loop triggers when appropriate
- [ ] Response formatting is user-friendly
- [ ] End-to-end query works (ingest → query → response)

## Strengths & Design Decisions
- **CSV-Native**: Direct product data without complex chunking (already structured).
- **Semantic Search**: Users can query using natural language ("expensive items", "highly-rated products").
- **LLM Synthesis**: Multiple filters + ranking logic handled by LLM for flexibility.
- **Confidence-Aware**: Scores and clarifies low-confidence results.
- **Modular**: Same architecture as AutomotiveRAGFlow for consistency.

## Migration Path (from AutomotiveRAGFlow)
1. Reuse: `config/`, `llm/llm_client.py`, `loop/`, `core/state.py`.
2. Adapt: `prompt_templates.py` for product queries (simpler than diagnostics).
3. New: `retrieval/csv_loader.py`, `query_engine/product_query_engine.py`.
4. Simplify: No need for PDF extraction or complex chunking.
