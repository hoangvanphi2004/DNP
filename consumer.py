#!/usr/bin/env python

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

class FrameConsumer(KafkaConsumer):
    def __init__(self, groupId):
        # def on_assign(consumer, partitions):
        #     for p in partitions:
        #         p.offset = OFFSET_END
        #     print('assign', partitions)
        #     consumer.assign(partitions)

        super().__init__(groupId = groupId, topics = "frame")

        self.topic = TopicPartition("frame", partition = 0)

    def receive_frame(self):
        msg = self.consumer.poll(0)
        if msg is None:
            #print("Waiting...")
            pass
        elif msg.error():
            print("ERROR: %s".format(msg.error()))
        else:
            print("Consumed event from topic {topic}: offset = {offset} partition = {partition}".format(
                topic=msg.topic(), offset=msg.offset(), partition = msg.partition()))
            return True, np.array(list(msg.value())).reshape(480, 640, 3).astype(np.uint8), msg.offset()
        return False, 0, 0
    
    def receive_latest_frame(self):
        msg = self.consumer.poll(0)

        # latest_offset = self.consumer.get_watermark_offsets(self.topic)[1]
        topic_with_latest_offset = TopicPartition("frame", partition = 0, offset = OFFSET_END)
        self.consumer.assign([topic_with_latest_offset])

        # print(self.consumer.assignment())
        # print(self.consumer.get_watermark_offsets(self.topic)[1])
        # time.sleep(0.04)

        # preMsg = None
        # msg = self.consumer.poll(0)
        # while msg != None: 
        #     time1 = time.time();
        #     preMsg = msg
        #     msg = self.consumer.poll(0)
        #     time2 = time.time();
        #     #print("inner:", time2 - time1)
        # msg = preMsg
        time.sleep(0.6)
        if msg is None:
            #print("Waiting...")
            pass
        elif msg.error():
            print("ERROR: %s".format(msg.error()))
        else:
            print("Consumed event from topic {topic}: offset = {offset} partition = {partition}".format(
                topic=msg.topic(), offset=msg.offset(), partition = msg.partition()))
            return True, np.array(list(msg.value())).reshape(480, 640, 3).astype(np.uint8), msg.offset()
        return False, 0, 0

class BoundingBoxConsumer(KafkaConsumer):
    def __init__(self, groupId):
        super().__init__(groupId = groupId, topics = "bounding_box")
        
    def receive_bounding_box(self):
        msg = self.consumer.poll(0)
        if msg is None:
            #print("Waiting...")
            pass
        elif msg.error():
            print("ERROR: %s".format(msg.error()))
        else:
            print("Consumed event from topic {topic}: offset = {offset} partition = {partition}".format(
                topic=msg.topic(), offset=msg.offset(), partition = msg.partition()))
            return True, json.loads(msg.value()), msg.offset()
        return False, 0, 0

