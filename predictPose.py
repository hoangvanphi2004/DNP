import consumer
import poseEstimation
import writeVideo
import writeToJSON
import cv2 as cv
import numpy as np
import time

def draw(bounding_box, keypoints, frame):
    result = frame
    cv.rectangle(result, (int(bounding_box[0]), int(bounding_box[1])), (int(bounding_box[2]), int(bounding_box[3])), (255, 0, 0), 4)
    
    cv.putText(result, str(int(bounding_box[4])), (int(bounding_box[0]), int(bounding_box[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
    for keypoint in keypoints:
        cv.circle(result, (int(keypoint[0]), int(keypoint[1])), radius = 2, color = (0, 255, 0), thickness = -1)
    return result

if __name__ == "__main__":
    boundingBoxConsumer = consumer.BoundingBoxConsumer("FandB")
    frameConsumer = consumer.FrameConsumer("FandB")
    poseEstimationModel = poseEstimation.PoseEstimation()
    videoWriter = writeVideo.VideoWriter()
    jsonWriter = writeToJSON.JSONWriter()
    try:
        frames = []
        while True:
            time1 = time.time()
            retFrame, frame, offsetFrame = frameConsumer.receive_frame()
            #print("finish receive frame")
            time2 = time.time()
            retBoundingBox, boundingBoxData, offsetBoundingBox = boundingBoxConsumer.receive_bounding_box()
            #print("finish receive bounding box")
            time3 = time.time()

            # if retBoundingBox:
            #     print("->", offsetFrame, offsetBoundingBox)

            if retFrame:
                #print(data);
                frames.append({
                    "offset": offsetFrame,
                    "data": frame
                }); 
                if retBoundingBox:
                    print(len(frames))
                    frame = [frame for frame in frames if frame["offset"] == boundingBoxData["offset"]][0]["data"]
                    bounding_boxs = boundingBoxData["data"]
                    #print(frame, bounding_boxs)

                    showing_frame = frame
                    allKeypoints = []
                    humanBoundingBox = []
                    for bounding_box in bounding_boxs:
                        if bounding_box[6] == 0:
                            keypoints = poseEstimationModel.predict(frame, bounding_box)
                            showing_frame = draw(bounding_box, keypoints, frame)
                            allKeypoints.append(keypoints.tolist())
                            humanBoundingBox.append(bounding_box)

                    videoWriter.write(showing_frame)

                    if(len(humanBoundingBox) != 0):
                        bounding_boxs = np.array(humanBoundingBox)
                        jsonWriter.write_data(boundingBoxs = bounding_boxs[:, : 4], ids = bounding_boxs[:, 4], keypointsList = allKeypoints, frameId = boundingBoxData["offset"])

                    # cv.imshow('frame', showing_frame)
                    # if cv.waitKey(1) == ord('q'):
                    #     break

                    frames = [frame for frame in frames if frame["offset"] != boundingBoxData["offset"]]
            #else:
                # cv.destroyAllWindows()
            time4 = time.time();
            #print(time4 - time3, time3 - time2, time2 - time1);
    except KeyboardInterrupt:
        pass
    finally:
        videoWriter.video.release()
        # boundingBoxAndFrameConsumer.consumer.close()