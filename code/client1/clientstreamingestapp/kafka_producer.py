from confluent_kafka import Producer
import json
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="Path to input JSON file")
parser.add_argument("topic", help="Name of the topic in kafka")
args = parser.parse_args()

if not os.path.isfile(args.input_file):
    print(f"Error: File '{args.input_file}' does not exist.")
    exit()

producer = Producer({
    "bootstrap.servers": "127.0.0.1:9092",
    "broker.address.family": "v4"
})


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {format(err)}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


with open(args.input_file, "r") as jsonfile:
    data = json.load(jsonfile)

for item in data:
    filtered_item = {
        "created_utc": item["created_utc"],
        "ups": item["ups"],
        "subreddit": item["subreddit"],
        "id": item["id"],
        "author": item["author"],
        "score": item["score"]
    }

    filtered_item_str = json.dumps(filtered_item)

    producer.produce(args.topic, value=filtered_item_str, callback=delivery_report)

    producer.flush()

input_file_name = os.path.basename(args.input_file)
print(f"All messages from '{input_file_name}' have been produced to the {args.topic} topic.")
