"""
50 epochs
MODEL       BATCH       TRAINABLE (on local GPU)  FILE REF (runs/detect)  TRAIN MEMORY (dedicated GPU - shared GPU - GPU memory)
yolov10n    32          V                         train7  val4            10 GB (Task Manager) 6.5 GB (Terminal)
yolov10l    32          V                         train11 val7            31/32 GB (Task Manager) 28.5 GB (Terminal) <---- BEST I CAN DO WITH LOCAL PC
yolov10x    16          V                         train9  val6            24/32 GB
yolov10x    32          X                         train8  val5            /

100 epochs
MODEL       BATCH       TRAINABLE (on local GPU)  FILE REF (runs/detect)  TRAIN MEMORY (dedicated GPU - shared GPU - GPU memory)
yolov10n    32          V                         train12 val8            6.5 GB (Terminal)
yolov10l    32          V                         train13 val9            28.5 GB (Terminal) <---- BEST I CAN DO WITH LOCAL PC
yolov10x    16          V                         
yolov10x    32          X                         /                         /

"""

import os
import re
from ultralytics import YOLO

def train_model():
    # Load YOLOv3 model from scratch
    model = YOLO("yolov10l.pt") 

    # Train the model using the specified dataset configuration
    model.train(data="data/formatted_bronchoscopy/bronchoscopy.yaml", epochs=100, imgsz=480, batch=32)

def val_model():
    # Path to the training directories
    train_directory = "runs/detect"
    
    # Get all directories in the train_directory
    all_train_dirs = [dir for dir in os.listdir(train_directory) if os.path.isdir(os.path.join(train_directory, dir)) and dir.startswith("train")]

    # Use regular expression to filter and sort directories by their numeric suffix
    regex = re.compile(r"train(\d+)")
    all_train_dirs = [dir for dir in all_train_dirs if regex.search(dir)]
    all_train_dirs.sort(key=lambda x: int(regex.search(x).group(1)))
    
    # Get the last directory (highest number)
    latest_train_dir = all_train_dirs[-1]
    
    # Load YOLOv3 model from the latest checkpoint
    model = YOLO(os.path.join(train_directory, latest_train_dir, "weights", "best.pt"))

    # Using ultralytics
    metrics = model.val()
    metrics.box.map  # map50-95
    metrics.box.map50  # map50
    metrics.box.map75  # map75
    metrics.box.maps  # a list contains map50-95 of each category

if __name__ == '__main__':
    train_model()
    val_model()
