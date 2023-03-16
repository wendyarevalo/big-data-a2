import os
import argparse
import sys
import re
import statistics
import datetime
from confluent_kafka import Producer
import json

parser = argparse.ArgumentParser()
parser.add_argument("log_file", help="Path to log file")
parser.add_argument("date", help="Day to search in format YYYY-MM-DD")
parser.add_argument("topic", help="Topic to send report")
args = parser.parse_args()

if not os.path.isfile(args.log_file):
    print(f"Error: File '{args.log_file}' does not exist.")
    exit()

producer = Producer({
    "bootstrap.servers": "127.0.0.1:9092",
    "broker.address.family": "v4"
})


def delivery_report(err, msg):
    if err is not None:
        print(f"Report delivery failed: {format(err)}")
    else:
        print(f"Report delivered to {msg.topic()} [{msg.partition()}]")


time_regex = re.compile(r".*Finished delivering one message in (\d+\.\d+) seconds$")

durations = []

with open(args.log_file, "r") as log_file:
    for line in log_file:
        match = time_regex.match(line)
        if match:
            timestamp_str = line.split()[0]
            print(timestamp_str)
            timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d")
            if timestamp.date() == datetime.datetime.strptime(args.date, "%Y-%m-%d").date():
                durations.append(float(match.group(1)))

report = {
    "date": args.date,
    "avg_ingestion_time": 0.0,
    "total_messages": 0
   }
if not durations:
    print("No INFO logs with time data found in the log file")
    producer.produce(args.topic, value=json.dumps(report), callback=delivery_report)
    producer.poll(1)
    sys.exit(1)

report["avg_ingestion_time"] = statistics.mean(durations)
report["total_messages"] = len(durations)

print(report)
producer.produce(args.topic, value=json.dumps(report), callback=delivery_report)
producer.poll(1)