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
    size_time_regex = re.compile(r".*tenant1 Finished ingesting one file of (\d+\.\d+) MB in (\d+\.\d+) seconds$")
elif args.tenant == 'tenant2':
    size_time_regex = re.compile(r".*tenant2 Finished ingesting one file of (\d+\.\d+) MB in (\d+\.\d+) seconds$")
else:
    size_time_regex = re.compile(r".*Finished ingesting one file of (\d+\.\d+) MB in (\d+\.\d+) seconds$")

durations = []
sizes = []

with open(args.log_file, "r") as log_file:
    for line in log_file:
        match = size_time_regex.match(line)
        if match:
            sizes.append(float(match.group(1)))
            durations.append(float(match.group(2)))


if not durations and not sizes:
    print("No INFO log with size and time data found in the log file")
    sys.exit(1)

print(f"Number of files processed: {len(durations)} by {args.tenant}")
print(f"Minimum time taken to process a file: {min(durations)} seconds by {args.tenant}")
print(f"Maximum time taken to process a file: {max(durations)} seconds by {args.tenant}")
print(f"Average time taken to process a file: {statistics.mean(durations)} seconds by {args.tenant}")

print(f"Minimum file size: {min(sizes)} seconds by {args.tenant}")
print(f"Maximum file size: {max(sizes)} seconds by {args.tenant}")
print(f"Average file size: {statistics.mean(sizes)} seconds by {args.tenant}")

plt.scatter(sizes, durations)
plt.xlabel('File size (MB)')
plt.ylabel('Time taken to process file (seconds)')
plt.title('Relationship between file size and processing time')
plt.show()
