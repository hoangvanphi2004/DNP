import torch
import numpy as np
from ultralytics import YOLO
from pathlib import Path
from boxmot import OCSORT
from PIL import Image

class YOLOv5:
    def __init__(self) -> None:
        self.model = torch.hub.load('ultralytics/yolov5', 'ckpt/yolov5l', pretrained=True)
        # self.tracker = DeepOCSORT(
        #     model_weights = Path('osnet_x0_25_msmt17.pt'),
        #     device = 'cuda:0',
        #     fp16 = False
        # );
        #self.tracker = OCSORT(delta_t = 4, max_age = 50, min_hits = 5, use_byte = True, inertia = 0.4);
        
    def predict(self, frame):
        bounding_box = np.array(self.model(frame).xyxy[0].cpu())
        bounding_box = bounding_box[bounding_box[:, 5] == 0]
        #results = self.tracker.update(bounding_box, np.array(frame))
        return bounding_box.tolist()
    
class YOLOv8:
    def __init__(self) -> None:
        self.model = YOLO("ckpt/yolov8l.pt") 
    def predict(self, frame):
        results = self.model(frame)
        results = results[0].boxes.data;
        results = np.array(results[results[:, 5] == 0].cpu())
        return results.tolist()
        #return np.array(results[0].boxes[results[0].boxes.cls == 0].xyxy.cpu()).tolist()
    
# test = YOLOv8()
# image = Image.open("./demo.jpg")
# print(test.predict(image))