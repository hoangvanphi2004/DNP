import sys
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Consumer, OFFSET_END, OFFSET_BEGINNING, TopicPartition
import numpy as np;
import json
import time

class KafkaConsumer:
    def __init__(self, groupId, topics, onAssign = None):
        config_parser = ConfigParser()
        config_parser.read("config.ini")
        self.config = dict(config_parser['default'])
        self.config.update(config_parser['consumer'])
        self.config.update({"group.id": groupId})
        self.consumer = Consumer(self.config)
        if onAssign != None:
            self.consumer.subscribe([topics], on_assign = onAssign)
        else:
            self.consumer.subscribe([topics])

class SetupConsumer(KafkaConsumer):
    def __init__(self, groupId):
        super().__init__(groupId = groupId, topics = "setup")

        self.topic = TopicPartition("setup", partition = 0)

    def receive_setup_value(self):
        msg = self.consumer.poll(0)
        if msg is None:
            pass
        elif msg.error():
            print("ERROR: %s".format(msg.error()))
        else:
            return True, int(msg.value())
        return False, 0
    
class FrameConsumer(KafkaConsumer):
    def __init__(self, groupId):
        super().__init__(groupId = groupId, topics = "frame")

    def receive_frame(self):
        msg = self.consumer.poll(0)
        if msg is None:
            pass
        elif msg.error():
            print("ERROR: %s".format(msg.error()))
        else:
            return True, {
                "offset": int(msg.key()),
                "data": np.array(list(msg.value())).reshape(480, 640, 3).astype(np.uint8)
                }, msg.offset()
        return False, 0, 0
    
class LatestFrameConsumer(KafkaConsumer):
    def __init__(self, groupId):
        super().__init__(groupId = groupId, topics = "latest_frame")

        self.topic = TopicPartition("latest_frame", partition = 0)
    def receive_latest_frame(self):
        msg = self.consumer.poll(0.15)

        topic_with_latest_offset = TopicPartition("latest_frame", partition = 0, offset = OFFSET_END)
        self.consumer.assign([topic_with_latest_offset])
        
        if msg is None:
            pass
        elif msg.error():
            print("ERROR: %s".format(msg.error()))
        else:
            return True, np.array(list(msg.value())).reshape(480, 640, 3).astype(np.uint8), msg.offset()
        return False, 0, 0

class BoundingBoxConsumer(KafkaConsumer):
    def __init__(self, groupId):
        super().__init__(groupId = groupId, topics = "bounding_box")
        
    def receive_bounding_box(self):
        msg = self.consumer.poll(0)
        if msg is None:
            pass
        elif msg.error():
            print("ERROR: %s".format(msg.error()))
        else:
            return True, json.loads(msg.value()), msg.offset()
        return False, 0, 0
    
class KeypointsConsumer(KafkaConsumer):
    def __init__(self, groupId):
        super().__init__(groupId = groupId, topics = "keypoints")
        
    def receive_keypoints(self):
        msg = self.consumer.poll(0)
        if msg is None:
            pass
        elif msg.error():
            print("ERROR: %s".format(msg.error()))
        else:
            return True, json.loads(msg.value()), msg.offset()
        return False, 0, 0

