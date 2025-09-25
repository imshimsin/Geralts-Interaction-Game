@echo off
echo Starting Emotion Detection Application...

:: Change to the project directory
cd /d D:\MYGAME\FACE

:: Activate the virtual environment
call venv\Scripts\activate.bat

:: Install required packages if they're not already installed
echo Checking for required packages...
pip install -q tensorflow==2.12.0 opencv-python fer==22.5.1 moviepy==1.0.3 Pillow flask

:: Run the emotion detection script
echo Running emotion detection script...
python emotion_detection.py

:: Deactivate the virtual environment when done
call deactivate

:: Keep the window open if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred while running the script.
    echo Error code: %ERRORLEVEL%
    pause
)
