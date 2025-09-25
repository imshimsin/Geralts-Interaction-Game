#!/usr/bin/env python
import os
import sys
import subprocess
import time
import signal
import atexit

# Global variables to track subprocesses
api_process = None
camera_process = None

def cleanup():
    """Clean up function to terminate subprocesses on exit"""
    if api_process:
        print("Shutting down API server...")
        if sys.platform == 'win32':
            api_process.terminate()
        else:
            os.killpg(os.getpgid(api_process.pid), signal.SIGTERM)

    if camera_process:
        print("Shutting down camera application...")
        if sys.platform == 'win32':
            camera_process.terminate()
        else:
            os.killpg(os.getpgid(camera_process.pid), signal.SIGTERM)

def main():
    """
    Launch both the API server and the gesture recognition camera application
    using the Python executable from the virtual environment
    """
    global api_process, camera_process

    # Register cleanup function
    atexit.register(cleanup)

    # Path to the virtual environment's Python executable
    venv_python = os.path.join('.venv', 'Scripts', 'python.exe')

    # Path to the application scripts
    api_script = 'new_api.py'
    camera_script = 'gesture_recognition_with_api.py'

    # Check if files exist
    if not os.path.exists(api_script):
        print(f"Error: {api_script} not found.")
        return 1

    if not os.path.exists(camera_script):
        print(f"Error: {camera_script} not found.")
        return 1

    try:
        # Start API server first
        print(f"Starting API server with {venv_python}...")
        api_process = subprocess.Popen([venv_python, api_script],
                                     creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0)

        # Give the API server a moment to start
        print("Waiting for API server to initialize...")
        time.sleep(2)

        # Start camera application
        print(f"Starting gesture recognition with {venv_python}...")
        camera_process = subprocess.Popen([venv_python, camera_script],
                                        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0)

        print("Both applications are running. Press Ctrl+C to stop both.")

        # Wait for camera process to finish (or be interrupted)
        camera_process.wait()

    except KeyboardInterrupt:
        print("\nReceived interrupt, shutting down...")
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
