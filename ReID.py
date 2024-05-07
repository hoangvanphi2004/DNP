from boxmot import OCSORT
import numpy as np
import math

def area(boundingBox):
    return (int(boundingBox[2]) - int(boundingBox[0])) * (int(boundingBox[3]) - int(boundingBox[1]))

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

def deleteOverLap(boundingBoxs, keypointLists):
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
    print(uselessBox)
    boundingBoxs = np.delete(boundingBoxs, uselessBox, 0)
    keypointLists = [keypointLists[i] for i in range(len(keypointLists)) if i not in uselessBox]
    return boundingBoxs, keypointLists

class Track:
    def __init__(self) -> None:
        self.tracker = OCSORT(min_hits = 5, max_age = 50, delta_t = 10, inertia = 0.05, use_byte = True);
    
    def tracking(self, boundingBoxs, frame):
        results = self.tracker.update(np.array(boundingBoxs), np.array(frame))
        return results.tolist()