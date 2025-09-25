# Geralts-Interaction-Game
This thesis develops an interactive storytelling game inspired by the Witcher, where players shape the narrative through gestures and emotions, using technologies such as Flask, OpenCV, Mediapipe, and FER for natural interaction.


## Overview
*A Witcher's Story* is an interactive storytelling game inspired by **The Witcher** universe. Unlike traditional games controlled by mouse or keyboard, this project allows the player to shape the narrative using **hand gestures** and **facial expressions**.  
The story is written in `.twee` format and dynamically adapts to the player's actions, creating a unique narrative experience each time.

Two main game versions are included:
- **Hand Gesture Game**: Controlled by recognized gestures (thumbs up, thumbs down, peace, index finger).
- **Emotion Game**: Controlled by facial expressions (happiness, sadness, surprise, etc.).

Both versions follow an **event-driven logic**, where each detected gesture or emotion is treated as an event that drives the story forward.

## Features
- Real-time **hand gesture recognition** using Mediapipe and OpenCV.
- Real-time **facial emotion recognition** using FER.
- Dynamic story rendering with Flask, HTML, CSS, and JavaScript.
- Interactive branching narratives written in `.twee` format.
- Works both on desktop and on **Raspberry Pi**.

## Requirements
- Python 3.11+
- Flask
- OpenCV
- Mediapipe
- FER
- Requests
- Tkinter (for small GUI setup window)

On Raspberry Pi:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install libatlas-base-dev

How to Run
Gesture Game

Run the gesture recognition API and camera handler:

python run_both.py


Start the game application:

python witcher_story_app_hands.py


When prompted, enter the API address shown by run_both.py.

Emotion Game

Run the emotion-based game directly:

python Witcher_emotion_game.py


A window will display the API address where the emotion API is running.

Project Structure
├── A_Witchers_Story.twee        # The interactive story script
├── witcher_story_app_hands.py   # Hand gesture game frontend
├── Witcher_emotion_game.py      # Emotion recognition game
├── gesture_recognition_with_api.py
├── emotion_detection.py
├── new_api.py
├── run_both.py
├── static/                      # CSS, JS, images
└── templates/                   # HTML templates
