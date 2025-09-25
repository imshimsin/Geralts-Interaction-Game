import cv2
from fer import FER
import tkinter as tk
from tkinter import scrolledtext, Button, messagebox
from datetime import datetime
from PIL import Image, ImageTk
import threading
import requests
import json
import os
from flask import Flask, request, jsonify, render_template_string
import webbrowser

# Flask app setup with proper name
app = Flask("emotion_detector")
SERVER_PORT = 5000
SERVER_HOST = '0.0.0.0'

# File to store logs persistently
LOGS_FILE = "emotion_logs.json"

# Get the server's actual IP address
import socket


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


SERVER_IP = get_ip()

# Load existing logs from file if available
all_logs = []


def load_logs_from_file():
    global all_logs
    if os.path.exists(LOGS_FILE):
        try:
            with open(LOGS_FILE, 'r') as f:
                all_logs = json.load(f)
            print(f"Loaded {len(all_logs)} logs from file")
        except Exception as e:
            print(f"Error loading logs from file: {e}")
            all_logs = []
    else:
        all_logs = []
        print("No existing logs file found, starting with empty logs")


# Initialize with empty logs
load_logs_from_file()


# Function to save logs to file
def save_logs_to_file():
    try:
        with open(LOGS_FILE, 'w') as f:
            json.dump(all_logs, f)
        print(f"Saved {len(all_logs)} logs to file")
    except Exception as e:
        print(f"Error saving logs to file: {e}")


# Create a simple HTML homepage for the API with auto-refresh
@app.route('/')
def home():
    html = """
	<!DOCTYPE html>
	<html>
	<head>
    	<title>Emotion Detection Logs</title>
    	<style>
        	body { font-family: Arial, sans-serif; margin: 20px; }
        	.container { max-width: 800px; margin: 0 auto; }
        	h1 { color: #333; }
        	#logs { margin-top: 20px; }
        	.log-entry { padding: 8px; border-bottom: 1px solid #eee; }
        	button { padding: 8px 15px; color: white; border: none; cursor: pointer; margin-top: 10px; margin-right: 10px; }
        	.green-button { background: #4CAF50; }
        	.red-button { background: #F44336; }
        	.status { color: #666; font-style: italic; margin-top: 10px; }
        	.button-group { display: flex; align-items: center; }
    	</style>
	</head>
	<body>
    	<div class="container">
        	<h1>Emotion Detection Logs</h1>
        	<div class="button-group">
            	<button class="green-button" onclick="fetchLogs()">Refresh Logs</button>
            	<button class="red-button" onclick="clearLogs()">Clear All Logs</button>
            	<span id="auto-refresh-status" class="status">Auto-refresh: ON (every 5 seconds)</span>
        	</div>
        	<div id="logs">
            	<p>Loading logs...</p>
        	</div>
    	</div>

    	<script>
        	// Fetch logs when page loads
        	document.addEventListener('DOMContentLoaded', fetchLogs);
       	 
        	// Set up auto-refresh
        	let autoRefreshInterval = setInterval(fetchLogs, 5000);
        	let autoRefreshEnabled = true;
       	 
        	// Toggle auto-refresh
        	function toggleAutoRefresh() {
            	if (autoRefreshEnabled) {
                	clearInterval(autoRefreshInterval);
                	autoRefreshEnabled = false;
                	document.getElementById('auto-refresh-status').textContent = 'Auto-refresh: OFF';
            	} else {
                	autoRefreshInterval = setInterval(fetchLogs, 5000);
                	autoRefreshEnabled = true;
                	document.getElementById('auto-refresh-status').textContent = 'Auto-refresh: ON (every 5 seconds)';
            	}
        	}
       	 
        	document.getElementById('auto-refresh-status').addEventListener('click', toggleAutoRefresh);

        	function fetchLogs() {
            	fetch('/get_logs')
                	.then(response => response.json())
                	.then(data => {
                    	const logsContainer = document.getElementById('logs');
                    	logsContainer.innerHTML = '';

                    	if (data.logs.length === 0) {
                        	logsContainer.innerHTML = '<p>No logs recorded yet.</p>';
                    	} else {
                        	data.logs.forEach(log => {
                            	const logElement = document.createElement('div');
                            	logElement.className = 'log-entry';
                            	logElement.textContent = log;
                            	logsContainer.appendChild(logElement);
                        	});
                    	}
                	})
                	.catch(error => {
                    	console.error('Error fetching logs:', error);
                    	document.getElementById('logs').innerHTML = '<p>Failed to load logs. Please try again later.</p>';
                	});
        	}
       	 
        	function clearLogs() {
            	if (confirm('Are you sure you want to clear all logs?')) {
                	fetch('/clear_logs', { method: 'POST' })
                    	.then(response => response.json())
                    	.then(data => {
                        	alert('All logs cleared successfully!');
                        	fetchLogs(); // Refresh the logs display
                    	})
                    	.catch(error => {
                        	console.error('Error clearing logs:', error);
                        	alert('Failed to clear logs. Please try again.');
                    	});
            	}
        	}
    	</script>
	</body>
	</html>
	"""
    return render_template_string(html)


