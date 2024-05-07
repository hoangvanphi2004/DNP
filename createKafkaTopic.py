from confluent_kafka.admin import AdminClient, NewTopic
from configparser import ConfigParser
import time

def createKafkaServer():
    config_parser = ConfigParser()
    config_parser.read("config.ini")
    config = dict(config_parser['default'])

    admin_client = AdminClient(config)
    new_topics = []

    for name in ['bounding_box', 'frame', 'keypoints', 'latest_frame', 'setup']:
        topic_name = name
        num_partitions = 1
        replication_factor = 1
        new_topics.append(NewTopic(topic_name, num_partitions, replication_factor))

    admin_client.create_topics(new_topics)
    # admin_client.delete_topics(['bounding_box', 'frame'])
    print(admin_client.list_topics().topics)

createKafkaServer()