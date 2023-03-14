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

First create a virtual environment in python and install python requirements.

### Start batchingestmanager
To start batch ingest manager run the following command:
```shell
python mysimbdp/batchingestmanager/batchingestmanager.py mysimbdp/client-staging-input-directory mysimbdp/batchingestmanager/config_model.json
```
The first argument is the staging folder, the second argument is the configuration model file. To stop the watcher use CTRL+C
### Send files to client-staging-input-directory
I used a similar structure from the producers of assignment 1 for the move_to_provider.py files. 

Use the files from _clientNumber/original-client-data_ or create more data sets from the original reddit comments dataset. Each example tenant
has a set of test files (only uploaded the small ones).
#### From client 1 (json):

Run the following command using python:
```shell
python client1/clientbatchingestapp/move_to_provider.py client1/original-client-data/filename.json
```
#### From client 2 (csv):
Run the following command using python:
```shell
python client2/clientbatchingestapp/move_to_provider.py client2/original-client-data/filename.csv
```
If you want to try the constraints easily then just create/move new files directly to [client-staging-input-directory](../code/mysimbdp/client-staging-input-directory):
* To make fail the tenant constraint: use a prefix like _tenant23-_ or don't use a prefix. It won't process the file.
* To make fail the format constraint: use a non-correspondant file extension for a tenant, for example _tenant1-file.txt_. It won't process the file.
* To make fail the size constraint: use a bigger file, for tenant1 use bigger than 10 MB, for tenant2 use bigger than 50 MB.
* To make fail the files per day: upload 20 small files times for _tenant2_, after that it will fail.
* To make fail the size per day: upload a file bigger than 500 MB for tenant1.
* Another option is to modify [config_model.json](../code/mysimbdp/batchingestmanager/config_model.json) to smaller values.

To validate that data was inserted, directly query the database from any node. Don't forget to use the correspondant namespace.
