from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os
import datetime

app = Flask(__name__)

# Database setup - simple table with gesture and timestamp
DB_PATH = os.path.abspath("gesture.db")


def init_db():
 with sqlite3.connect(DB_PATH)as conn:
    conn.execute('''
    CREATE TABLE IF NOT EXISTS gestures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gesture TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    ''')
init_db()


@app.route('/')
def home():
    """Render a simple HTML interface"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gesture Recorder</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; }
            input { padding: 8px; width: 300px; }
            button { padding: 8px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Gesture Recorder</h1>

            <div class="form-group">
                <h2>Record New Gesture</h2>
                <label for="gesture">Gesture:</label>
                <input type="text" id="gesture" placeholder="Enter gesture name">
                <button onclick="recordGesture()">Record</button>
                <div id="result"></div>
            </div>

            <div>
                <h2>Recorded Gestures</h2>
                <button onclick="loadGestures()">Refresh Gestures</button>
                <table id="gesturesTable">
                    <thead>
                        <tr>
                            <th>Gesture</th>
                            <th>Timestamp</th>
                        </tr>
                    </thead>
                    <tbody id="gesturesList">
                        <!-- Data will be loaded here -->
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            // Load gestures when page loads
            document.addEventListener('DOMContentLoaded', loadGestures);

            function recordGesture() {
                const gesture = document.getElementById('gesture').value;
                if (!gesture) {
                    alert('Please enter a gesture name');
                    return;
                }

                fetch('/record', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        gesture: gesture
                    })
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('result').textContent = data.message;
                    document.getElementById('gesture').value = '';
                    loadGestures();
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('result').textContent = 'Error recording gesture';
                });
            }

            function loadGestures() {
                fetch('/gestures')
                .then(response => response.json())
                .then(data => {
                    const tableBody = document.getElementById('gesturesList');
                    tableBody.innerHTML = '';

                    if (data.length === 0) {
                        const row = document.createElement('tr');
                        row.innerHTML = '<td colspan="2">No gestures recorded yet</td>';
                        tableBody.appendChild(row);
                    } else {
                        data.forEach(item => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${item.gesture}</td>
                                <td>${item.timestamp}</td>
                            `;
                            tableBody.appendChild(row);
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route('/record', methods=['POST'])
def record_gesture():
    data = request.json

    if not data or 'gesture' not in data:
        return jsonify({'error': 'Missing gesture data'}), 400

    gesture = data['gesture']
    timestamp =datetime.datetime.now().isoformat()



    with sqlite3.connect(DB_PATH)as conn:
     conn.execute(
        "INSERT INTO gestures (gesture, timestamp) VALUES (?, ?)",
        (gesture, timestamp)
     )

    return jsonify({'success': True, 'message': f'Recorded gesture: {gesture}'}), 201


@app.route('/gestures', methods=['GET'])
def get_gestures():
 with sqlite3.connect(DB_PATH)as conn:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gestures ORDER BY timestamp DESC")
    rows = cursor.fetchall()

 return jsonify([dict(row) for row in rows])



if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)