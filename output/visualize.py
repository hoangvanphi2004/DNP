import cv2
import json
import numpy
import time
import writeVideo
import os
from sys import argv
colors = []
lines = [[11, 9], [9, 7], [7, 6], [6, 12], [12, 13], [13, 7], [6, 8], [8, 10], [12, 14], [14, 16], [16, 20], [20, 18], [20, 19], [13, 15], [15, 17], [17, 23], [23, 22], [23, 21]]

def drawSkeleton(keypointsList, frame, img_w, img_h):
    result = frame
    
    for index, keypoints in keypointsList.items():
        for index, line in enumerate(lines):
            p1 = keypoints[str(line[0] - 1)]
            p2 = keypoints[str(line[1] - 1)]
            cv2.line(result, (int(p1[0] * img_w), int(p1[1] * img_h)), (int(p2[0] * img_w), int(p2[1] * img_h)), color = (255, 255, 0), thickness = 1)
            
        for index, keypoint in keypoints.items():
            cv2.circle(result, (int(keypoint[0] * img_w), int(keypoint[1] * img_h)), radius = 1, color = (0, 255, 255), thickness = -1)
    return result

background = cv2.imread("black_screen.png" if len(argv) <= 2 else argv[2], cv2.IMREAD_COLOR)

def drawBoudingBox(boungdingBoxs, frame, staff_check = False, staff_id = None):
    result = frame
    
    for index, boudndingBox in boungdingBoxs.items():
        if staff_check:
            if(staff_id[index]):
                cv2.putText(result, "staff", (int(boudndingBox["br_coord2d"][0]), int(boudndingBox["tl_coord2d"][1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 1, cv2.LINE_AA)
        cv2.rectangle(result, (int(boudndingBox["tl_coord2d"][0]), int(boudndingBox["tl_coord2d"][1])), (int(boudndingBox["br_coord2d"][0]), int(boudndingBox["br_coord2d"][1])), (255, 0, 0), 1)
    
        cv2.putText(result, str(int(index)), (int(boudndingBox["tl_coord2d"][0]), int(boudndingBox["tl_coord2d"][1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)

    return result

data = []
with open(argv[1]) as f:
    for line in f:
        data.append(json.loads(line))
        
videoEngine = writeVideo.VideoWriter(data[0]["img_w"], data[0]["img_h"])

for frame in data:
    backgroundTemp = numpy.copy(background)
    backgroundTemp = cv2.resize(backgroundTemp, (frame["img_w"], frame["img_h"]))
    backgroundTemp = cv2.putText(backgroundTemp, str(int(frame["frame_id"])), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)
    
    backgroundTemp = drawSkeleton(frame["pose"]["persons"], backgroundTemp, frame["img_w"], frame["img_h"])
    backgroundTemp = drawBoudingBox(frame["approach"], backgroundTemp, staff_check = True, staff_id = frame["pose"]["is_staff"])
    videoEngine.write(backgroundTemp);
    cv2.imshow("frame", backgroundTemp)

    if cv2.waitKey(1) == ord('q'):
        break
cv2.destroyAllWindows()