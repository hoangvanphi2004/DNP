import torch
import numpy as np
from ultralytics import YOLO

class YOLOv5:
    def __init__(self) -> None:
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

    def predict(self, frame):
        results = self.model(frame)
        return np.array(results.xyxy[0].cpu()).tolist()
    
class YOLOv8:
    def __init__(self) -> None:
        self.model = YOLO("yolov8n.pt") 
    def predict(self, frame):
        results = self.model(frame)
        return np.array(results[0].boxes[results[0].boxes.cls == 0].xyxy[0].cpu()).tolist()
    
