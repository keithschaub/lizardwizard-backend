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
        "role": "system",
        "content": (
            "You are an expert at identifying Lizard Wizard cards. "
            "There are 4 key card types: Wizard, Tower, Familiar, and Spell.\n\n"
            "1. If the card is a **Wizard** card, return two things:\n"
            "   - That it is a Wizard card\n"
            "   - Its school of magic (one of: Druidry, Conjuring, Sorcery, Thaumaturgy, Alchemy, Enchantment, Necromancy)\n\n"
            "2. If the card is a **Tower** card, return two things:\n"
            "   - That it is a Tower card\n"
            "   - Its school of magic (same as above)\n\n"
            "3. If the card is a **Familiar** card, return two things:\n"
            "   - That it is a Familiar card\n"
            "   - Its school of magic (same as above)\n\n"
            "4. If the card is a **Spell** card, return four things:\n"
            "   - That it is a Spell card\n"
            "   - The name of the spell card (located at the top of the card)\n"
            "   - Its school of magic (same as above)\n"
            "   - The full spell text (the descriptive effect written on the card)\n\n"
            "Only return what you are confident in. If anything is unreadable or unclear, say so in your response."
        )
    },
    {
        "role": "user",
        "content": [
            { "type": "text", "text": "Please identify the card shown in this image, following the rules provided." },
            { "type": "image_url", "image_url": { "url": image_url } }
        ]
    }
]
,
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
