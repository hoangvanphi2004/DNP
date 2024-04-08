import consumer
import producer
import poseEstimation
import writeVideo
import writeToJSON
import cv2 as cv
import numpy as np
import time
from queue import Queue

if __name__ == "__main__":
    keypointsProducer = producer.KeyPointsProducer()
    boundingBoxConsumer = consumer.BoundingBoxConsumer("FandB")
    frameConsumer = consumer.FrameConsumer("FandB")
    poseEstimationModel = poseEstimation.PoseEstimation()
    setupProducer = producer.SetupProducer()
    setupProducer.send_setup_value(1)
    setupProducer.producer.flush()
    
    try:
        frames = []
        boundingBoxQueue = []
        while True:
            # time1 = time.time()
            retFrame, frame, offsetFrame = frameConsumer.receive_frame()
            #print("finish receive frame")
            # time2 = time.time()
            retBoundingBox, boundingBoxData, offsetBoundingBox = boundingBoxConsumer.receive_bounding_box()
            # retBoundingBox = None
            #print("finish receive bounding box")

            # if retBoundingBox:
            #     print("->", offsetFrame, offsetBoundingBox)

            if retFrame:
                #print(data);
                frames.append(frame); 
            if retBoundingBox:
                boundingBoxQueue.append(boundingBoxData);
            
            while(len(frames) > 0 and len(boundingBoxQueue) > 0):
                #print(frames.qsize())
                boundingBoxData = boundingBoxQueue[0];
                frame = frames[0]
                while frame['offset'] < boundingBoxData['offset'] and len(frames) > 1:
                    frames.pop(0)
                    frame = frames[0]
                
                if(frame['offset'] < boundingBoxData['offset']):
                    frames.pop(0)
                    break;
                
                frames.pop(0)
                boundingBoxQueue.pop(0)
                offset = frame['offset']
                frame = frame['data']
                bounding_boxs = boundingBoxData["data"]
                
                # time3 = time.time()
                showing_frame = frame
                allKeypoints = []
                humanBoundingBox = []
                for bounding_box in bounding_boxs:
                    keypoints = poseEstimationModel.predict(frame, bounding_box)
                    allKeypoints.append(keypoints.tolist())
                    humanBoundingBox.append(bounding_box)

                #videoWriter.write(showing_frame)

                ### -------------------Send Keypoints---------------------###

                keypoints = {
                    "offset": offset,
                    "data": allKeypoints
                }

                keypointsProducer.send_keypoints(keypoints)

                # time4 = time.time();
                # print(time4 - time3, time3 - time2, time2 - time1);
    except KeyboardInterrupt:
        pass
    finally:
        # videoWriter.video.release()
        boundingBoxConsumer.consumer.close()
        frameConsumer.consumer.close()
        keypointsProducer.producer.flush()