import consumer
import producer
import boundingBoxDetection
import cv2 as cv
import time
import writeVideo
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
    try:
        framesQueue = Queue()
        boundingBoxsQueue = Queue()
        while True:
            retBoundingBox, boundingBoxData, offset = boundingBoxConsumer.receive_bounding_box()
            retKeypoints, keypointsData, offset = keypointsConsumer.receive_keypoints()
            retFrame, frame, offset = frameConsumer.receive_frame()


            if retFrame:
                framesQueue.put({
                    "offset": offset,
                    "data": frame
                });
             
            if retBoundingBox:
                boundingBoxsQueue.put(boundingBoxData)

            if retKeypoints:
                print(framesQueue.qsize(), boundingBoxsQueue.qsize(), keypointsData['offset'])
                frame = framesQueue.get()
                while frame['offset'] < keypointsData['offset']:
                    frame = framesQueue.get()
                    pass
                
                boundingBoxs = boundingBoxsQueue.get()
                while boundingBoxs['offset'] < keypointsData['offset']:
                    boundingBoxs = boundingBoxsQueue.get()
                    pass
                
                frame = frame['data']
                boundingBoxs = boundingBoxs["data"]
                keypointsList = keypointsData["data"]
                
                #print("frame", frame, "bb", len(boundingBoxs), "kps", len(keypointsList))

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