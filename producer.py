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
        else:
            print("Produced event to topic {topic}".format(
                topic=msg.topic()))
            
class FrameProducer(KafkaProducer):
    def __init__(self):
        super().__init__()

    def send_frame(self, frame):
        self.producer.produce("frame", value = frame.tobytes(), callback=self.delivery_callback)
        self.producer.poll(0)

class BoundingBoxProducer(KafkaProducer):
    def __init__(self):
        super().__init__()

    def send_bounding_box(self, bounding_box):
        self.producer.produce("bounding_box", value = json.dumps(bounding_box), callback=self.delivery_callback)
        self.producer.poll(0)

        
