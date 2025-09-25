# A Witcher's Story – Gesture & Emotion Driven Interactive Game

## Overview
*A Witcher's Story* is an interactive storytelling game inspired by **The Witcher** universe. Unlike traditional games controlled by mouse or keyboard, this project allows the player to shape the narrative using **hand gestures** and **facial expressions**.  
The story is written in `.twee` format and dynamically adapts to the player's actions, creating a unique narrative experience each time. This version works only on Windows. I will add soon support for Lunix and Raspberry pi machines.

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



## How to Run

In order for the game to run property, you have to make a virtual environment in each of the folders containing the python algorithms

### Running with myenv Virtual Environment


1. Navigate to your project folder:
```bash
cd ~/Desktop/Witcher_Game
```

2. Create the virtual environment:
```bash
python3 -m venv myenv
```

3. Activate it:
```bash
myenv\Scripts\activate
```
4. Download all the necessary librarys
```bash
pip install pip install flask opencv-python mediapipe fer requests pillow
```
Or
```bash
pip install -r requirements.txt
```
When you downloaded all the necessary librarys, then type "deactivate" on the terminal to exit the Virtual Enviroment.

### Gesture Game
1. Run the gesture recognition API and camera handler:
   ```bash
   python run_both.py
   ```
2. Start the game application:
   ```bash
   python witcher_story_app_hands.py
   ```
3. When prompted, enter the API address shown by `run_both.py`.

### Emotion Game
1. Run the emotion-based game directly:
   ```bash
   python Witcher_emotion_game.py
   ```
2. A window will display the API address where the emotion API is running.

## Project Structure
```
├── A_Witchers_Story.twee        # The interactive story script
├── witcher_story_app_hands.py   # Hand gesture game frontend
├── Witcher_emotion_game.py      # Emotion recognition game
├── gesture_recognition_with_api.py
├── emotion_detection.py
├── new_api.py
├── run_both.py
├── static/                      # CSS, JS, images
└── templates/                   # HTML templates
```

## License
This project was created as part of a university thesis. Free to use for educational purposes.
