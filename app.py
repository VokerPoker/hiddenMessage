from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from pydub import AudioSegment
import numpy as np
import os
import re

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Указываем путь к ffmpeg, если требуется
AudioSegment.converter = r"A:\\ffmpeg\\ffm\\bin\\ffmpeg.exe"

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
    bits = (samples & mask).astype(np.uint8)
    return ''.join(str(b) for b in bits)

def bits_to_text(bits):
    bit_string = bits[:len(bits) - (len(bits) % 8)]  # Делаем длину кратной 8
    if not bit_string or '1' not in bit_string:
        return "No hidden message found"
    
    bytes_list = [bit_string[i:i+8] for i in range(0, len(bit_string), 8)]
    
    try:
        decoded_bytes = bytes([int(b, 2) for b in bytes_list])
        decoded_text = decoded_bytes.decode("utf-8", errors="ignore")
        
        # Обрезаем по первому `\0` (конец сообщения)
        cleaned_text = decoded_text.split("\0")[0]

        # Оставляем только печатные символы
        final_text = re.sub(r'[^\x20-\x7E]', '', cleaned_text).strip()
        
        return final_text if final_text else "No hidden message found"
    except:
        return "Error decoding message"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze_audio():
    if 'file' not in request.files:
        return jsonify({"error": "Файл не найден"}), 400
    
    file = request.files['file']
    file_path = os.path.join("temp", file.filename)
    file.save(file_path)

    samples, _ = load_audio(file_path)
    if samples is None:
        return jsonify({"error": "Ошибка обработки файла"}), 500

    hidden_bits = extract_lsb(samples)
    extracted_text = bits_to_text(hidden_bits)

    return jsonify({"filename": file.filename, "message": extracted_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
