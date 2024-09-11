from boxmot import OCSORT
import numpy as np
import math
import copy

re_id_bounding_boxs = []
re_id_keypoint_lists = []
max_size = 100

def push(boundingBoxs, keypointLists):
    global re_id_bounding_boxs, re_id_keypoint_lists
    re_id_bounding_boxs.append(boundingBoxs)
    re_id_keypoint_lists.append(keypointLists)
    if(len(re_id_bounding_boxs) > max_size):
        re_id_bounding_boxs = re_id_bounding_boxs[1:]
        re_id_keypoint_lists = re_id_keypoint_lists[1:]

def area(boundingBox):
    return (max(int(boundingBox[2]) - int(boundingBox[0]), 0)) * (max(int(boundingBox[3]) - int(boundingBox[1]), 0))
#--------------------------Delete Overlap--------------------------------------#    

def iou(bb1, bb2):
    ## xmin, ymin, xmax, ymax
    bb_intersection = np.array([max(bb1[0], bb2[0]), max(bb1[1], bb2[1]), min(bb1[2], bb2[2]), min(bb1[3], bb2[3])])
    
    intersection = area(bb_intersection)
    bb1_area = area(bb1)
    bb2_area = area(bb2)
    return max(intersection / bb1_area, intersection / bb2_area)

def compareKeypoints(this, other, threshold = 10):
    sum = 0
    for i in range(len(this)):
        if(i <= 6 or (23 <= i and i <= 90)):
            thisPoint = np.array(this[i])
            otherPoint = np.array(other[i])
            distance = np.sqrt(np.sum((thisPoint - otherPoint) * (thisPoint - otherPoint)))
            sum += distance
    sum /= (7 + 90 - 23 + 1)
    return sum < threshold

def deleteOverLap(boundingBoxs, keypointLists, iob_threshold = 0.9):
    uselessBox = []
    for i in range(boundingBoxs.shape[0]):
        boundingBox = boundingBoxs[i]
        keypointList = keypointLists[i]
        
        for j in range(boundingBoxs.shape[0]):
            otherBoundingBox = boundingBoxs[j]
            otherKeypointsList = keypointLists[j]
            if i != j and compareKeypoints(keypointList, otherKeypointsList):
                if(area(boundingBox) <= area(otherBoundingBox)):
                    uselessBox.append(j)
                else:
                    uselessBox.append(i)
    
    for i in range(boundingBoxs.shape[0]):
        if area(boundingBoxs[i]) < 2000:
            uselessBox.append(i); 
    boundingBoxs = np.delete(boundingBoxs, uselessBox, 0)
    keypointLists = [keypointLists[i] for i in range(len(keypointLists)) if i not in uselessBox]
    return boundingBoxs, keypointLists

class Track:
    def __init__(self) -> None:
        self.tracker = OCSORT(det_thresh = 0.1, asso_threshold = 0.1, delta_t = 1);
    def tracking(self, boundingBoxs, frame):
        results = self.tracker.update(np.array(boundingBoxs), np.array(frame))
        return results.tolist()