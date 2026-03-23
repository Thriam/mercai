# UTChatbot AI ChatBot

## Overview
**UTChatbot** is a lightweight, local-first AI chatbot specialized in Mercedes engine maintenance queries. It uses a simple Flask backend integrated with local Ollama (tinyllama model) for responses, with conversation memory. A Node.js Express frontend serves static files from `public/` and proxies chat requests to the backend.

- **Core Paradigm**: Local LLM inference (no API keys needed), basic memory for context.
- **LLM Backend**: Ollama tinyllama model (`http://localhost:11434`).
- **Theme**: Engine maintenance queries (prompt-enforced).
- **Status**: Ready to run locally after starting Ollama.

## Architecture & Flow
```
Frontend (localhost:3000/public/index.html + JS)
    ↓ POST /api/chat
Node.js server.js → proxy → 
    ↓ POST /chat
Flask app.py
    ↓ build_prompt() (memory + 'engine maintenance' context)
    ↓ call_ollama()
    ↓ update_memory()
    ↓ return response
```

## Key Components

### Backend (app.py - Flask)
- **Memory**: Global `chat_memory` list (last 10 exchanges).
- **Prompt Building**: Appends history + enforces engine maintenance context.
- **Ollama Client**: Direct POST to `/api/generate` (stream=False).
- **Endpoints**:
  - `POST /chat`: Receives `{\"message\": \"user input\"}`, returns `{\"response\": \"bot reply\"}`.
  - `GET /`: Health check \"🚀 Local Ollama Chatbot Running\".
- **Config**: `OLLAMA_URL = \"http://localhost:11434/api/generate\"`, `MODEL_NAME = \"tinyllama\"`.

### Frontend (server.js - Express)
- Serves `public/` static files (e.g., index.html with chat UI).
- **Proxy**: `POST /api/chat` forwards to Flask `localhost:5000/chat`.
- **Port**: 3000.

### Data Flow
- No persistent storage/vector DB; in-memory only.
- Memory prune: Keeps ≤10 messages.

## Configuration
Hard-coded in `app.py`. Update `OLLAMA_URL`/`MODEL_NAME` if changing Ollama setup.

## Dependencies

**Backend** (requirements.txt):
```
flask
requests
```

**Frontend** (package.json):
```
express@^4.18.2
```
Scripts: `npm start` (runs `node server.js`).

## Running the ChatBot

### Prerequisites
1. Install [Ollama](https://ollama.com), run `ollama pull tinyllama`.

### Backend
```
cd Mercedes_AI_Project/utchatbot
pip install -r requirements.txt
python app.py  # Runs on http://localhost:5000
```

### Frontend (in separate terminal)
```
cd Mercedes_AI_Project/utchatbot
npm install
npm start  # Runs on http://localhost:3000
```

### Test
- Open http://localhost:3000 (assumes public/index.html has chat UI).
- Chat about engine issues, e.g., \"My Mercedes engine is overheating.\"

## Sample Interaction
**User**: Engine light on, rough idle.  
**Bot**: [Ollama response grounded in maintenance context, with history].

## Strengths & Notes
- **Zero-cost**: Fully local, no cloud APIs/keys.
- **Simple**: Easy to hack/extend (add RAG, better memory, UI).
- **Memory**: Basic context retention.
- **TODO** (from existing TODO.md): Enhance UI in public/index.html if needed.

This document summarizes the UTChatbot project structure, setup, and usage based on source files.

