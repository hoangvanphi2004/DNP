import consumer
import producer
import boundingBoxDetection
import cv2 as cv
import numpy as np
import time
import writeVideo
import writeToJSON
import ReID
from random import randint

from queue import Queue

colors = []
lines = [[11, 9], [9, 7], [7, 6], [6, 12], [12, 13], [13, 7], [6, 8], [8, 10], [12, 14], [14, 16], [16, 20], [20, 18], [20, 19], [13, 15], [15, 17], [17, 23], [23, 22], [23, 21]]

def draw(bounding_box, keypoints, frame):
    result = frame
    cv.rectangle(result, (int(bounding_box[0]), int(bounding_box[1])), (int(bounding_box[2]), int(bounding_box[3])), (255, 0, 0), 1)
    
    cv.putText(result, str(int(bounding_box[4])), (int(bounding_box[0]), int(bounding_box[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv.LINE_AA)
    
    for index, line in enumerate(lines):
        p1 = keypoints[line[0] - 1]
        p2 = keypoints[line[1] - 1]
        cv.line(result, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), color = (255, 255, 0), thickness = 1)
        
    for keypoint in keypoints:
        cv.circle(result, (int(keypoint[0]), int(keypoint[1])), radius = 1, color = (0, 255, 255), thickness = -1)
    return result

if __name__ == "__main__":
    for line in lines:
        colors.append((randint(0, 255), randint(0, 255), randint(0, 255)))
    frameConsumer = consumer.FrameConsumer("receive_video")
    boundingBoxConsumer = consumer.BoundingBoxConsumer("receive_video")
    keypointsConsumer = consumer.KeypointsConsumer("receive_video")
    videoWriter = writeVideo.VideoWriter()
    jsonWriter = writeToJSON.JSONWriter()
    setupProducer = producer.SetupProducer()
    tracking = ReID.Track()
    setupProducer.send_setup_value(2)
    setupProducer.producer.flush()
    
    try:
        framesQueue = []
        boundingBoxsQueue = []
        keypointsQueue = []
        while True:
            retBoundingBox, boundingBoxData, offset = boundingBoxConsumer.receive_bounding_box()
            retKeypoints, keypointsData, offset = keypointsConsumer.receive_keypoints()
            retFrame, frame, offset = frameConsumer.receive_frame()
                
            if retFrame:
                framesQueue.append(frame);
             
            if retBoundingBox:
                boundingBoxsQueue.append(boundingBoxData)

            if retKeypoints:
                keypointsQueue.append(keypointsData)

            while(len(keypointsQueue) > 0 and len(boundingBoxsQueue) > 0 and len(framesQueue) > 0):
                #print(framesQueue.qsize(), boundingBoxsQueue.qsize(), keypointsData['offset'])
                #print(len(keypointsQueue), len(boundingBoxsQueue), len(framesQueue))
                keypointsData = keypointsQueue[0]
                frame = framesQueue[0]
                while frame['offset'] < keypointsData['offset'] and len(framesQueue) > 1:
                    framesQueue.pop(0)
                    frame = framesQueue[0]
                
                if(frame["offset"] < keypointsData["offset"]):
                    framesQueue.pop(0)
                    break;
                
                boundingBoxs = boundingBoxsQueue[0]
                while boundingBoxs['offset'] < keypointsData['offset'] and len(boundingBoxsQueue) > 1:
                    boundingBoxsQueue.pop(0)
                    boundingBoxs = boundingBoxsQueue[0]
                
                if(boundingBoxs["offset"] < keypointsData["offset"]):
                    boundingBoxsQueue.pop(0)
                    break;
                
                framesQueue.pop(0)
                boundingBoxsQueue.pop(0)
                keypointsQueue.pop(0)
                
                frame = frame['data']
                boundingBoxs = boundingBoxs["data"]
                keypointsList = keypointsData["data"]
                
                if len(boundingBoxs) != 0:
                    boundingBoxs = np.array(boundingBoxs)
                    boundingBoxs, keypointsList = ReID.deleteOverLap(boundingBoxs = boundingBoxs, keypointLists = keypointsList)
                    boundingBoxs = np.array(tracking.tracking(boundingBoxs = boundingBoxs, frame = frame))
                    if boundingBoxs.shape[0] != 0:
                        jsonWriter.write_data(boundingBoxs = boundingBoxs[:, : 4], ids = boundingBoxs[:, 4], keypointsList = keypointsList, frameId = keypointsData["offset"])
                
                #print("frame", frame, "bb", len(boundingBoxs), "kps", len(keypointsList))

                showing_frame = frame

                for index in range(len(boundingBoxs)):
                    keypoints = keypointsList[index]
                    boundingBox = boundingBoxs[index]
                    showing_frame = draw(boundingBox, keypoints, frame)
                
                videoWriter.write(showing_frame)
    except KeyboardInterrupt:
        pass
    finally:
        frameConsumer.consumer.close()
        boundingBoxConsumer.consumer.close()
        keypointsConsumer.consumer.close()