@app.route('/endpoint', methods=['POST'])
def receive_logs():
    global all_logs
    data = request.get_json()
    if 'logs' in data:
        print(f"Received {len(data['logs'])} logs")
        # Add new logs to the beginning of the list
        all_logs = data['logs'] + all_logs
        # Save logs to file after each update
        save_logs_to_file()
        return jsonify({"message": "Logs received and saved!"}), 200
    else:
        return jsonify({"error": "No logs provided!"}), 400


@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    global all_logs
    all_logs = []
    save_logs_to_file()
    print("All logs cleared")
    return jsonify({"message": "All logs cleared"}), 200


@app.route('/get_logs', methods=['GET'])
def get_logs():
    return jsonify({"logs": all_logs})


# Start Flask API in a separate thread
def run_server():
    print(f"Starting server at http://{SERVER_IP}:{SERVER_PORT}")
    app.run(host=SERVER_HOST, port=SERVER_PORT)


# Initialize variables for the emotion detection app
detector = FER()
capture = cv2.VideoCapture(0)

if not capture.isOpened():
    print("Camera not responding.")
    exit()

emotion_mapping = {
    'happy': 'Xara',
    'sad': 'Stenaxwria',
    'angry': 'Nebra',
    'surprised': 'Ekplhksh',
    'disgust': 'Ahdeia',
    'fear': 'Fobos',
    'neutral': 'Oudeterothta'
}

action_log = []
last_logged_emotion = None  # Variable to track the last logged emotion
running = True  # Flag for running state


def log_action(action):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} - {action}"
    action_log.insert(0, log_entry)

    # Send the log to the API immediately
    send_log_to_api(log_entry)


def send_log_to_api(log_entry):
    """Send a single log entry to the API immediately"""
    try:
        response = requests.post(f"http://{SERVER_IP}:{SERVER_PORT}/endpoint",
                               json={"logs": [log_entry]})
        if response.status_code == 200:
            print(f"Log sent to API: {log_entry}")
        else:
            print(f"Failed to send log. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending log to API: {e}")



def update_log_display():
    log_text = "\n".join(action_log)
    log_box.config(state=tk.NORMAL)
    log_box.delete(1.0, tk.END)
    log_box.insert(tk.END, log_text)
    log_box.config(state=tk.DISABLED)


