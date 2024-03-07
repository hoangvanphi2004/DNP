import readVideo
import producer
import cv2 as cv
import time

if __name__ == "__main__":
    videoReader = readVideo.VideoReader()
    frameProducer = producer.FrameProducer()

    cnt = 0
    while True:
        ret, frame, frame_number  = videoReader.read_frame()
        if not ret:
            break
        frame = cv.resize(frame, (640, 480))
        frameProducer.send_frame(frame)
        if cnt < 600:
            cnt += 1
        else:
            break
        #time.sleep(0.1)
    frameProducer.producer.flush()
    