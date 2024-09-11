import cv2
import json
import numpy as np
import time
import copy
import math
import os
from sys import argv
from statistics import mode
def area_bb(tl ,br):
    return max(br[0] - tl[0], 0) * max(br[1] - tl[1], 0)

def norm(vec):
    return math.sqrt(vec[0] ** 2 + vec[1] ** 2)

def velocity_bb(tl1, br1, tl2, br2, vec_thres):
    tl1 = np.array(tl1)
    br1 = np.array(br1)
    tl2 = np.array(tl2)
    br2 = np.array(br2)
    if(norm(br2 - br1) < vec_thres or norm(tl2 - tl1) < vec_thres):
        return np.array([0, 0]);
    return ((br2 - br1) + (tl2 - tl1)) / 2;

def iou(bb1, bb2):
    p11 = bb1["tl_coord2d"]
    p12 = bb1["br_coord2d"]
    p21 = bb2["tl_coord2d"]
    p22 = bb2["br_coord2d"]
    
    intersection = area_bb((max(p11[0], p21[0]), max(p11[1], p21[1])), (min(p12[0], p22[0]), min(p12[1], p22[1])))
    bb1_area = area_bb(p11, p12)
    bb2_area = area_bb(p21, p22)
    return intersection / (bb1_area + bb2_area - intersection)

def iob(bb1, bb2):
    p11 = bb1["tl_coord2d"]
    p12 = bb1["br_coord2d"]
    p21 = bb2["tl_coord2d"]
    p22 = bb2["br_coord2d"]
    
    intersection = area_bb((max(p11[0], p21[0]), max(p11[1], p21[1])), (min(p12[0], p22[0]), min(p12[1], p22[1])))
    bb1_area = area_bb(p11, p12)
    bb2_area = area_bb(p21, p22)
    return max(intersection / bb1_area, intersection / bb2_area)

def re_id_new_id(data, num_pre_frames_check, iou_threshold, chance_threshold, max_volume):
    staff_chances = [0 for i in range(max_volume)]
    appear_times = [0 for i in range(max_volume)]
    for index, frame in enumerate(data):
        for id, bb in data[index]["approach"].items():
            appear_times[int(id)] += 1;
            for index_previous in range(index - 1, max(index - num_pre_frames_check, 0), -1):
                previous_frame = dict(data[index_previous])
                previous_of_previous_frame = dict(data[index_previous - 1])
                found = False
                for id_previous, bb_previous in previous_frame["approach"].items():
                    if(id_previous == id):
                        if iob(bb, bb_previous) < iou_threshold:
                            staff_chances[int(id)] += 1;
                            found = True
                            break;
                if found:
                    break;
                
    epsilon = 1e-9
    staff_chances = np.array(staff_chances) / (np.array(appear_times) + epsilon)
    staff_chances.astype(np.int64)
    
    for staff_id, chance in enumerate(staff_chances):
        for index, frame in enumerate(data):
            if str(staff_id) in data[index]["approach"]:
                if not "is_staff" in data[index]["pose"]:
                    data[index]["pose"]["is_staff"] = {}
                if(chance > chance_threshold):
                    data[index]["pose"]["is_staff"][str(staff_id)] = 1
                else:
                    data[index]["pose"]["is_staff"][str(staff_id)] = 0
                                
    return data

def main(json_file_name):
    data = []
    with open(json_file_name) as f:
        for line in f:
            data.append(json.loads(line))

    new_data = re_id_new_id(data = data, num_pre_frames_check = 100, iou_threshold = 0.9, chance_threshold = 0.6, max_volume = 100)

    with open(json_file_name, "w") as f:
        for line in new_data:
            json.dump(line, f)
            f.write("\n")