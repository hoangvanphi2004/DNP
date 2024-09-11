import cv2
import json
import numpy as np
import time
import copy
import math
import os
from sys import argv
from statistics import mode

def area(tl ,br):
    return max(br[0] - tl[0], 0) * max(br[1] - tl[1], 0)

def area_bb(bb):
    return max(bb["br_coord2d"][0] - bb["tl_coord2d"][0], 0) * max(bb["br_coord2d"][1] - bb["tl_coord2d"][1], 0)

def iou(bb1, bb2):
    p11 = bb1["tl_coord2d"]
    p12 = bb1["br_coord2d"]
    p21 = bb2["tl_coord2d"]
    p22 = bb2["br_coord2d"]
    
    intersection = area((max(p11[0], p21[0]), max(p11[1], p21[1])), (min(p12[0], p22[0]), min(p12[1], p22[1])))
    bb1_area = area(p11, p12)
    bb2_area = area(p21, p22)
    return intersection / (bb1_area + bb2_area - intersection)

def iob(bb1, bb2):
    p11 = bb1["tl_coord2d"]
    p12 = bb1["br_coord2d"]
    p21 = bb2["tl_coord2d"]
    p22 = bb2["br_coord2d"]
    
    intersection = area((max(p11[0], p21[0]), max(p11[1], p21[1])), (min(p12[0], p22[0]), min(p12[1], p22[1])))
    bb1_area = area(p11, p12)
    bb2_area = area(p21, p22)
    return max(intersection / bb1_area, intersection / bb2_area)

def norm(vec):
    return math.sqrt(vec[0] ** 2 + vec[1] ** 2)

def keypoints_diff(kpts1, kpts2, w, h):
    avg = 0;
    
    for id in [6, 7, 12, 13]:
        point1 = kpts1[str(id)]
        point2 = kpts2[str(id)]
        
        point1 = np.array(point1[:2])
        point2 = np.array(point2[:2])
        
        vec = point2 - point1
        vec[0] = vec[0] * w
        vec[1] = vec[1] * h
        avg += norm(vec = vec)
    return avg / 4

def keypoints_diff_for_overlap(kpts1, kpts2, w, h):
    avg = 0;
    
    for id in range(7):
        point1 = kpts1[str(id)]
        point2 = kpts2[str(id)]
        
        point1 = np.array(point1[:2])
        point2 = np.array(point2[:2])
        
        vec = point2 - point1
        vec[0] = vec[0] * w
        vec[1] = vec[1] * h
        avg += norm(vec = vec)
    
    for id in range(23, 91):
        point1 = kpts1[str(id)]
        point2 = kpts2[str(id)]
        
        point1 = np.array(point1[:2])
        point2 = np.array(point2[:2])
        
        vec = point2 - point1
        vec[0] = vec[0] * w
        vec[1] = vec[1] * h
        avg += norm(vec = vec)
    return avg / 75

def found_value_continuous(real_id, stay_in_a_row):
    now = 0;
    ans = 0;
    val = -1;
    cnt = 0;
    for each_id in real_id:
        if(now != each_id):
            if(cnt > ans and now != -1):
                val = now
                ans = cnt
            now = each_id
            cnt = 0;
        else:
            cnt += 1;
    if(cnt > ans):
        val = now
        ans = cnt;
    if(ans < stay_in_a_row):
        val = -1;
    return val

def delelte_over_lap(data, iob_threshold, keypoints_threshold):    
    for index, frame in enumerate(data):
        del_ids = []
        for id1, bb1 in frame["approach"].items():
            for id2, bb2 in frame["approach"].items():
                if (not id1 == id2) and (iob(bb1, bb2) > iob_threshold or keypoints_diff_for_overlap(frame["pose"]["persons"][id1], frame["pose"]["persons"][id2], frame["img_w"], frame["img_h"]) < keypoints_threshold):
                    if(area_bb(bb1) > area_bb(bb2)):
                        del_ids.append(id1)
                    else:
                        del_ids.append(id2)
        for del_id in del_ids:            
            if (del_id in data[index]["approach"]): 
                del data[index]["approach"][del_id]
                del data[index]["pose"]["persons"][del_id]
                    
    return data
