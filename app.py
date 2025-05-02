from flask import Flask, Response, render_template
from flask_cors import CORS
import cv2
import threading
import time

app = Flask(__name__)
CORS(app)

frame = None

def video_stream():
    global frame
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    while True:
        ret, img = cap.read()
        print("ret:", ret, "img type:", type(img), "img shape:", getattr(img, 'shape', None))
        if not ret or img is None:
            print('Error: Failed to read frame from webcam or frame is None.')
            time.sleep(1)
            continue
        ret_enc, buffer = cv2.imencode('.jpg', img)
        if not ret_enc:
            print("Erreur d'encodage JPEG")
            time.sleep(1)
            continue
        frame = buffer.tobytes()
        time.sleep(0.1)
    cap.release()

def gen_frames():
    global frame
    while True:
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stats')
def stats_page():
    # Minimal dummy stats for frontend compatibility
    return {'with_mask': 0, 'without_mask': 0, 'mask_weared_incorrect': 0}

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/time')
def time_page():
    return render_template('time.html')

if __name__ == '__main__':
    # Start video stream thread
    video_thread = threading.Thread(target=video_stream)
    video_thread.daemon = True
    video_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True) 