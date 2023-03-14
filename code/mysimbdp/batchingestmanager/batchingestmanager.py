import csv
import json
import os
import time
import datetime
from datetime import timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import argparse
from cassandra.cluster import Cluster
import logging

# cluster = Cluster(['cassandra1', 'cassandra2', 'cassandra3'])
cluster = Cluster()
session = cluster.connect()

parser = argparse.ArgumentParser()
parser.add_argument("staging_folder", help="Path to staging folder in mysimbdp")
parser.add_argument("config_models", help="Path to configuration models file")
parser.add_argument("log_file", help="Path to log file")
args = parser.parse_args()

if not os.path.isdir(args.staging_folder):
    print(f"Error: Directory '{args.staging_folder}' does not exist.")
    exit()

if not os.path.isfile(args.config_models):
    print(f"Error: File '{args.config_models}' does not exist.")
    exit()

if not os.path.isfile(args.log_file):
    print(f"Error: File '{args.log_file}' does not exist.")
    exit()

logging.basicConfig(filename=args.log_file, encoding='utf-8', level=logging.INFO,
                    format="%(asctime)s - %(levelname)s: %(message)s")

watch_dir = args.staging_folder


def validate(tenant, file_extension, file_size):
    with open(args.config_models, "r") as jsonfile:
        data = json.load(jsonfile)
        if tenant in data:
            try:
                model = data[tenant]
                session.execute("CREATE KEYSPACE IF NOT EXISTS " + model["namespace"] + " WITH REPLICATION = "
                                                                                        "{'class': 'SimpleStrategy', "
                                                                                        "'replication_factor': 3}")
                session.set_keyspace(model["namespace"])
                session.execute("CREATE TABLE IF NOT EXISTS batch_ingestion_metrics ("
                                "ingestion_time_start timestamp,"
                                "ingestion_time_end timestamp,"
                                "file_name text,"
                                "file_size float,"
                                "PRIMARY KEY (file_name)"
                                ")")
                if model["file_type"] != file_extension:
                    logging.error(f"{tenant} The extension '{file_extension}' is not supported")
                    return 1
                if file_size > model["max_file_size"]:
                    logging.error(
                        f"{tenant} {file_size} MB exceeds the limit of file size of {model['max_file_size']} MB")
                    return 1

                query = "SELECT SUM(file_size) FROM batch_ingestion_metrics WHERE ingestion_time_start >= %s AND ingestion_time_start <= %s ALLOW FILTERING"
                total_size_last_day = session.execute(query, [(datetime.datetime.today() - timedelta(days=1)),
                                                              datetime.datetime.today()]).one()

                query = "SELECT COUNT(*) FROM batch_ingestion_metrics WHERE ingestion_time_start >= %s AND ingestion_time_start <= %s ALLOW FILTERING"
                files_in_last_day = session.execute(query, [(datetime.datetime.today() - timedelta(days=1)),
                                                            datetime.datetime.today()]).one()

                if total_size_last_day[0] >= model["max_amount_of_data"]:
                    logging.error(
                        f"{tenant} The limit per day ({model['max_amount_of_data']} MB) has been reached. Current size is {total_size_last_day[0]} MB")
                    return 1

                if files_in_last_day[0] >= model["max_number_of_files"]:
                    logging.error(
                        f"{tenant} The limit of files per day ({model['max_number_of_files']}) has been reached. Current files is {files_in_last_day[0]}")
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
            if model["file_type"] == ".json":
                row["created_utc"] = datetime.datetime.utcfromtimestamp(row["created_utc"]).strftime(
                    "%Y-%m-%d %H:%M:%S")
                query = "INSERT INTO " + model["table_name"] + " JSON" + "'" + json.dumps(row) + "'"
                session.execute(query)
            else:
                query = "INSERT INTO " + model["table_name"] + " ("
                for field in model["schema"]:
                    if field != "key":
                        query += field + ","
                query = query[:-1] + ") VALUES ("
                for field in range(len(model["schema"]) - 1):
                    query += "%s,"
                query = query[:-1] + ")"
                row[0] = datetime.datetime.utcfromtimestamp(int(row[0])).strftime("%Y-%m-%d %H:%M:%S")
                session.execute(query, row)
        except Exception as e:
            logging.error(f"{tenant} an error occurred during ingestion {e}")


def ingest_csv_file(tenant, file, file_size):
    start_time = datetime.datetime.now()
    logging.info(f"{tenant} Started ingestion of csv file at {start_time}")
    with open(file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        for row in csvreader:
            insert_data(tenant, row)
    save_metrics(tenant, start_time, file, file_size)


def ingest_json_file(tenant, file, file_size):
    start_time = datetime.datetime.now()
    logging.info(f"{tenant} Started ingestion of json file at {start_time}")
    with open(file, "r") as jsonfile:
        data = json.load(jsonfile)
        for json_item in data:
            insert_data(tenant, json_item)
    save_metrics(tenant, start_time, file, file_size)


def save_metrics(tenant, start_time, file, file_size):
    session.set_keyspace(tenant)
    insert_query = "INSERT INTO batch_ingestion_metrics (ingestion_time_start, ingestion_time_end, file_name, file_size) VALUES (%s, %s, %s, %s)"
    finished_time = datetime.datetime.now()
    file = os.path.basename(file)
    session.execute(insert_query, (start_time, finished_time, file, file_size))
    logging.info(f"{tenant} Finished ingesting {file} at {finished_time} a total of {file_size} MB where processed")


class MyEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        input_file_name, input_file_extension = os.path.splitext(os.path.basename(event.src_path))
        tenant = input_file_name.split("-")[0]
        time.sleep(1)
        file_size_mb = os.path.getsize(event.src_path) / (1024.0 * 1024.0)
        logging.info(f"{tenant} Added {input_file_name}{input_file_extension}, with a size of {file_size_mb} MB")
        if validate(tenant, input_file_extension, file_size_mb) == 0:
            if input_file_extension == ".json":
                ingest_json_file(tenant, event.src_path, file_size_mb)
            else:
                ingest_csv_file(tenant, event.src_path, file_size_mb)
        else:
            logging.error(f"{tenant} An error occurred in the validation process")


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
