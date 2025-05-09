from flask import Flask, Response, render_template, jsonify
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
import math
from flask_socketio import SocketIO
import json

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Load YOLOv8 model (custom mask detector)
model = YOLO('weights/best.pt')

# Global counters
counters = {'with_mask': 0, 'without_mask': 0, 'mask_weared_incorrect': 0}

# Global detection history (in-memory)
detection_history = []

# Cumulative counters
cumulative_counters = {
    'with_mask': 0,
    'without_mask': 0,
    'mask_weared_incorrect': 0
}

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

class HourlyStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hour = db.Column(db.String(16), nullable=False, unique=True)  # e.g., '2024-05-07 14'
    with_mask = db.Column(db.Integer, nullable=False)
    without_mask = db.Column(db.Integer, nullable=False)
    mask_weared_incorrect = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

# Thread-safe queue for DB writes
stats_queue = queue.Queue()

# Open the camera ONCE at the top
CAMERA_INDEX = 0  # Set to your working index
camera = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
latest_processed_frame = None
processed_frame_lock = threading.Lock()

# --- Tracking logic ---
class TrackedFace:
    def __init__(self, box, cls, label, color, max_missed=10):
        self.box = box  # (x1, y1, x2, y2)
        self.cls = cls
        self.label = label
        self.color = color
        self.missed = 0
        self.max_missed = max_missed

    def update(self, box, cls, label, color):
        self.box = box
        self.cls = cls
        self.label = label
        self.color = color
        self.missed = 0

    def increment_missed(self):
        self.missed += 1

    def is_lost(self):
        return self.missed > self.max_missed

tracked_faces = []
tracker_lock = threading.Lock()

# Helper: compute centroid
def box_centroid(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) // 2, (y1 + y2) // 2)

def iou(boxA, boxB):
    # Compute intersection over union for matching
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
    return iou

