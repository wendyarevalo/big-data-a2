from confluent_kafka import Consumer, Producer
import argparse
import json
import os
import re
import datetime
import statistics

parser = argparse.ArgumentParser()
parser.add_argument("topic", help="Name of the topic in kafka")
parser.add_argument("group", help="Name of the consumer group")
parser.add_argument("log_file", help="Path to log file")
args = parser.parse_args()

if not os.path.isfile(args.log_file):
    print(f"Error: File '{args.log_file}' does not exist.")
    exit()

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {format(err)}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def compare_to_local_stats(data):
    producer = Producer({
        "bootstrap.servers": "127.0.0.1:9092",
        "broker.address.family": "v4"
    })
    tenant = ""
    if 'tenant1' in args.topic:
        tenant = "tenant1"
        time_regex = re.compile(r".*tenant1 Finished ingesting one message in (\d+\.\d+) seconds$")
    elif 'tenant2' in args.topic:
        tenant = "tenant2"
        time_regex = re.compile(r".*tenant2 Finished ingesting one message in (\d+\.\d+) seconds$")

    durations = []

    with open(args.log_file, "r") as log_file:
        for line in log_file:
            match = time_regex.match(line)
            if match:
                timestamp_str = line.split()[0]
                timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d")
                if timestamp.date() == datetime.datetime.strptime(data["date"], "%Y-%m-%d").date():
                    durations.append(float(match.group(1)))

    message = {
        "type": "INFO",
        "content": tenant + " report is normal"
    }

    local_report = {
        "date": data["date"],
        "avg_ingestion_time": 0,
        "total_messages": 0
    }
    if durations:
        local_report = {
            "date": data["date"],
            "avg_ingestion_time": statistics.mean(durations),
            "total_messages": len(durations)
        }

        if data["total_messages"] > len(durations):
            message = {
                "type" : "ERROR",
                "content": tenant + " send more messages than the ones ingested."
            }

        avg_throughput_ingestion = 60 / statistics.mean(durations)
        avg_throughput_delivery = 60 / data["avg_delivery_time"]

        if avg_throughput_delivery > avg_throughput_ingestion:
            message = {
                "type": "ERROR",
                "content": tenant + " is sending more messages than the average ingestion throughput"
            }

    elif not durations and data["total_messages"] > 0:
        message = {
            "type": "ERROR",
            "content": tenant + " send more messages than the ones ingested."
        }

    elif not durations and data["total_messages"] == 0:
        message = {
                "type": "INFO",
                "content": tenant + " did not send any messages in the last day"
            }

    print(f"Local report: {local_report}")
    print(message)
    producer.produce('stream-monitor', value=json.dumps(message), callback=delivery_report)
    producer.flush()



consumer = Consumer({
    "bootstrap.servers": "127.0.0.1:9092",
    "broker.address.family": "v4",
    "group.id": args.group,
    "auto.offset.reset": "earliest"
})

consumer.subscribe([args.topic])

while True:
    report = consumer.poll(1.0)

    if report is None:
        continue
    if report.error():
        print(f"Consumer error: {report.error()}")
        continue
    else:
        data = json.loads(report.value().decode('utf-8'))
        print(f"Received report: {data}")
        compare_to_local_stats(data)

consumer.close()
