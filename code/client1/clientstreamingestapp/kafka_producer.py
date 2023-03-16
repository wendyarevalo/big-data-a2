from confluent_kafka import Producer
import json
import argparse
import os
import logging
import datetime

parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="Path to input JSON file")
parser.add_argument("topic", help="Name of the topic in kafka")
parser.add_argument("log_file", help="Path to output log file")
args = parser.parse_args()

if not os.path.isfile(args.input_file):
    print(f"Error: File '{args.input_file}' does not exist.")
    exit()

if not os.path.isfile(args.log_file):
    print(f"Error: File '{args.log_file}' does not exist.")
    exit()

logging.basicConfig(filename=args.log_file, encoding='utf-8', level=logging.INFO,
                    format="%(asctime)s - %(levelname)s: %(message)s")


producer = Producer({
    "bootstrap.servers": "127.0.0.1:9092",
    "broker.address.family": "v4"
})


def delivery_report(err, msg):
    if err is not None:
        logging.error(f"Message delivery failed: {format(err)}")
        print(f"Message delivery failed: {format(err)}")
    else:
        start_time = datetime.datetime.utcfromtimestamp(msg.timestamp()[1] / 1000.0)
        finished_time = datetime.datetime.utcnow()
        seconds = (finished_time - start_time).total_seconds()
        logging.info(f"Finished delivering one message in {seconds} seconds")
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] in {seconds} seconds")


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

    producer.poll(1)

input_file_name = os.path.basename(args.input_file)
print(f"All messages from '{input_file_name}' have been produced to the {args.topic} topic.")
