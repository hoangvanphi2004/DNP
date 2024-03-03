import consumer
import poseEstimation
import cv2 as cv

def draw(bounding_box, keypoints, frame):
    result = frame
    cv.rectangle(result, (int(bounding_box[0]), int(bounding_box[1])), (int(bounding_box[2]), int(bounding_box[3])), (255, 0, 0), 4)
    for keypoint in keypoints:
        cv.circle(result, (int(keypoint[0]), int(keypoint[1])), radius = 2, color = (0, 255, 0), thickness = -1)
    return result

if __name__ == "__main__":
    boundingBoxAndFrameConsumer = consumer.BoundingBoxAndFrameConsumer()
    poseEstimationModel = poseEstimation.PoseEstimation()
    try:
        frames = []

        cnt = 0

        while True:
            # if cnt == 0:
            #     ret, data, topic = boundingBoxAndFrameConsumer.receive_frame()
            # else:
            #     ret, data, topic = boundingBoxAndFrameConsumer.receive_bounding_box()
            # cnt += 1
            # cnt %= 2

            ret, data, topic = boundingBoxAndFrameConsumer.receive()
            print(ret);
            if ret:
                #print(data);
                if(topic == "frame"):
                    frames.append(data); 
                else:
                    frame = [frame for frame in frames if frame["offset"] == data["offset"]][0]["data"]
                    bounding_boxs = data["data"]
                    #print(frame, bounding_boxs)

                    showing_frame = frame

                    #for bounding_box in bounding_boxs:
                        #if bounding_box[5] == 0:
                    keypoints = poseEstimationModel.predict(frame, bounding_boxs)
                    showing_frame = draw(bounding_boxs, keypoints, frame)
                    
                    cv.imshow('frame', showing_frame)
                    if cv.waitKey(1) == ord('q'):
                        break

                    frames = [frame for frame in frames if frame["offset"] != data["offset"]]
            else:
                cv.destroyAllWindows()
    except KeyboardInterrupt:
        pass
    finally:
        boundingBoxAndFrameConsumer.consumer.close()