import torch
import numpy as np
from ultralytics import YOLO
from pathlib import Path
from PIL import Image

class YOLOv5:
    def __init__(self) -> None:
        self.model = torch.hub.load('ultralytics/yolov5', 'ckpt/yolov5l', pretrained=True)
        
    def predict(self, frame):
        bounding_box = np.array(self.model(frame, verbose=False).xyxy[0].cpu())
        bounding_box = bounding_box[bounding_box[:, 5] == 0]
        return bounding_box.tolist()
    
class YOLOv8:
    def __init__(self) -> None:
        self.model = YOLO("ckpt/yolov8x.pt") 
    def predict(self, frame):
        results = self.model(frame, verbose=False)
        results = results[0].boxes.data;
        results = np.array(results[results[:, 5] == 0].cpu())
        return results.tolist()