def update_camera_frame():
    global running, last_logged_emotion
    if running:
        success, frame = capture.read()
    if not success:
        log_action("Can't read frame.")
        return

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    emotions = detector.detect_emotions(rgb_frame)

    emotion_message = "Kanena Proswpo"  # Default message

    if emotions and len(emotions) > 0:
        face = emotions[0]
        emotion_score = face['emotions']
        renamed_emotions = {emotion_mapping.get(key, key): value for key, value in emotion_score.items()}
        strongest_emotion = max(renamed_emotions, key=renamed_emotions.get)
        emotion_message = strongest_emotion

        # Log the emotion if it has changed
        if strongest_emotion != last_logged_emotion:
            log_action(f"Detected emotion: {strongest_emotion}")
        last_logged_emotion = strongest_emotion  # Update last logged emotion

        (x, y, w, h) = face['box']
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 3)

    text_position = (10, 30)
    text_size = cv2.getTextSize(emotion_message, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    cv2.rectangle(frame, (text_position[0] - 5, text_position[1] - text_size[1] - 5),
                  (text_position[0] + text_size[0] + 5, text_position[1] + 5), (0, 0, 0), -1)
    cv2.putText(frame, emotion_message, text_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Convert frame to Image for tkinter
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    img = img.resize((640, 480))
    img_tk = ImageTk.PhotoImage(img)

    camera_label.imgtk = img_tk
    camera_label.config(image=img_tk)

    update_log_display()  # Update log display

    # Schedule the next frame update
    window.after(30, update_camera_frame)  # Update every 30 ms (about 33 FPS)


def read_camera():
    global running
    log_action("Starting the camera feed.")
    update_log_display()
    update_camera_frame()  # Start the camera feed


# Clear logs function for GUI
def clear_logs_gui():
    if messagebox.askyesno("Clear Logs", "Are you sure you want to clear all logs?"):
        try:
            global all_logs
            # Clear logs on server
            response = requests.post(f"http://{SERVER_IP}:{SERVER_PORT}/clear_logs")
            if response.status_code == 200:
                print("All logs cleared successfully")
                messagebox.showinfo("Success", "All logs cleared successfully!")
            else:
                print(f"Failed to clear logs. Status code: {response.status_code}")
                messagebox.showerror("Error", "Failed to clear logs from server.")
        except Exception as e:
            print(f"Error clearing logs: {e}")
            messagebox.showerror("Error", f"Error clearing logs: {e}")



# Set up the GUI with tkinter
def setup_gui():
    global camera_label, log_box, window

    window = tk.Tk()
    window.title("Emotion Face Detection (EFD)")

    # Update API information label with the correct URL
    api_url = f"http://{SERVER_IP}:{SERVER_PORT}"
    api_info_label = tk.Label(window, text=f"API Access: {api_url}", fg="blue", cursor="hand2")
    api_info_label.pack(pady=5)
    api_info_label.bind("<Button-1>", lambda e: webbrowser.open(api_url))

    # Create camera display area
    camera_label = tk.Label(window)
    camera_label.pack()

    # Create log display area
    log_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, state=tk.DISABLED, height=10)
    log_box.pack(fill=tk.BOTH, padx=10, pady=10)

    # Create button frame
    button_frame = tk.Frame(window)
    button_frame.pack(pady=10)

    # Create clear logs button
    clear_logs_button = Button(button_frame, text="Clear All Logs", command=clear_logs_gui, bg="#F44336", fg="white")
    clear_logs_button.pack(side=tk.LEFT, padx=5)

    # Create exit button
    exit_button = Button(button_frame, text="Close", command=on_closing)
    exit_button.pack(side=tk.LEFT, padx=5)

    # Add option to clear logs at startup
    if os.path.exists(LOGS_FILE) and messagebox.askyesno("Logs Found",
                                                         "Previous logs found. Do you want to clear them and start fresh?"):
        clear_logs_gui()

    # Start reading the camera in a separate thread
    threading.Thread(target=read_camera, daemon=True).start()

    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.mainloop()


def on_closing():
    global running
    running = False  # Set running to False to stop the camera feed
    capture.release()  # Release the capture
    window.destroy()


def send_logs_to_server():
    global logs_to_send
    if not logs_to_send:
        print("No logs to send")
        return

    try:
        response = requests.post(f"http://{SERVER_IP}:{SERVER_PORT}/endpoint",
                                 json={"logs": logs_to_send},
                                 timeout=5)
        if response.status_code == 200:
            print(f"Successfully sent {len(logs_to_send)} logs to server")
            logs_to_send = []  # Clear the logs after successful send
        else:
            print(f"Failed to send logs. Server responded with status {response.status_code}")
    except Exception as e:
        print(f"Error sending logs to server: {e}")


if __name__ == '__main__':
    # Start the API server in a separate thread
    threading.Thread(target=run_server, daemon=True).start()

    # Set up the GUI
    setup_gui()
