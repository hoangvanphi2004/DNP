import consumer
import producer
import boundingBoxDetection
import cv2 as cv
import numpy as np
import time
import writeVideo
import writeToJSON

from queue import Queue

def draw(bounding_box, keypoints, frame):
    result = frame
    cv.rectangle(result, (int(bounding_box[0]), int(bounding_box[1])), (int(bounding_box[2]), int(bounding_box[3])), (255, 0, 0), 4)
    
    cv.putText(result, str(int(bounding_box[4])), (int(bounding_box[0]), int(bounding_box[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
    for keypoint in keypoints:
        cv.circle(result, (int(keypoint[0]), int(keypoint[1])), radius = 2, color = (0, 255, 0), thickness = -1)
    return result

if __name__ == "__main__":
    frameConsumer = consumer.FrameConsumer("receive_video")
    boundingBoxConsumer = consumer.BoundingBoxConsumer("receive_video")
    keypointsConsumer = consumer.KeypointsConsumer("receive_video")
    videoWriter = writeVideo.VideoWriter()
    jsonWriter = writeToJSON.JSONWriter()
    setupProducer = producer.SetupProducer()
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