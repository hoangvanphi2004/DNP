import torch
import numpy as np
from ultralytics import YOLO
from pathlib import Path
from boxmot import DeepOCSORT
from PIL import Image

class YOLOv5:
    def __init__(self) -> None:
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        self.tracker = DeepOCSORT(
            model_weights = Path('osnet_x0_25_msmt17.pt'),
            device = 'cuda:0',
            fp16 = False
        );

    def predict(self, frame):
        bounding_box = np.array(self.model(frame).xyxy[0].cpu())
        results = self.tracker.update(bounding_box, np.array(frame))
        return results.tolist()
    
class YOLOv8:
    def __init__(self) -> None:
        self.model = YOLO("yolov8s.pt") 
    def predict(self, frame):
        results = self.model(frame)
        #return results[0].boxes;
        return np.array(results[0].boxes[results[0].boxes.cls == 0].xyxy.cpu()).tolist()
    
# test = YOLOv5()
# image = Image.open("./demo.jpg")
# print(test.predict(image))