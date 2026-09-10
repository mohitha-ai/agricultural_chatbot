import os
import logging

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from google import genai
from google.genai import types

from chatbot_config import SYSTEM_PROMPT

load_dotenv()

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.1-flash-lite"

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set.")

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

        answer = response.text

        if not answer:
            return jsonify({"error": "Gemini returned an empty response."}), 500

        return jsonify({"answer": answer})

    except Exception as error:
        app.logger.exception("Gemini API error: %s", error)
        return jsonify({
            "error": "Gemini API error. Please check the Render logs."
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
