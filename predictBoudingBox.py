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
            ret, frame, offset = frameConsumer.receive_latest_frame()
            if ret:
                boundingBox = boundingBoxPrediction.predict(frame)
                boundingBox = {
                    "offset": offset,
                    "data": boundingBox,
                }
                boundingBoxProducer.send_bounding_box(bounding_box = boundingBox)
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