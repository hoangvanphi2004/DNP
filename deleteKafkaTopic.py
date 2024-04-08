from confluent_kafka.admin import AdminClient, NewTopic
from configparser import ConfigParser

def deleteKafkaServer():
    config_parser = ConfigParser()
    config_parser.read("config.ini")
    config = dict(config_parser['default'])

    admin_client = AdminClient(config)
    new_topics = []

    admin_client.delete_topics(['bounding_box', 'frame', 'keypoints', 'latest_frame', 'setup'])
    print(admin_client.list_topics().topics)

deleteKafkaServer()