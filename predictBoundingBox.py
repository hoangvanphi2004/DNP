import consumer
import producer
import boundingBoxDetection
import cv2 as cv
import time
import os

if __name__ == "__main__":
    latestFrameConsumer = consumer.LatestFrameConsumer("latest_frame")
    frameProducer = producer.FrameProducer()
    boundingBoxPrediction = boundingBoxDetection.YOLOv5()
    boundingBoxProducer = producer.BoundingBoxProducer()
    keypointsConsumer = consumer.KeypointsConsumer("receive_back_keypoints")
    setupProducer = producer.SetupProducer()
    setupProducer.send_setup_value(0)
    setupProducer.producer.flush()
    setupConsumer = consumer.SetupConsumer("end")
    
    boundingBox = None
    firstTime = True
    isEnd = False
    try:
        while True:
            retKeypoints, keypointsData, _ = keypointsConsumer.receive_keypoints()
            retSetup, value = setupConsumer.receive_setup_value()
            
            if retSetup and value == 3:
                isEnd = True
                
            if boundingBox == None:
                retFrame, frame, offset = latestFrameConsumer.receive_latest_frame()
                if retFrame:
                    boundingBox = boundingBoxPrediction.predict(frame)
                    boundingBox = {
                        "offset": offset,
                        "data": boundingBox,
                    }
                elif isEnd:
                    break
                
            if (retKeypoints or firstTime) and boundingBox != None:
                frameProducer.send_frame(frame, offset)
                boundingBoxProducer.send_bounding_box(boundingBox)
                boundingBox = None
                firstTime = False
            
            # print(time2 - time1, " -> ", time3 - time2);
            #     cv.imshow("frame", frame)
            #     if cv.waitKey(1) == ord('q'):
            #         break
            # else:
            #     cv.destroyAllWindows()
            #time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        # cv.destroyAllWindows()
        latestFrameConsumer.consumer.close()
        keypointsConsumer.consumer.close()
        boundingBoxProducer.producer.flush()
        frameProducer.producer.flush()
    os.system("./close.sh")