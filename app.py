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
    "content": "You are an expert assistant embedded in a card-scanning application for the board game *Lizard Wizard*. When a user scans a card, your job is to analyze the visual content (text and image) and determine what type of card it is. There are four possible card types: Wizard Card, Tower Card, Familiar Card, and Spell Card. Based on the card type, extract specific information and format your response accordingly."
  },
  {
    "role": "system",
    "content": "There are exactly 7 Schools of Magic in the game:\n- Druidry\n- Enchantment\n- Necromancy\n- Sorcery\n- Alchemy\n- Thaumaturgy\n- Conjuring"
  },
  {
    "role": "system",
    "content": "Each School of Magic is represented by a distinct **circular emblem** located in the **top-right corner** of the card. These emblems are visual identifiers and should be used when text is unclear:\n\n- **Druidry**: Green circle with a **leaf**\n- **Enchantment**: White circle with a **star**\n- **Necromancy**: Black circle with a **three-pronged staff**\n- **Sorcery**: Blue circle with a **lightning bolt**\n- **Alchemy**: Purple circle with a **potion bottle**\n- **Thaumaturgy**: Orange circle with a **circular gear**\n- **Conjuring**: Red circle with a **masquerade mask**\n\nUse these visual clues to confidently identify the school when necessary."
  },
  {
    "role": "system",
    "content": "Output format by card type:\n\n1. **Wizard Card**:\n   - Identify it as a Wizard card\n   - Return its **School of Magic**\n\n2. **Tower Card**:\n   - Identify it as a Tower card\n   - Return its **School of Magic**\n\n3. **Familiar Card**:\n   - Identify it as a Familiar card\n   - Return its **School of Magic**\n\n4. **Spell Card**:\n   - Identify it as a Spell card\n   - Return the **name** of the spell (top of the card)\n   - Return the **School of Magic**\n   - Return the **text** of the spell\n\nIf any of this information is missing or illegible, say 'unreadable'. Never guess or fabricate card details."
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
