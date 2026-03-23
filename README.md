# MercAI

**Key Features:**
- PDF extraction and semantic chunking
- Vector database integration for retrieval
- LLM orchestration with custom prompts
- Diagnosis engine with confidence scoring
- Clarification and feedback handling
- Processed data pipeline (raw → processed → vector_db)

## Quick Start

1. **Install Dependencies:**
   ```
   cd AutomotiveRAGFlow
   pip install -r requirements.txt
   ```

2. **Ingest Data:**
   ```
   python ingest.py
   ```
   Place raw PDFs in `app/data/raw/`.

3. **Run the Application:**
   ```
   streamlit run main.py
   ```
   Or use `app/core/orchestrator.py` for API mode.

## Project Structure

```
AutomotiveRAGFlow/
├── ingest.py          # Data ingestion script
├── main.py            # Streamlit app entry
├── requirements.txt
└── app/
    ├── config/        # Settings, logging
    │   └── settings.py
    ├── core/          # Pipeline, orchestrator, state
    ├── data/          # raw/, processed/, vector_db/
    ├── diagnosis/     # Confidence scorer, engine, response builder
    ├── extraction/    # PDF extractor, chunker, text cleaner
    ├── llm/           # LLM client, prompts
    ├── loop/          # Clarification, feedback
    └── utils/         # Utilities
```

Legacy projects:
- `Mercedes_AI_Project/`: Early chatbots and vector DB prototypes.

## Configuration

Edit `app/config/settings.py` for:
- LLM provider/API keys
- Vector DB path (`app/data/vector_db/`)
- Chunk size/overlap
- Logging levels

## Usage

**Example Query:**
```
User: "Mercedes C-Class P0300 misfire code"
RAG Response: Retrieves relevant sections, diagnoses possible causes (ignition coil, spark plugs), confidence: 92%, suggestions.
```

**Data Flow:**
```
Raw PDFs → Extraction/Chunking → Embeddings → Vector DB → Retrieval → LLM → Diagnosis → Response
             ↑ Feedback Loop for clarification
```

## Contributing

1. Add new prompt templates in `app/llm/prompt_templates.py`
2. Extend diagnosis rules in `app/diagnosis/`
3. Test with new automotive datasets.

## Next Steps
- Multi-modal support (images/DTC scans)
- Deploy to cloud (FastAPI + Docker)
- UI improvements