# --- Camera + YOLO + Tracking thread ---
def camera_yolo_thread():
    global latest_processed_frame
    global tracked_faces
    global cumulative_counters
    # Release the camera if it's already open
    if 'camera' in globals():
        camera.release()
    while True:
        ret, frame = camera.read()
        if not ret or frame is None:
            print("No frame received in camera_yolo_thread!")
            time.sleep(0.03)
            continue
        # Run YOLO detection
        results = model(frame, verbose=False)[0]
        boxes = results.boxes.xyxy.cpu().numpy() if results.boxes is not None else []
        clss = results.boxes.cls.cpu().numpy().astype(int) if results.boxes is not None else []
        # Prepare detections
        detections = []
        for box, cls in zip(boxes, clss):
            x1, y1, x2, y2 = map(int, box)
            if cls == 0:
                color = (0, 230, 0)
                label = 'With Mask'
            elif cls == 1:
                color = (0, 0, 255)
                label = 'Without Mask'
            elif cls == 2:
                color = (0, 165, 255)
                label = 'Incorrect Mask'
            else:
                color = (128, 128, 128)
                label = 'Unknown'
            detections.append({'box': (x1, y1, x2, y2), 'cls': cls, 'label': label, 'color': color})
        # --- Tracking ---
        with tracker_lock:
            # Mark all tracked faces as missed
            for tf in tracked_faces:
                tf.increment_missed()
            # Match detections to tracked faces (by IOU)
            for det in detections:
                best_iou = 0
                best_tf = None
                for tf in tracked_faces:
                    iou_score = iou(det['box'], tf.box)
                    if iou_score > best_iou:
                        best_iou = iou_score
                        best_tf = tf
                if best_iou > 0.3:
                    best_tf.update(det['box'], det['cls'], det['label'], det['color'])
                else:
                    tracked_faces.append(TrackedFace(det['box'], det['cls'], det['label'], det['color']))
                    # Increment cumulative counter for new face
                    if det['cls'] == 0:
                        cumulative_counters['with_mask'] += 1
                    elif det['cls'] == 1:
                        cumulative_counters['without_mask'] += 1
                    elif det['cls'] == 2:
                        cumulative_counters['mask_weared_incorrect'] += 1
            # Remove lost faces
            tracked_faces = [tf for tf in tracked_faces if not tf.is_lost()]
            # Draw all tracked faces
            for tf in tracked_faces:
                x1, y1, x2, y2 = tf.box
                cv2.rectangle(frame, (x1, y1), (x2, y2), tf.color, 3)
                cv2.putText(frame, tf.label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, tf.color, 2)
        # Optionally, add a timestamp for debugging
        cv2.putText(frame, f"Time: {datetime.datetime.now().strftime('%H:%M:%S')}",
                  (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        with processed_frame_lock:
            latest_processed_frame = frame.copy()
        time.sleep(0.01)

threading.Thread(target=camera_yolo_thread, daemon=True).start()

def gen_frames():
    """Yield the latest processed frame from the background thread."""
    while True:
        with processed_frame_lock:
            frame = latest_processed_frame.copy() if latest_processed_frame is not None else None
        if frame is not None:
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.01)

@app.route('/')
def index():
    return render_template('index.html')

def test_camera():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    def generate():
        while True:
            ret, frame = cap.read()
            print("ret:", ret, "frame shape:", getattr(frame, 'shape', None))
            if not ret or frame is None:
                print("No frame received!")
                time.sleep(1)
                continue
            
            ret_enc, buffer = cv2.imencode('.jpg', frame)
            if ret_enc:
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                print("Failed to encode frame")
                time.sleep(1)
                continue
    
    return Response(generate(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/test_camera')
def test_camera_route():
    return test_camera()

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/ws')
def ws_route():
    def generate():
        while True:
            with processed_frame_lock:
                frame = latest_processed_frame.copy() if latest_processed_frame is not None else None
            if frame is not None:
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield f"data: {frame_bytes}\n\n"
            time.sleep(0.01)

    return Response(generate(), mimetype='text/event-stream')

@app.route('/stats')
def stats_page():
    from flask import request
    # Dynamic stats from tracked faces
    with tracker_lock:
        with_mask = sum(1 for tf in tracked_faces if tf.cls == 0)
        without_mask = sum(1 for tf in tracked_faces if tf.cls == 1)
        mask_weared_incorrect = sum(1 for tf in tracked_faces if tf.cls == 2)
    latest_counters = {
        'with_mask': with_mask,
        'without_mask': without_mask,
        'mask_weared_incorrect': mask_weared_incorrect
    }
    # Add cumulative counters
    total_counters = cumulative_counters.copy()
    stats = {
        'current': latest_counters,
        'total': total_counters
    }
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes['application/json'] > request.accept_mimetypes['text/html']:
        return stats
    return render_template('stats.html', stats=stats)

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

@app.route('/test')
def test_page():
    return render_template('test.html')

# --- Hourly stats aggregation thread ---
def hourly_stats_aggregator():
    from sqlalchemy.exc import IntegrityError
    import time
    last_hour = None
    while True:
        now = datetime.datetime.now()
        current_hour = now.strftime('%Y-%m-%d %H')
        if last_hour != current_hour:
            # Aggregate stats for the previous hour
            if last_hour is not None:
                with tracker_lock:
                    with_mask = sum(1 for tf in tracked_faces if tf.cls == 0)
                    without_mask = sum(1 for tf in tracked_faces if tf.cls == 1)
                    mask_weared_incorrect = sum(1 for tf in tracked_faces if tf.cls == 2)
                with app.app_context():
                    entry = HourlyStats(
                        hour=last_hour,
                        with_mask=with_mask,
                        without_mask=without_mask,
                        mask_weared_incorrect=mask_weared_incorrect
                    )
                    try:
                        db.session.add(entry)
                        db.session.commit()
                    except IntegrityError:
                        db.session.rollback()
            last_hour = current_hour
        time.sleep(60)  # Check every minute

threading.Thread(target=hourly_stats_aggregator, daemon=True).start()

def process_frame(frame):
    global with_mask_count, without_mask_count, incorrect_mask_count
    
    # Run YOLO detection
    results = model(frame)
    
    # Process results
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            
            if conf > 0.5:  # Confidence threshold
                if cls == 0:  # with_mask
                    with_mask_count += 1
                elif cls == 1:  # without_mask
                    without_mask_count += 1
                elif cls == 2:  # mask_weared_incorrect
                    incorrect_mask_count += 1
    
    # Send stats via WebSocket
    socketio.emit('stats', {
        'type': 'stats',
        'with_mask': with_mask_count,
        'without_mask': without_mask_count,
        'mask_weared_incorrect': incorrect_mask_count
    })
    
    return frame

def generate_frames():
    cap = cv2.VideoCapture(0)
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # Process frame
        processed_frame = process_frame(frame)
        
        # Convert to JPEG
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed_socket')
def video_feed_socket():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)