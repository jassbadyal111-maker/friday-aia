from flask import Flask, request, jsonify, send_from_directory
import requests, json, os

app = Flask(__name__, static_folder="static")

# STATIC FIX
@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory('static', filename)

# LOAD CONFIG (model only)
with open("config.json", "r") as f:
    cfg = json.load(f)

MODEL = cfg.get("MODEL", "llama-70b-instruct")

# API KEY FROM RENDER ENV VARIABLE
API_KEY = os.environ.get("OPENROUTER_API_KEY")

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    msg = data.get("message", "")

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are Friday — a helpful, polite Hinglish AI."
            },
            {
                "role": "user",
                "content": msg
            }
        ],
        "temperature": 0.3,
        "max_tokens": 800
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=40)
        j = r.json()
        reply = j["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": "Error: " + str(e)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)