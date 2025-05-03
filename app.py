from flask import Flask, request, jsonify
import openai
import os
import time

app = Flask(__name__)

# Set your OpenAI API key as an environment variable in Render
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/")
def index():
    return "🧙‍♂️ Lizard Wizard Backend is alive."

@app.route("/predict", methods=["POST"])
def predict():
    start_time = time.time()
    print("⏱ Received request, starting processing...")

    try:
        data = request.get_json()
        image_url = data.get("imageUrl")
        if not image_url:
            print("❌ No imageUrl provided.")
            return jsonify({"error": "No imageUrl provided"}), 400

        print(f"📥 Downloading image from: {image_url}")
        print("🔁 Sending image to OpenAI...")

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that identifies cards from the board game Lizard Wizard."
                },
                {
                    "role": "user",
                    "content": [
                        { "type": "text", "text": "What is the name and school of this card?" },
                        { "type": "image_url", "image_url": { "url": image_url } }
                    ]
                }
            ],
            max_tokens=200
        )

        result = response.choices[0].message.content
        elapsed = round(time.time() - start_time, 2)
        print(f"✅ OpenAI response received in {elapsed}s. Sending back to client.")

        return jsonify({"prediction": result})

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
