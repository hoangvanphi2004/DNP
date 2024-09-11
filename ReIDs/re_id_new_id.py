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

def re_id_new_id(data, num_pre_frames_check, iou_threshold, vec_thres, max_volume):
    result = []
    set_id = [i for i in range(max_volume)]
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
            for index_previous in range(index - 1, max(index - num_pre_frames_check, 0), -1):
                previous_frame = data[index_previous]
                previous_of_previous_frame = data[index_previous - 1]
                found = False
                for id_previous, bb_previous in previous_frame["approach"].items():
                    if((str(id_previous) in previous_of_previous_frame["approach"]) and (str(id_previous) not in data[index]["approach"])):
                        tl = bb_previous["tl_coord2d"]
                        br = bb_previous["br_coord2d"]
                        pre_tl = previous_of_previous_frame["approach"][str(id_previous)]["tl_coord2d"]
                        pre_br = previous_of_previous_frame["approach"][str(id_previous)]["br_coord2d"]
                        vec = velocity_bb(pre_tl, pre_br, tl, br, vec_thres)
                        t = index - index_previous
                        predict_bb = {
                            "tl_coord2d": tl + vec * t, 
                            "br_coord2d": br + vec * t
                        };
                        if iob(predict_bb, bb) >= iou_threshold and norm(vec) >= vec_thres:
                            id = int(id)
                            id_previous = int(id_previous)
                            set_id[id], set_id[id_previous] = set_id[id_previous], set_id[id]
                            set_new_id[id], set_new_id[id_previous] = set_new_id[id_previous], set_new_id[id]
                            found = True
                            break;
                if found:
                    break;
                
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
    
    #--------------------------------Naive way----------------------------------------#
    # for index, frame in enumerate(data):
    #     # for i in range(max(index - num_pre_frames_check, 0), index + 1):
    #     #     result.append(copy.deepcopy(data[i]))
    #     recent = copy.deepcopy(frame)
    #     if(len(recent) > 0):
    #         for id, bb in recent["approach"].items():
    #             real_id = []
    #             for index_previous in range(index - 1, index - num_pre_frames_check, -1):
    #                 previous_frame = data[index_previous]
    #                 previous_of_previous_frame = data[index_previous - 1]
    #                 found = False
    #                 for id_previous, bb_previous in previous_frame["approach"].items():
    #                     if((str(id_previous) in previous_of_previous_frame["approach"]) and (str(id_previous) not in recent["approach"]) and (str(id) not in previous_frame["approach"])):
    #                         tl = bb_previous["tl_coord2d"]
    #                         br = bb_previous["br_coord2d"]
    #                         pre_tl = previous_of_previous_frame["approach"][str(id_previous)]["tl_coord2d"]
    #                         pre_br = previous_of_previous_frame["approach"][str(id_previous)]["br_coord2d"]
    #                         vec = velocity_bb(pre_tl, pre_br, tl, br, vec_thres)
    #                         t = index - index_previous
    #                         predict_bb = {
    #                             "tl_coord2d": tl + vec * t, 
    #                             "br_coord2d": br + vec * t
    #                         };
    #                         if iou(predict_bb, bb) >= iou_threshold and norm(vec) >= vec_thres:
    #                             for future_index in range(index, len(data)):
    #                                 if(str(id) in data[future_index]["approach"]):
    #                                     bb_id = copy.deepcopy(data[future_index]["approach"][str(id)])
    #                                     data[future_index]["approach"][str(id_previous)] = bb_id
    #                                     data[future_index]["approach"].pop(str(id))
                                
    return data

def main(json_file_name):
    data = []
    with open(json_file_name) as f:
        for line in f:
            data.append(json.loads(line))

    new_data = re_id_new_id(data = data, num_pre_frames_check = 100, iou_threshold = 0.9, vec_thres = 10, max_volume = 100)

    with open(json_file_name, "w") as f:
        for line in new_data:
            json.dump(line, f)
            f.write("\n")
