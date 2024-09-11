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
    setupConsumer = consumer.SetupConsumer("pose")

    try:
        frames = []
        boundingBoxQueue = []
        while True:
            retFrame, frame, offsetFrame = frameConsumer.receive_frame()
            retSetup, setupValue = setupConsumer.receive_setup_value()
            if setupValue == 5:
                break
            retBoundingBox, boundingBoxData, offsetBoundingBox = boundingBoxConsumer.receive_bounding_box()

            if retFrame:
                frames.append(frame); 
            if retBoundingBox:
                boundingBoxQueue.append(boundingBoxData);
            
            while(len(frames) > 0 and len(boundingBoxQueue) > 0):
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
                
                showing_frame = frame
                allKeypoints = []
                humanBoundingBox = []
                for bounding_box in bounding_boxs:
                    keypoints = poseEstimationModel.predict(frame, bounding_box)
                    allKeypoints.append(keypoints.tolist())
                    humanBoundingBox.append(bounding_box)

                ### -------------------Send Keypoints---------------------###

                keypoints = {
                    "offset": offset,
                    "data": allKeypoints
                }

                keypointsProducer.send_keypoints(keypoints)
    except KeyboardInterrupt:
        pass
    finally:
        boundingBoxConsumer.consumer.close()
        frameConsumer.consumer.close()
        keypointsProducer.producer.flush()