import json
import numpy as np
from datetime import datetime

class JSONWriter:
    def __init__(self) -> None:
        now = datetime.now()
        date = now.strftime("%d_%m_%Y_%H_%M_%S")
        self.filename = "./output/data_" + date + ".json"

    def turnToNumpy(self, *data):
        results = []
        for value in data:
            results.append(np.array(value))
        return results
    
    def write_data(self, boundingBoxs, ids, keypointsList, frameId):
        boundingBoxs, ids, keypointsList = self.turnToNumpy(boundingBoxs, ids, keypointsList)
        #print(boundingBoxs.shape, keypointsList.shape);
        data = {
            "frame_id": frameId,
            "data": [{
                "bounding_box": {
                    "xmin": boundingBoxs[i, 0],
                    "ymin": boundingBoxs[i, 1], 
                    "xmax": boundingBoxs[i, 2], 
                    "ymax": boundingBoxs[i, 3]
                },
                "id": ids[i],
                "keypoints": [{
                    "x": keypoint[0],
                    "y": keypoint[1]
                } 
                for keypoint in keypointsList[i, :]]
            }
            for i in range(boundingBoxs.shape[0])]
        }
        with open(self.filename, 'a') as f:
            json.dump(data, f)