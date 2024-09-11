#!/usr/bin/env python

import sys
from random import choice
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Producer
import numpy as np;
import cv2 as cv
import json

class KafkaProducer:
    def __init__(self):
        config_parser = ConfigParser()
        config_parser.read("config.ini")
        config = dict(config_parser['default'])

        self.producer = Producer(config)
    
    def delivery_callback(self, err, msg):
        if err:
            print('ERROR: Message failed delivery: {}'.format(err))
            
class SetupProducer(KafkaProducer):
    def __init__(self):
        super().__init__()

    def send_setup_value(self, setupValue):
        self.producer.produce("setup", value = str(setupValue), callback=self.delivery_callback)
        self.producer.poll(0)
        
class FrameProducer(KafkaProducer):
    def __init__(self):
        super().__init__()

    def send_frame(self, frame, offset):
        self.producer.produce("frame", value = frame.tobytes(), key = str(offset), callback=self.delivery_callback)
        self.producer.poll(0)
        
    def send_latest_frame(self, frame):
        self.producer.produce("latest_frame", value = frame.tobytes(), callback=self.delivery_callback)
        self.producer.poll(0)

class BoundingBoxProducer(KafkaProducer):
    def __init__(self):
        super().__init__()

    def send_bounding_box(self, boundingBox):
        self.producer.produce("bounding_box", value = json.dumps(boundingBox), callback=self.delivery_callback)
        self.producer.poll(0)

class KeyPointsProducer(KafkaProducer):
    def __init__(self):
        super().__init__()

    def send_keypoints(self, keypoints):
        self.producer.produce("keypoints", value = json.dumps(keypoints), callback=self.delivery_callback)
        self.producer.poll(0)
        
