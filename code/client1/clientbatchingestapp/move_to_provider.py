import json
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="Path to input JSON file")
args = parser.parse_args()

if not os.path.isfile(args.input_file):
    print(f"Error: File '{args.input_file}' does not exist.")
    exit()

with open(args.input_file, "r") as jsonfile:
    data = json.load(jsonfile)

filtered_data = []
for item in data:
    filtered_item = {
        "created_utc": item["created_utc"],
        "ups": item["ups"],
        "subreddit": item["subreddit"],
        "id": item["id"],
        "author": item["author"],
        "score": item["score"]
    }
    filtered_data.append(filtered_item)

input_file_name = os.path.basename(args.input_file)
output_file_name = f"tenant1-{input_file_name}"
output_file_path = os.path.join("mysimbdp/client-staging-input-directory", output_file_name)
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

with open(output_file_path, "w") as outputjson:
    json.dump(filtered_data, outputjson, indent=2)

print(f"Filtered data written to '{output_file_path}'.")