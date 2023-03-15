from confluent_kafka import Consumer, KafkaError
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("topic", help="Name of the topic in kafka")
parser.add_argument("group", help="Name of the consumer group")
args = parser.parse_args()

consumer = Consumer({
    "bootstrap.servers": "127.0.0.1:9092",
    "broker.address.family": "v4",
    "group.id": args.group,
    "auto.offset.reset": "earliest"
})

consumer.subscribe([args.topic])

while True:
    msg = consumer.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print(f"Consumer error: {msg.error()}")
        continue
    else:
        data = json.loads(msg.value().decode('utf-8'))
        print(f"Received message: {data}")

consumer.close()
