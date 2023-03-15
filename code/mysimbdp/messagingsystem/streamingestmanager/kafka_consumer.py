from confluent_kafka import Consumer, KafkaError
import argparse
import json
from cassandra.cluster import Cluster
import logging
import os
import datetime

cluster = Cluster()
session = cluster.connect()

parser = argparse.ArgumentParser()
parser.add_argument("topic", help="Name of the topic in kafka")
parser.add_argument("group", help="Name of the consumer group")
parser.add_argument("config_models", help="Path to configuration models file")
parser.add_argument("log_file", help="Path to log file")
args = parser.parse_args()

if not os.path.isfile(args.config_models):
    print(f"Error: File '{args.config_models}' does not exist.")
    exit()

if not os.path.isfile(args.log_file):
    print(f"Error: File '{args.log_file}' does not exist.")
    exit()

logging.basicConfig(filename=args.log_file, encoding='utf-8', level=logging.INFO,
                    format="%(asctime)s - %(levelname)s: %(message)s")


def validate(tenant):
    with open(args.config_models, "r") as jsonfile:
        data = json.load(jsonfile)
        if tenant in data:
            try:
                model = data[tenant]
                session.execute("CREATE KEYSPACE IF NOT EXISTS " + model["namespace"] + " WITH REPLICATION = "
                                                                                        "{'class': 'SimpleStrategy', "
                                                                                        "'replication_factor': 3}")
                session.set_keyspace(model["namespace"])
                session.execute("CREATE TABLE IF NOT EXISTS stream_ingestion_metrics ("
                                "today date,"
                                "topic text,"
                                "received_messages counter,"
                                "PRIMARY KEY ((today), topic))")

                query = "SELECT received_messages FROM stream_ingestion_metrics WHERE today = %s AND topic = %s"
                total_messages_today = session.execute(query, [datetime.datetime.now().strftime("%Y-%m-%d"), tenant]).one()
                if total_messages_today is not None:
                    if total_messages_today[0] >= model["max_messages_per_day"]:
                        logging.error(
                            f"{tenant} The limit of messages per day ({model['max_messages_per_day']}) has been reached. Current messages {total_messages_today[0]}")
                        return 1

                create_schema(tenant)
                return 0

            except Exception as e:
                logging.error(f"{tenant} an error occurred during validation {e}")
                return 1
        else:
            logging.error(f"{tenant} Does not exist in the configuration file.")
            return 1


def create_schema(tenant):
    with open(args.config_models, "r") as jsonfile:
        data = json.load(jsonfile)
        try:
            model = data[tenant]
            query = "CREATE TABLE IF NOT EXISTS " + model["table_name"] + " ("
            for field in model["schema"]:
                if field != "key":
                    query += field + " " + model["schema"][field] + ", "
                else:
                    query += "PRIMARY KEY " + model["schema"][field] + ")"
            session.execute(query)
        except Exception as e:
            logging.error(f"{tenant} an error occurred in the creation of the schema {e}")


def insert_data(tenant, row):
    session.set_keyspace(tenant)
    with open(args.config_models, "r") as jsonfile:
        data = json.load(jsonfile)
        try:
            model = data[tenant]
            row["created_utc"] = datetime.datetime.utcfromtimestamp(int(row["created_utc"])).strftime(
                "%Y-%m-%d %H:%M:%S")
            query = "INSERT INTO " + model["table_name"] + " JSON" + "'" + json.dumps(row) + "'"

            start_time = datetime.datetime.now()
            session.execute(query)
            finished_time = datetime.datetime.now()
            seconds = (finished_time - start_time).total_seconds()
            logging.info(f"{tenant} Finished ingesting one message in {seconds} seconds")

            query = "UPDATE stream_ingestion_metrics SET received_messages = received_messages + 1 WHERE today = %s AND topic = %s;"
            session.execute(query, [datetime.datetime.now().strftime("%Y-%m-%d"), tenant])
        except Exception as e:
            logging.error(f"{tenant} an error occurred during ingestion {e}")


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
        if validate(args.topic) == 0:
            insert_data(args.topic, data)
            print(f"Received message: {data}")
        else:
            logging.error(f"{args.topic} An error occurred in the validation process")


consumer.close()
