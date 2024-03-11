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
    jsonWriter = writeToJSON.JSONWriter()
    try:
        frames = Queue()
        while True:
            time1 = time.time()
            retFrame, frame, offsetFrame = frameConsumer.receive_frame()
            #print("finish receive frame")
            time2 = time.time()
            retBoundingBox, boundingBoxData, offsetBoundingBox = boundingBoxConsumer.receive_bounding_box()
            # retBoundingBox = None
            #print("finish receive bounding box")

            # if retBoundingBox:
            #     print("->", offsetFrame, offsetBoundingBox)

            if retFrame:
                #print(data);
                frames.put({
                    "offset": offsetFrame,
                    "data": frame
                }); 
            if retBoundingBox:
                #print(frames.qsize())
                frame = frames.get()
                while frame['offset'] < boundingBoxData['offset']:
                    frame = frames.get()
                    pass
                
                #print(frames.qsize(), "frame", frame['offset'], "bounding_box", boundingBoxData['offset'])
                offset = frame['offset']
                frame = frame['data']
                bounding_boxs = boundingBoxData["data"]
                #print(frame, bounding_boxs)
                
                time3 = time.time()
                showing_frame = frame
                allKeypoints = []
                humanBoundingBox = []
                for bounding_box in bounding_boxs:
                    keypoints = poseEstimationModel.predict(frame, bounding_box)
                    #showing_frame = draw(bounding_box, keypoints, frame)
                    allKeypoints.append(keypoints.tolist())
                    humanBoundingBox.append(bounding_box)

                #videoWriter.write(showing_frame)

                if(len(humanBoundingBox) != 0):
                    bounding_boxs = np.array(humanBoundingBox)
                    jsonWriter.write_data(boundingBoxs = bounding_boxs[:, : 4], ids = bounding_boxs[:, 4], keypointsList = allKeypoints, frameId = boundingBoxData["offset"])

                ### -------------------Send Keypoints---------------------###

                keypoints = {
                    "offset": offset,
                    "data": allKeypoints
                }

                keypointsProducer.send_keypoints(keypoints)

                time4 = time.time();
                print(time4 - time3, time3 - time2, time2 - time1);
    except KeyboardInterrupt:
        pass
    finally:
        # videoWriter.video.release()
        boundingBoxConsumer.consumer.close()
        frameConsumer.consumer.close()
        keypointsProducer.producer.flush()