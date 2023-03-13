import json
import os
import time
import datetime
from datetime import timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import argparse
from cassandra.cluster import Cluster

# cluster = Cluster(['cassandra1', 'cassandra2', 'cassandra3'])
cluster = Cluster()
session = cluster.connect()

parser = argparse.ArgumentParser()
parser.add_argument("staging_folder", help="Path to staging folder in mysimbdp")
parser.add_argument("config_models", help="Path to configuration models file")
args = parser.parse_args()

if not os.path.isdir(args.staging_folder):
    print(f"Error: Directory '{args.staging_folder}' does not exist.")
    exit()

if not os.path.isfile(args.config_models):
    print(f"Error: File '{args.config_models}' does not exist.")
    exit()

watch_dir = args.staging_folder


def validate(tenant, file_extension, file_size):
    with open(args.config_models, "r") as jsonfile:
        data = json.load(jsonfile)
        try:
            model = data[tenant]
            session.execute("CREATE KEYSPACE IF NOT EXISTS " + model["namespace"] + " WITH REPLICATION = "
                                                                                    "{'class': 'SimpleStrategy', "
                                                                                    "'replication_factor': 3}")
            session.set_keyspace(model["namespace"])
            session.execute("CREATE TABLE IF NOT EXISTS batch_ingestion_metrics ("
                            "ingestion_time timestamp,"
                            "file_size float,"
                            "PRIMARY KEY (ingestion_time)"
                            ")")
            if model["file_type"] != file_extension:
                print(f"Error: The extension '{file_extension}' is not supported for {tenant}.")
                return 1
            if file_size > model["max_file_size"]:
                print(f"Error: This file exceeds the limit of file size set for {tenant}.")
                return 1

            query = "SELECT SUM(file_size) FROM batch_ingestion_metrics WHERE ingestion_time >= %s AND ingestion_time <= %s ALLOW FILTERING"
            total_size_last_day = session.execute(query, [(datetime.datetime.today() - timedelta(days=1)),
                                                          datetime.datetime.today()]).one()

            query = "SELECT COUNT(*) FROM batch_ingestion_metrics WHERE ingestion_time >= %s AND ingestion_time <= %s ALLOW FILTERING"
            files_in_last_day = session.execute(query, [(datetime.datetime.today() - timedelta(days=1)),
                                                        datetime.datetime.today()]).one()

            if total_size_last_day[0] > model["max_amount_of_data"]:
                print(f"Error: This file exceeds the limit of total size per day set for {tenant}.")
                return 1

            if files_in_last_day[0] > model["max_number_of_files"]:
                print(f"Error: This file exceeds the limit of files per day set for {tenant}.")
                return 1

            return 0

        except Exception:
            print(f"Error: {tenant} does not have a configuration model.")
            return 1


def ingestCsvFile(tenant, file, file_size):
    session.set_keyspace(tenant)

    saveMetrics(tenant, file_size)


def ingestJsonFile(tenant, file, file_size):
    session.set_keyspace(tenant)
    saveMetrics(tenant, file_size)


def saveMetrics(tenant, file_size):
    session.set_keyspace(tenant)
    insert_query = "INSERT INTO batch_ingestion_metrics (ingestion_time, file_size) VALUES (%s, %s)"
    session.execute(insert_query, (datetime.datetime.now(), file_size))


class MyEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        input_file_name, input_file_extension = os.path.splitext(os.path.basename(event.src_path))
        tenant = input_file_name.split("-")[0]
        time.sleep(1)
        file_size_mb = os.path.getsize(event.src_path) / (1024.0 * 1024.0)
        print(f"{tenant} added {input_file_name}{input_file_extension}, with a size of {file_size_mb} MB")
        if validate(tenant, input_file_extension, file_size_mb) == 0:
            if input_file_extension == ".json":
                ingestJsonFile()
            else:
                ingestCsvFile()
        else:
            print(f"An error occurred in the ingestion process")

event_handler = MyEventHandler()
observer = Observer()
observer.schedule(event_handler, watch_dir, recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
