# Mask Detection System using YOLOv8

This project implements a real-time mask detection system using YOLOv8, capable of detecting whether people are wearing masks in images or video streams. The system provides visual feedback with green boxes for masked individuals and red boxes for unmasked ones, along with a counter for each category.

## Features

- Real-time mask detection using YOLOv8
- Webcam integration for live detection
- Visual feedback with colored bounding boxes
- Counter for masked and unmasked individuals
- Web interface for monitoring and control

## Project Structure

```
mask-detector-yolo/
├── backend/
│   ├── app.py              # FastAPI backend server
│   ├── mask_detector.py    # YOLO mask detection logic
│   ├── requirements.txt    # Python dependencies
│   └── data/
│       └── models/         # Trained YOLO models
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/ # Angular components
│   │   │   └── services/   # API services
│   │   └── assets/        # Static assets
│   └── package.json       # Frontend dependencies
└── README.md
```

## Prerequisites

- Python 3.8+
- Node.js 14+
- Angular CLI
- CUDA-capable GPU (recommended for better performance)

## Installation

### Backend Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

## Usage

### Starting the Backend

1. Navigate to the backend directory:
```bash
cd backend
```

2. Start the FastAPI server:
```bash
uvicorn app:app --reload
```

The backend will be available at `http://localhost:8000`

### Starting the Frontend

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Start the Angular development server:
```bash
ng serve
```

The frontend will be available at `http://localhost:4200`

## Model Training

The YOLOv8 model was trained on a custom dataset of masked and unmasked faces. The training process is documented in the `training/` directory.

### Training Requirements

- Kaggle API credentials
- Sufficient GPU memory (recommended: 8GB+)
- Training dataset in YOLO format

### Training Steps

1. Prepare the dataset in YOLO format
2. Configure the training parameters in `data.yaml`
3. Run the training script:
```bash
python train.py
```

## API Endpoints

- `POST /detect`: Process an image and return mask detection results
- `GET /stream`: Start/stop the webcam stream
- `GET /stats`: Get current detection statistics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- YOLOv8 by Ultralytics
- OpenCV for computer vision operations
- FastAPI for the backend framework
- Angular for the frontend framework 