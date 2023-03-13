# Deployment guide

__Prerequisites__

* Docker
* Docker compose
* Python
* All commands are run inside the _code_ folder

## coredms - Cassandra

For coredms I used the same configuration for Cassandra as in assignment 1. 

To configure Cassandra, I have used the docker-compose.yml file provided in the tutorial
with the needed modifications to work in my environment. Assuming docker and docker compose
are installed and running, follow these steps:

1. Start the containers:
    ```
   docker-compose -f mysisbdp/coredms/docker-compose.yml up -d
    ```
## Part 1 - Batch Ingestion

### Start batchingestmanager
To start batch ingest manager run the following command:
```shell
python mysimbdp/batchingestmanager/batchingestmanager.py mysimbdp/client-staging-input-directory mysimbdp/batchingestmanager/config_model.json
```
The first argument is the staging folder, the second argument is the configuration model file. To stop the watcher use CTRL+C
### Send files to client-staging-input-directory
I used a similar structure from the producers of assignment 1 for the move_to_provider.py files.
#### From client 1:
Use the files from original-client-data or create more data sets from the original reddit comments dataset.
Run the following command using python:
```shell
python client1/clientbatchingestapp/move_to_provider.py client1/original-client-data/filename.json
```
#### From client 2:
Use the files from original-client-data or create more data sets from the original reddit comments dataset.
Run the following command using python:
```shell
python client2/clientbatchingestapp/move_to_provider.py client2/original-client-data/filename.csv
```
