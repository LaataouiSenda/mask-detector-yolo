from ultralytics import YOLO
import os

def main():
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Download YOLOv8s weights if not already present
    if not os.path.exists('models/yolov8s.pt'):
        print("Downloading YOLOv8s weights...")
        model = YOLO('yolov8s.pt')
        model.save('models/yolov8s.pt')
    
    # Load the model
    model = YOLO('models/yolov8s.pt')
    
    # Train the model
    results = model.train(
        data='data.yaml',
        epochs=50,  # Reduced number of epochs for CPU training
        imgsz=640,
        batch=8,  # Reduced batch size for CPU training
        device='cpu',  # Use CPU
        project='runs/train',
        name='mask_detector',
        exist_ok=True,
        pretrained=True,
        optimizer='auto',
        verbose=True,
        seed=42,
        deterministic=True
    )
    
    print("Training completed successfully!")

if __name__ == '__main__':
    main() 