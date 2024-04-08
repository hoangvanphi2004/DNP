# from mmpose.apis import inference_topdown, init_model
# from mmpose.utils import register_all_modules

# import numpy as np
# from PIL import Image
# import time

# class PoseEstimation:
#     def __init__(self) -> None:
#         register_all_modules()

#         config_file = 'td-hm_hrnet-w48_8xb32-210e_coco-256x192.py'
#         checkpoint_file = 'td-hm_hrnet-w48_8xb32-210e_coco-256x192-0e67c616_20220913.pth'

#         self.model = init_model(config_file, checkpoint_file, device="cuda:0")

#     def predict(self, frame, bounding_box):
#         #(480, 640, 3)
#         # print(frame.shape)
#         # print(bounding_box)
#         time1 = time.time()
#         obj = frame[int(bounding_box[1]): int(bounding_box[3]), int(bounding_box[0]): int(bounding_box[2]), :]
#         results = inference_topdown(self.model, obj)
#         keypoints = results[0].pred_instances.keypoints[0]
#         time2 = time.time();
        
#         print("what time ?", time2 - time1)
#         # Object -> frame
#         keypoints[:, 0] = keypoints[:, 0] + int(bounding_box[0])
#         keypoints[:, 1] = keypoints[:, 1] + int(bounding_box[1])
#         return keypoints

import numpy as np
import rtmpose.model
from PIL import Image


class PoseEstimation:
    def __init__(self) -> None:
        self.model = rtmpose.model.WholeBody()

    def predict(self, frame, bounding_box):
        #(480, 640, 3)
        # print(frame.shape)
        # print(bounding_box)

        obj = frame[int(bounding_box[1]): int(bounding_box[3]), int(bounding_box[0]): int(bounding_box[2]), :]
        keypoints = self.model.predict(obj)

        # Object -> frame
        keypoints[:, 0] = keypoints[:, 0] + int(bounding_box[0])
        keypoints[:, 1] = keypoints[:, 1] + int(bounding_box[1])
        return keypoints
    
