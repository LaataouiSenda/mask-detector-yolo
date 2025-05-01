import cv2
from ultralytics import YOLO
import numpy as np

def main():
    # Load the trained model
    model = YOLO('runs/train/mask_detector/weights/best.pt')
    
    # Initialize video capture
    cap = cv2.VideoCapture(0)
    
    # Define colors for different classes
    colors = {
        'with_mask': (0, 255, 0),  # Green
        'without_mask': (0, 0, 255),  # Red
        'mask_weared_incorrect': (0, 165, 255)  # Orange
    }
    
    # Initialize counters
    counters = {
        'with_mask': 0,
        'without_mask': 0,
        'mask_weared_incorrect': 0
    }
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Perform detection
        results = model(frame)
        
        # Reset counters
        for key in counters:
            counters[key] = 0
        
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
                
                # Update counter
                counters[class_name] += 1
                
                # Draw bounding box
                color = colors[class_name]
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw label
                label = f"{class_name} {conf:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw counters
        y_offset = 30
        for class_name, count in counters.items():
            text = f"{class_name}: {count}"
            cv2.putText(frame, text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, colors[class_name], 2)
            y_offset += 30
        
        # Display frame
        cv2.imshow('Mask Detection', frame)
        
        # Break loop on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main() 