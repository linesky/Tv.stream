import cv2
import mss
import numpy as np
import pygetwindow as gw
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
#pip install pygetwindow mss opencv-python flask flask-socketio

app = Flask(__name__)
socketio = SocketIO(app)
stop_recording = False

def record_screen(window_title):
    global stop_recording

    window = gw.getWindowsWithTitle(window_title)
    if not window:
        print(f'No window with title "{window_title}" found.')
        return
    
    window = window[0]
    left, top, right, bottom = window.left, window.top, window.right, window.bottom
    width = right - left
    height = bottom - top

    sct = mss.mss()
    monitor = {"top": top, "left": left, "width": width, "height": height}
    
    print("Recording... Press Enter to stop.")
    while not stop_recording:
        img = sct.grab(monitor)
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        socketio.emit('frame', frame_bytes)
        socketio.sleep(0.04)

    print("Recording stopped.")

def wait_for_enter():
    global stop_recording
    input()  # Aguarda o pressionamento da tecla Enter
    stop_recording = True

@app.route('/')
def index():
    return render_template('index.html')

print("\x1bc\x1b[47;34m")
if __name__ == "__main__":
    window_title = gw.getActiveWindow().title

    recording_thread = threading.Thread(target=record_screen, args=(window_title,))
    recording_thread.start()

    socketio.run(app, host='0.0.0.0', port=5000)

    wait_for_enter()
    recording_thread.join()

