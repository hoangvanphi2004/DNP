import consumer
import producer
import boundingBoxDetection
import cv2 as cv
import time

if __name__ == "__main__":
    frameConsumer = consumer.FrameConsumer("frame")
    boundingBoxPrediction = boundingBoxDetection.YOLOv5()
    boundingBoxProducer = producer.BoundingBoxProducer()
    try:
        while True:
            time1 = time.time()
            ret, frame, offset = frameConsumer.receive_latest_frame()
            time2 = time.time();

            if ret:
                boundingBox = boundingBoxPrediction.predict(frame)
                boundingBox = {
                    "offset": offset,
                    "data": boundingBox,
                }
                boundingBoxProducer.send_bounding_box(bounding_box = boundingBox)
            time3 = time.time()
            
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
        frameConsumer.consumer.close()