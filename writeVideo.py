import cv2 as cv
from datetime import datetime

class VideoWriter:
    def __init__(self) -> None:
        now = datetime.now()
        date = now.strftime("%d_%m_%Y_%H_%M_%S")
        filename = "./output/video_" + date + ".avi"
        fourcc = cv.VideoWriter_fourcc(*'MJPG')
        self.video = cv.VideoWriter(filename, fourcc, 15.0, (640,  480))
    def write(self, frame):
        self.video.write(frame);