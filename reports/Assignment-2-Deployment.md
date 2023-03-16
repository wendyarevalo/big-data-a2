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

First create a virtual environment in python and install python requirements with these commands

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Start batchingestmanager
To start batch ingest manager for each tenant run the following command:
```shell
python mysimbdp/batchingestmanager/batchingestmanager.py mysimbdp/client-staging-input-directory mysimbdp/batchingestmanager/config_model.json ../logs/ingestion_batch.log tenantNumber
```
The first argument is the staging folder, the second argument is the configuration model file, then the log file to save logs, and finally the tenant number. To stop the watcher use CTRL+C
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

#### Test performance
Two performance tests are available to test batch ingestion, they can measure performance per individual tenant or by all, use the second
argument accordingly (_tenant1, tenant2_ or _all_):
1. Performance by message: give statistics on ingestion times per message. To try it run the following command:
```shell
python mysimbdp/performance-metrics/performance_by_message.py ../logs/ingestion_batch.log tenantNumber
```
2. Performance by file: give statistics on ingestion times per file. To try it run the following command:
```shell
python mysimbdp/performance-metrics/performance_by_file.py ../logs/ingestion_batch.log tenantNumber
```
Both tests show a graphic at the end.

## Part 2
For this part of the project I am following the [docker compose file](https://version.aalto.fi/gitlab/bigdataplatforms/cs-e4640/-/blob/master/tutorials/basickafka/docker-compose1.yml) provided in the tutorial, just added some modifications to work correctly in my environment.
I am also using the [confluent examples](https://github.com/confluentinc/confluent-kafka-python#usage) for producers and consumers, adding modifications to process data accordingly.

### Kafka environment

To start kafka environment use the following command:
```shell
docker-compose -f mysimbdp/messagingsystem/docker-compose.yml up -d
```
Create topics for both tenants:
```shell
docker exec messagingsystem-kafka-1 /opt/bitnami/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 2 --topic tenant1
```
```shell
docker exec messagingsystem-kafka-1 /opt/bitnami/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 2 --topic tenant2
```

And the topic for reports:

```shell
docker exec messagingsystem-kafka-1 /opt/bitnami/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 2 --topic tenant1-stats
```
```shell
docker exec messagingsystem-kafka-1 /opt/bitnami/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 2 --topic tenant2-stats
```

#### To start the __producers__: 

The first argument is the file that contains data, the second argument is the topic, the last parameter is the log file.

___For tenant1___

Use json files to process data. Sample files are in [original-client-data](../code/client1/original-client-data).
```shell
python client1/clientstreamingestapp/kafka_producer.py client1/original-client-data/1000rows.json tenant1 client1/clientstreamingestapp/stats.log
```
___For tenant2___ 

Use csv files to process data. Sample files are in [original-client-data](../code/client2/original-client-data)
```shell
python client2/clientstreamingestapp/kafka_producer.py client2/original-client-data/1000rows.csv tenant2 client2/clientstreamingestapp/stats.log
```

#### To start the __consumers__:

There can be more than one consumer, just increase the number of partitions in the kafka command for the creation of the topic.
The first argument is the topic, the second argument is the consumer group, third is the configuration models and lastly the log file.

___To read tenant1 messages:___
```shell
python mysimbdp/messagingsystem/streamingestmanager/kafka_consumer.py tenant1 mysimbdp mysimbdp/messagingsystem/model-config.json ../logs/ingestion_stream.log
```

___To read tenant2 messages:___
```shell
python mysimbdp/messagingsystem/streamingestmanager/kafka_consumer.py tenant2 mysimbdp mysimbdp/messagingsystem/model-config.json ../logs/ingestion_stream.log
```

### Test performance
One performance test is available to test stream ingestion, it can measure performance per individual tenant or by all, use the second
argument accordingly (_tenant1, tenant2_ or _all_):
1. Performance by message: give statistics on ingestion times per message. To try it run the following command:
```shell
python mysimbdp/performance-metrics/performance_by_message.py ../logs/ingestion_stream.log tenantNumber
```
The test shows a histogram at the end.

### Send reports from client
Each client has its own stats.log which contains information on how much time
a message took to get delivered.
To send the report to stream monitor run the following commands:

___tenant1:___
```shell
python client1/clientstreamingestapp/send-report.py client1/clientstreamingestapp/stats.log 2023-03-16 tenant1-stats
```

___tenant2:___
```shell
python client2/clientstreamingestapp/send-report.py client2/clientstreamingestapp/stats.log 2023-03-16 tenant2-stats
```

The first argument is the location of the log to analyze, then the date and the topic to
send the report. Change the date to the one desired one to generate the report.

### Receive reports from client
