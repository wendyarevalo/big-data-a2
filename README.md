# Assignment Assignment_2  100517312

The project tree is the following:
1. code
   1. __client1__ and __client2:__
      1. clientbatchingestapp:
         * _move_to_provider.py_: a script that moves data to client-staging-input-directory
      2. clientstreamingestapp:
         * _kafka_producer.py_: a script that reads from a file and sends individual messages to messagingsystem
         * _send_report.py_: a script that reads logs from stats.log and sends a report to messagingsystem
         * _stats.log_: log that contains information from the messages sent by the producer.
      3. original-client-data:
         * json files (tenant1) and csv files (tenant2) of different sizes to test the environment.
   2. __mysimbdp:__
      1. batchingestmanager:
         * _batchingestmanager.py_: script in charge of monitoring the client-staging-input-directory to check if a new file was added and then ingest the data to coredms.
         * _config_model.json_: configuration models for batch ingestion from tenants.
      2. client-staging-input-directory: destination folder.
      3. coredms:
         * _docker-compose.yml_: creates Cassandra cluster in docker
      4. messagingsystem:
         1. streamingestmanager:
            * _kafka_consumer.py_: script in charge of receiving messages from tenants and streamingestmonitor. Messages from tenants get ingested to coredms.
         2. streamingestmonitor:
            * _receive_report.py_: script in charge of receiving reports from tenants about their delivery rates.
         3. _docker-compose.yml_: creates a kafka environment.
         4. _model-config.json_: configuration models for stream ingestion from tenants.
      5. performance-metrics:
         * _performance_by_file.py_: test to measure ingestion rates for single messages.
         * _performance_by_message.py_: test to measure ingestion rates for files.
   3. __requirements.txt:__ libraries for the project
2. data: empty, all samples are in the original-client-data-folder
3. logs:
   1. __ingestion_batch.log:__ success and errors from batch ingestion
   2. __ingestion_stream.log:__ success, errors, and reports from stream ingestion
4. reports:
   1. __images:__ images to complete the report
   2. __Assignment-2-Deployment.md:__ instructions to run the project
   3. __Assignment-2-report.md:__ design and answers to the questions


This project is far from perfect as has many repetitive code that can definitely be refactored in single units. Now is mostly not
hardcoded. 
It does not completely run in docker, however it is possible to have tenants and provider in diferent containers to emulate different 
networks, but maybe in the future.
It also needs to have some security measurements, like use credentials in the database, not using kafka over plain text connections,
having some authentication for tenants, among other things.
I hope my design is not overcomplicated :)