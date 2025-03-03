from pydub import AudioSegment
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re

AudioSegment.converter = r"A:\\ffmpeg\\ffm\\bin\\ffmpeg.exe"

app = Flask(__name__)
CORS(app)
os.makedirs("temp", exist_ok=True)

def load_audio(file_path):
    try:
        audio = AudioSegment.from_file(file_path)
        samples = np.array(audio.get_array_of_samples(), dtype=np.int16)
        return samples, audio.frame_rate
    except Exception as e:
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
    
    text = ''.join(chars).strip()
    return text if text else "No hidden message found"

def plot_lsb(hidden_bits):
    plt.figure(figsize=(12, 5))
    plt.plot(hidden_bits[:500], linestyle='-', marker='o', markersize=2)
    plt.xlabel("Семплы")
    plt.ylabel("Младший бит")
    plt.title("График младших битов аудиофайла")
    plt.grid()
    plt.show()

@app.route("/analyze", methods=["POST"])
def analyze_audio():
    if 'file' not in request.files:
        return jsonify({"error": "Файл не найден"}), 400
    
    file = request.files['file']
    file_path = os.path.join("temp", file.filename)
    file.save(file_path)
    
    samples, frame_rate = load_audio(file_path)
    if samples is None:
        return jsonify({"error": "Ошибка обработки файла"}), 500
    
    hidden_bits = extract_lsb(samples)
    extracted_text = bits_to_text(hidden_bits)
    
    return jsonify({"filename": file.filename, "message": extracted_text})

@app.route('/')
def home():
    return "Backend is running!"

if __name__ == "__main__":
    app.run(debug=True)
