from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Set your API keys here
WHISPER_API_KEY = "your_whisper_api_key"
OPENAI_API_KEY = "your_openai_api_key"

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    filename = file.filename
    file.save(filename)
    
    # Send to Whisper API for transcription
    headers = {"Authorization": f"Bearer {WHISPER_API_KEY}"}
    files = {"file": open(filename, 'rb')}
    response = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files)
    
    os.remove(filename)
    if response.status_code != 200:
        return jsonify({"error": "Failed to transcribe"}), 500
    
    transcription = response.json().get("text", "")
    return jsonify({"transcription": transcription})

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": f"Summarize this: {text}"}]
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
    
    if response.status_code != 200:
        return jsonify({"error": "Failed to summarize"}), 500
    
    summary = response.json()["choices"][0]["message"]["content"]
    return jsonify({"summary": summary})

if __name__ == '__main__':
    app.run(debug=True)
