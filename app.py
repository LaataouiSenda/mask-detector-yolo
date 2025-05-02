from flask import Flask, Response, render_template
from flask_cors import CORS
import cv2
import threading
import time
from ultralytics import YOLO
import numpy as np
import datetime
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.orm import sessionmaker
import queue

app = Flask(__name__)
CORS(app)

# Load YOLOv8 model (custom mask detector)
model = YOLO('weights/best.pt')

# Global counters
counters = {'with_mask': 0, 'without_mask': 0, 'mask_weared_incorrect': 0}

# Global detection history (in-memory)
detection_history = []

# Database setup for MySQL (no password)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1:3306/mask-detector-yolo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class DetectionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(32), nullable=False)
    with_mask = db.Column(db.Integer, nullable=False)
    without_mask = db.Column(db.Integer, nullable=False)
    mask_weared_incorrect = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

# Thread-safe queue for DB writes
stats_queue = queue.Queue()

# Background thread for DB writes
def db_writer():
    Session = sessionmaker(bind=db.engine)
    last_counts = None
    while True:
        try:
            stats = stats_queue.get()
            if stats is None:
                break  # Shutdown signal
            # Only write if counts changed
            if last_counts != stats['frame_counts'] or last_counts is None:
                session = Session()
                new_entry = DetectionHistory(
                    timestamp=stats['timestamp'],
                    with_mask=stats['frame_counts']['with_mask'],
                    without_mask=stats['frame_counts']['without_mask'],
                    mask_weared_incorrect=stats['frame_counts']['mask_weared_incorrect']
                )
                try:
                    session.add(new_entry)
                    session.commit()
                except Exception as e:
                    print(f"[DB ERROR] {e}")
                    session.rollback()
                finally:
                    session.close()
                last_counts = stats['frame_counts'].copy()
        except Exception as e:
            print(f"[DB WRITER ERROR] {e}")

import threading
writer_thread = threading.Thread(target=db_writer, daemon=True)
writer_thread.start()

def gen_frames():
    def open_camera():
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        return cap
    cap = open_camera()
    fail_count = 0
    last_queue_time = 0
    while True:
        try:
            ret, img = cap.read()
            if not ret or img is None:
                print('Error: Failed to read frame from webcam or frame is None.')
                fail_count += 1
                time.sleep(1)
                if fail_count >= 5:
                    print('Re-opening camera...')
                    cap.release()
                    time.sleep(1)
                    cap = open_camera()
                    fail_count = 0
                continue
            fail_count = 0
            # Run YOLOv8 detection
            results = model(img, verbose=False)[0]
            boxes = results.boxes.xyxy.cpu().numpy() if results.boxes is not None else []
            clss = results.boxes.cls.cpu().numpy().astype(int) if results.boxes is not None else []
            # Reset counters for this frame
            frame_counts = {'with_mask': 0, 'without_mask': 0, 'mask_weared_incorrect': 0}
            # Draw boxes
            for box, cls in zip(boxes, clss):
                x1, y1, x2, y2 = map(int, box)
                if cls == 0:
                    color = (0, 230, 0)  # Green for with_mask
                    label = 'With Mask'
                    frame_counts['with_mask'] += 1
                elif cls == 1:
                    color = (0, 0, 255)  # Red for without_mask (BGR)
                    label = 'Without Mask'
                    frame_counts['without_mask'] += 1
                elif cls == 2:
                    color = (0, 165, 255)  # Orange for mask_weared_incorrect (BGR)
                    label = 'Incorrect Mask'
                    frame_counts['mask_weared_incorrect'] += 1
                else:
                    color = (128, 128, 128)
                    label = 'Unknown'
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
                cv2.putText(img, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            # Update global counters
            for k in counters:
                counters[k] = frame_counts[k]
            # --- Put stats in queue once per second ---
            now = time.time()
            if now - last_queue_time >= 1:
                stats_queue.put({
                    'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'frame_counts': frame_counts.copy()
                })
                last_queue_time = now
            # Encode frame
            ret_enc, buffer = cv2.imencode('.jpg', img)
            if not ret_enc:
                print("Erreur d'encodage JPEG")
                time.sleep(1)
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
        except Exception as e:
            print(f"[GEN_FRAMES ERROR] {e}")
            time.sleep(1)
    cap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stats')
def stats_page():
    from flask import request
    # Always return the latest counters for AJAX/fetch requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes['application/json'] > request.accept_mimetypes['text/html']:
        return counters
    return render_template('stats.html')

@app.route('/history')
def history():
    history_entries = DetectionHistory.query.order_by(DetectionHistory.id.desc()).limit(500).all()
    return render_template('history.html', history=history_entries)

@app.route('/clear_history', methods=['POST'])
def clear_history():
    num_deleted = DetectionHistory.query.delete()
    db.session.commit()
    return {'status': 'cleared', 'deleted': num_deleted}

@app.route('/time')
def time_page():
    return render_template('time.html')

if __name__ == '__main__':
    # Start Flask app (no video thread)
    app.run(host='0.0.0.0', port=5000, debug=True) 