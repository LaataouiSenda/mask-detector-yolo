import xml.etree.ElementTree as ET
import glob
import os
from tqdm import tqdm

def convert_voc_to_yolo(xml_file, class_mapping):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Get image size
    size = root.find('size')
    width = float(size.find('width').text)
    height = float(size.find('height').text)
    
    # Process each object
    yolo_lines = []
    for obj in root.findall('object'):
        class_name = obj.find('name').text
        if class_name not in class_mapping:
            continue
            
        class_id = class_mapping[class_name]
        
        # Get bounding box coordinates
        bbox = obj.find('bndbox')
        xmin = float(bbox.find('xmin').text)
        ymin = float(bbox.find('ymin').text)
        xmax = float(bbox.find('xmax').text)
        ymax = float(bbox.find('ymax').text)
        
        # Convert to YOLO format
        x_center = (xmin + xmax) / (2.0 * width)
        y_center = (ymin + ymax) / (2.0 * height)
        box_width = (xmax - xmin) / width
        box_height = (ymax - ymin) / height
        
        # Ensure values are within [0, 1]
        x_center = min(max(x_center, 0.0), 1.0)
        y_center = min(max(y_center, 0.0), 1.0)
        box_width = min(max(box_width, 0.0), 1.0)
        box_height = min(max(box_height, 0.0), 1.0)
        
        yolo_lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}")
    
    return yolo_lines

def main():
    # Define class mapping
    class_mapping = {
        'with_mask': 0,
        'without_mask': 1,
        'mask_weared_incorrect': 2
    }
    
    # Create output directories if they don't exist
    os.makedirs('data/train/labels', exist_ok=True)
    os.makedirs('data/val/labels', exist_ok=True)
    
    # Get all XML files
    xml_files = glob.glob('data/raw/annotations/*.xml')
    
    # Get train and val image filenames
    train_images = set(os.path.basename(f).replace('.png', '') for f in glob.glob('data/train/images/*.png'))
    val_images = set(os.path.basename(f).replace('.png', '') for f in glob.glob('data/val/images/*.png'))
    
    print("Converting training annotations...")
    for xml_file in tqdm(xml_files):
        base_name = os.path.basename(xml_file).replace('.xml', '')
        
        # Convert and save training labels
        if base_name in train_images:
            yolo_lines = convert_voc_to_yolo(xml_file, class_mapping)
            if yolo_lines:
                with open(f'data/train/labels/{base_name}.txt', 'w') as f:
                    f.write('\n'.join(yolo_lines))
        
        # Convert and save validation labels
        if base_name in val_images:
            yolo_lines = convert_voc_to_yolo(xml_file, class_mapping)
            if yolo_lines:
                with open(f'data/val/labels/{base_name}.txt', 'w') as f:
                    f.write('\n'.join(yolo_lines))
    
    print("\nConversion completed!")

if __name__ == '__main__':
    main() 