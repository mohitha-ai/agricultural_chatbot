import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from google import genai
from google.genai import types
from chatbot_config import SYSTEM_PROMPT

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.1-flash-lite"

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in the .env file.")

client = genai.Client(api_key=API_KEY)

@app.route("/")
def home():
    return render_template("index.html")

@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    user_message = str(data.get("message", "")).strip()

    if not user_message:
        return jsonify({"error": "Please enter a question."}), 400

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            ),
        )
        return jsonify({"answer": response.text or "I could not generate a response."})
    except Exception:
        return jsonify({"error": "Unable to get a response right now. Please try again."}), 500

if __name__ == "__main__":
    app.run(debug=True)
