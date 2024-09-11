from confluent_kafka.admin import AdminClient, NewTopic
from configparser import ConfigParser
import time

def createKafkaServer():
    config_parser = ConfigParser()
    config_parser.read("config.ini")
    config = dict(config_parser['default'])

    admin_client = AdminClient(config)
    new_topics = []

    for name in ['bounding_box', 'frame', 'keypoints', 'latest_frame', 'setup', 'end']:
        topic_name = name
        num_partitions = 1
        replication_factor = 1
        new_topics.append(NewTopic(topic_name, num_partitions, replication_factor))

    admin_client.create_topics(new_topics)

createKafkaServer()