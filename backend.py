from flask import Flask, request, jsonify
from flask_cors import CORS
from pydub import AudioSegment
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import os

app = Flask(__name__)
CORS(app)  # Включаем CORS
os.makedirs("temp", exist_ok=True)

def load_audio(file_path):
    try:
        audio = AudioSegment.from_file(file_path)
        samples = np.array(audio.get_array_of_samples(), dtype=np.int16)
        return samples, audio.frame_rate
    except Exception:
        return None, None

def extract_lsb(samples, num_bits=1):
    mask = (1 << num_bits) - 1
    return (samples & mask).astype(np.uint8)

def bits_to_text(bits):
    bit_string = ''.join(map(str, bits))
    bit_string = bit_string[:len(bit_string) - (len(bit_string) % 8)]
    
    if not bit_string or '1' not in bit_string:
        return "No hidden message found"
    
    chars = []
    for i in range(0, len(bit_string), 8):
        byte = bit_string[i:i+8]
        char = chr(int(byte, 2))
        if char.isprintable():
            chars.append(char)
        else:
            break
    
    return ''.join(chars).strip() or "No hidden message found"

def generate_waveform(samples):
    plt.figure(figsize=(10, 4))
    plt.plot(samples, alpha=0.7)
    plt.title("Audio Waveform")
    plt.xlabel("Time")
    plt.ylabel("Amplitude")

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)

    return base64.b64encode(img.getvalue()).decode("utf-8")

@app.route("/analyze", methods=["POST"])
def analyze_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    file_path = os.path.join("temp", file.filename)
    file.save(file_path)

    samples, _ = load_audio(file_path)
    if samples is None:
        return jsonify({"error": "Error processing file"}), 500

    hidden_bits = extract_lsb(samples)
    extracted_text = bits_to_text(hidden_bits)
    waveform_img = generate_waveform(samples)

    return jsonify({"message": extracted_text, "waveform": waveform_img})

@app.route("/")
def home():
    return "Backend is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
