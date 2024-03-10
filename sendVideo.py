import readVideo
import producer
import cv2 as cv
import time

if __name__ == "__main__":
    videoReader = readVideo.VideoReader()
    frameProducer = producer.FrameProducer()

    cnt = 0
    while True:
        time1 = time.time();
        ret, frame, frame_number  = videoReader.read_frame()
        time2 = time.time();

        if not ret:
            break
        frame = cv.resize(frame, (640, 480))
        frameProducer.send_frame(frame)
        if cnt < 600:
            cnt += 1
        else:
            break
        time3 = time.time();
        time.sleep(0.3)
        print(time2 - time1, " -> ", time3 - time2);
    frameProducer.producer.flush()
    