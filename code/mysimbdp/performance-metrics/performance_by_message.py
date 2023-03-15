import os
import argparse
import sys
import re
import statistics
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("log_file", help="Path to log file")
parser.add_argument("tenant", help="Name of the tenant")
args = parser.parse_args()

if not os.path.isfile(args.log_file):
    print(f"Error: File '{args.log_file}' does not exist.")
    exit()


if args.tenant == 'tenant1':
    time_regex = re.compile(r".*tenant1 Finished ingesting one message in (\d+\.\d+) seconds$")
elif args.tenant == 'tenant2':
    time_regex = re.compile(r".*tenant2 Finished ingesting one message in (\d+\.\d+) seconds$")
else:
    time_regex = re.compile(r".*Finished ingesting one message in (\d+\.\d+) seconds$")

durations = []

with open(args.log_file, "r") as log_file:
    for line in log_file:
        match = time_regex.match(line)
        if match:
            durations.append(float(match.group(1)))

if not durations:
    print("No INFO logs with time data found in the log file")
    sys.exit(1)

print(f"Number of messages processed: {len(durations)} by {args.tenant}")
print(f"Minimum time taken to process a message: {min(durations)} seconds by {args.tenant}")
print(f"Maximum time taken to process a message: {max(durations)} seconds by {args.tenant}")
print(f"Average time taken to process a message: {statistics.mean(durations)} seconds by {args.tenant}")

plt.hist(durations, bins=50)
plt.xlabel('Time taken to process one message (seconds)')
plt.ylabel('Number of messages')
plt.title('Histogram of message processing times')
plt.show()
