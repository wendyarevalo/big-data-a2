# Deployment guide

__Prerequisites__

* Docker
* Python

## Send files to client-staging-input-directory
I used a similar structure from the producers of assignment 1 for the move_to_provider.py files.
### From client 1:
Use the files from original-client-data or create more data sets from the original reddit comments dataset.
Run the following command using python:
```shell
python client1/clientbatchingestapp/move_to_provider.py client1/original-client-data/filename.json
```
### From client 2:
Use the files from original-client-data or create more data sets from the original reddit comments dataset.
Run the following command using python:
```shell
python client2/clientbatchingestapp/move_to_provider.py client2/original-client-data/filename.csv
```

