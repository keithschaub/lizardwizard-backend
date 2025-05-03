from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    image_url = data.get("imageUrl")
    if not image_url:
        return jsonify({"error": "Missing imageUrl"}), 400

    try:
        response = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that identifies Lizard Wizard cards."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is the full name and school of this card?"},
                        {"type": "image_url", "image_url": {"url": image_url }}
                    ]
                }
            ],
            max_tokens=300
        )

        prediction = response.choices[0].message.content
        return jsonify({"prediction": prediction})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)