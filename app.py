from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import os
import openai

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS for all origins

openai.api_key = os.getenv("OPENAI_API_KEY")  # Make sure this is set on Render

@app.route("/predict", methods=["POST"])
def predict():
    print("⏱ Received request, starting processing...")
    data = request.get_json()
    image_url = data.get("imageUrl")
    if not image_url:
        return jsonify({"error": "No image URL provided"}), 400

    print(f"📥 Downloading image from: {image_url}")
    try:
        image_response = requests.get(image_url)
        image_bytes = image_response.content
    except Exception as e:
        print(f"❌ Error downloading image: {e}")
        return jsonify({"error": "Failed to download image"}), 500

    print("🔁 Sending image to OpenAI...")
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",  # or "gpt-4o" if you want newer model
            messages=[
                {
                    "role": "user",
                    "content": [
                        { "type": "text", "text": "What is the name and school of this Lizard Wizard card?" },
                        { "type": "image_url", "image_url": { "url": image_url } }
                    ]
                }
            ],
            max_tokens=300
        )
        result = response.choices[0].message.content
        print("✅ OpenAI response received, sending back to client.")
        return jsonify({ "prediction": result })

    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return jsonify({ "error": "OpenAI API request failed" }), 500



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
