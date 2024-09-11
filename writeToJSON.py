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
        data = {
            "frame_id": frameId,
            "img_w": 640,
            "img_h": 480,
            "approach": {
                int(k): {
                    "tl_coord2d": v[: 2].astype(int).tolist(),
                    "br_coord2d": v[2:].astype(int).tolist()
                } for k, v in zip(ids, boundingBoxs)
            },
            "action": {
                
            },
            "pose": {
                "persons": {
                    int(k): {
                        index: [point[0] / 680, point[1] / 480] for index, point in enumerate(v)
                    } for k, v in zip(ids, keypointsList)
                },
                "Datetime": str(datetime.now())
            }
        }
        with open(self.filename, 'a') as f:
            json.dump(data, f)
            f.write("\n")