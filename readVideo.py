import numpy as np
import cv2 as cv

class VideoReader:
    def __init__(self, video = 'TetMarketRef.mp4'):
        self.cap = cv.VideoCapture(video)
        self.frame_number = 0

    def read_frame(self):    
        ret, frame = self.cap.read()
        self.frame_number += 1

        if not ret:
            self.cap.release()
            
        return ret, frame, self.frame_number