#!/usr/bin/env python

import sys
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Consumer, OFFSET_END, TopicPartition
import numpy as np;
import json
import time

class KafkaConsumer:
    def __init__(self, group_id, topics):
        config_parser = ConfigParser()
        config_parser.read("config.ini")
        self.config = dict(config_parser['default'])
        self.config.update(config_parser['consumer'])
        self.config.update({"group.id": group_id})

        self.consumer = Consumer(self.config)
        self.consumer.subscribe(topics)

class FrameConsumer(KafkaConsumer):
    def __init__(self):
        super().__init__("frame", ["frame"])

        self.topic = TopicPartition("frame", partition = 0)

    def receive_frame(self):
        msg = self.consumer.poll(1.0)
        if msg is None:
            print("Waiting...")
        elif msg.error():
            print("ERROR: %s".format(msg.error()))
        else:
            print("Consumed event from topic {topic}: offset = {offset} partition = {partition}".format(
                topic=msg.topic(), offset=msg.offset(), partition = msg.partition()))
            return True, np.array(list(msg.value())).reshape(480, 640, 3).astype(np.uint8), msg.offset()
        return False, 0, 0
    
    def receive_latest_frame(self):
        # latest_offset = self.consumer. get_watermark_offsets(self.topic)[1]
        # topic_with_latest_offset = TopicPartition("frame", partition = 0, offset = latest_offset)
        # self.consumer.assign([topic_with_latest_offset])

        msg = self.consumer.poll(1.0)
        if msg is None:
            print("Waiting...")
        elif msg.error():
            print("ERROR: %s".format(msg.error()))
        else:
            print("Consumed event from topic {topic}: offset = {offset} partition = {partition}".format(
                topic=msg.topic(), offset=msg.offset(), partition = msg.partition()))
            return True, np.array(list(msg.value())).reshape(480, 640, 3).astype(np.uint8), msg.offset()
        return False, 0, 0

class BoundingBoxAndFrameConsumer(KafkaConsumer):
    def __init__(self):
        super().__init__("frame_and_bounding_box", ["frame", "bounding_box"])

        self.consumer1 = Consumer(self.config)
        self.consumer2 = Consumer(self.config)
        self.consumer1.subscribe(["frame"])
        self.consumer2.subscribe(["bounding_box"])

    def receive(self):
        msg = self.consumer.poll(1.0)
        print(msg)
        if msg is None:
            print("Waiting...")
        elif msg.error():
            print("ERROR: %s".format(msg.error()))
        else:
            print("Consumed event from topic {topic}: offset = {offset} partition = {partition}".format(
                topic=msg.topic(), offset=msg.offset(), partition = msg.partition()))
            if msg.topic() == "frame":
                return True, {"offset": msg.offset(), "data": np.array(list(msg.value())).reshape(480, 640, 3).astype(np.uint8)}, msg.topic()
            else:
                return True, json.loads(msg.value()), msg.topic()
        return False, 0, 0
    
    def receive_frame(self):
        msg = self.consumer1.poll(1.0)
        if msg is None:
            print("Waiting...")
        elif msg.error():
            print("ERROR: %s".format(msg.error()))
        else:
            print("Consumed event from topic {topic}: offset = {offset} partition = {partition}".format(
                topic=msg.topic(), offset=msg.offset(), partition = msg.partition()))
            return True, {"offset": msg.offset(), "data": np.array(list(msg.value())).reshape(480, 640, 3).astype(np.uint8)}, msg.topic()
        return False, 0, 0
        
    def receive_bounding_box(self):
        msg = self.consumer2.poll(1.0)
        if msg is None:
            print("Waiting...")
        elif msg.error():
            print("ERROR: %s".format(msg.error()))
        else:
            print("Consumed event from topic {topic}: offset = {offset} partition = {partition}".format(
                topic=msg.topic(), offset=msg.offset(), partition = msg.partition()))
            return True, json.loads(msg.value()), msg.topic()
        return False, 0, 0

