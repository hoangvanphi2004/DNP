import readVideo
import producer
import consumer
import cv2 as cv
import time
import glob

if __name__ == "__main__":
    frameProducer = producer.FrameProducer()
    
    setupConsumer = consumer.SetupConsumer("setup_first")
    setupDone = []
    
    while True:
        ret, value = setupConsumer.receive_setup_value()
        if ret:
            setupDone.append(value)
        if (0 in setupDone) and (1 in setupDone) and (2 in setupDone):
            break
    
    setupConsumer.consumer.close()
    
    setupProducer = producer.SetupProducer()
    cnt = 0
    
    for path in glob.glob("./input/*"):
        videoReader = readVideo.VideoReader(path)
        print(f"Read from: {path}")
        while True:
            time1 = time.time();
            ret, frame, frame_number  = videoReader.read_frame()
            time2 = time.time();

            if not ret:
                break
            frame = cv.resize(frame, (640, 480))
            frameProducer.send_latest_frame(frame)
            time3 = time.time();
            time.sleep(0.05)
            cnt += 1;
        
    setupProducer.send_setup_value(3)
    frameProducer.producer.flush()
    setupProducer.producer.flush()
    