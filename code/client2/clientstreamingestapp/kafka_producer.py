import csv

from confluent_kafka import Producer
import json
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="Path to input CSV file")
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


with open(args.input_file, 'r') as csvfile:
    csvreader = csv.reader(csvfile)

    next(csvreader)

    for row in csvreader:
        if len(row) >= 18:
            filtered_row = [row[0], row[8], row[9], row[14], row[17]]
            filtered_item = {
                "created_utc": filtered_row[0],
                "subreddit": filtered_row[1],
                "id": filtered_row[2],
                "author": filtered_row[3],
                "body": filtered_row[4]
            }

            filtered_item_str = json.dumps(filtered_item)

            producer.produce(args.topic, value=filtered_item_str, callback=delivery_report)

            producer.flush()

input_file_name = os.path.basename(args.input_file)
print(f"All messages from '{input_file_name}' have been produced to the {args.topic} topic.")
