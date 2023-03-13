import csv
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="Path to input CSV file")
args = parser.parse_args()

if not os.path.isfile(args.input_file):
    print(f"Error: File '{args.input_file}' does not exist.")
    exit()

filtered_data = []
with open(args.input_file, 'r') as csvfile:
    csvreader = csv.reader(csvfile)

    next(csvreader)

    for row in csvreader:
        if len(row) >= 18 :
            filtered_row = [row[0], row[8], row[9], row[14], row[17]]
            filtered_data.append(filtered_row)

input_file_name = os.path.basename(args.input_file)
output_file_name = f"tenant2-{input_file_name}"
output_file_path = os.path.join("mysimbdp/client-staging-input-directory", output_file_name)
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

with open(output_file_path, "w", newline='') as outputcsv:
    writer = csv.writer(outputcsv)
    writer.writerow(["created_utc", "subreddit", "id", "author", "body"])
    for row in filtered_data:
        writer.writerow(row)

print(f"Filtered data written to '{output_file_path}'.")
