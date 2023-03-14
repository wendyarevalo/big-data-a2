import os
import argparse
from cassandra.cluster import Cluster
import logging

# cluster = Cluster(['cassandra1', 'cassandra2', 'cassandra3'])
cluster = Cluster()
session = cluster.connect()

parser = argparse.ArgumentParser()
parser.add_argument("log_file", help="Path to log file")
parser.add_argument("tenant", help="Name of the tenant")
args = parser.parse_args()

if not os.path.isfile(args.log_file):
    print(f"Error: File '{args.log_file}' does not exist.")
    exit()

logging.basicConfig(filename=args.log_file, encoding='utf-8', level=logging.INFO,
                    format="%(asctime)s - %(levelname)s: %(message)s")


session.set_keyspace(args.tenant)
query = "SELECT ingestion_time_start , ingestion_time_end, file_size FROM batch_ingestion_metrics LIMIT 100;"
rows = session.execute(query)
total_mb_per_second = 0
total_rows = 0
for row in rows:
    seconds = (row[1] - row[0]).total_seconds()
    mb_per_second = row[2]/seconds
    total_mb_per_second += mb_per_second
    total_rows += 1

logging.info(f"{args.tenant} Average MBs per second {total_mb_per_second/total_rows}")
