# A Witcher's Story – Gesture & Emotion Driven Interactive Game


## Overview
*A Witcher's Story* is not a traditional video game. It is an **interactive storytelling experience** inspired by *The Witcher* universe, where the player becomes part of the narrative itself. Instead of clicking buttons or pressing keys, the story unfolds through **natural human interaction**: hand gestures and facial expressions.

The project demonstrates how **event-driven logic** can be applied to digital narratives. Each gesture or emotion acts as an event that drives the story forward, allowing the player to shape the outcome in real time. A simple smile, a look of surprise, or a thumbs up can completely change the path of the narrative.

Behind the scenes, the system combines **computer vision and web technologies**. Hand gestures are recognized with Mediapipe and OpenCV, while emotions are detected with FER. The story is written in `.twee` format and rendered dynamically with Flask, HTML, CSS, and JavaScript. This makes the game lightweight, flexible, and easy to expand with new narrative branches.

The project was also designed to run on **Raspberry Pi**, proving that immersive and creative interactions can be achieved even on low-cost hardware. This flexibility makes it suitable not only as a proof of concept for a thesis, but also as a foundation for future applications in education, therapy, or entertainment.


Two main game versions are included:
- **Hand Gesture Game**: Controlled by recognized gestures (thumbs up, thumbs down, peace, index finger).
- **Emotion Game**: Controlled by facial expressions (happiness, sadness, surprise, etc.).

Both versions follow an **event-driven logic**, where each detected gesture or emotion is treated as an event that drives the story forward.
## Disclaimer 
The two algorithms that captures Face Emotions and Hand Gestures are made by two of my friends and fellow students. More specifically, the `gesture_recognition_with_api.py` and `new_api.py` that exist in the XERIA folder are the two scrips that captures the hand gestures and simultaneously uploads the records to the API. 

Also the `emotion_detection.py` in the FACE folder provides the same things but with the Face emotions. The difference with that is the API and the detection scripts are bind together in a single app, rather that the Hand Gesture app that's in a two separate scripts. 

In order to match this, i made a different script called `run_both.py` that allows the `gesture_recognition_with_api.py` and `new_api.py` to run at the same time, so that the user would not have to run every single time the two different scripts.


<img width="2513" height="1291" alt="image" src="https://github.com/user-attachments/assets/37b31218-bc37-4a1c-9d71-ca40d8108091" />



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

https://opencv.org/

https://pypi.org/project/mediapipe/

## How to Run

In order for the game to run property, you have to make a virtual environment in each of the folders containing the python algorithms. 

You can import all the game files to a IDE (for example Pycharm) and work from there.

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
