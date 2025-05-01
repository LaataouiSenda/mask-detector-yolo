from flask import Flask, Response, render_template
from flask_cors import CORS
import cv2
from ultralytics import YOLO
import numpy as np
import threading
import time

app = Flask(__name__)
CORS(app)

# Global variables
model = None
frame = None
lock = threading.Lock()

def init_model():
    global model
    model = YOLO('runs/train/mask_detector/weights/best.pt')

def video_stream():
    global frame, model
    
    # Initialize video capture
    cap = cv2.VideoCapture(0)
    
    # Define colors for different classes
    colors = {
        'with_mask': (0, 255, 0),  # Green
        'without_mask': (0, 0, 255),  # Red
        'mask_weared_incorrect': (0, 165, 255)  # Orange
    }
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Perform detection
        results = model(frame)
        
        # Process detections
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # Get class and confidence
                cls = int(box.cls[0].cpu().numpy())
                conf = float(box.conf[0].cpu().numpy())
                
                # Get class name
                class_name = model.names[cls]
                
                # Draw bounding box
                color = colors[class_name]
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw label
                label = f"{class_name} {conf:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        time.sleep(0.1)  # Control frame rate
    
    cap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames():
    global frame
    while True:
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.1)

if __name__ == '__main__':
    # Initialize model
    init_model()
    
    # Start video stream thread
    video_thread = threading.Thread(target=video_stream)
    video_thread.daemon = True
    video_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True) 