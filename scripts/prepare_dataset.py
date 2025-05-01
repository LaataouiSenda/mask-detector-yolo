import os
import shutil
import random
from pathlib import Path

def prepare_dataset():
    # Create necessary directories
    base_dir = Path('data')
    raw_dir = base_dir / 'raw2'
    train_dir = base_dir / 'train'
    val_dir = base_dir / 'val'
    
    # Create directories if they don't exist
    for dir_path in [train_dir, val_dir]:
        (dir_path / 'images').mkdir(parents=True, exist_ok=True)
        (dir_path / 'labels').mkdir(parents=True, exist_ok=True)
    
    # Get all image files
    image_files = list(raw_dir.glob('**/*.jpg')) + list(raw_dir.glob('**/*.png'))
    
    # Shuffle the files
    random.shuffle(image_files)
    
    # Split into train and validation sets (80/20)
    split_idx = int(0.8 * len(image_files))
    train_files = image_files[:split_idx]
    val_files = image_files[split_idx:]
    
    print(f"Found {len(image_files)} images")
    print(f"Training set: {len(train_files)} images")
    print(f"Validation set: {len(val_files)} images")
    
    # Copy images to their respective directories
    for img_path in train_files:
        shutil.copy2(img_path, train_dir / 'images' / img_path.name)
        # Copy corresponding label file if it exists
        label_path = img_path.with_suffix('.txt')
        if label_path.exists():
            shutil.copy2(label_path, train_dir / 'labels' / label_path.name)
    
    for img_path in val_files:
        shutil.copy2(img_path, val_dir / 'images' / img_path.name)
        # Copy corresponding label file if it exists
        label_path = img_path.with_suffix('.txt')
        if label_path.exists():
            shutil.copy2(label_path, val_dir / 'labels' / label_path.name)
    
    print("Dataset preparation completed!")

if __name__ == '__main__':
    prepare_dataset() 