# --- Witcher Emotion Game ---
import os
import time
import threading
import json
import webbrowser
import tkinter as tk
from tkinter import messagebox, simpledialog
from flask import Flask, request, jsonify, render_template, send_from_directory
import socket
import cv2
from fer import FER
from datetime import datetime

# --- Constants ---
EMOTION_COOLDOWN = 3
POLLING_INTERVAL = 2
VOLUME_DEFAULT = 20

# --- Emotion Detection Setup ---
detector = FER()
cap = cv2.VideoCapture(0)
last_detected_emotion = None
last_emotion_time = 0

# --- Emotion → Option Mapping ---
emotion_map = {
    'happy': 0,
    'sad': 1,
    'angry': 2,
}

# --- Flask Setup ---
app = Flask(__name__, static_folder='static', template_folder='templates')

# --- IP Detection ---
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

SERVER_IP = get_ip()
SERVER_PORT = 5001

# --- Paths ---
base_path = os.path.dirname(os.path.abspath(__file__))
twee_file_path = os.path.join(base_path, "A_Witchers_Story.twee")
audio_dir = os.path.join(base_path, "static", "music")
image_dir = os.path.join(base_path, "static", "images")
static_dir = os.path.join(base_path, "static")
templates_dir = os.path.join(base_path, "templates")

# --- Static File Checks ---
def setup_static_dirs():
    css_path = os.path.join(static_dir, 'style.css')
    js_path = os.path.join(static_dir, 'script.js')
    html_path = os.path.join(templates_dir, 'index.html')

    print(f"✅ Found CSS file at {css_path}" if os.path.exists(css_path) else f"❌ Missing CSS: {css_path}")
    print(f"✅ Found JS file at {js_path}" if os.path.exists(js_path) else f"❌ Missing JS: {js_path}")
    print(f"✅ Found HTML template at {html_path}" if os.path.exists(html_path) else f"❌ Missing HTML: {html_path}")

    if os.path.exists(static_dir):
        print(f"📂 Static files found: {', '.join(os.listdir(static_dir))}")
    if os.path.exists(templates_dir):
        print(f"📂 Template files found: {', '.join(os.listdir(templates_dir))}")

# --- GUI Prompt for IP Display ---
def show_api_window():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Witcher Emotion API", f"API is live at http://{SERVER_IP}:{SERVER_PORT}")
    root.destroy()

# --- Story Engine ---
class Story:
    def __init__(self, path):
        self.passages = self.parse_twee_file(path)
        self.current_passage_name = "Start"
        self.current_passage = self.passages.get("Start", "")

    def parse_twee_file(self, path):
        passages = {}
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        for block in content.split('::')[1:]:
            lines = block.strip().split('\n')
            title = lines[0].split('{')[0].strip()
            text = '\n'.join(lines[1:]).strip()
            passages[title] = text
        return passages

    def choose_option(self, name):
        if name in self.passages:
            self.current_passage_name = name
            self.current_passage = self.passages[name]

    def extract_options(self, text):
        options = []
        for line in text.split('\n'):
            if '[[' in line and '->' in line:
                opt, dest = line.strip('[] ').split('->')
                options.append({'text': opt.strip(), 'destination': dest.strip()})
        return options

    def get_current(self):
        return {
            'name': self.current_passage_name,
            'text': '\n'.join([l for l in self.current_passage.split('\n') if not l.startswith('[[')]),
            'options': self.extract_options(self.current_passage),
            'has_image': os.path.exists(os.path.join(image_dir, f"{self.current_passage_name}.jpg"))
        }

story = Story(twee_file_path)

# --- Emotion Detection Loop ---
def emotion_loop():
    global last_detected_emotion, last_emotion_time
    print("🎭 Emotion control started")
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        emotions = detector.detect_emotions(rgb)
        if emotions:
            detected = emotions[0]['emotions']
            emotion = max(detected, key=detected.get)
            now = time.time()
            if emotion != last_detected_emotion and (now - last_emotion_time > EMOTION_COOLDOWN):
                last_detected_emotion = emotion
                last_emotion_time = now
                print(f"🧠 Detected emotion: {emotion}")
                idx = emotion_map.get(emotion)
                if idx is not None:
                    options = story.extract_options(story.current_passage)
                    if idx < len(options):
                        story.choose_option(options[idx]['destination'])
        time.sleep(POLLING_INTERVAL)

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/api/passage')
def get_passage():
    return jsonify(story.get_current())

@app.route('/api/current_passage')
def get_current_passage():
    return jsonify(story.get_current())

@app.route('/api/last_emotion')
def get_last_emotion():
    return jsonify({"emotion": last_detected_emotion or "None"})

@app.route('/api/status')
def api_status():
    return jsonify({"api_connected": True, "mode": "emotions", "volume": VOLUME_DEFAULT})

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory(audio_dir, filename)

@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(image_dir, filename)

@app.route('/api/volume', methods=['POST'])
def update_volume():
    data = request.get_json()
    vol = data.get("volume", VOLUME_DEFAULT)
    return jsonify({"status": "success", "volume": vol})

@app.route('/api/reconnect')
def reconnect_api():
    return jsonify({"status": "success", "connected": True})

@app.route('/api/debug/endpoints')
def debug_endpoints():
    return jsonify({"available": ["/api/passage", "/api/status", "/api/current_passage", "/api/last_emotion"]})

@app.route('/get_logs')
def get_logs():
    return jsonify({"logs": ["2025-06-05 17:21:00 - Detected emotion: happy"]})

# --- Launcher ---
def launch():
    setup_static_dirs()
    show_api_window()

    threading.Thread(target=emotion_loop, daemon=True).start()
    threading.Thread(target=lambda: app.run(host=SERVER_IP, port=SERVER_PORT, debug=False, use_reloader=False), daemon=True).start()

    time.sleep(2)
    try:
        webbrowser.open(f"http://{SERVER_IP}:{SERVER_PORT}")
    except:
        print("Please open the browser manually at:", f"http://{SERVER_IP}:{SERVER_PORT}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")

if __name__ == '__main__':
    launch()