def re_id_sitting_person(data, stay_in_a_row, num_pre_frames_check, iou_threshold, keypoints_threshold, max_volume):
    result = []
    w = data[0]["img_w"]
    h = data[0]["img_h"]
    # max volume : max number of people in the frame
    set_id = [i for i in range(max_volume)]
    
    #-----------------------------O(n)----------------------------#
    for index, frame in enumerate(data):
        set_new_id = [i for i in range(max_volume)]
        
        data[index]["approach2"] = {}
        data[index]["pose"]["persons2"] = {}
        for i in range(max_volume):
            if str(set_id[i]) in data[index]["approach"]:
                data[index]["approach2"][str(i)] = data[index]["approach"][str(set_id[i])]
                data[index]["pose"]["persons2"][str(i)] = data[index]["pose"]["persons"][str(set_id[i])]
                
        del data[index]["pose"]["persons"]
        data[index]["pose"]["persons"] = data[index]["pose"]["persons2"]
        del data[index]["pose"]["persons2"]
        
        del data[index]["approach"]
        data[index]["approach"] = data[index]["approach2"]
        del data[index]["approach2"]

        for id, bb in data[index]["approach"].items():
            kpts = data[index]["pose"]["persons"][id]
            real_id = []
            for index_previous in range(index - 1, max(index - num_pre_frames_check - 1, -1), -1):
                previous_frame = data[index_previous]
                found = False
                for id_previous, bb_previous in previous_frame["approach"].items():
                    kpts_previous = previous_frame["pose"]["persons"][id_previous]
                    if(iou(bb, bb_previous) >= iou_threshold or keypoints_diff(kpts, kpts_previous, w, h) <= keypoints_threshold):
                        real_id.append(id_previous)
                        found = True
                        break;
                    
                if not found:
                    real_id.append(-1)
            most_common = found_value_continuous(stay_in_a_row = stay_in_a_row, real_id = real_id)
            if(most_common != -1):
                real_id = int(most_common)
                id = int(id)
                if((id != real_id)):
                    set_id[id], set_id[real_id] = set_id[real_id], set_id[id]
                    set_new_id[id], set_new_id[real_id] = set_new_id[real_id], set_new_id[id]
                    
        data[index]["approach2"] = {}
        data[index]["pose"]["persons2"] = {}
        for i in range(max_volume):
            if str(i) in data[index]["approach"]:
                data[index]["approach2"][str(set_new_id[i])] = data[index]["approach"][str(i)]
                data[index]["pose"]["persons2"][str(set_new_id[i])] = data[index]["pose"]["persons"][str(i)]
                
        del data[index]["pose"]["persons"]
        data[index]["pose"]["persons"] = data[index]["pose"]["persons2"]
        del data[index]["pose"]["persons2"]
        
        del data[index]["approach"]
        data[index]["approach"] = data[index]["approach2"]
        del data[index]["approach2"]
        
        # ----------------------------Naive ways---------------------------------#
        # recent = copy.deepcopy(frame)
        # if(len(recent) > 0):
        #     for id, bb in recent["approach"].items():
        #         real_id = []
        #         for index_previous in range(index - 1, max(index - num_pre_frames_check - 1, -1), -1):
        #             previous_frame = data[index_previous]
        #             found = False
        #             for id_previous, bb_previous in previous_frame["approach"].items():
        #                 if(iou(bb, bb_previous) >= iou_threshold):
        #                     real_id.append(id_previous)
        #                     found = True
        #                     break;
                        
        #             if not found:
        #                 real_id.append(-1)
        #         most_common = found_value_continuous(stay_in_a_row = stay_in_a_row, real_id = real_id)
        #         if(most_common != -1):
        #             real_id = int(most_common)
        #             id = int(id)
        #             if((id != real_id)):
        #                 for future_index in range(index, len(data)):
        #                     if(str(id) in data[future_index]["approach"]):
        #                         res_id = dict(data[future_index]["approach"][str(id)])
        #                     if(str(real_id) in data[future_index]["approach"]):
        #                         res_real_id =  dict(data[future_index]["approach"][str(real_id)])
        #                     if(str(id) in data[future_index]["approach"] and str(real_id) in data[future_index]["approach"]):
        #                         data[future_index]["approach"][str(id)], data[future_index]["approach"][str(real_id)] = res_real_id, res_id 
        #                     elif(str(id) in data[future_index]["approach"]):
        #                         data[future_index]["approach"][str(real_id)] = res_id
        #                         data[future_index]["approach"].pop(str(id))
        #                         pass
        #                     elif(str(real_id) in data[future_index]["approach"]):
        #                         data[future_index]["approach"][str(id)] = res_real_id
        #                         data[future_index]["approach"].pop(str(real_id))
        #                         pass
    return data
    
def main(json_file_name):
    data = []
    with open(json_file_name) as f:
        for line in f:
            data.append(json.loads(line))

    new_data = delelte_over_lap(data = data, iob_threshold = 0.9, keypoints_threshold = 10)
    new_data = re_id_sitting_person(data = new_data, stay_in_a_row = 5, num_pre_frames_check = 100, iou_threshold = 0.8, keypoints_threshold = 10, max_volume = 40)

    with open(json_file_name, "w") as f:
        for line in new_data:
            json.dump(line, f)
            f.write("\n")