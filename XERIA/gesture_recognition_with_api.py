import mediapipe as mp
import cv2
import numpy as np
import requests
import datetime
import time
import threading

# MediaPipe setup with performance optimization
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,  # Set to False for video processing
    max_num_hands=1,
    min_detection_confidence=0.5,  # Increased to reduce false positives
    min_tracking_confidence=0.5,
    model_complexity=0  # Use 0 for fastest performance (0, 1, or 2)
)

# API configuration
API_URL = "http://localhost:5000/record"

# Tracking to avoid duplicate submissions
last_gesture = None
last_gesture_time = 0
GESTURE_COOLDOWN = 1  # seconds


# For API calls to happen in background
def send_gesture_to_api(gesture_data):
    try:
        requests.post(API_URL, json=gesture_data, timeout=1)
    except Exception as e:
        print(f"API error: {e}")


def detect_gesture(landmarks):
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]

    wrist = landmarks[0]
    thumb_base = landmarks[2]
    index_base = landmarks[5]
    middle_base = landmarks[9]
    ring_base = landmarks[13]
    pinky_base = landmarks[17]

    thumb_direction = thumb_tip[1] < thumb_base[1]

    index_extended = index_tip[1] < index_base[1]
    middle_extended = middle_tip[1] < middle_base[1]
    ring_extended = ring_tip[1] < ring_base[1]
    pinky_extended = pinky_tip[1] < pinky_base[1]

    if thumb_direction and not any([index_extended, middle_extended, ring_extended, pinky_extended]):
        return "Thumbs Up"
    elif not thumb_direction and not any([index_extended, middle_extended, ring_extended, pinky_extended]):
        return "Thumbs Down"
    elif index_extended and not any([middle_extended, ring_extended, pinky_extended]):
        return "Index Up"
    elif index_extended and middle_extended and not any([ring_extended, pinky_extended]):
        return "Peace Sign"
    elif all([index_extended, middle_extended, ring_extended, pinky_extended]):
        return "Open Palm"
    elif index_extended and pinky_extended and not middle_extended and not ring_extended:
        return "Rock Sign"

    return "Unknown Gesture"


def log_gesture_to_api(gesture):
    """Send the gesture to our simple API in a background thread"""
    global last_gesture, last_gesture_time

    current_time = time.time()

    # Only log if it's a different gesture or enough time has passed
    if gesture != last_gesture or (current_time - last_gesture_time) > GESTURE_COOLDOWN:
        # Prepare data for API
        gesture_data = {
            "gesture": gesture,
            "timestamp": datetime.datetime.now().isoformat()
        }

        # Send to API in background thread
        threading.Thread(target=send_gesture_to_api, args=(gesture_data,), daemon=True).start()

        last_gesture = gesture
        last_gesture_time = current_time
        return True

    return False


# Main camera loop (robust version)
CAMERA_INDEX = 1  # Use the index that works for your setup (0, 1, etc.)
camera = cv2.VideoCapture(CAMERA_INDEX)

# Try different camera indices
# Start with the one that worked before
for camera_index in [1, 0, 2]:
    print(f"Trying camera index: {camera_index}")
    camera = cv2.VideoCapture(camera_index)
    
    # Try to read a test frame
    ret, test_frame = camera.read()
    
    if ret and camera.isOpened():
        print(f"Successfully opened camera with index {camera_index}")
        CAMERA_INDEX = camera_index
        break
    else:
        print(f"Failed to open camera with index {camera_index}")
        camera.release()
else:
    print("Could not open any camera")
    exit()

# Performance optimization for OpenCV
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_FPS, 30)

if not camera.isOpened():
    print(f"Cannot open camera (index {CAMERA_INDEX}). Please check your camera connection or use a different index.")
    exit()

# Only use this section for testing if the camera works without MediaPipe
"""
# This is the simplified test to see if camera works
while True:
    ret, frame = camera.read()
    if not ret:
        print("Failed to grab frame")
        break
    
    cv2.imshow('Camera Test', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

camera.release()
cv2.destroyAllWindows()
exit()  # Stop here for the test
"""

# For FPS calculation
prev_frame_time = 0
new_frame_time = 0

# Simplified drawing specs for better performance
drawing_spec = mp_drawing.DrawingSpec(thickness=2, circle_radius=1)
connection_spec = mp_drawing.DrawingSpec(thickness=2, circle_radius=1)

# Process frames only on every Nth frame
PROCESS_EVERY_N_FRAMES = 1
frame_count = 0

while True:
    ret, frame = camera.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame_count += 1

    # Calculate FPS
    new_frame_time = time.time()
    fps = 1 / (new_frame_time - prev_frame_time) if prev_frame_time > 0 else 0
    prev_frame_time = new_frame_time

    # Process and display status
    status_message = "No hand detected"
    status_color = (200, 200, 200)  # Gray

    # Flip the frame horizontally
    frame = cv2.flip(frame, 1)

    # Only process every N frames to reduce CPU usage
    if frame_count % PROCESS_EVERY_N_FRAMES == 0:
        # Convert to RGB before processing
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the image with MediaPipe
        results = hands.process(image_rgb)

        if results.multi_hand_landmarks:
            for hand_landmark in results.multi_hand_landmarks:
                # Draw landmarks with simplified specs
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmark,
                    mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=drawing_spec,
                    connection_drawing_spec=connection_spec
                )

                # Extract landmarks
                landmarks = []
                for landmark in hand_landmark.landmark:
                    h, w, c = frame.shape
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    landmarks.append((x, y))

                # Detect gesture
                gesture = detect_gesture(landmarks)

                # Log to API in background
                if log_gesture_to_api(gesture):
                    status_message = f"Recorded: {gesture}"
                    status_color = (0, 255, 0)  # Green
                else:
                    status_message = f"Detected: {gesture}"
                    status_color = (255, 165, 0)  # Orange

    # Display gesture and status with optimized text rendering
    cv2.putText(
        frame,
        f"Gesture: {last_gesture if last_gesture else 'None'}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        1
    )

    # Display status message
    cv2.putText(
        frame,
        status_message,
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        status_color,
        1
    )

    # Display FPS
    cv2.putText(
        frame,
        f"FPS: {int(fps)}",
        (10, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 255),
        1
    )

    cv2.imshow('Gesture Tracking', frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

camera.release()
cv2.destroyAllWindows()