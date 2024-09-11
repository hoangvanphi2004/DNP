import numpy as np
import rtmpose.model
from PIL import Image


class PoseEstimation:
    def __init__(self) -> None:
        self.model = rtmpose.model.WholeBody()

    def predict(self, frame, bounding_box):
        #Frame: (480, 640, 3)

        obj = frame[int(bounding_box[1]): int(bounding_box[3]), int(bounding_box[0]): int(bounding_box[2]), :]
        keypoints = self.model.predict(obj)

        # Object -> frame
        keypoints[:, 0] = keypoints[:, 0] + int(bounding_box[0])
        keypoints[:, 1] = keypoints[:, 1] + int(bounding_box[1])
        return keypoints
    
