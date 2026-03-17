import requests
from flask import Flask, request, jsonify

# ============================
# CONFIG (LOCAL ONLY)
# ============================
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "tinyllama"

app = Flask(__name__)

# ============================
# SIMPLE IN-MEMORY STORE
# ============================
chat_memory = []

def update_memory(user, bot):
    chat_memory.append({"user": user, "bot": bot})
    if len(chat_memory) > 10:
        chat_memory.pop(0)

def build_prompt(user_input):
    context = ""

    for chat in chat_memory:
        context += f"User: {chat['user']}\nAssistant: {chat['bot']}\n"

    return f"""
    This user input is regarding engine maintanence
    {user_input}"""

# ============================
# OLLAMA CALL (NO KEY)
# ============================
def call_ollama(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]

# ============================
# CHAT ENDPOINT
# ============================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message")

    prompt = build_prompt(user_input)
    bot_response = call_ollama(prompt)

    update_memory(user_input, bot_response)

    return jsonify({
        "response": bot_response
    })

# ============================
# ROOT
# ============================
@app.route("/")
def home():
    return "🚀 Local Ollama Chatbot Running (No API Key)"

# ============================
# RUN
# ============================
if __name__ == "__main__":
    app.run(debug=True, port=5000)
